"""Markdown to HTML conversion core."""

from pathlib import Path

import markdown


# 跟随门户主题:读 localStorage,监听 storage 事件即时换肤(同源 iframe 自动收到)
_THEME_SYNC_SCRIPT = """\
(function(){
  var KEY='ai-demos-theme', VALID=['mono-light','light','deepblue','cyber','machine'];
  function apply(t){ if(VALID.indexOf(t)<0)t='mono-light'; document.documentElement.setAttribute('data-demo-theme',t); }
  try{ apply(localStorage.getItem(KEY)); }catch(e){ apply('mono-light'); }
  window.addEventListener('storage', function(e){ if(e.key===KEY) apply(e.newValue); });
})();
"""

_THEME_PALETTE_CSS = """\
:root, [data-demo-theme="mono-light"]{
  --d-bg:#fafafa;--d-surface:#fff;--d-surface-soft:#f8f8f9;--d-border:rgba(0,0,0,.12);
  --d-text:#09090b;--d-dim:#71717a;--d-accent:#09090b;--d-accent-text:#fafafa;--d-danger:#dc2626;
  --d-font:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
}
[data-demo-theme="light"]{
  --d-bg:#f6f7fb;--d-surface:#fff;--d-surface-soft:#f8fafc;--d-border:#e2e8f0;
  --d-text:#0f172a;--d-dim:#64748b;--d-accent:#4f46e5;--d-accent-text:#fff;--d-danger:#dc2626;
  --d-font:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
}
[data-demo-theme="deepblue"]{
  --d-bg:#0b1120;--d-surface:#111827;--d-surface-soft:#172033;--d-border:#1f2937;
  --d-text:#f8fafc;--d-dim:#94a3b8;--d-accent:#2563eb;--d-accent-text:#fff;--d-danger:#f87171;
  --d-font:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
}
[data-demo-theme="cyber"]{
  --d-bg:#050507;--d-surface:#0f0f12;--d-surface-soft:#141417;--d-border:#27272a;
  --d-text:#e4e4e7;--d-dim:#71717a;--d-accent:#a3e635;--d-accent-text:#050507;--d-danger:#ff5577;
  --d-font:"JetBrains Mono",ui-monospace,Consolas,"PingFang SC","Microsoft YaHei",monospace;
}
[data-demo-theme="machine"]{
  --d-bg:#0a0a0c;--d-surface:#0e0e11;--d-surface-soft:#111114;--d-border:rgba(227,179,65,.30);
  --d-text:#e3b341;--d-dim:#9a8c5a;--d-accent:#e3b341;--d-accent-text:#0a0a0c;--d-danger:#ff4500;
  --d-font:"JetBrains Mono",ui-monospace,Consolas,"PingFang SC","Microsoft YaHei",monospace;
}
"""

HTML_TEMPLATE = f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{title}}</title>
<script>
{_THEME_SYNC_SCRIPT}
</script>
<style>
{_THEME_PALETTE_CSS}
body {{
  max-width: 900px;
  margin: 40px auto;
  padding: 0 20px;
  font: 16px/1.7 var(--d-font);
  color: var(--d-text);
  background: var(--d-bg);
  transition: background .25s, color .25s;
}}
a {{ color: var(--d-accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
h1, h2 {{ border-bottom: 1px solid var(--d-border); padding-bottom: .3em; }}
h3, h4, h5, h6 {{ margin-top: 1.5em; }}
code {{
  padding: .2em .4em;
  background: var(--d-surface-soft);
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace;
  font-size: 85%;
}}
pre {{
  padding: 16px;
  overflow: auto;
  background: var(--d-surface-soft);
  border-radius: 6px;
  line-height: 1.45;
}}
pre code {{ padding: 0; background: transparent; }}
blockquote {{
  margin: 0;
  padding: 0 1em;
  color: var(--d-dim);
  border-left: .25em solid var(--d-border);
}}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
table th, table td {{ border: 1px solid var(--d-border); padding: 6px 13px; }}
table tr:nth-child(2n) {{ background: var(--d-surface-soft); }}
img {{ max-width: 100%; }}
nav {{ margin-bottom: 24px; font-size: 14px; }}
nav a {{ margin-right: 12px; }}
.toc {{ background: var(--d-surface-soft); padding: 12px 20px; border-radius: 6px; margin-bottom: 24px; }}
.toc ul {{ padding-left: 20px; }}
</style>
</head>
<body>
{{nav}}
{{toc}}
{{content}}
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
<script>
{_THEME_SYNC_SCRIPT}
</script>
<style>
{_THEME_PALETTE_CSS}
body {{
  max-width: 900px;
  margin: 40px auto;
  padding: 0 20px;
  font: 16px/1.7 var(--d-font);
  color: var(--d-text);
  background: var(--d-bg);
  transition: background .25s, color .25s;
}}
a {{ color: var(--d-accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
h1 {{ border-bottom: 1px solid var(--d-border); padding-bottom: .3em; }}
li {{ margin: 6px 0; }}
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


def convert_directory(src_dir: Path, out_dir: Path, _job_id: str) -> list[Path]:
    """Convert all Markdown files under src_dir to out_dir, preserving structure."""
    md_files = sorted(p for p in src_dir.rglob("*.md") if p.is_file())
    html_files: list[Path] = []

    for md in md_files:
        rel = md.relative_to(src_dir)
        out_path = out_dir / rel.with_suffix(".html")
        depth = len(out_path.parent.relative_to(out_dir).parts)
        index_link = ("../" * depth) + "index.html" if depth > 0 else "index.html"
        convert_markdown_file(md, out_path, index_link=index_link)
        html_files.append(out_path)

    if html_files:
        build_dir_index(out_dir, html_files, out_dir)

    return html_files


def build_global_index(output_root: Path) -> None:
    """Build a global index of all upload and path conversion jobs."""
    sections = []

    uploads_dir = output_root / "uploads"
    if uploads_dir.exists():
        items = []
        for d in sorted(uploads_dir.iterdir()):
            if d.is_dir() and (d / "index.html").exists():
                items.append(f'<li><a href="uploads/{d.name}/index.html">{d.name}</a></li>')
        if items:
            sections.append("<h2>上传的文档</h2>\n<ul>\n" + "\n".join(items) + "\n</ul>")

    paths_dir = output_root / "paths"
    if paths_dir.exists():
        items = []
        for d in sorted(paths_dir.iterdir()):
            if d.is_dir() and (d / "index.html").exists():
                items.append(f'<li><a href="paths/{d.name}/index.html">{d.name}</a></li>')
        if items:
            sections.append("<h2>本地路径转换</h2>\n<ul>\n" + "\n".join(items) + "\n</ul>")

    html = f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DocHub 文档总目录</title>
<script>
{_THEME_SYNC_SCRIPT}
</script>
<style>
{_THEME_PALETTE_CSS}
body {{
  max-width: 900px;
  margin: 40px auto;
  padding: 0 20px;
  font: 16px/1.7 var(--d-font);
  color: var(--d-text);
  background: var(--d-bg);
  transition: background .25s, color .25s;
}}
a {{ color: var(--d-accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
h1 {{ border-bottom: 1px solid var(--d-border); padding-bottom: .3em; }}
li {{ margin: 6px 0; }}
</style>
</head>
<body>
<h1>DocHub 文档总目录</h1>
{chr(10).join(sections)}
</body>
</html>
"""
    (output_root / "index.html").write_text(html, encoding="utf-8")
