"""Command-line entry point for DocHub batch conversion."""

import argparse
from pathlib import Path

from backends.md_converter_app.converter import build_global_index, convert_directory


def collect_markdown_files(path: Path) -> list[Path]:
    if path.is_file() and path.suffix.lower() in (".md", ".markdown"):
        return [path]
    if path.is_dir():
        return sorted(p for p in path.rglob("*.md") if p.is_file())
    return []


def convert_paths(paths: list[Path], output_dir: Path, no_index: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    all_html: list[Path] = []

    for src in paths:
        md_files = collect_markdown_files(src)
        if not md_files:
            print(f"未找到 Markdown 文件：{src}")
            continue

        if src.is_file():
            out = output_dir / src.with_suffix(".html").name
            convert_directory(src.parent, output_dir, "cli")
        else:
            out_root = output_dir / src.name
            convert_directory(src, out_root, "cli")
            all_html.extend(p for p in out_root.rglob("*.html"))

    if not no_index:
        build_global_index(output_dir)
        print(f"生成全局索引：{output_dir / 'index.html'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="DocHub Markdown 批量转 HTML")
    parser.add_argument("paths", nargs="+", help="Markdown 文件或目录")
    parser.add_argument("-o", "--output", help="输出目录", default="output")
    parser.add_argument("--no-index", action="store_true", help="不生成索引")
    args = parser.parse_args()

    output_dir = Path(args.output)
    convert_paths([Path(p) for p in args.paths], output_dir, args.no_index)


if __name__ == "__main__":
    main()
