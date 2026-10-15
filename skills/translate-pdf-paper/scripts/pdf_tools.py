#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pdf_tools.py — mechanical helpers for the translate-pdf-paper skill.

The agent drives the workflow; this script handles the parts that should NOT
be left to an LLM: PDF parsing, figure-region cropping, char-balanced chunking
that splits at sentence boundaries (so no sentence spans chunks), assembly, and
post-assembly cleanup of references / markers / blank lines.

Requires: PyMuPDF  (`pip install PyMuPDF`). Import as `pymupdf` (the `fitz`
alias is deprecated).

Subcommands:
  analyze <pdf>                       -> figures.json + tables.json + prints a summary
  extract  <pdf> <out.txt>            -> per-page text with "===== PAGE N =====" markers
  render-figures <pdf> <images-dir> [figures.json]   -> figureN.png crops
  chunk <all_text.txt> <n> <out_dir>  -> n char-balanced chunks split at sentence boundaries
  assemble <header.md> <out.md> <chunk1> [chunk2 ...]  -> concatenated output
  cleanup <out.md> [ref_heading]      -> normalize references / strip markers / collapse blanks

Run `python pdf_tools.py <cmd> --help` for per-command options.
"""
import sys, os, re, json, argparse

try:
    import pymupdf
except ImportError:
    sys.exit("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF")

FIG_RE = re.compile(r'(?:Figure|Fig\.)\s*(\d+)\s*[:.]?\s', re.I)
TBL_RE = re.compile(r'(?:Table|Tab\.)\s*(\d+)\s*[:.]?\s', re.I)
# caption form used by most venues (arXiv/TMLR/NeurIPS/ICML): "Figure N:" / "Table N:"
FIG_CAP = re.compile(r'(?:Figure|Fig\.)\s*(\d+)\s*:')
TBL_CAP = re.compile(r'(?:Table|Tab\.)\s*(\d+)\s*:')
# Sentence-boundary detector for chunking. A boundary is a terminal-punctuation char
# (. ! ? 。 ！ ？ …) followed by optional closing quote/paren/bracket, then whitespace,
# then a CAPITAL letter or opening paren/quote (the start of the next sentence).
#
# The lookahead is what filters out non-sentence periods:
#   "et al.,"  -> period then comma (no whitespace)     -> no match
#   "e.g.,"    -> same                                    -> no match
#   "Fig. 2"   -> period then space then DIGIT          -> no match (lookahead wants [A-Z("])
#   "arXiv:2409.08264" -> period then DIGIT, no space    -> no match
#   "openreview.net/"  -> period then non-space          -> no match (URL safe)
#   "Smith et al. (2023) showed" -> period, " ", "("     -> match (starts a real sentence)
# Excludes "\n" alone (PDF line breaks mid-sentence) and ";" (splits inside citations).
_SENT_END = re.compile(r'[。！？]|[.!?][^A-Za-z0-9\s]?\s+(?=[A-Z("])')


# --------------------------------------------------------------------------------------
# ANALYZE
# --------------------------------------------------------------------------------------
def _caption_y(page, num, kind):
    """y-position of the 'Figure N:' / 'Table N:' caption line on this page, or None."""
    pat = re.compile(rf'^{kind}\s*{num}\s*[:.]', re.I)
    for b in page.get_text("dict").get("blocks", []):
        for l in b.get("lines", []):
            full = "".join(s["text"] for s in l.get("spans", [])).strip()
            if pat.match(full):
                return l["bbox"][1]
    return None


def _image_union(page):
    """Union bbox of all raster images on a page, or None if there are none."""
    pts = []
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            pts += [(r.x0, r.y0), (r.x1, r.y1)]
    if not pts:
        return None
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def _figure_region(page, cap_y):
    """Region for a figure on this page.
    Raster figure -> union of image rects (padded). Vector figure (no raster) ->
    full width from page top down to the caption."""
    ib = _image_union(page)
    if ib:
        pad = 8
        return (max(0, ib[0] - pad), max(0, ib[1] - pad),
                min(page.rect.width, ib[2] + pad), min(page.rect.height, ib[3] + pad))
    # vector: from top margin to just above the caption
    return (20, 40, page.rect.width - 20, max(50, cap_y - 4))


def cmd_analyze(args):
    doc = pymupdf.open(args.pdf)
    figures, tables = {}, {}
    page_chars = []
    for i, page in enumerate(doc):
        txt = page.get_text()
        page_chars.append(len(txt))
        # colon-form caption scan (reliable for arXiv/TMLR/NeurIPS/ICML style).
        # NOTE: period form ("Figure N.") is NOT scanned — it collides with body
        # references ("Figure 1. Recent research…") and mis-assigns the page. If a
        # paper uses period-form captions, the agent verifies/edits figures.json by hand.
        for rx, store in ((FIG_CAP, figures), (TBL_CAP, tables)):
            for m in rx.finditer(txt):
                num = int(m.group(1))
                store.setdefault(num, i + 1)  # keep the FIRST page each is captioned
    # build figure records with render regions
    figs = []
    for num in sorted(figures):
        pno = figures[num]
        page = doc[pno - 1]
        cap_y = _caption_y(page, num, "Figure") or _caption_y(page, num, "Fig")
        region = _figure_region(page, cap_y or (page.rect.height - 60))
        figs.append({"num": num, "page": pno, "caption": f"Figure {num}",
                     "region": [round(c, 1) for c in region]})
    tbls = [{"num": n, "page": tables[n], "caption": f"Table {n}"} for n in sorted(tables)]
    json.dump(figs, open("figures.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(tbls, open("tables.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    tot = sum(page_chars)
    print(f"pages={doc.page_count} total_chars={tot} figures={len(figs)} tables={len(tbls)}")
    for f in figs:
        print(f"  Figure {f['num']}: page {f['page']} -> images/figure{f['num']}.png")
    for t in tbls:
        print(f"  Table {t['num']}: page {t['page']}")
    n = max(2, -(-tot // 40000))
    print(f"suggested_chunks={n}")
    return 0


# --------------------------------------------------------------------------------------
# EXTRACT
# --------------------------------------------------------------------------------------
def cmd_extract(args):
    doc = pymupdf.open(args.pdf)
    with open(args.out, "w", encoding="utf-8") as f:
        for i, page in enumerate(doc):
            f.write(f"\n\n===== PAGE {i+1} =====\n\n")
            f.write(page.get_text())
    print(f"wrote {args.out} ({doc.page_count} pages)")
    return 0


# --------------------------------------------------------------------------------------
# RENDER FIGURES
# --------------------------------------------------------------------------------------
def cmd_render(args):
    doc = pymupdf.open(args.pdf)
    figs = json.load(open(args.figures, encoding="utf-8")) if args.figures and os.path.exists(args.figures) \
           else json.load(open("figures.json", encoding="utf-8")) if os.path.exists("figures.json") else None
    if not figs:
        sys.exit("No figures.json found. Run `analyze` first (or pass --figures).")
    os.makedirs(args.dir, exist_ok=True)
    mat = pymupdf.Matrix(args.zoom, args.zoom)
    for f in figs:
        page = doc[f["page"] - 1]
        r = pymupdf.Rect(f["region"])
        r = pymupdf.Rect(max(0, r.x0), max(0, r.y0),
                         min(page.rect.width, r.x1), min(page.rect.height, r.y1))
        pix = page.get_pixmap(matrix=mat, clip=r)
        out = os.path.join(args.dir, f"figure{f['num']}.png")
        pix.save(out)
        print(f"Figure {f['num']} (page {f['page']}) -> {out} ({pix.width}x{pix.height})")
    return 0


# --------------------------------------------------------------------------------------
# CHUNK  (split flowing text into n parts at sentence boundaries)
# --------------------------------------------------------------------------------------
def _flowing_text(path):
    """Strip PAGE markers -> one continuous stream of text (paragraphs preserved)."""
    txt = open(path, encoding="utf-8").read()
    txt = re.sub(r'\n*===== PAGE \d+ =====\s*\n*', '\n\n', txt)
    return txt


def _split_at_sentences(txt, n, target):
    """Split txt into n chunks ending at sentence boundaries near `target` chars.

    Pre-computes every sentence-boundary position via `_SENT_END`, then for each chunk
    picks the FIRST boundary at/after the target offset for that chunk — so every chunk
    ends at a real sentence end and no sentence spans chunks. Fallback: if a 1.5x-target
    stretch has no boundary (a long formula/table/reference block), cut at a newline.
    """
    bounds = [m.end() for m in _SENT_END.finditer(txt)]
    B, L = len(bounds), len(txt)
    chunks, start, bi = [], 0, 0
    for _ in range(n - 1):
        goal = start + target
        while bi < B and bounds[bi] < goal:        # advance to first boundary >= goal
            bi += 1
        cut = None
        if bi < B and bounds[bi] - start < int(target * 1.5):  # boundary close enough
            cut = bounds[bi]
            bi += 1
        if cut is None:                           # runaway: no boundary near target
            nl = txt.find('\n', goal)
            cut = (nl + 1) if nl != -1 else L
            if cut <= start or cut >= L:
                break
        chunks.append(txt[start:cut])
        start = cut
    chunks.append(txt[start:])                    # remainder -> final chunk
    return chunks


def cmd_chunk(args):
    txt = _flowing_text(args.text)
    n = args.n
    target = len(txt) // n
    parts = _split_at_sentences(txt, n, target)
    os.makedirs(args.out_dir, exist_ok=True)
    # figure captions: which chunk index holds each "Figure N:" caption?
    figs = json.load(open("figures.json", encoding="utf-8")) if os.path.exists("figures.json") else []
    fig_map = {}
    cursor = 0
    for idx, part in enumerate(parts):
        end = cursor + len(part)
        for f in figs:
            cap = f["caption"].split(":")[0] + ":"  # e.g. "Figure 3:"
            if cap in part or f"Figure {f['num']}:" in part or f"Fig. {f['num']}:" in part:
                fig_map.setdefault(idx, []).append(f["num"])
        cursor = end
    for idx, part in enumerate(parts):
        path = os.path.join(args.out_dir, f"chunk{idx+1}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(part)
        figs_here = fig_map.get(idx, [])
        print(f"chunk{idx+1}: {len(part)} chars{', figures=' + str(figs_here) if figs_here else ''} -> {path}")
    print("(pass these figure lists to each translation subagent)")
    return 0


# --------------------------------------------------------------------------------------
# ASSEMBLE
# --------------------------------------------------------------------------------------
def cmd_assemble(args):
    with open(args.out, "w", encoding="utf-8") as out:
        if args.header and os.path.exists(args.header):
            out.write(open(args.header, encoding="utf-8").read())
            if not out.tell() == 0:
                out.write("\n\n")
        for i, p in enumerate(args.chunks, 1):
            t = open(p, encoding="utf-8").read()
            out.write("\n\n")
            out.write(t)
            if not t.endswith("\n"):
                out.write("\n")
    print(f"assembled {len(args.chunks)} chunks -> {args.out} ({os.path.getsize(args.out)} bytes)")
    return 0


# --------------------------------------------------------------------------------------
# CLEANUP
# --------------------------------------------------------------------------------------
def cmd_cleanup(args):
    s = open(args.out, encoding="utf-8").read()
    orig = len(s)
    # 1. references: keep ONE heading, strip "N. " numeric prefixes, drop duplicate headings
    ref_pat = re.compile(r'^(#+\s*(?:参考文献|References))\s*$', re.M)
    heads = list(ref_pat.finditer(s))
    if heads:
        first = heads[0]
        tail = s[first.end():]
        tail = re.sub(r'\n+#+\s*(?:参考文献|References)\s*\n*', '\n', tail)        # dup headings
        tail = re.sub(r'(?m)^\d{1,3}\.\s+', '', tail)                                # "12. " prefixes (skip 4-digit years)
        s = s[:first.end()] + tail
    # 2. strip leading "……" continuation markers that subagents may add at chunk starts
    s = re.sub(r'(?m)^…+\s*', '', s)
    # 3. remove chunk provenance markers
    s = re.sub(r'\n*<!-- chunk[^>]*-->\s*\n*', '\n', s)
    # 4. collapse 3+ blank lines
    s = re.sub(r'\n{3,}', '\n\n', s)
    s = s.strip() + "\n"
    open(args.out, "w", encoding="utf-8").write(s)
    n_fig = len(re.findall(r'!\[图\d|!\[Figure', s))
    n_tab = len(re.findall(r'^\*\*表\d|^\*\*Table', s, re.M))
    print(f"cleanup: {orig} -> {len(s)} chars | figure refs={n_fig} table captions={n_tab}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="PDF translation helpers (translate-pdf-paper skill).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze"); a.add_argument("pdf"); a.set_defaults(fn=cmd_analyze)
    a = sub.add_parser("extract"); a.add_argument("pdf"); a.add_argument("out"); a.set_defaults(fn=cmd_extract)
    a = sub.add_parser("render-figures"); a.add_argument("pdf"); a.add_argument("dir")
    a.add_argument("--figures"); a.add_argument("--zoom", type=float, default=3.0); a.set_defaults(fn=cmd_render)
    a = sub.add_parser("chunk"); a.add_argument("text"); a.add_argument("n", type=int); a.add_argument("out_dir")
    a.set_defaults(fn=cmd_chunk)
    a = sub.add_parser("assemble"); a.add_argument("header"); a.add_argument("out")
    a.add_argument("chunks", nargs="+"); a.set_defaults(fn=cmd_assemble)
    a = sub.add_parser("cleanup"); a.add_argument("out"); a.set_defaults(fn=cmd_cleanup)

    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
