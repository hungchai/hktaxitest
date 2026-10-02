"""Build English question bank (JSON) for the HK Taxi & Ride-hailing Combined Written Test.

Sources (official Transport Department English materials):
  1. Taxi and Ride-hailing Vehicle Operation Booklet EN (2026-09-09) - Appendix II: places 1-255, routes 256-273
  2. Road Users' Code EN (June 2020) - Part B text + sign captions (printed pages 111/112/114 orders 1-104, 116/117/118 warnings 1-67)

Output: app/questions_en.json - same schema as zh QUESTIONS.
"""
import json
import re

from pypdf import PdfReader

BOOKLET_TXT = '/Users/tomma/.cursor/projects/Users-tomma-GIT/agent-tools/ecfbc93c-3bd0-4b0e-8d50-24ef6a790ca8.txt'
RUC_PDF = '/tmp/ruc_en.pdf'
ZH_HTML = '/Users/tomma/GIT/道路試資訊/app/index.html'
OUT = '/Users/tomma/GIT/道路試資訊/app/questions_en.json'

DISTRICTS = '''Sandy Bay, Pok Fu Lam, Sha Tin, Tai Wai, Sheung Wan, Wong Chuk Hang, Wong Chuk Hang Path, Chai Wan,
Tai Hang, Wan Chai, Causeway Bay, Yau Ma Tei, Kowloon City, Lok Fu, Shatin Pass Road, Wong Tai Sin,
Cheung Sha Wan, Lai King, Kwai Chung, Tsuen Wan, Tsuen King Circuit, Sau Mau Ping, Tseung Kwan O, Po Ning Lane,
A Kung Kok, A Kung Kok Street, Tai Po, Chuen On Road, Sheung Shui, Fanling, Tsing Chung Koon Road, Yuen Long, Kam Tin, Pat Heung,
Mid-Levels, The Peak, Happy Valley, Sham Shui Po, Un Chau Street, Tung Chau Street, Lei Yue Mun Road,
Tin Shui Wai, Tsim Sha Tsui, Tsim Sha Tsui East, Tung Chung, Tat Tung Road, Quarry Bay, Taikoo Shing, Sai Wan Ho,
Kwun Tong, Fu Kin Street, Central, Shek Tong Tsui, North Point, Fortress Hill, Tin Hau, Jordan, Mong Kok, Prince Edward,
To Kwa Wan, Hung Hom, Ho Man Tin, Kowloon Tong, Kowloon Bay, Ngau Tau Kok, Diamond Hill, San Po Kong,
Cheung Sha, Chek Lap Kok, Stanley, Aberdeen, Ap Lei Chau, Repulse Bay, Tai Koo, Sai Ying Pun, Kennedy Town, Cyberport,
Cheung Chau, Discovery Bay, Siu Sai Wan, Heng Fa Chuen, Lam Tin, Yau Tong, Tiu Keng Leng,
Sai Kung, Sha Tau Kok, Shek Kong, Tsing Yi, Ma On Shan, Wu Kai Sha, Lantau, Tai O, Tong Fuk,
So Kon Po, Jardine's Lookout, Braemar Hill, Stubbs Road, Wong Nai Chung Gap, Shouson Hill, Chung Hom Kok,
Stone Nullah Lane, Old Peak Road, Robinson Road, Caine Road, Conduit Road,
Tuen Mun, Tuen Hi Road, Penny's Bay, Canton Road, Museum Drive, Austin Road West, Tai Kok Tsui, So Kwun Wat,
Queen's Road East, Harbour Road, Queensway, Pui Ching Road, Gascoigne Road, Hoi Ting Road, Ma Tau Kok Road,
Ngan Kwong Wan Road, Che Kung Miu Road, Pak Shek Kok, Chui Ling Lane, Bonham Road, Kai Tak, Admiralty,
Hospital Road, Junction Road, Kadoorie Avenue, Ede Road, Chak Cheung Street, Ngong Ping, Johnston Road,
Hollywood Road, Ting Kau, Lai Wan Road, Hing Fong Road, Kai Shing Street, Lai Chi Kok, Ma Wan, Clear Water Bay,
Siu Lek Yuen, Tat Chee Avenue'''.replace('\n', ' ')
DISTRICTS = [d.strip() for d in DISTRICTS.split(',') if d.strip()]

