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

1. Place this script **next to** the Confluence export folder (`<Exported_Space>/`)
2. Edit the script (`confluence_export_to_docx.py`) and update these top-level variables:

```python
EXPORT_ROOT = Path("<Exported_Space>")
OUTPUT_ROOT = Path("<Output_Folder>")
ROOT_SPACE_NAME = "<Root_Space_Name>"  # This becomes the top-level folder in the DOCX export
```

Replace each placeholder with your actual folder and space name.

3. Run the script:

```bash
python confluence_export_to_docx.py
```

4. Output will be created in `<Output_Folder>/`:

   * Cleaned and structured HTML
   * `.docx` versions of each page (with embedded images)

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
