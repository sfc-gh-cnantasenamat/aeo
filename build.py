#!/usr/bin/env python3
"""
Build a Matrix-themed HTML presentation from markdown slides.

Reads slide content from a markdown file (slides separated by ---) and injects
it into the HTML template to produce a standalone .html file.

Usage:
    python3 build.py --slides presentation.md                    # Minimal
    python3 build.py --slides slides.md --output deck.html       # Custom output
    python3 build.py --slides slides.md --title "My Talk"        # Custom title
    python3 build.py --slides slides.md --template custom.html   # Custom template
"""

import argparse
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(SCRIPT_DIR, 'template.html')

SLIDES_PLACEHOLDER = '%%SLIDES_DATA%%'
TITLE_PLACEHOLDER = '%%TITLE%%'


def parse_slides(md_path):
    """Parse markdown file into list of slide content strings."""
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    parts = re.split(r'^---\s*$', text, flags=re.MULTILINE)

    slides = []
    for part in parts:
        content = part.strip()
        if content:
            slides.append(content)

    return slides


def extract_title_from_slides(slides):
    """Extract title from first slide's H1 heading."""
    if slides:
        match = re.search(r'^#\s+(.+)$', slides[0], re.MULTILINE)
        if match:
            return match.group(1).strip()
    return 'Presentation'


def slides_to_json(slides, title):
    """Convert list of slide markdown strings to SLIDES_DATA JSON block."""
    slide_objects = []
    for i, content in enumerate(slides):
        slide_objects.append({
            "id": f"slide-{i}",
            "content": content,
            "path": "main",
            "type": "normal"
        })

    data = {
        "title": title,
        "slides": slide_objects
    }

    json_str = json.dumps(data, indent=4, ensure_ascii=False)

    js_block = (
        '// ============================================================\n'
        '// SLIDES DATA\n'
        '// ============================================================\n'
        f'const SLIDES_DATA = {json_str};'
    )

    return js_block


def build(slides_md, template_html, output_html, title=None):
    """Build the final HTML from slides markdown and template."""
    if not os.path.exists(slides_md):
        print(f"Error: Slides file not found: {slides_md}")
        sys.exit(1)
    if not os.path.exists(template_html):
        print(f"Error: Template file not found: {template_html}")
        sys.exit(1)

    slides = parse_slides(slides_md)
    print(f"Parsed {len(slides)} slides from {os.path.basename(slides_md)}")

    if not title:
        title = extract_title_from_slides(slides)

    js_block = slides_to_json(slides, title)

    with open(template_html, 'r', encoding='utf-8') as f:
        template = f.read()

    if SLIDES_PLACEHOLDER not in template:
        print(f"Error: Placeholder '{SLIDES_PLACEHOLDER}' not found in template")
        sys.exit(1)

    output = template.replace(SLIDES_PLACEHOLDER, js_block)
    output = output.replace(TITLE_PLACEHOLDER, title)

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Built {os.path.basename(output_html)} ({len(output)} chars, {len(slides)} slides)")
    print(f"Title: {title}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build Matrix-themed HTML presentation from markdown slides')
    parser.add_argument('--slides', required=True, help='Path to markdown file with slides separated by ---')
    parser.add_argument('--template', default=DEFAULT_TEMPLATE, help='Path to HTML template (default: references/template.html)')
    parser.add_argument('--output', default=None, help='Output HTML path (default: same dir as slides, named presentation.html)')
    parser.add_argument('--title', default=None, help='Presentation title (default: extracted from first slide H1)')

    args = parser.parse_args()

    if not args.output:
        slides_dir = os.path.dirname(os.path.abspath(args.slides))
        args.output = os.path.join(slides_dir, 'presentation.html')

    build(args.slides, args.template, args.output, args.title)
