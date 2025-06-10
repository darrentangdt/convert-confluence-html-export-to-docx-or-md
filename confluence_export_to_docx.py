import os
import shutil
import subprocess
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import unquote

# ---- Default Config ----
DEFAULT_EXPORT_ROOT = "Exported_Space"  # Input: flat Confluence HTML export
DEFAULT_OUTPUT_ROOT = "Output"  # Output: rewritten structure + DOCX
DEFAULT_DOCX_BASE = "Exported Space"
ASSET_DIRS = ["images", "attachments", "styles"]
PANDOC = "pandoc"  # or full path to pandoc if needed
# -----------------------


def sanitize(name):
    return "".join(c if c.isalnum() or c in " -._" else "_" for c in name).strip()


def walk_index(ul, current_path):
    page_map = {}
    for li in ul.find_all("li", recursive=False):
        a = li.find("a")
        if a and "href" in a.attrs:
            href = unquote(a["href"])
            title = sanitize(a.get_text(strip=True))
            rel_docx_path = current_path / f"{title}.docx"
            page_map[href] = rel_docx_path
            for child_ul in li.find_all("ul", recursive=False):
                page_map.update(walk_index(child_ul, current_path / title))
    return page_map


def rewrite_assets(soup: BeautifulSoup, docx_path: Path):
    for tag, attr in [("img", "src"), ("link", "href"), ("script", "src"), ("a", "href")]:
        for el in soup.find_all(tag):
            src = el.get(attr)
            if not src:
                continue
            for asset_dir in ASSET_DIRS:
                if src.startswith(asset_dir + "/"):
                    abs_asset_path = EXPORT_ROOT / src
                    rel_path = os.path.relpath(abs_asset_path, start=(OUTPUT_ROOT / docx_path).parent)
                    el[attr] = rel_path.replace(os.sep, "/")
                    break


def build_structure_and_rewrite_links(page_map):
    rewritten_html_paths = []
    for html_filename, docx_path in page_map.items():
        src_path = EXPORT_ROOT / html_filename
        if not src_path.exists():
            print(f"⚠ Missing source HTML: {html_filename}")
            continue

        dest_html_path = OUTPUT_ROOT / docx_path.with_suffix(".html")
        dest_html_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(src_path, dest_html_path)

            with open(dest_html_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # --- Remove unwanted elements ---
            # Remove breadcrumbs
            breadcrumb_section = soup.select_one("div#breadcrumb-section")
            if breadcrumb_section:
                breadcrumb_section.decompose()

            # Remove attachments section
            attachments_header = soup.select_one("h2#attachments")
            if attachments_header:
                try:
                    attachments_section = attachments_header.parent.parent
                    attachments_section.decompose()
                except Exception:
                    pass  # Skip if structure isn't what we expect
                    
            # Remove metadata table
            metadata_table = soup.select_one("#main-content > div.plugin-tabmeta-details")
            if metadata_table:
                metadata_table.decompose()
                
            # Remove title heading
            title_heading = soup.select_one("h1#title-heading")
            if title_heading:
                title_heading.decompose()
            
            # Remove footer
            footer = soup.select_one("div#footer")
            if footer:
                footer.decompose()
                
            # Remove expander divs with IDs like 'expander-123'
            for expander in soup.find_all('div', id=lambda x: x and x.startswith('expander-')):
                expander.decompose()

            # --- Rewrite internal page links ---
            for a in soup.find_all("a", href=True):
                href = unquote(a["href"])
                if href.endswith(".html") and href in page_map:
                    target_docx = page_map[href]
                    rel_path = os.path.relpath(target_docx, start=docx_path.parent)
                    a["href"] = rel_path.replace(os.sep, "/")

            # --- Rewrite asset paths (images, css, etc) ---
            rewrite_assets(soup, docx_path)

            with open(dest_html_path, "w", encoding="utf-8") as f:
                f.write(str(soup))

            rewritten_html_paths.append(dest_html_path)
            print(f"✓ Rewritten: {html_filename} → {dest_html_path.relative_to(OUTPUT_ROOT)}")

        except Exception as e:
            print(f"✗ Failed rewriting {html_filename}: {e}")
    return rewritten_html_paths


def copy_asset_dirs():
    for asset_dir in ASSET_DIRS:
        src = EXPORT_ROOT / asset_dir
        dst = OUTPUT_ROOT / asset_dir
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"✓ Copied asset dir: {asset_dir}")


def convert_html_to_docx(input_path: Path):
    output_path = input_path.with_suffix(".docx")
    
    # Get the directory of the current script to find the Lua filter
    script_dir = Path(__file__).parent
    lua_filter = script_dir / "image-fullsize.lua"
    
    cmd = [
        PANDOC,
        "-o", str(output_path.name),
        f"--lua-filter={lua_filter}",
        str(input_path.name)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=input_path.parent
        )
        if result.returncode == 0:
            print(f"✓ Converted: {input_path.relative_to(OUTPUT_ROOT)} → {output_path.name}")
        else:
            print(f"✗ Pandoc failed: {input_path.name} ({result.stderr.strip()})")
    except Exception as e:
        print(f"✗ Error running Pandoc on {input_path.name}: {e}")


