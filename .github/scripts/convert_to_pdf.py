#!/usr/bin/env python3
"""Convert resume.html to PDF using weasyprint with Chinese font support.

Runs on GitHub Actions (Ubuntu) where fonts-noto-cjk / fonts-wqy-zenhei
are pre-installed via apt.  Weasyprint uses fontconfig to resolve fonts,
so we only need to make sure the CSS font-family matches an installed font.
"""

import subprocess
import sys
import re
import weasyprint


def get_cjk_fonts():
    """Return a prioritised list of installed CJK font family names."""
    try:
        result = subprocess.run(
            ["fc-list", ":lang=zh", "family"],
            capture_output=True, text=True, timeout=10,
        )
    except FileNotFoundError:
        print("ERROR: fc-list not found – install fontconfig", file=sys.stderr)
        return None

    raw = sorted(set(
        line.strip()
        for line in result.stdout.strip().split("\n")
        if line.strip()
    ))
    if not raw:
        return None

    # Priority: Noto Sans CJK SC > WenQuanYi Micro Hei > WenQuanYi Zen Hei > others
    priority = []
    others = []
    for f in raw:
        if "Noto Sans CJK SC" in f:
            priority.insert(0, f)
        elif "WenQuanYi Micro Hei" in f:
            priority.append(f)
        elif "WenQuanYi Zen Hei" in f:
            priority.append(f)
        else:
            others.append(f)
    return priority + others


def main():
    # Usage: python convert_to_pdf.py [input.html] [output.pdf]
    input_file = sys.argv[1] if len(sys.argv) > 1 else "resume.html"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "简历 钱佳宏.pdf"
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")

    fonts = get_cjk_fonts()
    if not fonts:
        print("ERROR: No CJK font found!", file=sys.stderr)
        sys.exit(1)

    primary = fonts[0]
    # Build a CSS font-family fallback chain
    font_chain = ", ".join(f'"{f}"' for f in fonts[:4]) + ", sans-serif"
    print(f"Primary CJK font: {primary}")
    print(f"Font chain: {font_chain}")

    with open(input_file, "r", encoding="utf-8") as f:
        html = f.read()

    # ── Step 1: Replace every font-family declaration inside <style> ──
    # The original CSS uses:
    #   font-family: "Microsoft YaHei", "PingFang SC", "SimHei", sans-serif;
    # We replace the entire value so weasyprint can resolve it via fontconfig.
    html = re.sub(
        r'(font-family\s*:\s*)[^;]+(;)',
        rf'\1{font_chain}\2',
        html,
    )

    # ── Step 2: Inject an override block before </head> ──
    # This guarantees every element uses the CJK font, even if inline styles
    # or other rules try to override it.
    override_css = f"""
<style>
  /* Force CJK font for PDF rendering (injected by convert_to_pdf.py) */
  body, h1, td, span, a, div, li, b, p {{
    font-family: {font_chain} !important;
  }}
</style>
"""
    html = html.replace("</head>", override_css + "</head>")

    # ── Step 3: Write temp file and convert ──
    temp_html = "/tmp/resume_converted.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Converting {temp_html} → PDF …")
    doc = weasyprint.HTML(filename=temp_html)
    doc.write_pdf(output_file)
    print("PDF generated successfully.")


if __name__ == "__main__":
    main()
