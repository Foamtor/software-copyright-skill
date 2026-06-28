# docxtpl Post-Processing Pitfalls

## Why Post-Processing is Needed

docxtpl renders Jinja2 templates into Word documents, but several issues require post-processing:

## Pitfall 1: Long Paragraphs with `\n`

**Problem**: When `content` field contains `\n` (newlines), docxtpl puts the entire text into a single paragraph. Only the first line gets first-line indent.

**Solution**: `split_long_paragraphs()` — split each `\n` into a separate paragraph, copying format from the original.

```python
# In content.json:
"content": "第一段内容。\n第二段内容。\n第三段内容。"

# After docxtpl render: ONE paragraph with all text
# After post_process: THREE paragraphs, each with proper indent
```

## Pitfall 2: Jinja2 Tags Become Empty Lines

**Problem**: `{% for %}` and `{% endfor %}` tags in the template become empty paragraphs after rendering.

**Solution**: `remove_consecutive_empty_lines()` — delete consecutive empty paragraphs, keeping only one.

```
Before: [Heading 1] → [empty] → [empty] → [Heading 2]
After:  [Heading 1] → [empty] → [Heading 2]
```

## Pitfall 3: Figure Captions Embedded in Content

**Problem**: Figure captions (e.g., "图8 系统总体架构图") are part of the `content` text, not separate paragraphs. This prevents:
- Setting different font size (14pt for captions vs 16pt for body)
- Centering captions
- Inserting images above captions

**Solution**: `split_paragraph_at_figure_captions()` — extract figure captions into separate paragraphs with 14pt, centered alignment.

## Pitfall 4: Image Insertion Position

**Problem**: Images should be inserted ABOVE the figure caption, not below.

**Wrong**: `doc.add_paragraph()` — appends to end of document
**Correct**: `para._element.addprevious(new_p)` — inserts before the caption paragraph

```python
# Wrong way (appends to end):
new_para = doc.add_paragraph()

# Correct way (inserts before caption):
new_p = OxmlElement('w:p')
caption_para._element.addprevious(new_p)
new_para = Paragraph(new_p, caption_para._parent)
```

## Pitfall 5: Cover Formatting Overwritten

**Problem**: `apply_formatting()` iterates all paragraphs and applies styles. This overwrites the cover page formatting (title should be 22pt centered, not body style).

**Solution**: Find the first `Heading 1` paragraph index, skip all paragraphs before it.

```python
first_heading_idx = 0
for i, para in enumerate(doc.paragraphs):
    if para.style.name == 'Heading 1':
        first_heading_idx = i
        break

# Skip cover paragraphs
if para_idx < first_heading_idx:
    continue
```

## Pitfall 6: Page Header/Footer Placeholders

**Problem**: docxtpl does NOT replace text in headers/footers. The `{software_name}{version}` placeholder remains as-is.

**Solution**: After rendering, load the document with python-docx and manually replace header text + add PAGE field code to footer.

## Pitfall 7: `apply_formatting` Must Use Document Object

**Problem**: `replace_header_footer()` was called with file path string instead of Document object.

**Solution**: Load document first, then pass to function.

```python
# Wrong:
replace_header_footer(output_path, software_name, version)

# Correct:
doc = Document(output_path)
replace_header_footer(doc, software_name, version)
doc.save(output_path)
```

## Pitfall 8: Figure Caption Detection

**Problem**: Regex `r'^图\d+\s+'` only matches captions at start of paragraph. After splitting long paragraphs, captions may be at start of new paragraphs.

**Solution**: Split long paragraphs FIRST, then split figure captions.

## Processing Order

The order of post-processing steps matters:

1. **Split long paragraphs** — ensures each line is a separate paragraph
2. **Split figure captions** — extracts captions into separate paragraphs
3. **Insert images** — inserts images above caption paragraphs
4. **Remove empty lines** — cleans up Jinja2 artifacts
5. **Replace header/footer** — adds page numbers
6. **Apply formatting** — applies body/heading styles (skip cover)
