# Confluence HTML导出转换工具使用文档

本项目基于https://github.com/jrogersdb/convert-confluence-html-export-to-docx/ 进行了优化，同时支持了markdown和docx格式。

## 目录
- [功能概述](#功能概述)
- [系统要求](#系统要求)
- [安装指南](#安装指南)
- [使用方法](#使用方法)
  - [基本命令](#基本命令)
  - [参数详解](#参数详解)
  - [使用示例](#使用示例)
- [输出结构](#输出结构)
- [常见问题](#常见问题)
- [最佳实践](#最佳实践)

## 功能概述

本工具用于将Confluence导出的HTML空间转换为结构化文档，支持两种输出格式：

1. **Markdown**（默认输出）
   - 符合GitHub Flavored Markdown规范
   - 自动清理Confluence特有标签
   - 智能处理图片引用

2. **DOCX**（Word文档）
   - 保留原始格式
   - 支持自定义模板
   - 自动处理图表和附件

## 系统要求

| 组件 | 要求 |
|------|------|
| 操作系统 | Windows/macOS/Linux |
| Python | 3.6+ |
| 依赖包 | packaging, beautifulsoup4 |
| Pandoc | 1.12+ |

## 安装指南

### 1. 安装Python依赖

```bash
pip install packaging beautifulsoup4
```

### 2. 安装Pandoc

#### macOS (Homebrew)
```bash
brew install pandoc
```
#### Windows (Chocolatey)
```bash
choco install pandoc
```
#### Linux (APT)
```bash
sudo apt-get install pandoc
```
### 3. 验证安装
```bash
python convert_confluence.py --help
```
## 使用方法
### 基本命令
```bash
python convert_confluence.py [选项]
参数详解
参数	说明	默认值	示例
--export-root	Confluence导出目录	Exported_Space	--export-root /path/to/export
--output-root	输出目录	Output	--output-root /path/to/output
--type	输出格式 (markdown/docx)	markdown	--type docx
--skip-html	跳过HTML预处理	False	--skip-html
--cleanup	转换后删除中间文件	False	--cleanup
```
### 使用示例
#### 示例1：基本转换（Markdown）
python convert_confluence.py   --export-root Confluence_Export   --output-root Markdown_Output
#### 示例2：转换为Word文档
python convert_confluence.py   --type docx   --export-root Confluence_Export   --output-root Word_Docs
#### 示例3：继续未完成的转换
python convert_confluence.py   --skip-html   --export-root Confluence_Export
#### 示例4：转换后自动清理
python convert_confluence.py   --cleanup   --export-root Confluence_Export

## 输出结构
### Markdown输出
```bash
Output/
├── assets/               # 资源文件目录
│   ├── image1.png
│   └── attachment.pdf
├── 首页.md
└── 产品文档/
    ├── 功能说明.md
    └── 用户手册.md
```

### DOCX输出
```bash
Output/
├── images/               # 图片目录
│   ├── diagram1.png
│   └── screenshot.jpg
├── attachments/          # 附件目录
│   └── document.pdf
├── 首页.docx
└── 技术文档/
    ├── API参考.docx
    └── 部署指南.docx
```


## 常见问题
Q1: 转换失败怎么办？
- 检查错误日志
- 确认Pandoc已安装
- 尝试减少批量转换的文件数量

Q2: 图片显示不正常？
- 检查assets或images目录是否存在
- 确认图片路径是否正确
- 尝试使用--skip-html重新转换

Q3: 如何保留更多格式？
- 编辑template.docx自定义样式
- 修改Lua过滤器处理特定元素

## 最佳实践
首次测试
- 先用小空间导出测试，确认效果后再处理大空间




## 🧹 What Gets Cleaned / 清理了什么

The following elements are removed from the output:
以下元素将从输出中移除：

* Confluence **breadcrumbs** (`<div id="breadcrumb-section">`)  / Confluence 面包屑 ( <div id="breadcrumb-section"> )
* **Attachments sections** (`<h2 id="attachments">` and its surrounding container) / 附件部分（ <h2 id="attachments"> 及其周围容器）
* Internal links rewritten to point to relative `.docx` equivalents / 内部链接重写为指向相对的 .docx 等价项
* Asset links (images, styles) rewritten as relative paths / 资产链接（图片、样式）重写为相对路径


---

## 📃 Tips

* If `pandoc` isn't embedding images, it may be due to incorrect working directory. This script automatically invokes `pandoc` from the correct folder. / 如果 pandoc 没有嵌入图片，可能是由于工作目录不正确。此脚本会从正确的文件夹自动调用 pandoc 。

* You can modify the output folder name by changing the `OUTPUT_ROOT` variable inside the script. / 您可以通过修改脚本内的 OUTPUT_ROOT 变量来更改输出文件夹名称。


## 📄 License

MIT License
