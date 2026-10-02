"""Final assembly of the English bank:
  1. places (auto-split + overrides)
  2. routes (ROUTES_EN + SAMPLE_ROUTES_EN)
  3. sign questions (EN captions)
  4. text questions/options/explanations via en_strings_fixed + overrides
  5. sign image paths unchanged (universal)
Output: app/questions_en.json
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_en_bank import (PLACE_OVERRIDES, QID_OVERRIDES, SIGN_OVERRIDES,  # noqa: E402
                           captions_en, caption_text, clean, extract_numbered,
                           load_zh, parse_places, parse_routes, split_place)
from routes_en import ROUTES_EN, SAMPLE_ROUTES_EN  # noqa: E402
from q_overrides import Q_OVERRIDES  # noqa: E402
from overrides import OPT_OVERRIDES  # noqa: E402

EN_STRINGS = '/tmp/en_strings_fixed.json'
OUT = '/Users/tomma/GIT/道路試資訊/app/questions_en.json'
BOOKLET_TXT = '/Users/tomma/.cursor/projects/Users-tomma-GIT/agent-tools/ecfbc93c-3bd0-4b0e-8d50-24ef6a790ca8.txt'
RUC_PDF = '/tmp/ruc_en.pdf'


def main():
    zh = load_zh()
    booklet_txt = open(BOOKLET_TXT, encoding='utf-8').read()
    places = parse_places(booklet_txt)
    routes = parse_routes(booklet_txt)
    pages = captions_en()
    en_map = json.load(open(EN_STRINGS, encoding='utf-8'))

    def en_of(kind, s, fallback=None):
        if s in Q_OVERRIDES:
            return Q_OVERRIDES[s]
        if s in OPT_OVERRIDES:
            return OPT_OVERRIDES[s]
        return en_map.get(f'{kind}:{s}', fallback if fallback is not None else s)

    out = []
    problems = []

    for q in zh:
        nq = {'id': q['id'], 'part': q['part'], 'cat': q['cat']}
        if q['src'] == '小冊子附錄二（地方及路線試題）':
            if q['id'] in QID_OVERRIDES:
                num, name, dist = QID_OVERRIDES[q['id']]
            else:
                m = re.search(r'(地方表|路線表)：(\d+)\.', q['ex'])
                if not m:
                    problems.append(('appendix-src', q['id']))
                    continue
                num = int(m.group(2))
                if m.group(1) == '地方表':
                    if num in PLACE_OVERRIDES:
                        name, dist = PLACE_OVERRIDES[num]
                    else:
                        sp = split_place(places[num])
                        if not sp:
                            problems.append(('place-split', q['id'], num))
                            continue
                        name, dist = sp
                else:
                    if num in ROUTES_EN:
                        start, dest, ansroute = ROUTES_EN[num]
                    else:
                        problems.append(('route-missing', q['id'], num))
                        continue
                    nq['q'] = (f'If you drive from {start} to {dest}, under normal traffic conditions and not '
                               f'considering tunnel fees (if applicable), which route is the most direct viable route?')
                    nq['opts'] = [ansroute if i == q['ans'] else o for i, o in enumerate(q['opts'])]
                    # distractor routes are zh; keep them EN-translated via options map
                    nq['opts'] = [en_of('o', o, o) for o in nq['opts']]
                    # ensure correct option equals EN answer route
                    nq['opts'][q['ans']] = ansroute
                    nq['ans'] = q['ans']
                    nq['src'] = 'Booklet Appendix II (Places & Routes)'
                    nq['ex'] = f'Booklet Appendix II, Route {num}: {start} to {dest} - {ansroute}'
                    out.append(nq)
                    continue
                nq['q'] = f'Where is {name}?'
                nq['opts'] = [dist if i == q['ans'] else o for i, o in enumerate(q['opts'])]
                nq['ans'] = q['ans']
                nq['src'] = 'Booklet Appendix II (Places & Routes)'
                nq['ex'] = f'Booklet Appendix II, Place {num}: {re.sub(r"^\\d+\\.\\s*", "", name)} - {dist}'
                out.append(nq)
                continue

        if q['cat'] == '交通標誌（圖片題）':
            page = int(q['img'].split('_')[0].split('/')[1][1:])
            num = int(re.search(r'標誌表第(\d+)號', q['ex']).group(1))
            if (page, num) in SIGN_OVERRIDES:
                cap = SIGN_OVERRIDES[(page, num)]
            else:
                caps = pages[page].get(num)
                cap = caption_text(caps) if caps else None
            nq['q'] = 'What does the traffic sign in the picture mean?'
            nq['img'] = q['img']
            nq['opts'] = [cap if i == q['ans'] else o for i, o in enumerate(q['opts'])]
            nq['opts'] = [en_of('o', o, o) for o in nq['opts']]
            nq['opts'][q['ans']] = cap
            nq['ans'] = q['ans']
            nq['src'] = f'RUC p.{page}'
            nq['ex'] = f"Road Users' Code p.{page}, sign {num}: {cap}"
            out.append(nq)
            continue

        if q['id'] in SAMPLE_ROUTES_EN:
            sr = SAMPLE_ROUTES_EN[q['id']]
            nq['q'] = (f'If you drive from {sr["start"]} to {sr["dest"]}, under normal traffic conditions and not '
                       f'considering tunnel fees (if applicable), which route is the most direct viable route?')
            nq['opts'] = list(sr['opts'])
            nq['ans'] = sr['ans']
            nq['src'] = 'TD Official Sample Questions'
            nq['ex'] = f'TD official sample: {sr["start"]} to {sr["dest"]} - {sr["opts"][sr["ans"]]}'
            out.append(nq)
            continue

        # text question (甲部 service knowledge / 乙部 RUC / TD samples)
        nq['q'] = en_of('q', q['q'])
        nq['opts'] = [en_of('o', o) for o in q['opts']]
        nq['ans'] = q['ans']
        nq['src'] = q['src'].replace('小冊子', 'Booklet p.').replace('守則', "RUC p.")
        ex_en = en_of('e', q.get('ex', ''), fallback='')
        nq['ex'] = ex_en if ex_en else en_of('e', q['ex'][:80], '')
        out.append(nq)

    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('EN bank written:', len(out), 'problems:', problems)


if __name__ == '__main__':
    main()
