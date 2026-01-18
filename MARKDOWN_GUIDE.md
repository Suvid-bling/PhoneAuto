# Markdown Syntax Guide

This is a comprehensive guide to Markdown formatting.

## Headers

# H1 Header
## H2 Header
### H3 Header
#### H4 Header
##### H5 Header
###### H6 Header

## Text Formatting

**Bold text** or __bold text__

*Italic text* or _italic text_

***Bold and italic*** or ___bold and italic___

~~Strikethrough text~~

## Lists

### Unordered List
- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
- Item 3

### Ordered List
1. First item
2. Second item
3. Third item
   1. Nested item 3.1
   2. Nested item 3.2

### Task List
- [x] Completed task
- [ ] Incomplete task
- [ ] Another task

## Links and Images

[Link text](https://example.com)

[Link with title](https://example.com "Hover title")

![Image alt text](https://example.com/image.png)

## Code

Inline code: `print("Hello World")`

Code block with syntax highlighting:

```python
def hello_world():
    print("Hello, World!")
    return True
```

```javascript
function helloWorld() {
    console.log("Hello, World!");
}
```

## Blockquotes

> This is a blockquote
> It can span multiple lines
>
> > Nested blockquote

## Horizontal Rule

---

or

***

or

___

## Tables

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Row 1    | Data     | More data|
| Row 2    | Data     | More data|

Alignment:

| Left aligned | Center aligned | Right aligned |
|:-------------|:--------------:|--------------:|
| Left         | Center         | Right         |

## Escape Characters

Use backslash to escape special characters:

\*Not italic\*

\# Not a header

## HTML in Markdown

You can also use HTML tags:

<strong>Bold with HTML</strong>

<em>Italic with HTML</em>

<br>

## Footnotes

Here's a sentence with a footnote[^1].

[^1]: This is the footnote content.

## Definition Lists

Term 1
: Definition 1

Term 2
: Definition 2a
: Definition 2b

## Emoji (GitHub flavored)

:smile: :rocket: :thumbsup: :fire:

## Project-Specific Example

### Phone Automation Project

**Features:**
- Account Management
- Machine Management  
- SMS Login automation

**Quick Start:**
```bash
pip install -r requirements.txt
python SMSLogin/Auto.py
```

**Configuration:**
Edit `config.json` to set your parameters.

See [AccountManage](./AccountManage/) for account handling.
