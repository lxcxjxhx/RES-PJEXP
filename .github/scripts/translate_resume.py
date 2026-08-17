#!/usr/bin/env python3
"""
Translate resume.html (Chinese) into resume.en.html (English).

Structure-preserving translation: the HTML tree, all tags, styles, the base64
photo and every attribute except `lang`/`alt` are kept byte-for-byte; only the
human-readable text nodes (and img alt texts) are translated.

Translation backends (in priority order):
  1. DeepSeek chat completions - only if DEEPSEEK_API_KEY is set (best quality,
     consistent with the README translation workflow).
  2. Google Translate public endpoint (translate.googleapis.com, client=gtx)
     - free, no API key required. This is the default. Long segments are split
     into sentence-level chunks (<= 80 chars), each translated in its own
     request, because Google truncates longer multi-sentence requests.
  3. MyMemory (api.mymemory.translated.net) - free fallback if Google fails.

Environment:
  DEEPSEEK_API_KEY / DEEPSEEK_BASE_URL / DEEPSEEK_MODEL (optional, as in the
  README translation workflow). HTTP(S)_PROXY are honoured automatically when
  set (useful behind a local proxy).

Usage:
  python .github/scripts/translate_resume.py [input.html] [output.html]
  Defaults: resume.html -> resume.en.html
"""

import os
import re
import sys
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup, Comment

INPUT_FILE = sys.argv[1] if len(sys.argv) > 1 else "resume.html"
OUTPUT_FILE = sys.argv[2] if len(sys.argv) > 2 else "resume.en.html"

CJK_RE = re.compile(r'[\u4e00-\u9fff]')

API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
BASE_URL = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com').rstrip('/')
MODEL = os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')

# Google caps the number of translatable units per request; 4 is a safe margin.
MAX_BATCH = 4
GTX_DELIM = ' ~#~ '

# Tiny glossary for terms that translate poorly out of context (source -> target).
GLOSSARY = {
    '合并': 'Merged',
    '照片': 'Photo',
}

# Output-side normalisation for terms Google sometimes lowercases or rephrases.
TERM_FIXES = [
    (re.compile(r'\bsafety hyacinth\b', re.I), 'Security Hyacinth'),
    (re.compile(r'\bsecurity hyacinth\b', re.I), 'Security Hyacinth'),
    (re.compile(r'\bsafety engineer\b', re.I), 'Security Engineer'),
]

# Full-width punctuation -> ASCII (mainly for the MyMemory fallback).
FULLWIDTH = str.maketrans({
    '：': ':', '，': ',', '。': '.', '；': ';',
    '（': '(', '）': ')', '、': ',', '！': '!', '？': '?',
    '“': '"', '”': '"', '‘': "'", '’': "'",
})


def normalize(text):
    """Normalise a translated segment: full-width punct, whitespace, terms."""
    text = text.replace('——', ' - ')
    text = text.translate(FULLWIDTH)
    text = re.sub(r'\s+', ' ', text).strip()
    for pat, repl in TERM_FIXES:
        text = pat.sub(repl, text)
    return text


# ---- Backends ---------------------------------------------------------------

def deepseek_translate(segments):
    """Translate a batch with DeepSeek; markers guarantee a 1:1 mapping back."""
    markers = [f'\u27e6{i}\u27e7' for i in range(len(segments))]
    joined = '\n'.join(f'{m} {s}' for m, s in zip(markers, segments))
    payload = {
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': (
                'You translate Simplified Chinese to English for a resume. '
                'Keep every marker token such as \u27e60\u27e7 exactly as-is on its own line. '
                'Translate only the text after each marker. Output ONLY the translated lines.'
            )},
            {'role': 'user', 'content': joined},
        ],
        'temperature': 0.2,
        'max_tokens': 4096,
    }
    url = f'{BASE_URL}/chat/completions'
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    r = requests.post(url, headers=headers, json=payload, timeout=180)
    r.raise_for_status()
    content = r.json()['choices'][0]['message']['content']

    result = [''] * len(segments)
    pattern = re.compile(r'\u27e6(\d+)\u27e7\s*(.*?)(?=\u27e6\d+\u27e7|$)', re.S)
    for m in pattern.finditer(content):
        result[int(m.group(1))] = m.group(2).strip()
    return result


