import os
import shutil
import subprocess
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import unquote
from packaging.version import parse as parse_version

# ---- Default Config ----
DEFAULT_EXPORT_ROOT = "Exported_Space"
DEFAULT_OUTPUT_ROOT = "Output"
ASSET_DIRS = ["images", "attachments", "styles"]
PANDOC = "pandoc"
DEFAULT_OUTPUT_TYPE = "markdown"
# -----------------------

def print_usage_example():
    """打印使用示例"""
    print("\n使用示例:")
    print("1. 转换为Markdown(默认):")
    print("   python convert_confluence.py --export-root MyConfluenceExport --output-root MyOutput")
    print("\n2. 转换为DOCX:")
    print("   python convert_confluence.py --type docx --export-root MyConfluenceExport --output-root MyOutput")
    print("\n3. 跳过HTML生成(仅转换):")
    print("   python convert_confluence.py --skip-html --export-root MyConfluenceExport --output-root MyOutput")
    print("\n4. 转换后清理中间文件:")
    print("   python convert_confluence.py --cleanup --export-root MyConfluenceExport --output-root MyOutput")
    print("\n5. 显示完整帮助:")
    print("   python convert_confluence.py --help")

def get_pandoc_version():
    """获取Pandoc版本号"""
    try:
        result = subprocess.run([PANDOC, "--version"], 
                              capture_output=True, 
                              text=True,
                              check=True)
        first_line = result.stdout.split('\n')[0]
        version_str = first_line.split()[1]
        return parse_version(version_str)
    except Exception as e:
        print(f"⚠ 警告: 无法获取Pandoc版本 ({e})")
        return parse_version("0.0.0")

def sanitize(name):
    """清理文件名中的非法字符"""
    return "".join(c if c.isalnum() or c in " -._" else "_" for c in name).strip()

def walk_index(ul, base_path):
    """遍历Confluence索引文件"""
    page_map = {}
    for li in ul.find_all("li", recursive=False):
        a = li.find("a")
        if a and "href" in a.attrs:
            href = unquote(a["href"])
            title = sanitize(a.get_text(strip=True))
            rel_path = base_path / title
            page_map[href] = {
                'path': rel_path,
                'title': title
            }
            for child_ul in li.find_all("ul", recursive=False):
                page_map.update(walk_index(child_ul, rel_path))
    return page_map

def rewrite_assets(soup: BeautifulSoup, output_path: Path, format_type: str):
    """重写资源文件路径"""
    for tag, attr in [("img", "src"), ("link", "href"), ("script", "src"), ("a", "href")]:
        for el in soup.find_all(tag):
            src = el.get(attr)
            if not src:
                continue
            for asset_dir in ASSET_DIRS:
                if src.startswith(asset_dir + "/"):
                    abs_asset_path = EXPORT_ROOT / src
                    if format_type == 'docx':
                        rel_path = os.path.relpath(abs_asset_path, start=output_path.parent)
                    else:  # MD格式
                        rel_path = os.path.relpath(abs_asset_path, start=EXPORT_ROOT)
                        rel_path = str(Path('assets') / rel_path.split('/')[-1])
                    el[attr] = rel_path.replace(os.sep, "/")
                    break

