#!/usr/bin/env python3
"""Generate a structured markdown report from combined research results."""

import argparse
import json
import sys
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path


def title_similarity(a: str, b: str) -> float:
    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    if not tokens_a or not tokens_b:
        return 0.0
    return SequenceMatcher(None, " ".join(sorted(tokens_a)), " ".join(sorted(tokens_b))).ratio()


def deduplicate_papers(arxiv_papers: list[dict], s2_papers: list[dict]) -> list[dict]:
    merged = list(arxiv_papers)
    for s2 in s2_papers:
        is_dup = False
        for existing in merged:
            if title_similarity(s2.get("title", ""), existing.get("title", "")) > 0.7:
                if s2.get("citationCount", 0) > existing.get("citationCount", 0):
                    existing.update(s2)
                is_dup = True
                break
        if not is_dup:
            merged.append(s2)
    return merged


def generate_summary(data: dict, topic: str = "") -> str:
    observations = []

    otel = data.get("standards", {}).get("otel", {})
    pr_count = len([p for p in otel.get("prs", []) if "error" not in p])
    issue_count = len([i for i in otel.get("issues", []) if "error" not in i])

    paper_count = len(data.get("papers", []))
    tools_native = len(data.get("tools", {}).get("ai_native", []))
    tools_traditional = len(data.get("tools", {}).get("traditional", []))
    blogs_count = len(data.get("enterprise_blogs", []))
    newsletters_count = len(data.get("newsletters", []))
    domestic_count = len(data.get("domestic", []))

    if newsletters_count > 0:
        observations.append(f"行业周刊共收录 {newsletters_count} 条{topic}相关资讯。")

    if domestic_count > 0:
        observations.append(f"国内信源收录 {domestic_count} 篇文章，覆盖 InfoQ、量子位、AI 前线等渠道。")

    if paper_count > 0:
        observations.append(f"学术论文板块收录 {paper_count} 篇论文，涵盖 arXiv 预印本、顶会论文及学术社交媒体精选。")

    if pr_count > 0 or issue_count > 0:
        observations.append(f"开源社区有 {pr_count} 个活跃 PR 和 {issue_count} 个讨论中的 Issue，规范与实现持续演进。")

    if blogs_count > 0:
        observations.append(f"大厂工程博客收录 {blogs_count} 篇文章，来自 Azure、AWS、Anthropic、OpenAI、Datadog 及国内云厂商。")

    if tools_native > 0:
        observations.append(f"开源工具共发布 {tools_native} 个版本更新，生态快速迭代。")

    if tools_traditional > 0:
        observations.append(f"传统工具/平台在{topic}方向有 {tools_traditional} 项新进展。")

    if not observations:
        return "本监测窗口内各板块活动相对平静。建议扩大时间范围或放宽话题关键词以获取更多信号。"

    return "\n\n".join(f"{i + 1}. {o}" for i, o in enumerate(observations))


# --- Table renderers for each plate ---

def render_newsletters_table(items: list[dict]) -> str:
    if not items:
        return "*本周期无相关行业周刊内容。*"
    lines = []
    for item in items:
        title = item.get("title", "")
        source = item.get("source", "")
        summary = item.get("summary", "")
        url = item.get("url", "")
        short_title = title if len(title) <= 50 else title[:47] + "..."
        lines.append(f"| {source} | {short_title} | {summary[:80]} | [链接]({url}) |")
    return "\n".join(lines)


def render_domestic_table(items: list[dict]) -> str:
    if not items:
        return "*本周期无相关国内信源内容。*"
    lines = []
    for item in items:
        title = item.get("title", "")
        source = item.get("source", "")
        summary = item.get("summary", "")
        url = item.get("url", "")
        short_title = title if len(title) <= 50 else title[:47] + "..."
        lines.append(f"| {source} | {short_title} | {summary[:80]} | [链接]({url}) |")
    return "\n".join(lines)


def render_papers_table(papers: list[dict]) -> str:
    if not papers:
        return "*本周期无相关学术论文。*"
    lines = []
    for p in papers:
        title = p.get("title", "")
        authors = ", ".join(p.get("authors", [])[:3])
        if len(p.get("authors", [])) > 3:
            authors += " et al."
        summary = p.get("summary", "")
        source = p.get("source", "arxiv")
        citations = p.get("citationCount", 0) or 0
        url = p.get("url", "")
        short_title = title if len(title) <= 50 else title[:47] + "..."
        lines.append(f"| {short_title} | {authors} | {summary[:80]} | {source} | {citations} | [链接]({url}) |")
    return "\n".join(lines)