# num -> (name, district); used where the automatic split fails on PDF extraction artefacts
PLACE_OVERRIDES = {
    7: ('Pamela Youde Nethersole Eastern Hospital', 'Chai Wan'),
    37: ('Precious Blood Hospital (Caritas)', 'Sham Shui Po'),
    43: ('Castle Peak Hospital', 'Tuen Mun'),
    26: ('Shatin Hospital', 'A Kung Kok'),
    52: ('The CUHK Medical Centre', 'Chak Cheung Street'),
    55: ('Hong Kong Disneyland', "Penny's Bay"),
    61: ('Po Lin Monastery', 'Ngong Ping'),
    75: ('1881 Heritage', 'Canton Road'),
    82: ('The Pawn', 'Johnston Road'),
    83: ('Tai Kwun', 'Hollywood Road'),
    88: ('M+ Museum', 'Museum Drive'),
    117: ('The Ritz-Carlton, Hong Kong', 'Austin Road West'),
    119: ('Dorsett Mongkok, Hong Kong', 'Tai Kok Tsui'),
    128: ('Royal View Hotel', 'Ting Kau'),
    129: ('Hong Kong Gold Coast Hotel', 'So Kwun Wat'),
    134: ("Disney's Hollywood Hotel", "Penny's Bay"),
    136: ('Hong Kong SkyCity Marriott Hotel', 'Chek Lap Kok'),
    137: ('Regal Airport Hotel', 'Chek Lap Kok'),
    116: ('W Hong Kong', 'Austin Road West'),
    139: ('Queensway Government Offices', 'Queensway'),
    144: ('West Kowloon Government Offices', 'Hoi Ting Road'),
    145: ('Pui Ching Road Government Offices', 'Pui Ching Road'),
    147: ('Ma Tau Kok Road Government Offices', 'Ma Tau Kok Road'),
    151: ('Lai Chi Kok Government Offices', 'Lai Wan Road'),
    159: ('Kwai Hing Government Offices', 'Hing Fong Road'),
    160: ('Tuen Mun Government Offices', 'Tuen Hi Road'),
    161: ('Tai Hing Government Offices', 'Tuen Mun'),
    163: ('Mui Wo Government Offices', 'Ngan Kwong Wan Road'),
    164: ('Electrical and Mechanical Services Department Headquarters', 'Kai Shing Street'),
    177: ('District Court', 'Harbour Road'),
    184: ('Tuen Mun Law Courts Building', 'Tuen Hi Road'),
    185: ('Labour Tribunal', 'Gascoigne Road'),
    195: ('Lippo Centre', 'Admiralty'),
    211: ('Festival Walk', 'Tat Chee Avenue'),
    216: ('AIRSIDE', 'Kai Tak'),
    219: ('The Wai', 'Che Kung Miu Road'),
    231: ('Mei Foo Sun Chuen', 'Lai Chi Kok'),
    237: ('Park Island', 'Ma Wan'),
    240: ('Mayfair By The Sea', 'Pak Shek Kok'),
    244: ('Main Building of The University of Hong Kong', 'Bonham Road'),
    246: ('The Hong Kong University of Science and Technology', 'Clear Water Bay'),
    254: ('The Hang Seng University of Hong Kong', 'Siu Lek Yuen'),
    255: ('Saint Francis University', 'Chui Ling Lane'),
    30: ('Tuen Mun Hospital', 'Tsing Chung Koon Road'),
    34: ("St. Paul's Hospital", 'Eastern Hospital Road'),
    47: ('Tin Shui Wai Hospital', 'Tin Tan Street'),
    62: ('The Peak Tower', 'Peak Road'),
    76: ('Sha Tin Town Hall', 'Yuen Wo Road'),
    89: ('Kai Tak Sports Park', 'Shing Kai Road'),
    138: ('Central Government Offices', 'Tim Mei Avenue'),
    141: ('North Point Government Offices', 'Java Road'),
    142: ('Mong Kok Government Offices', 'Luen Wan Street'),
    146: ('Ho Man Tin Government Offices', 'Chung Hau Street'),
    148: ('To Kwa Wan Government Offices', 'Ma Tau Wai Road'),
    153: ('Ngau Tau Kok Government Offices', 'On Wah Street'),
    154: ('Sai Kung Government Offices', 'Chan Man Street'),
    155: ('Sha Tin Government Offices', 'Sheung Wo Che Road'),
    156: ('Tai Po Government Offices', 'Ting Kok Road'),
    158: ('Tsuen Wan Government Offices', 'Sai Lau Kok Road'),
    162: ('Yuen Long Government Offices', 'Kiu Lok Square'),
    166: ('Central District Police Station', 'Chung Kong Road'),
    169: ('Tseung Kwan O District Police Station', 'Po Lam Road North'),
    180: ('Kowloon City Law Courts Building', 'Argyle Street'),
    182: ('Sha Tin Law Courts Building', 'Yi Ching Lane'),
    183: ('Fanling Law Courts Building', 'Pik Fung Road'),
    857: ('The Chinese University of Hong Kong', 'Sha Tin'),  # id-level: appended below via qid
}

# qid -> (name, district) for rows whose zh ex lacks a parsable entry number
QID_OVERRIDES = {
    857: (245, 'The Chinese University of Hong Kong', 'Sha Tin'),
}

# EN sign captions where PDF extraction merges cells (page, num) -> caption
SIGN_OVERRIDES = {
    (112, 55): 'No vehicles over length shown',
    (112, 56): 'No vehicles over gross vehicle weight shown',
}


def clean(s):
    return re.sub(r'\s+', ' ', s.replace('|', ' ')).strip()


