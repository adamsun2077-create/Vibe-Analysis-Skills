#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path("/Users/adam/Aidam_3/vibe-analysis-skills/projects/ep02-fertility-earth")
SOURCE = ROOT / "成果" / "公众号正文.md"
TARGET = ROOT / "成果" / "公众号正文.html"


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text).strip("-").lower()
    return text or "section"


def render_inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(
        r"(https?://[^\s<]+)",
        lambda m: f'<a href="{m.group(1)}" target="_blank" rel="noopener noreferrer">{m.group(1)}</a>',
        escaped,
    )
    return escaped


def build_html(markdown_text: str) -> str:
    lines = markdown_text.splitlines()

    title = "公众号正文"
    sections: list[tuple[str, str]] = []
    blocks: list[str] = []

    paragraph: list[str] = []
    list_items: list[str] = []
    list_type: str | None = None
    quote_lines: list[str] = []
    table_rows: list[list[str]] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items, list_type
        if list_items and list_type:
            tag = "ol" if list_type == "ol" else "ul"
            items = "".join(f"<li>{render_inline(item)}</li>" for item in list_items)
            blocks.append(f"<{tag}>{items}</{tag}>")
        list_items = []
        list_type = None

    def flush_quote() -> None:
        nonlocal quote_lines
        if not quote_lines:
            return
        quote_text = "\n".join(quote_lines)
        if "【此处插入 40 秒视频】" in quote_text:
            parts = [line.strip() for line in quote_lines if line.strip()]
            headline = parts[0] if parts else "视频占位"
            desc = "<br>".join(render_inline(line) for line in parts[1:])
            blocks.append(
                f"""
                <div class="video-placeholder">
                  <div class="video-icon">▶</div>
                  <div class="video-title">{render_inline(headline)}</div>
                  <div class="video-desc">{desc}</div>
                </div>
                """
            )
        else:
            content = "<br>".join(render_inline(line) for line in quote_lines)
            blocks.append(f"<blockquote>{content}</blockquote>")
        quote_lines = []

    def flush_table() -> None:
        nonlocal table_rows
        if not table_rows:
            return
        header = table_rows[0]
        body = [row for row in table_rows[1:] if not all(re.fullmatch(r"-+", cell or "") for cell in row)]
        thead = "".join(f"<th>{render_inline(cell)}</th>" for cell in header)
        tbody = "".join(
            "<tr>" + "".join(f"<td>{render_inline(cell)}</td>" for cell in row) + "</tr>"
            for row in body
        )
        blocks.append(f"<div class='table-wrap'><table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table></div>")
        table_rows = []

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("# "):
            flush_paragraph()
            flush_list()
            flush_quote()
            flush_table()
            title = stripped[2:].strip()
            blocks.append(f"<header class='hero'><div class='eyebrow'>Vibe Analysis</div><h1>{render_inline(title)}</h1></header>")
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            flush_list()
            flush_quote()
            flush_table()
            heading = stripped[3:].strip()
            heading_id = slugify(heading)
            sections.append((heading_id, heading))
            blocks.append(f"<h2 id='{heading_id}'>{render_inline(heading)}</h2>")
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            flush_list()
            flush_quote()
            flush_table()
            heading = stripped[4:].strip()
            blocks.append(f"<h3>{render_inline(heading)}</h3>")
            continue

        if stripped.startswith("#### "):
            flush_paragraph()
            flush_list()
            flush_quote()
            flush_table()
            heading = stripped[5:].strip()
            blocks.append(f"<h4>{render_inline(heading)}</h4>")
            continue

        if stripped == "---":
            flush_paragraph()
            flush_list()
            flush_quote()
            flush_table()
            blocks.append("<hr>")
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            flush_list()
            flush_table()
            quote_lines.append(stripped[2:])
            continue
        else:
            flush_quote()

        if stripped.startswith("- "):
            flush_paragraph()
            flush_table()
            if list_type not in (None, "ul"):
                flush_list()
            list_type = "ul"
            list_items.append(stripped[2:].strip())
            continue

        if re.match(r"^\d+\.\s", stripped):
            flush_paragraph()
            flush_table()
            if list_type not in (None, "ol"):
                flush_list()
            list_type = "ol"
            list_items.append(re.sub(r"^\d+\.\s+", "", stripped))
            continue

        flush_list()

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            row = [cell.strip() for cell in stripped.strip("|").split("|")]
            table_rows.append(row)
            continue
        else:
            flush_table()

        if not stripped:
            flush_paragraph()
            continue

        paragraph.append(stripped)

    flush_paragraph()
    flush_list()
    flush_quote()
    flush_table()

    toc = ""
    if sections:
        toc_items = "".join(
            f"<li><a href='#{section_id}'>{render_inline(section_title)}</a></li>"
            for section_id, section_title in sections
        )
        toc = f"""
        <aside class="toc">
          <div class="toc-title">文章导航</div>
          <ul>{toc_items}</ul>
        </aside>
        """

    article_body = "\n".join(blocks)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #f7f3ec;
      --paper: #fffdf9;
      --text: #2f2a24;
      --muted: #75685a;
      --line: #e8dfd2;
      --accent: #c96d4b;
      --accent-soft: #f3e1d8;
      --accent-deep: #7b3f2e;
      --code-bg: #f4eee7;
      --shadow: 0 12px 40px rgba(85, 60, 36, 0.08);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background:
        radial-gradient(circle at top, rgba(201,109,75,0.10), transparent 35%),
        var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB",
        "Microsoft YaHei", sans-serif;
      line-height: 1.92;
    }}

    .page {{
      max-width: 900px;
      margin: 0 auto;
      padding: 36px 20px 64px;
    }}

    .article {{
      background: var(--paper);
      border: 1px solid rgba(201, 184, 160, 0.45);
      border-radius: 24px;
      box-shadow: var(--shadow);
      padding: 40px 34px 56px;
    }}

    .hero {{
      margin-bottom: 28px;
      padding-bottom: 24px;
      border-bottom: 1px solid var(--line);
    }}

    .eyebrow {{
      display: inline-block;
      margin-bottom: 14px;
      padding: 6px 12px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent-deep);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    h1 {{
      margin: 0;
      font-size: 38px;
      line-height: 1.28;
      letter-spacing: -0.02em;
    }}

    h2 {{
      margin: 40px 0 18px;
      font-size: 28px;
      line-height: 1.4;
      position: relative;
      padding-left: 16px;
    }}

    h2::before {{
      content: "";
      position: absolute;
      left: 0;
      top: 0.28em;
      width: 5px;
      height: 1.2em;
      border-radius: 999px;
      background: linear-gradient(180deg, var(--accent), #e6b89f);
    }}

    h3 {{
      margin: 28px 0 12px;
      font-size: 22px;
      line-height: 1.5;
      color: #2d241c;
    }}

    h4 {{
      margin: 22px 0 10px;
      font-size: 18px;
      line-height: 1.6;
      color: #5f3c2f;
    }}

    p {{
      margin: 0 0 16px;
      font-size: 17px;
    }}

    strong {{
      color: #1d1611;
      font-weight: 800;
    }}

    a {{
      color: var(--accent-deep);
      text-decoration: none;
      border-bottom: 1px solid rgba(123, 63, 46, 0.28);
    }}

    ul, ol {{
      margin: 0 0 18px 1.4em;
      padding: 0;
    }}

    li {{
      margin: 8px 0;
      font-size: 17px;
    }}

    hr {{
      border: 0;
      border-top: 1px solid var(--line);
      margin: 30px 0;
    }}

    blockquote {{
      margin: 18px 0 24px;
      padding: 16px 18px;
      background: #fcf7f1;
      border-left: 4px solid var(--accent);
      border-radius: 12px;
      color: var(--muted);
    }}

    code {{
      padding: 2px 7px;
      border-radius: 8px;
      background: var(--code-bg);
      font-size: 0.92em;
      color: #5f3c2f;
    }}

    .table-wrap {{
      margin: 18px 0 24px;
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: #fff;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 560px;
    }}

    th, td {{
      padding: 14px 14px;
      text-align: left;
      border-bottom: 1px solid var(--line);
      font-size: 15px;
      vertical-align: top;
    }}

    th {{
      background: #faf4ee;
      color: #4a382d;
      font-weight: 700;
    }}

    tr:last-child td {{
      border-bottom: 0;
    }}

    .toc {{
      margin: 0 0 28px;
      padding: 18px 20px;
      border-radius: 18px;
      background: linear-gradient(180deg, #fffaf5 0%, #fff 100%);
      border: 1px solid var(--line);
    }}

    .toc-title {{
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: var(--muted);
      text-transform: uppercase;
      margin-bottom: 10px;
    }}

    .toc ul {{
      margin: 0;
      padding-left: 1.2em;
    }}

    .toc li {{
      margin: 6px 0;
      font-size: 15px;
    }}

    .video-placeholder {{
      margin: 22px 0 30px;
      padding: 28px 22px;
      border-radius: 20px;
      background:
        linear-gradient(135deg, rgba(201,109,75,0.10), rgba(123,63,46,0.08)),
        #fff8f3;
      border: 1px solid rgba(201,109,75,0.20);
      text-align: center;
    }}

    .video-icon {{
      width: 68px;
      height: 68px;
      margin: 0 auto 12px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      background: linear-gradient(135deg, var(--accent), #e09a79);
      color: white;
      font-size: 28px;
      font-weight: 700;
      box-shadow: 0 10px 24px rgba(201,109,75,0.22);
    }}

    .video-title {{
      font-size: 18px;
      font-weight: 800;
      margin-bottom: 8px;
    }}

    .video-desc {{
      color: var(--muted);
      font-size: 15px;
      line-height: 1.8;
    }}

    .footer-note {{
      margin-top: 34px;
      padding-top: 20px;
      border-top: 1px dashed var(--line);
      color: var(--muted);
      font-size: 14px;
    }}

    @media (max-width: 640px) {{
      .page {{
        padding: 18px 12px 40px;
      }}

      .article {{
        padding: 26px 18px 34px;
        border-radius: 18px;
      }}

      h1 {{
        font-size: 30px;
      }}

      h2 {{
        font-size: 24px;
      }}

      h3 {{
        font-size: 20px;
      }}

      p, li {{
        font-size: 16px;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <article class="article">
      {toc}
      {article_body}
      <div class="footer-note">
        本页为单文件排版版 HTML，适合直接预览、截图、继续改文案，再同步到公众号编辑器。
      </div>
    </article>
  </div>
</body>
</html>
"""


def main() -> None:
    markdown_text = SOURCE.read_text(encoding="utf-8")
    TARGET.write_text(build_html(markdown_text), encoding="utf-8")
    print(f"Rendered HTML -> {TARGET}")


if __name__ == "__main__":
    main()