def render_standards_summary(data: dict) -> str:
    otel = data.get("otel", {})
    oi = data.get("openinference", {})
    cncf = data.get("cncf", [])

    otel_prs = len([p for p in otel.get("prs", []) if "error" not in p])
    otel_issues = len([i for i in otel.get("issues", []) if "error" not in i])
    oi_prs = len([p for p in oi.get("prs", []) if "error" not in p])
    oi_issues = len([i for i in oi.get("issues", []) if "error" not in i])
    cncf_count = len(cncf)

    lines = []
    lines.append(f"| OTel GenAI SIG | {otel_prs} | {otel_issues} | 语义规范持续演进，GenAI span/metric 定义活跃 |")
    lines.append(f"| OpenInference WG | {oi_prs} | {oi_issues} | 多框架埋点适配（LangChain/CrewAI） |")
    lines.append(f"| CNCF AI/ML WG | - | - | 收录 {cncf_count} 项议题 |")
    return "\n".join(lines)


def render_prs_table(prs: list[dict]) -> str:
    if not prs:
        return "*无 GenAI 相关活跃 PR。*"
    lines = []
    for pr in prs:
        if "error" in pr:
            lines.append(f"| Error | {pr.get('repo', '')} | - | {pr['error']} |")
            continue
        title = pr.get("title", "")
        url = pr.get("url", "")
        repo = pr.get("repo", "").split("/")[-1] if "/" in pr.get("repo", "") else pr.get("repo", "")
        state = pr.get("state", "")
        short_title = title if len(title) <= 60 else title[:57] + "..."
        lines.append(f"| [{short_title}]({url}) | {repo} | {state} | {title[:80]} |")
    return "\n".join(lines)


def render_issues_table(issues: list[dict]) -> str:
    if not issues:
        return "*无 GenAI 相关活跃 Issue。*"
    lines = []
    for issue in issues:
        title = issue.get("title", "")
        url = issue.get("url", "")
        repo = issue.get("repo", "").split("/")[-1] if "/" in issue.get("repo", "") else issue.get("repo", "")
        labels = ", ".join(issue.get("labels", []))
        short_title = title if len(title) <= 60 else title[:57] + "..."
        lines.append(f"| [{short_title}]({url}) | {repo} | {labels} | {title[:80]} |")
    return "\n".join(lines)


def render_cncf_table(items: list[dict]) -> str:
    if not items:
        return "*本周期无 CNCF AI/ML WG 相关内容。*"
    lines = []
    for item in items:
        title = item.get("title", "")
        summary = item.get("summary", "")
        url = item.get("url", "")
        lines.append(f"| {title[:60]} | {summary[:80]} | [链接]({url}) |")
    return "\n".join(lines)


def render_enterprise_blogs_table(items: list[dict]) -> str:
    if not items:
        return "*本周期无大厂工程博客相关内容。*"
    lines = []
    for item in items:
        source = item.get("source", "")
        title = item.get("title", "")
        significance = item.get("significance", "")
        url = item.get("url", "")
        short_title = title if len(title) <= 50 else title[:47] + "..."
        lines.append(f"| {source} | {short_title} | {significance[:80]} | [链接]({url}) |")
    return "\n".join(lines)


def render_ai_native_tools_table(items: list[dict]) -> str:
    if not items:
        return "*本周期无 AI-Native 工具发版。*"
    lines = []
    for item in items:
        if "error" in item:
            lines.append(f"| {item.get('name', '')} | Error | {item.get('error', '')} | - | - |")
            continue
        name = item.get("name", "")
        version = item.get("version", "")
        change = item.get("change", "")
        published = item.get("published", "")
        url = item.get("url", "")
        lines.append(f"| {name} | {version} | {change[:80]} | {published} | [链接]({url}) |")
    return "\n".join(lines)


