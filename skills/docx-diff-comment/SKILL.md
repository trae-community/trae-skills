---
name: docx-diff-comment
description: Compare two Word documents to find new features in V2, add comments to the V2 document for each new feature, and generate a requirements table with effort estimation in person-days. Invoke when user asks to compare two docx documents, add comments for new features, or generate a requirements diff table.
---

# Docx Diff & Comment

## Description

This skill compares two versions of a Word document (V1 and V2), identifies new features added in V2, adds Word comments (annotations) to the V2 document at each new feature location, and generates a standalone requirements table sorted by development effort (person-days).

## Usage Scenario

- Comparing two versions of a requirements document or project plan
- Annotating new features in a revised document
- Generating a development effort estimation table for new requirements

## Instructions

### Step 1: Extract Text & Compare

1. Use `pandoc` to convert both docx files to markdown:
   ```
   pandoc v1.docx -o v1_content.md
   pandoc v2.docx -o v2_content.md
   ```
2. Read both md files, compare paragraph by paragraph, identify new features, chapters, and sub-modules in V2
3. For each new item, record: feature name, module, description

### Step 2: Add Comments to V2 Document

1. Unpack V2 docx:
   ```
   python scripts/unpack.py v2.docx v2_unpacked/
   ```
2. Read `v2_unpacked/word/document.xml`, locate the `<w:r>...</w:r>` block containing each new feature text
3. Create comments using `comment.py`:
   ```
   python scripts/comment.py v2_unpacked/ <comment_id> "V2 new feature: <description>"
   ```
4. Insert comment markers into document.xml:
   - Before the target `<w:r>`: `<w:commentRangeStart w:id="N"/>`
   - After `</w:r>`: `<w:commentRangeEnd w:id="N"/><w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="N"/></w:r>`
   - Markers must be direct children of `<w:p>`, never inside `<w:r>`
   - Insert from the end backward to avoid position offset
5. Pack the annotated document:
   ```
   python scripts/pack.py v2_unpacked/ v2_annotated.docx --original v2.docx
   ```
6. Run `sanitize.py` to clean up

### Step 3: Generate Requirements Table

Use `python-docx` to generate a Word table with these columns:

| Column | Description |
|--------|-------------|
| No. | Sorted by effort descending |
| Feature Name | Name of the new feature |
| Module | Functional module |
| Description | Brief description |
| Development Content | Specific dev work |
| Effort (person-days) | Estimated days |

Append summary row with total feature count and total person-days.

### Effort Estimation Reference

| Feature Type | Range (days) | Example |
|-------------|-------------|--------|
| New module with algorithm/model | 6-10 | AI calculation, NLP |
| Visualization integration | 4-6 | GIS map, dashboard |
| Interactive feature | 3-5 | Area selection, layer switch |
| Data storage/export | 2-3 | Save/download, file export |
| Statistics/classification | 1-2 | Status count, report filter |
| Documentation/design | 1 | Non-code item |

## Examples

### Input
User provides two docx files:
- `Platform_V1.docx` (old version)
- `Platform_V2.docx` (new version)

### Output
1. `Platform_V2_annotated.docx` — V2 document with comments on all new features
2. `V2_new_requirements_table.docx` — Requirements table sorted by effort, e.g.:

| No. | Feature | Module | Effort (days) |
|-----|---------|--------|---------------|
| 1 | AI Calculation | Investment | 8 |
| 2 | Map Visualization | Dashboard | 5 |
| 3 | Infrastructure Dashboard | Dashboard | 5 |
| ... | ... | ... | ... |
| Total | | | 34 |
