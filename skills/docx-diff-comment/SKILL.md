---
name: docx-diff-comment
description: Compare two Word documents to find new features in V2, add comments to the V2 document for each new feature, and generate a requirements table with effort estimation in person-days. Invoke when user asks to compare two docx documents, add comments for new features, or generate a requirements diff table.
---

# Docx Diff & Comment

## Description

This skill compares two versions of a Word document (V1 and V2), identifies new features added in V2, adds Word comments (annotations) to the V2 document at each new feature location, and generates a standalone requirements table sorted by development effort (person-days).

## Prerequisites

The following tools are required:

- **pandoc**: Convert docx to markdown for text extraction and comparison
- **python-docx**: Generate the requirements table as a Word document
- **docx unpack/pack utilities**: Helper scripts (`unpack.py`, `comment.py`, `pack.py`, `sanitize.py`) to manipulate the OOXML structure of docx files (these scripts are typically available in docx-processing toolkits)

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
3. Create comments using `comment.py`. Use a consistent comment template and author:
   ```
   python scripts/comment.py v2_unpacked/ <comment_id> "V2 new feature: <module> / <feature>. Not present in V1, added in V2."
   ```
   - Comment author should be set to "AI Assistant"
   - `comment_id` starts from 0 and increments for each new feature
4. Insert comment markers into document.xml:
   - Before the target `<w:r>`: `<w:commentRangeStart w:id="N"/>`
   - After `</w:r>`: `<w:commentRangeEnd w:id="N"/><w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="N"/></w:r>`
   - Markers must be direct children of `<w:p>`, never inside `<w:r>`
   - Insert from the end backward to avoid position offset
5. Pack the annotated document:
   ```
   python scripts/pack.py v2_unpacked/ v2_annotated.docx --original v2.docx
   ```
6. Run `sanitize.py` to clean up any malformed XML or orphaned comment references

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

## Effort Estimation Reference

The following table provides reference effort ranges for common feature types. Final estimates should be adjusted based on actual complexity, team size, and technology stack.

| Feature Type | Reference Range (person-days) | Description | Example |
|-------------|------------------------------|-------------|---------|
| Brand-new independent module (with algorithm/model) | 6–10 | Module introduces new technical capability; may involve ML/NLP components | AI measurement, NLP parsing, rule engine |
| Visualization component integration | 4–6 | Integrate third-party or self-built visualization widgets | GIS map dashboard, chart library, data timeline |
| Interactive feature development | 3–5 | New user interactions on existing pages | Area selection query, layer toggle, drag-and-drop |
| Data storage / export enhancement | 2–3 | Extend existing data workflows | Save & download, Excel export, file upload |
| Statistics / classification function | 1–2 | Add or refine counting/categorical logic | Project status statistics, report breakdown by dimension |
| Documentation / process design | 1 | Non-code work items | API doc writing, mechanism design, acceptance plan |

> **Note**: These are reference values only. Always document assumptions in the table footer.

## Notes

1. **Comparison scope**: Focus on structural differences — new modules, sub-features, chapters. Ignore wording tweaks, typo fixes, and formatting changes.
2. **Cleanup**: Delete temporary files (`.md`, unpacked directories) after completion. Only keep the final deliverables.
3. **Deliverable naming convention**:
   - `{DocumentName}_V2_with_comments.docx` — Annotated V2 document with all new features highlighted
   - `V2_New_Requirements_Table.docx` — Requirements table sorted by effort (person-days), with summary row
4. **Batch comment insertion**: When inserting multiple comment markers in `document.xml`, always process from the **end of the file backward** to avoid position offsets.

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
