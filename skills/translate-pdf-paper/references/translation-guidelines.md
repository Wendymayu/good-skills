# Translation Guidelines — Subagent Prompt Template

This is the prompt body to give EACH parallel translation subagent. Customize per chunk: chunk number, page/char range, input file, output file, and the figure list for that chunk.

---

You are translating a portion of an academic document from English into fluent, academic Simplified Chinese, producing Markdown.

**TASK:** Translate the assigned chunk completely and faithfully. Do NOT summarize, abbreviate, or skip any content — translate every paragraph fully.

**INPUT:** Read `<chunkN.txt>` — flowing English text (no page markers).
**OUTPUT:** Write translated Markdown to `<out_chunkN.md>`. Return ONLY a one-line confirmation; do NOT put the translation in your reply.

## Translation rules

1. **Fluent academic Simplified Chinese**, standard AI/ML terminology.
2. **Key terms:** on first use give Chinese then (English): e.g. 自演化智能体（self-evolving agents）. Thereafter Chinese alone is fine.
3. **Keep in ENGLISH, unchanged:**
   - Method / system / dataset / benchmark names (SCA, RAGEN, TextGrad, Voyager, WebArena, SWE-bench…).
   - Author citations exactly as-is: `(Zhou et al., 2025e)`.
   - Standard metric terms may stay English (Pass Rate, Success Rate, F1, ROUGE, Accuracy).
   - Math symbols, formulas, equations: keep as-is.
4. **Headings:** translate the text, keep the numbering. `3 What to Evolve?` → `3 演化什么？`. `3.1 Models` → `3.1 模型`.
5. **Strip running headers/footers:** delete the venue running header (e.g. `Published in Transactions on Machine Learning Research (01/2026)`) and any line that is ONLY a page number (a line that is just `9` or `10`).
6. **Hyphenation artifacts:** the extractor breaks words across lines with hyphens (`self-\nevolving`, `Adapt-\nive`, `Generaliza-\ntion`). Rejoin them (`self-evolving`, `Adaptive`, `Generalization`) BEFORE translating.
7. **Preserve** paragraph breaks and bullet lists.

## Figures (only those listed for your chunk)

When you reach a caption line `Figure N: …`, replace the figure + caption with EXACTLY this block (do not also output the English caption separately):

```
![图N](images/figureN.png)

**图N：** <translated caption text>
```

Combine a multi-line caption into one. Figures for this chunk: `<e.g. Figure 3 (images/figure3.png), Figure 4 (images/figure4.png)>`.

## Tables

The PDF extractor breaks tables into a **vertical cell sequence** (one cell or cell-fragment per line) but ALL data is present. Reconstruct each as a clean Markdown table:

- Caption `Table N: …` → output `**表N：** <translated caption>` then a blank line then the markdown table.
- Read the column headers (listed at the top of the table block). A new row begins at each leftmost-column entity (method / benchmark / metric name); cells follow in column order — each row has the same number of cells as columns.
- Translate natural-language cell content (`Scientific Data Analysis` → `科学数据分析`, `Web Search / Browse` → `网页搜索/浏览`). Keep names, metric names, numbers, and citations as-is.
- `✓`/`✗` marks: keep as-is. `•`/`◦` filled/hollow bullets: keep as-is (they mean “actively evolves” vs not). Time-scope labels may be translated: `Static`→`静态`, `Long-horizon`→`长时序`, `Short-horizon`→`短时序`.
- **If a table is genuinely unreconstructable** from the scrambled text, output the translated caption + `（此表较复杂，详见原文 Table N）` + your best-effort partial table. Prefer full reconstruction.

## Sentence-boundary seams (IMPORTANT)

Your chunk starts and ends at a **sentence boundary**, so no sentence is split across chunks. Do NOT prepend `……` or repeat the previous chunk’s last words. If your chunk happens to begin with a sentence fragment (lowercase, no subject) that visibly continues a prior sentence, translate just that fragment as-is — the assembler joins it to the preceding chunk.

## References / bibliography

If your chunk contains the reference list (entries like `Author, A. Title. Venue, year.`), **keep it in the original English** — do NOT translate reference entries (translating corrupts the bibliographic record). Just preserve them verbatim; you may join a single entry’s wrapped lines into one line. Output a single heading `## 参考文献（References）` once, above the list, then the entries.

---

## Why these rules exist (common failure modes this prevents)

| Without the rule | What goes wrong |
|---|---|
| Translate inline in one agent | A 77-page PDF (~320k chars) blows the context window; quality collapses mid-document. → dispatch parallel subagents that write to files and return only a one-line confirmation. |
| Render tables as images | Loses the ability to translate cell text; a comparison matrix becomes an un-translatable picture. → reconstruct as Markdown from the cell sequence. |
| Extract embedded images for figures | Many “images” are tile fragments or the figure is vector (no raster). → render the figure REGION (union of image rects, or full-page-above-caption for vector). |
| Split chunks on page boundaries | Sentences that span page breaks get duplicated or fragmented across chunks. → split at sentence boundaries (terminal punctuation). |
| Translate the reference list | Author names/titles become meaningless in another language and citations break. → keep bibliography in original language, unnumbered, single heading. |
| Leave hyphens / running headers | `self-\nevolving` stays broken; “Published in…” noise pollutes every page. → rejoin hyphens; strip running headers + page numbers. |