def build_structure_and_rewrite_links(page_map, format_type):
    """构建目录结构并重写链接"""
    rewritten_html_paths = []
    for html_filename, page_info in page_map.items():
        src_path = EXPORT_ROOT / html_filename
        if not src_path.exists():
            print(f"⚠ 缺少源HTML文件: {html_filename}")
            continue

        dest_html_path = OUTPUT_ROOT / page_info['path'].with_suffix(".html")
        dest_html_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(src_path, dest_html_path)

            with open(dest_html_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # 清理不需要的元素
            for element in [
                "div#breadcrumb-section",
                "h2#attachments",
                "#main-content > div.plugin-tabmeta-details",
                "h1#title-heading",
                "div#footer",
                lambda x: x and x.startswith('expander-')
            ]:
                if isinstance(element, str):
                    el = soup.select_one(element)
                    if el:
                        el.decompose()
                else:
                    for el in soup.find_all('div', id=element):
                        el.decompose()

            # 转换图片为Markdown格式
            if format_type == 'markdown':
                for img_wrapper in soup.find_all('span', class_='confluence-embedded-file-wrapper'):
                    img = img_wrapper.find('img')
                    if img and img.has_attr('src'):
                        alt_text = img.get('alt', '')
                        img_src = img['src']
                        md_img = f'![{alt_text}]({img_src})'
                        img_wrapper.replace_with(md_img)

            # 重写内部链接
            for a in soup.find_all("a", href=True):
                href = unquote(a["href"])
                if href.endswith(".html") and href in page_map:
                    target_path = page_map[href]['path']
                    rel_path = os.path.relpath(
                        OUTPUT_ROOT / target_path.with_suffix('.md' if format_type == 'markdown' else '.docx'),
                        start=dest_html_path.parent
                    )
                    a["href"] = rel_path.replace(os.sep, "/")

            rewrite_assets(soup, dest_html_path, format_type)

            with open(dest_html_path, "w", encoding="utf-8") as f:
                f.write(str(soup))

            rewritten_html_paths.append(dest_html_path)
            print(f"✓ 已重写: {html_filename} → {dest_html_path.relative_to(OUTPUT_ROOT)}")

        except Exception as e:
            print(f"✗ 重写失败 {html_filename}: {e}")
    return rewritten_html_paths

def copy_asset_dirs(format_type):
    """复制资源目录"""
    for asset_dir in ASSET_DIRS:
        src = EXPORT_ROOT / asset_dir
        if format_type == 'markdown':
            dst = OUTPUT_ROOT / 'assets'
        else:
            dst = OUTPUT_ROOT / asset_dir
            
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"✓ 已复制资源目录: {asset_dir} → {dst.relative_to(OUTPUT_ROOT)}")

def convert_to_format(input_path: Path, format_type: str):
    """完全兼容的格式转换函数"""
    output_path = input_path.with_suffix(".docx" if format_type == 'docx' else '.md')
    
    cmd = [
        PANDOC,
        "-o", str(output_path.name),
        "--to", "gfm" if format_type == 'markdown' else "docx",
        "--wrap=auto",
        str(input_path.name)
    ]

    # 添加Lua过滤器（如果存在）
    script_dir = Path(__file__).parent
    lua_filter = script_dir / "image-fullsize.lua"
    if lua_filter.exists():
        cmd.insert(1, f"--lua-filter={lua_filter}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=input_path.parent
        )
        if result.returncode == 0:
            if format_type == 'markdown':
                post_process_markdown_images(output_path)
            print(f"✓ 已转换为 {format_type.upper()}: {input_path.relative_to(OUTPUT_ROOT)} → {output_path.name}")
            return True
        print(f"✗ Pandoc转换失败 ({format_type}): {input_path.name} ({result.stderr.strip()})")
        return False
    except Exception as e:
        print(f"✗ 运行Pandoc出错 ({format_type}) 文件 {input_path.name}: {e}")
        return False