def load_zh():
    html = open(ZH_HTML, encoding='utf-8').read()
    return json.loads(re.search(r'const QUESTIONS = (\[.*?\]);\n', html, re.S).group(1))


def extract_numbered(text):
    toks = [(m.start(), int(m.group(1))) for m in re.finditer(r'(?<![\d.])(\d{1,3})\.\s', text)]
    ent = {}
    for i, (pos, num) in enumerate(toks):
        end = toks[i + 1][0] if i + 1 < len(toks) else len(text)
        if num not in ent:
            ent[num] = clean(text[pos:end])
    return ent


def parse_places(booklet_txt):
    seg = booklet_txt[booklet_txt.find('II. Location'):booklet_txt.find('Routes')]
    ent = extract_numbered(seg)
    missing = set(range(1, 256)) - set(ent)
    # 7/37 are split across page-header rows; add from pypdf text if missing
    if missing:
        r = PdfReader('/tmp/taxi_booklet_en.pdf')
        more = extract_numbered('\n'.join((p.extract_text() or '') for p in r.pages[13:23]))
        for n in list(missing):
            if n in more:
                ent[n] = more[n]
                missing.discard(n)
    assert not missing, f'places missing: {sorted(missing)[:10]}'
    return ent


def parse_routes(booklet_txt):
    seg = booklet_txt[booklet_txt.find('Routes'):]
    ent = extract_numbered(seg)
    assert set(ent) == set(range(256, 274)), f'routes missing: {sorted(set(range(256, 274)) - set(ent))}'
    return ent


def split_place(body):
    body = re.sub(r'^\d+\.\s*', '', body)  # strip leading entry number
    words = body.split(' ')
    best = None
    for d in DISTRICTS:
        parts = d.split(' ')
        for i in range(1, len(words)):
            if words[i:i + len(parts)] == parts:
                if best is None or i < best:
                    best = i
                break
    if best is None:
        return None
    return ' '.join(words[:best]).strip(' ,'), ' '.join(words[best:]).strip(' ,')


def captions_en():
    r = PdfReader(RUC_PDF)
    pages = {}
    for printed in [111, 112, 114, 116, 117, 118]:
        t = r.pages[printed + 1].extract_text() or ''
        pages[printed] = extract_numbered(t)
    return pages


def caption_text(caps):
    m = re.match(r'\d+\.\s*(.*)$', caps)
    body = m.group(1) if m else caps
    return re.sub(r'The Language of the Road.*$', '', body).strip()


def main():
    zh = load_zh()
    booklet_txt = open(BOOKLET_TXT, encoding='utf-8').read()
    places = parse_places(booklet_txt)
    routes = parse_routes(booklet_txt)
    pages = captions_en()

    out = []
    problems = []

    for q in zh:
        nq = dict(q)
        if q['src'] == '小冊子附錄二（地方及路線試題）':
            if q['id'] in QID_OVERRIDES:
                num, name, dist = QID_OVERRIDES[q['id']]
                nq['q'] = f'Where is {name}?'
                nq['opts'] = [dist if i == q['ans'] else o for i, o in enumerate(q['opts'])]
                nq['ex'] = f'Booklet Appendix II, Place {num}: {name} - {dist}'
                nq['src'] = 'Booklet Appendix II (Places & Routes)'
                out.append(nq)
                continue
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
                        problems.append(('place-split', q['id'], num, places[num]))
                        continue
                    name, dist = sp
                nq['q'] = f'Where is {name}?'
                nq['opts'] = [dist if i == q['ans'] else o for i, o in enumerate(q['opts'])]
                nq['ex'] = f'Booklet Appendix II, Place {num}: {name} - {dist}'
                nq['src'] = 'Booklet Appendix II (Places & Routes)'
            else:
                rb = re.match(r'\d+\.\s*(.*)$', routes[num]).group(1)
                nq['_route_raw'] = rb
        elif q['cat'] == '交通標誌（圖片題）':
            page = int(q['img'].split('_')[0].split('/')[1][1:])
            num = int(re.search(r'標誌表第(\d+)號', q['ex']).group(1))
            if (page, num) in SIGN_OVERRIDES:
                cap = SIGN_OVERRIDES[(page, num)]
            else:
                caps = pages[page].get(num)
                if caps is None:
                    problems.append(('sign-caption', q['id'], page, num))
                    continue
                cap = caption_text(caps)
            nq['q'] = 'What does the traffic sign in the picture mean?'
            nq['opts'] = [cap if i == q['ans'] else o for i, o in enumerate(q['opts'])]
            nq['ex'] = f"Road Users' Code p.{page}, sign {num}: {cap}"
            nq['src'] = f'RUC p.{page}'
        else:
            nq['_zh'] = True  # glossary pass
        out.append(nq)

    json.dump(out, open('/tmp/en_stage.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print('stage saved:', len(out), 'problems:', len(problems))
    for p in problems[:30]:
        print(p)


if __name__ == '__main__':
    main()
