# Confluence导出转换工具使用说明

## 📌 功能概述

本工具用于将Confluence导出的HTML空间转换为：
- **Markdown**（默认输出格式）
- **DOCX**（Microsoft Word格式）

主要功能特点：
✅ 保留原始页面层次结构  
✅ 自动清理Confluence特有元素  
✅ 智能处理图片和附件  
✅ 支持批量转换整个空间  

## 🛠️ 系统要求

- Python 3.6+
- Pandoc（文档转换工具）
- BeautifulSoup4（HTML处理库）

```bash
# 安装依赖
pip install packaging beautifulsoup4

# 安装Pandoc（各系统通用）
# macOS: brew install pandoc
# Windows: choco install pandoc
# Linux: sudo apt-get install pandoc

🚀 基本用法
bash
python convert_confluence.py [选项]
无参数运行时显示帮助
直接运行脚本将显示完整帮助信息和示例：

bash
python convert_confluence.py
⚙️ 参数说明
参数	说明	默认值
--export-root	Confluence导出目录路径	Exported_Space
--output-root	输出文件目录路径	Output
--type	输出格式 (markdown/docx)	markdown
--skip-html	跳过HTML预处理阶段	否
--cleanup	转换后删除中间HTML文件	否
🏆 最佳实践示例
示例1：转换为Markdown
bash
python convert_confluence.py \
  --export-root /path/to/confluence_export \
  --output-root /path/to/markdown_output
示例2：转换为DOCX
bash
python convert_confluence.py \
  --type docx \
  --export-root /path/to/confluence_export \
  --output-root /path/to/docx_output
示例3：仅转换（跳过HTML生成）
bash
python convert_confluence.py \
  --skip-html \
  --export-root /path/to/confluence_export
示例4：转换后自动清理
bash
python convert_confluence.py \
  --cleanup \
  --export-root /path/to/confluence_export
📂 输出结构
Markdown输出
text
Output/
├── assets/           # 图片/附件资源
├── 首页.md
├── 产品文档/
│   ├── 功能说明.md
│   └── 用户手册.md
└── 技术文档/
    ├── API参考.md
    └── 部署指南.md
DOCX输出
text
Output/
├── images/           # 图片资源
├── attachments/      # 附件文件
├── 首页.docx
├── 产品文档/
│   ├── 功能说明.docx
│   └── 用户手册.docx
└── 技术文档/
    ├── API参考.docx
    └── 部署指南.docx
💡 高级技巧
使用模板文件（仅DOCX）：

在脚本目录放置template.docx可自定义输出样式

图片处理：

Markdown格式使用assets统一目录

支持后处理Lua脚本（image-fullsize.lua）

错误排查：

bash
# 查看详细错误日志
python convert_confluence.py 2> error.log
⚠️ 注意事项
确保Confluence导出包含完整的：

index.html文件

images/和attachments/目录

首次使用建议不要加--cleanup参数，先检查输出结果

大空间转换建议：

bash
# Linux/Mac后台运行
nohup python convert_confluence.py > conversion.log 2>&1 &
转换中断后再次运行时，可添加--skip-html继续未完成的转换

📌 提示：转换完成后会显示详细的统计报告，包含成功/失败的文件数量





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
