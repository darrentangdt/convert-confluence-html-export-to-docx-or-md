# Confluence HTML Export to Structured DOCX Converter

This project converts a **Confluence HTML space export** (e.g., `index.html` and flat HTML files with `images/`, `attachments/`, etc.) into:

✅ A structured folder hierarchy matching the original space layout

✅ Cleaned-up HTML files with broken internal links and Confluence UI elements removed

✅ `.docx` files for each Confluence page, with **embedded images** and working relative links

---

## 🔧 Use Case

You’ve exported a Confluence space as HTML and need to:

* Upload the documentation to SharePoint or another DOCX-compatible platform
* Preserve the original page structure and hierarchy
* Embed images and attachments into the final Word documents
* Strip out Confluence-specific UI elements (breadcrumbs, attachment listings, footers)

---

## 📁 Input Structure (Confluence Export)

Expected layout from Confluence export:

```
<Exported_Space>/
├── index.html
├── 12345678.html
├── 23456789.html
├── images/
├── attachments/
├── styles/
```

---

## 📂 Output Structure (Generated)

The script will generate:

```
<Output_Folder>/
├── <Root_Space_Name>/
│   ├── Subfolder 1/
│   │   ├── Page A.docx
│   │   └── Page B.docx
│   ├── Page C.docx
│   └── ...
├── images/
├── attachments/
├── styles/
```

---

## 🧰 Requirements

* Python 3.8+
* `beautifulsoup4`
* [`pandoc`](https://pandoc.org/) must be installed and accessible in your PATH

Install Python dependencies:

```bash
pip install beautifulsoup4
```

Check if `pandoc` is installed:

```bash
pandoc --version
```

---

## 🚀 How to Use

### Option 1: Using Command Line Arguments (Recommended)

```bash
python confluence_export_to_docx.py \
    --export-root "path/to/exported/space" \
    --output-root "path/for/output" \
    --docx-base "Root Space Name" \
    --cleanup
```

#### Available Arguments:
- `--export-root`: Path to the directory containing the Confluence HTML export (default: "<Exported_Space>")
- `--output-root`: Directory where the DOCX files will be saved (default: "<Output_Folder>")
- `--docx-base`: Base directory name for the DOCX files (default: "<Root_Space_Name>")
- `--cleanup`: Optional flag to delete intermediate HTML files after DOCX conversion

### Option 2: Editing the Script

Alternatively, you can edit the default values in the script:

1. Open `confluence_export_to_docx.py`
2. Update these default values at the top of the file:

```python
DEFAULT_EXPORT_ROOT = "<Exported_Space>"
DEFAULT_OUTPUT_ROOT = "<Output_Folder>"
DEFAULT_DOCX_BASE = "<Root_Space_Name>"
```

3. Run the script:

```bash
python confluence_export_to_docx.py
```

### Output

Output will be created in the specified output directory:
- Cleaned and structured HTML (unless `--cleanup` is used)
- `.docx` versions of each page (with embedded images)

---

## 🧹 What Gets Cleaned

The following elements are removed from the output:

* Confluence **breadcrumbs** (`<div id="breadcrumb-section">`)
* **Attachments sections** (`<h2 id="attachments">` and its surrounding container)
* Internal links rewritten to point to relative `.docx` equivalents
* Asset links (images, styles) rewritten as relative paths

---

## 📃 Tips

* If `pandoc` isn't embedding images, it may be due to incorrect working directory. This script automatically invokes `pandoc` from the correct folder.
* You can modify the output folder name by changing the `OUTPUT_ROOT` variable inside the script.

---

## 📄 License

MIT License
