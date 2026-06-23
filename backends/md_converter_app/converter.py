"""Markdown to HTML conversion core."""

from pathlib import Path

import markdown


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root {{ color-scheme: light dark; }}
body {{
  max-width: 900px;
  margin: 40px auto;
  padding: 0 20px;
  font: 16px/1.7 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  color: #24292f;
  background: #ffffff;
}}
@media (prefers-color-scheme: dark) {{
  body {{ color: #c9d1d9; background: #0d1117; }}
  a {{ color: #58a6ff; }}
  code, pre {{ background: #161b22; }}
  blockquote {{ color: #8b949e; border-left-color: #30363d; }}
  table th, table td {{ border-color: #30363d; }}
  table tr:nth-child(2n) {{ background: #161b22; }}
  h1, h2 {{ border-bottom-color: #30363d; }}
}}
h1, h2 {{ border-bottom: 1px solid #d0d7de; padding-bottom: .3em; }}
h3, h4, h5, h6 {{ margin-top: 1.5em; }}
code {{
  padding: .2em .4em;
  background: #f6f8fa;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace;
  font-size: 85%;
}}
pre {{
  padding: 16px;
  overflow: auto;
  background: #f6f8fa;
  border-radius: 6px;
  line-height: 1.45;
}}
pre code {{ padding: 0; background: transparent; }}
blockquote {{
  margin: 0;
  padding: 0 1em;
  color: #57606a;
  border-left: .25em solid #d0d7de;
}}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
table th, table td {{ border: 1px solid #d0d7de; padding: 6px 13px; }}
table tr:nth-child(2n) {{ background: #f6f8fa; }}
img {{ max-width: 100%; }}
a {{ color: #0969da; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
nav {{ margin-bottom: 24px; font-size: 14px; }}
nav a {{ margin-right: 12px; }}
.toc {{ background: #f6f8fa; padding: 12px 20px; border-radius: 6px; margin-bottom: 24px; }}
.toc ul {{ padding-left: 20px; }}
@media (prefers-color-scheme: dark) {{ .toc {{ background: #161b22; }} }}
</style>
</head>
<body>
{nav}
{toc}
{content}
</body>
</html>
"""


def convert_markdown_file(md_path: Path, out_path: Path, index_link: str = "") -> None:
    """Convert a single Markdown file to HTML."""
    text = md_path.read_text(encoding="utf-8")

    md = markdown.Markdown(
        extensions=[
            "toc",
            "tables",
            "fenced_code",
            "codehilite",
            "nl2br",
            "md_in_html",
        ],
        extension_configs={
            "codehilite": {"css_class": "highlight", "guess_lang": False},
        },
    )
    content = md.convert(text)
    toc = md.toc if md.toc else ""

    nav = f'<nav><a href="{index_link}">← 返回索引</a></nav>' if index_link else ""
    title = md_path.stem

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        HTML_TEMPLATE.format(
            title=title,
            nav=nav,
            toc=toc,
            content=content,
        ),
        encoding="utf-8",
    )


def build_dir_index(directory: Path, html_files: list[Path], root: Path) -> None:
    """Build an index.html for a directory of HTML files."""
    items = []
    for p in sorted(html_files):
        rel = p.relative_to(root)
        label = rel.with_suffix("").as_posix()
        items.append(f'<li><a href="{rel.as_posix()}">{label}</a></li>')

    html = f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>索引 - {directory.name}</title>
<style>
:root {{ color-scheme: light dark; }}
body {{
  max-width: 900px;
  margin: 40px auto;
  padding: 0 20px;
  font: 16px/1.7 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}}
@media (prefers-color-scheme: dark) {{
  body {{ color: #c9d1d9; background: #0d1117; }}
  a {{ color: #58a6ff; }}
}}
h1 {{ border-bottom: 1px solid #d0d7de; padding-bottom: .3em; }}
li {{ margin: 6px 0; }}
a {{ text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>索引 - {directory.name}</h1>
<ul>
{chr(10).join(items)}
</ul>
</body>
</html>
"""
    (directory / "index.html").write_text(html, encoding="utf-8")