def print_summary(stats):
    """Print a summary of the conversion process."""
    print("\n" + "="*50)
    print("📊 Conversion Summary")
    print("="*50)
    
    if stats.get('html_generated', 0) > 0:
        print(f"✅ HTML Files Generated: {stats.get('html_generated', 0)}")
    
    if stats.get('docx_converted', 0) > 0:
        print(f"✅ DOCX Files Created: {stats.get('docx_converted', 0)}")
    
    if stats.get('html_cleaned', 0) > 0:
        print(f"🧹 HTML Files Cleaned Up: {stats.get('html_cleaned', 0)}")
    
    if stats.get('assets_copied', 0) > 0:
        print(f"📁 Assets Copied: {stats.get('assets_copied', 0)} directories")
    
    if stats.get('errors', []):
        print("\n❌ Errors:")
        for error in stats.get('errors', []):
            print(f"  - {error}")
    
    print("="*50 + "\n")


def main():
    # Initialize statistics
    stats = {
        'html_generated': 0,
        'docx_converted': 0,
        'html_cleaned': 0,
        'assets_copied': 0,
        'errors': []
    }
    
    parser = argparse.ArgumentParser(description='Convert Confluence HTML export to DOCX files.')
    parser.add_argument('--export-root', type=str, default=DEFAULT_EXPORT_ROOT,
                      help=f'Root directory of the Confluence HTML export (default: {DEFAULT_EXPORT_ROOT})')
    parser.add_argument('--output-root', type=str, default=DEFAULT_OUTPUT_ROOT,
                      help=f'Output directory for the DOCX files (default: {DEFAULT_OUTPUT_ROOT})')
    parser.add_argument('--docx-base', type=str, default=DEFAULT_DOCX_BASE,
                      help=f'Base directory name for the DOCX files (default: {DEFAULT_DOCX_BASE})')
    
    # Mutually exclusive group for conversion options
    conversion_group = parser.add_mutually_exclusive_group()
    conversion_group.add_argument('--skip-docx', action='store_true',
                               help='Skip DOCX conversion and only generate HTML files')
    conversion_group.add_argument('--skip-html', action='store_true',
                                help='Skip HTML generation and only convert existing HTML to DOCX')
    
    parser.add_argument('--cleanup', action='store_true',
                      help='Delete the generated HTML files after creating DOCX files (cannot be used with --skip-docx)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.cleanup and args.skip_docx:
        parser.error("--cleanup cannot be used with --skip-docx as it would delete the HTML files")
    
    # Set global variables from command line arguments
    global EXPORT_ROOT, OUTPUT_ROOT, DOCX_BASE, INDEX_HTML
    EXPORT_ROOT = Path(args.export_root)
    OUTPUT_ROOT = Path(args.output_root)
    DOCX_BASE = Path(args.docx_base)
    INDEX_HTML = EXPORT_ROOT / "index.html"
    
    print(f"📁 Export root: {EXPORT_ROOT}")
    print(f"📂 Output root: {OUTPUT_ROOT}")
    print(f"📄 DOCX base directory: {DOCX_BASE}")
    print(f"🔧 Skip HTML generation: {'Yes' if args.skip_html else 'No'}")
    print(f"🔧 Skip DOCX conversion: {'Yes' if args.skip_docx else 'No'}")
    print(f"🧹 Cleanup HTML: {'Yes' if args.cleanup else 'No'}")
    
    print("\n📁 Parsing index.html...")
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    nav = soup.find("ul")
    if not nav:
        print("✗ Could not find <ul> in index.html")
        return

    page_map = walk_index(nav, DOCX_BASE)

    rewritten_files = []
    
    # Generate HTML files if not skipped
    rewritten_files = []
    if not args.skip_html:
        print("🧱 Rewriting HTML and creating folder structure...")
        try:
            rewritten_files = build_structure_and_rewrite_links(page_map)
            stats['html_generated'] = len(rewritten_files)
            print("🖼️ Copying assets...")
            try:
                copy_asset_dirs()
                stats['assets_copied'] = len(ASSET_DIRS)
            except Exception as e:
                stats['errors'].append(f"Failed to copy assets: {str(e)}")
        except Exception as e:
            stats['errors'].append(f"HTML generation failed: {str(e)}")
            raise
    else:
        # If skipping HTML generation, find all HTML files in the output directory
        print("⏩ Skipping HTML generation, using existing files...")
        for docx_path in page_map.values():
            html_path = OUTPUT_ROOT / docx_path.with_suffix('.html')
            if not html_path.exists():
                error_msg = f"HTML file not found: {html_path}. Cannot skip HTML generation when files don't exist."
                stats['errors'].append(error_msg)
                raise FileNotFoundError(error_msg)
            rewritten_files.append(html_path)
    
    # Convert to DOCX if not skipped
    if not args.skip_docx:
        print("📄 Converting to DOCX with Pandoc...")
        for html_file in rewritten_files:
            try:
                convert_html_to_docx(html_file)
                stats['docx_converted'] += 1
                
                # Clean up HTML files if requested
                if args.cleanup:
                    try:
                        html_file.unlink()
                        print(f"🧹 Deleted: {html_file.relative_to(OUTPUT_ROOT)}")
                        stats['html_cleaned'] += 1
                    except Exception as e:
                        error_msg = f"Failed to delete {html_file.relative_to(OUTPUT_ROOT)}: {e}"
                        print(f"⚠ {error_msg}")
                        stats['errors'].append(error_msg)
            except Exception as e:
                error_msg = f"Failed to convert {html_file.relative_to(OUTPUT_ROOT)}: {e}"
                print(f"❌ {error_msg}")
                stats['errors'].append(error_msg)
    else:
        print("⏩ Skipping DOCX conversion")
    
    # Print summary
    print_summary(stats)


if __name__ == "__main__":
    main()