def render_traditional_tools_table(items: list[dict]) -> str:
    if not items:
        return "*本周期无传统可观测工具 AI 相关进展。*"
    lines = []
    for item in items:
        name = item.get("name", "")
        title = item.get("title", "")
        change = item.get("change", "")
        url = item.get("url", "")
        short_title = title if len(title) <= 50 else title[:47] + "..."
        lines.append(f"| {name} | {short_title} | {change[:80]} | [链接]({url}) |")
    return "\n".join(lines)


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Generate research landscape report")
    parser.add_argument("--input", required=True, help="Path to combined results JSON")
    parser.add_argument("--template", required=True, help="Path to report template markdown")
    parser.add_argument("--topic", required=True, help="Research topic for the report title")
    parser.add_argument("--since", default="N/A", help="Since date for report metadata")
    args = parser.parse_args()

    input_path = Path(args.input)
    template_path = Path(args.template)

    if not input_path.exists():
        print(json.dumps({"error": f"Input file not found: {input_path}"}))
        sys.exit(1)

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(json.dumps({"error": f"Failed to read input: {e}"}))
        sys.exit(1)

    if not template_path.exists():
        print(json.dumps({"error": f"Template file not found: {template_path}"}))
        sys.exit(1)

    template = template_path.read_text(encoding="utf-8")

    # Deduplicate papers
    arxiv_papers = [p for p in data.get("papers", []) if p.get("source") == "arxiv"]
    s2_papers = [p for p in data.get("papers", []) if p.get("source") == "semantic_scholar"]
    other_papers = [p for p in data.get("papers", []) if p.get("source") not in ("arxiv", "semantic_scholar")]
    papers = deduplicate_papers(arxiv_papers, s2_papers)
    papers.extend(other_papers)
    papers.sort(key=lambda p: p.get("published", ""), reverse=True)

    standards = data.get("standards", {})
    tools = data.get("tools", {})
    today = datetime.now().strftime("%Y-%m-%d")

    # Fill template
    report = template
    report = report.replace("{DATE}", today)
    report = report.replace("{TOPIC}", args.topic)
    report = report.replace("{SINCE_DATE}", args.since)
    report = report.replace("{SUMMARY}", generate_summary(data, args.topic))

    # Plate 1: Newsletters
    report = report.replace("{NEWSLETTERS_TABLE}", render_newsletters_table(data.get("newsletters", [])))

    # Plate 2: Domestic
    report = report.replace("{DOMESTIC_TABLE}", render_domestic_table(data.get("domestic", [])))

    # Plate 3: Papers
    report = report.replace("{PAPERS_TABLE}", render_papers_table(papers))

    # Plate 4: Standards
    report = report.replace("{STANDARDS_SUMMARY}", render_standards_summary(standards))

    otel = standards.get("otel", {})
    report = report.replace("{OTEL_PRS_TABLE}", render_prs_table(otel.get("prs", [])))
    report = report.replace("{OTEL_ISSUES_TABLE}", render_issues_table(otel.get("issues", [])))

    sig_url = otel.get("sig_notes_url")
    report = report.replace("{SIG_UPDATES}", f"[GenAI SIG 会议纪要]({sig_url})" if sig_url else "本周期未发现 SIG 会议纪要链接。")

    oi = standards.get("openinference", {})
    report = report.replace("{OI_PRS_TABLE}", render_prs_table(oi.get("prs", [])))
    report = report.replace("{OI_ISSUES_TABLE}", render_issues_table(oi.get("issues", [])))
    report = report.replace("{CNCF_TABLE}", render_cncf_table(standards.get("cncf", [])))

    # Plate 5: Enterprise blogs
    report = report.replace("{ENTERPRISE_BLOGS_TABLE}", render_enterprise_blogs_table(data.get("enterprise_blogs", [])))

    # Plate 6: Tools
    report = report.replace("{AI_NATIVE_TOOLS_TABLE}", render_ai_native_tools_table(tools.get("ai_native", [])))
    report = report.replace("{TRADITIONAL_TOOLS_TABLE}", render_traditional_tools_table(tools.get("traditional", [])))

    # Write report
    report_filename = f"research-landscape-report-{today}.md"
    report_path = Path(report_filename)
    report_path.write_text(report, encoding="utf-8")

    print(f"Report written to: {report_path.absolute()}")


if __name__ == "__main__":
    main()
