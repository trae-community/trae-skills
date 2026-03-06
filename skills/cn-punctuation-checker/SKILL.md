---
name: "cn-punctuation-checker"
description: "Checks Chinese text for incorrect English punctuation marks. Invoke when user wants to find and fix wrong punctuation in Chinese copy."
---

# Chinese Punctuation Checker

A skill for detecting incorrect English punctuation marks in Chinese text.

## Features

1. **Auto Detection**: Detect English punctuation marks incorrectly used in Chinese text
2. **Precise Location**: Report line number, column number, and context snippet for each error
3. **Report Generation**: Output Markdown format inspection report
4. **Batch Fix**: One-click replacement of all incorrect punctuation with correct Chinese punctuation
5. **Project-wide Scan**: Support scanning entire project with automatic exclusion of code files

## Supported Punctuation Marks

| English | Chinese |
|---------|---------|
| , | ， |
| . | 。 |
| ? | ？ |
| ! | ！ |
| : | ： |
| ; | ； |
| " | " or " |
| ' | ' or ' |
| ( ) | （ ） |
| [ ] | 【 】 |
| - | — |
| ... | …… |

## Usage

### 1. Check a Single File

Users can provide a file path or file content, and the skill will automatically analyze and generate a report.

### 2. Check Entire Project

Use the following command to check the entire project:
```
Check English punctuation in the entire project
```

The skill will automatically:
- Scan text files in the project (including .js, .ts script files)
- Exclude code files (.py, .java, .go, .cpp, .c, .cs, .php, .rb, .swift, .kt, .css, etc.)
- Exclude build directories (node_modules, .git, dist, target, build, out, etc.)

### 3. Scan Scope

**Default file types to check (text files):**
- `.md` - Markdown documents
- `.txt` - Text files
- `.html`, `.htm` - HTML files
- `.xml` - XML files
- `.json` - JSON files (only check string values)
- `.yml`, `.yaml` - YAML config files
- `.properties` - Properties files
- `.vue`, `.jsx`, `.tsx`, `.js`, `.ts` - Framework template files and script files

**Default excluded directories:**
- `node_modules`
- `.git`
- `dist`
- `target`
- `build`
- `out`
- `.idea`
- `.vscode`
- `__pycache__`
- `.next`
- `.nuxt`

**Default excluded file types (code files):**
- `.css`, `.scss`, `.less`, `.sass`
- `.py`
- `.java`
- `.go`
- `.cpp`, `.c`, `.h`, `.hpp`
- `.cs`
- `.php`
- `.rb`
- `.swift`
- `.kt`
- `.rs`
- `.sql`

### 4. Generate Report

After checking, generate a Markdown format report including:
- Original content of incorrect punctuation
- Location info (file path, line number, column number)
- Context snippet
- Suggested correct Chinese punctuation replacement

### 5. Batch Fix

Provide one-click fix functionality to automatically replace all detected incorrect punctuation with correct Chinese punctuation.

## Output Format Example

```markdown
# Chinese Punctuation Check Report

## Summary
- Files checked: 5 files
- Total errors found: 15
- Check time: 2026-01-01 10:00:00

---

## Error Details

### File: docs/README.md

| Line | Column | Wrong | Correct | Context |
|-----|-----|---------|---------|-------|
| 5   | 12  | ,       | ，      | "Hello, world" |
| 10  | 8   | .       | 。      | "This is a sentence" |

### File: content/about.txt

| Line | Column | Wrong | Correct | Context |
|-----|-----|---------|---------|-------|
| 3   | 15  | !       | ！      | "Welcome!" |

---

## Batch Fix

15 incorrect punctuation marks detected. Do you want to fix all? (yes/no)
```

## Execution Flow

1. **Scan Project**: Traverse project directory, filter text files
2. **Filter Exclusions**: Exclude code files and specified directories
3. **Read Content**: Read each qualified file
4. **Detect Errors**: Use regex to identify English punctuation marks
5. **Record Location**: Record file path, line number, column number for each error
6. **Generate Report**: Output Markdown format inspection report
7. **Provide Fix**: Offer batch fix option

## Smart Detection Rules

To avoid false positives, the skill uses the following smart detection rules:

1. **Only check lines containing Chinese characters**: Skip lines without Chinese characters
2. **Exclude URLs and file paths**: Do not replace punctuation in URLs or file paths
3. **Exclude strings in code**: Skip code strings even in allowed file extensions
4. **Exclude comments**: Skip Markdown code blocks, HTML comments, etc.
