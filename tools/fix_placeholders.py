"""Repair damaged placeholder tokens and residual zh glossary terms in MT output.

%%N%% / %N% / % N% tokens -> replace with the Nth glossary term EN translation.
Also strips stray '%' left after restore, and fixes '10%' artifacts from numbers like '10分'.
"""
import json
import re
import sys

sys.path.insert(0, '/Users/tomma/GIT/道路試資訊/tools')
from glossary import glossary_sub, TERMS  # noqa: E402

IN = '/tmp/en_strings.json'
OUT = '/tmp/en_strings_fixed.json'


def restore(zh, en):
    # map glossary term -> its slot index in zh
    _, m = glossary_sub(zh)
    slots = {}
    for k, v in m.items():
        n = int(re.search(r'\d+', k).group())
        slots[n] = v

    def repl(mm):
        n = int(mm.group(1))
        if n in slots:
            return ' ' + TERMS[slots[n]] + ' '
        return ' '

    en = re.sub(r'%\s*%?\s*(\d+)\s*%?\s*%?', repl, en)
    # collapse artifacts
    en = re.sub(r'\s+', ' ', en)
    en = re.sub(r'\s+([,.;:?!])', r'\1', en)
    en = re.sub(r'(\d)% ', r'\1 per cent ', en)
    en = re.sub(r'%', '', en)
    en = en.strip()
    if en and en[-1] not in '.?!:':
        en += '.'
    return en


def main():
    data = json.load(open(IN))
    fixed = {}
    n_rep = 0
    for key, en in data.items():
        kind, zh = key.split(':', 1)
        if re.search(r'%\s*\d', en) or '%%' in en:
            en2 = restore(zh, en)
            n_rep += 1
        else:
            en2 = en
        fixed[key] = en2
    json.dump(fixed, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
    print('repaired', n_rep, '->', OUT)


if __name__ == '__main__':
    main()