def _gtx_request(segments):
    """One gtx request for a small batch; returns translated strings or ''."""
    params = [('client', 'gtx'), ('sl', 'zh-CN'), ('tl', 'en'), ('dt', 't'),
              ('q', GTX_DELIM.join(segments))]
    r = requests.get(
        'https://translate.googleapis.com/translate_a/single',
        params=params, timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    # data[0] holds one array per sentence; join them all so multi-sentence
    # chunks are never truncated to their first sentence.
    full = ' '.join(seg[0] for seg in data[0] if seg and seg[0])
    parts = full.split('~#~')
    return [p.strip() for p in parts]


# Google truncates a single request at roughly 200 source characters, so
# segments are split into small sentence-level chunks (<= 80 chars); each
# chunk is then translated in its own request and joined back per segment.
CHUNK_LIMIT = 80

SENT_RE = re.compile(r'[^。！？；]+[。！？；]?')


def _split_segments(segments):
    """Return [(seg_idx, chunk), ...] with every chunk <= CHUNK_LIMIT chars."""
    out = []
    for i, s in enumerate(segments):
        if len(s) <= CHUNK_LIMIT:
            out.append((i, s))
            continue
        cur = ''
        for piece in SENT_RE.findall(s):
            if len(cur) + len(piece) <= CHUNK_LIMIT:
                cur += piece
                continue
            if cur:
                out.append((i, cur))
            while len(piece) > CHUNK_LIMIT:  # hard-cut an oversized sentence
                out.append((i, piece[:CHUNK_LIMIT]))
                piece = piece[CHUNK_LIMIT:]
            cur = piece
        if cur:
            out.append((i, cur))
    return out


def google_translate(segments):
    """Translate with Google gtx (free, keyless).

    One request per <= 80-char chunk. Batches are deliberately avoided:
    Google re-segments any multi-chunk request by sentence boundaries, which
    corrupts the delimiter mapping and drops content.
    """
    pairs = _split_segments(segments)
    translated = [None] * len(pairs)
    for k, (_, chunk) in enumerate(pairs):
        try:
            single = _gtx_request([chunk])
            if single and single[0]:
                translated[k] = single[0]
        except Exception:  # noqa: BLE001 - leave empty for mymemory mop-up
            pass

    # join the chunks back, one translated string per original segment
    out = [''] * len(segments)
    for (i, _), t in zip(pairs, translated):
        if t:
            out[i] = (out[i] + ' ' + t).strip() if out[i] else t
    return out


def mymemory_translate(segments):
    """Translate via the free MyMemory API (fallback), one request per segment."""
    out = []
    for s in segments:
        r = requests.get(
            'https://api.mymemory.translated.net/get',
            params={'q': s, 'langpair': 'zh-CN|en'},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        out.append(data.get('responseData', {}).get('translatedText') or '')
        time.sleep(0.25)
    return out


def translate_batch(batch):
    """Translate one batch of (text, setter) targets; fall back on failure."""
    segments = [text for text, _ in batch]
    for name, fn in (('deepseek', deepseek_translate), ('google', google_translate),
                     ('mymemory', mymemory_translate)):
        if name == 'deepseek' and not API_KEY:
            continue
        try:
            results = fn(segments)
        except Exception as e:  # noqa: BLE001 - fall back, keep original text
            print(f'  [WARN] {name} failed: {e}')
            continue
        # Mop up any empty slots via MyMemory, keep original text as last resort.
        empty = [i for i, t in enumerate(results) if not t]
        if empty and name != 'mymemory':
            try:
                mopped = mymemory_translate([segments[i] for i in empty])
                for i, t in zip(empty, mopped):
                    if t:
                        results[i] = t
            except Exception as e:  # noqa: BLE001
                print(f'  [WARN] mymemory mop-up failed: {e}')
        for i in empty:
            if not results[i]:
                results[i] = segments[i]
        return results, name
    return segments, 'none'


def main():
    with open(INPUT_FILE, encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # ---- collect targets: text nodes (skip comments) + img alt texts ----
    targets = []  # (text, setter)
    for s in soup.find_all(string=True):
        if isinstance(s, Comment):
            continue
        if s.strip() and CJK_RE.search(s):
            targets.append((s, lambda v, node=s: node.replace_with(v)))
    for img in soup.find_all('img'):
        alt = img.get('alt')
        if alt and CJK_RE.search(alt):
            targets.append((alt, lambda v, node=img: node.__setitem__('alt', v)))

    total_cjk = len(CJK_RE.findall(html))
    print(f'{len(targets)} text/alt target(s) to translate (source CJK chars: {total_cjk})')

    # ---- split off glossary hits (translate directly, no API needed) ----
    api_targets, direct = [], []
    for target in targets:
        (api_targets if target[0] not in GLOSSARY else direct).append(target)
    translated = 0
    for text, setter in direct:
        setter(GLOSSARY[text])
        translated += 1
    if direct:
        print(f'  {len(direct)} glossary term(s) applied directly')

    # ---- batch & translate ----
    batches, batch, size = [], [], 0
    for target in api_targets:
        text = target[0]
        if size + len(text) > 800 or len(batch) >= MAX_BATCH * 2:
            batches.append(batch)
            batch, size = [], 0
        batch.append(target)
        size += len(text) + 1
    if batch:
        batches.append(batch)

    translated_count = translated
    for i, batch in enumerate(batches, 1):
        results, backend = translate_batch(batch)
        for (text, setter), new_text in zip(batch, results):
            normalized = normalize(new_text)
            if normalized and normalized != text.strip():
                setter(normalized)
                translated_count += 1
        print(f'  batch {i}/{len(batches)} via {backend}')
        time.sleep(0.3)  # be gentle with the free endpoints
    # ---- language attribute -> English ----
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        html_tag['lang'] = 'en'

    # ---- leftover full-width punctuation in any remaining text node ----
    # e.g. "arXiv：" / "LinkedIn：" nodes contain no \u4e00-\u9fff chars, so
    # they were never selected for translation; normalise them to ASCII.
    for s in soup.find_all(string=True):
        if isinstance(s, Comment):
            continue
        t = s.translate(FULLWIDTH)
        if t != s:
            s.replace_with(t)

    out = str(soup)
    if out.startswith('\n'):
        out = out[1:]

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(out)
    print(f'[OK] {OUTPUT_FILE} written')

    remaining = len(CJK_RE.findall(out))
    ratio = remaining / total_cjk if total_cjk else 0
    if translated_count == 0:
        print('[ERROR] no text was translated - translation failed')
        sys.exit(1)
    if ratio > 0.1:
        print(f'  [WARN] {remaining} CJK chars remain ({ratio:.0%}) - check translation quality')

    print(f'[INFO] finished at {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")} UTC')


if __name__ == '__main__':
    main()
