"""Batch-translate all unique zh strings -> EN with glossary + canonical patterns + MT.

Strategy per string:
  1. exact canonical pattern match (deterministic) - or plain glossary term
  2. glossary-protect -> opus-mt-zh-en -> restore EN terms
Run:  /tmp/pdfenv/bin/python translate_batch.py
Writes /tmp/en_strings.json : {"kind:zh": "en"}
"""
import json
import os
import re
import sys

os.environ['HF_HOME'] = '/tmp/hf'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transformers import pipeline  # noqa: E402

from glossary import TERMS, glossary_sub  # noqa: E402
from canon import CANON_Q, OPT_PREFIX  # noqa: E402

IN = '/tmp/zh_strings.json'
OUT = '/tmp/en_strings.json'


def canon_fill(tmpl, groups):
    parts = []
    for g in groups:
        e = TERMS.get(g)
        if e is None:
            return None
        parts.append(e)
    try:
        return tmpl.format(*parts)
    except Exception:
        return None


def clean_mt(en):
    en = re.sub(r'\s+', ' ', en).strip()
    if en and en[-1] not in '.?!:':
        en += '.'
    return en


def main():
    strings = [tuple(x) for x in json.load(open(IN))]
    pipe = pipeline('translation', model='Helsinki-NLP/opus-mt-zh-en', max_new_tokens=320)
    out = {}

    todo = []
    for kind, zh in strings:
        if not zh.strip():
            out[f'{kind}:{zh}'] = ''
            continue
        # 1. exact glossary term
        if zh in TERMS:
            out[f'{kind}:{zh}'] = TERMS[zh]
            continue
        # 2. canonical question patterns
        hit = None
        for pat, tmpl in CANON_Q:
            m = re.match(pat, zh)
            if m:
                hit = canon_fill(tmpl, m.groups())
                if hit:
                    break
        if hit:
            out[f'{kind}:{zh}'] = hit
            continue
        todo.append((kind, zh))

    print('pattern hits:', len(out) - 1, 'todo:', len(todo), flush=True)

    # 3. MT in batches (restore glossary terms after)
    B = 32
    for i in range(0, len(todo), B):
        batch = todo[i:i + B]
        prot = []
        maps = []
        for kind, zh in batch:
            t, m = glossary_sub(zh)
            prot.append(t)
            maps.append(m)
        results = pipe(prot, truncation=True)
        for (kind, zh), res, m in zip(batch, results, maps):
            en = res['translation_text']
            for k, v in m.items():
                en = en.replace(k, TERMS[v])
            out[f'{kind}:{zh}'] = clean_mt(en)
        if (i // B) % 10 == 0:
            print(f'{i + len(batch)}/{len(todo)}', flush=True)

    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
    print('saved', len(out), '->', OUT)


if __name__ == '__main__':
    main()