def post_process_markdown_images(md_file: Path):
    """后处理Markdown文件中的图片引用"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        replacements = [
            ('<img src="', '![]('),
            ('" class="confluence-embedded-image">', ')'),
            ('</span>', ''),
            ('<span class="confluence-embedded-file-wrapper">', '')
        ]
        for old, new in replacements:
            content = content.replace(old, new)
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"⚠ 后处理Markdown图片失败 {md_file}: {e}")

def print_summary(stats):
    """打印转换摘要"""
    print("\n" + "="*50)
    print("📊 转换摘要")
    print("="*50)
    stats_map = {
        'html_generated': "✅ 生成的HTML文件",
        'docx_converted': "✅ 创建的DOCX文件",
        'md_converted': "✅ 创建的Markdown文件",
        'html_cleaned': "🧹 清理的HTML文件",
        'assets_copied': "📁 复制的资源目录"
    }
    for key, label in stats_map.items():
        if stats.get(key, 0) > 0:
            print(f"{label}: {stats[key]}")
    if stats.get('errors'):
        print("\n❌ 错误:")
        for error in stats['errors']:
            print(f"  - {error}")
    print("="*50 + "\n")

def main():
    global EXPORT_ROOT, OUTPUT_ROOT, INDEX_HTML
    
    stats = {
        'html_generated': 0,
        'docx_converted': 0,
        'md_converted': 0,
        'html_cleaned': 0,
        'assets_copied': 0,
        'errors': []
    }
    
    parser = argparse.ArgumentParser(
        description='将Confluence HTML导出转换为Markdown或DOCX文档',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="示例:\n"
               "  python convert_confluence.py --export-root MyExport --output-root MyOutput\n"
               "  python convert_confluence.py --type docx --export-root MyExport\n"
               "  python convert_confluence.py --skip-html --cleanup"
    )
    
    parser.add_argument('--export-root', default=DEFAULT_EXPORT_ROOT,
                      help=f'Confluence HTML导出目录 (默认: {DEFAULT_EXPORT_ROOT})')
    parser.add_argument('--output-root', default=DEFAULT_OUTPUT_ROOT,
                      help=f'输出目录 (默认: {DEFAULT_OUTPUT_ROOT})')
    parser.add_argument('--type', choices=['markdown', 'docx'], default=DEFAULT_OUTPUT_TYPE,
                      help=f'输出格式 (默认: {DEFAULT_OUTPUT_TYPE})')
    parser.add_argument('--skip-html', action='store_true',
                      help='跳过HTML生成阶段(使用已有HTML文件)')
    parser.add_argument('--cleanup', action='store_true',
                      help='转换完成后删除中间HTML文件')
    
    # 如果没有参数，显示帮助信息
    if len(os.sys.argv) == 1:
        parser.print_help()
        print_usage_example()
        return
    
    args = parser.parse_args()
    
    EXPORT_ROOT = Path(args.export_root)
    OUTPUT_ROOT = Path(args.output_root)
    INDEX_HTML = EXPORT_ROOT / "index.html"
    format_type = args.type
    
    # 验证导出目录
    if not EXPORT_ROOT.exists():
        print(f"❌ 错误: 导出目录不存在 {EXPORT_ROOT}")
        return
    
    print(f"\n{'='*50}")
    print(f"📁 导出目录: {EXPORT_ROOT}")
    print(f"📂 输出目录: {OUTPUT_ROOT}")
    print(f"🔧 输出格式: {format_type}")
    print(f"🔧 跳过HTML生成: {'是' if args.skip_html else '否'}")
    print(f"🧹 清理HTML: {'是' if args.cleanup else '否'}")
    print(f"{'='*50}\n")
    
    print("📁 解析index.html...")
    try:
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        nav = soup.find("ul")
        if not nav:
            raise ValueError("在index.html中找不到<ul>元素")
        page_map = walk_index(nav, Path())
    except Exception as e:
        stats['errors'].append(f"解析index.html失败: {str(e)}")
        print_summary(stats)
        return

    rewritten_files = []
    if not args.skip_html:
        print("🧱 重写HTML并创建目录结构...")
        try:
            rewritten_files = build_structure_and_rewrite_links(page_map, format_type)
            stats['html_generated'] = len(rewritten_files)
            print("🖼️ 复制资源文件...")
            try:
                copy_asset_dirs(format_type)
                stats['assets_copied'] = len(ASSET_DIRS)
            except Exception as e:
                stats['errors'].append(f"复制资源失败: {str(e)}")
        except Exception as e:
            stats['errors'].append(f"HTML生成失败: {str(e)}")
    else:
        print("⏩ 跳过HTML生成...")
        for page_info in page_map.values():
            html_path = OUTPUT_ROOT / page_info['path'].with_suffix('.html')
            if html_path.exists():
                rewritten_files.append(html_path)
            else:
                stats['errors'].append(f"HTML文件不存在: {html_path}")

    print(f"\n📄 转换为 {format_type.upper()}...")
    for html_file in rewritten_files:
        try:
            if convert_to_format(html_file, format_type):
                stats[f"{'md' if format_type == 'markdown' else 'docx'}_converted"] += 1
                if args.cleanup:
                    try:
                        html_file.unlink()
                        stats['html_cleaned'] += 1
                    except Exception as e:
                        stats['errors'].append(f"删除文件失败 {html_file}: {e}")
        except Exception as e:
            stats['errors'].append(f"转换失败 {html_file}: {e}")

    print_summary(stats)

if __name__ == "__main__":
    main()
