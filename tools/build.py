import pandas as pd, json, re, unicodedata, math, sys, collections
from maps import ACC, NOTE, BRAND, CURB, NICK, GLOSS, NICK2, TWB, DISC
HTML = sys.argv[1]
html = open(HTML).read()
RAW = html.split('const RAW = `')[1].split('`;')[0].strip().split('\n')
BP = json.loads(re.search(r'const BP=(\{.*?\});', html).group(1))

def norm(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower() if re.search('[A-Za-z]', str(s)) else str(s).lower()
    return re.sub(r'[^0-9a-z一-鿿]', '', s)
def slug(s): return re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()).strip('-')

d = pd.read_csv('aStyxxx__dataset_Fragrantica_perfumes/perfumes_actual.csv', low_memory=False)
c = pd.read_csv('leev75__fragrance-analytics-dashboard-/fra_cleaned.csv', sep=';', encoding='latin-1', on_bad_lines='skip')
country = c.groupby('Brand').Country.agg(lambda x: x.mode().iat[0]).to_dict()
REG = {'Japan':'日本','South Korea':'韓國','China':'中國','Hong Kong':'港台','Taiwan':'港台',
       'UAE':'中東','Arabia saudi ':'中東','Oman':'中東','Kuwait':'中東','Qatar':'中東','Bahrain':'中東','Bahrein':'中東','Turkey':'中東','Lebanon':'中東','Iran':'中東','Israel':'中東','Egypt':'中東'}
AMER_EU = {'France','USA','Italy','UK','Brazil','Spain','Germany','Sweden','Russia','Switzerland','Netherlands','Poland','Greece','Canada','Argentina','Latvia','Denmark','Czech Republic','Romania','Portugal','Australia','Ireland','Belgium','Monaco','Iceland','Bermuda','Peru','Mexico','Hungary','Ukraine','Finland'}
def region(b):
    if b in ('To Summer | 观夏',): return '中國'
    if b in ('Tamburins','Nonfiction'): return '韓國'
    if b == 'Shiro': return '日本'
    co = country.get(slug(b))
    if co in REG: return REG[co]
    if co in AMER_EU or co is None: return '歐美'
    return '其他'

inv = {v: k for k, v in CURB.items()}
brands, bidx = [], {}
def brand_i(b):
    if b not in bidx:
        cb = inv.get(b, b)
        pr = BP.get(cb)
        bidx[b] = len(brands); brands.append([b, region(b), BRAND.get(b, ''), pr or 0])
    return bidx[b]
notes, nidx = [], {}
def note_i(n):
    if n not in nidx: nidx[n] = len(notes); notes.append([n, NOTE.get(n.lower(), '')])
    return nidx[n]
perf, pidx = [], {}
def perf_i(n):
    if n not in pidx: pidx[n] = len(perf); perf.append(n)
    return pidx[n]

def parse(s):
    if not isinstance(s, str): return []
    out = []
    for x in s.split('|'):
        k, _, v = x.rpartition(':')
        try: out.append((k, float(v)))
        except: out.append((x, 0))
    return out

MO = ['soap','skin','morning','sea','rain','tea','garden','dessert','fire','study','temple','night']
nick = {(norm(b), norm(n)): a for b, n, a in NICK}
# curated keys
cur = {}
for i, l in enumerate(RAW):
    f = l.split('|'); n, b = f[0], f[1]
    db = CURB.get(b, b)
    cands = {n, re.sub(r'\s+(EDT|EDP)$', '', n), 'Replica ' + n, re.sub(r'\s[一-鿿]+$', '', n)}
    if n == 'N°5': cands.add('Chanel No 5 Eau de Parfum')
    for x in cands: cur[(norm(db), norm(x))] = i

rows, extras, matched = [], {}, set()
for r in d.itertuples(index=False):
    fam = collections.defaultdict(float)
    acc = parse(r.accords)
    for a, w in acc:
        k = ACC.get(a)
        if k: fam[k] += w / 100
    top = sorted(fam.items(), key=lambda x: -x[1])[:4]
    fs = {k: (3 if v >= 1.3 else 2 if v >= .65 else 1) for k, v in top if v >= .3}
    if not fs and top: fs = {top[0][0]: 2}
    sa = r.sillage_avg
    si = 1 if sa < 2.05 else 2 if sa < 2.55 else 3
    layers = []
    alln = []
    for col in ('notes_top', 'notes_middle', 'notes_base'):
        ns = [x for x, _ in sorted(parse(getattr(r, col)), key=lambda x: -x[1])][:5]
        alln += ns; layers.append(','.join(str(note_i(x)) for x in ns))
    if not any(layers):
        ns = [x for x, _ in sorted(parse(r.notes_flat), key=lambda x: -x[1])][:8]
        alln += ns; layers = [','.join(str(note_i(x)) for x in ns)]
    low = ' '.join(alln).lower()
    accd = dict(acc)
    g = lambda k: fs.get(k, 0)
    m = 0
    cond = [g('msk') >= 2 or accd.get('soapy', 0) >= 40 or accd.get('aldehydic', 0) >= 50,
            g('msk') >= 2 and sa < 2.3,
            g('cit') >= 2, g('aqu') >= 2, g('grn') >= 2, 'tea' in low or 'mate' in low,
            g('flo') >= 2 or g('wht') >= 2, g('gou') >= 3 or (g('gou') >= 2 and g('fru') >= 1),
            (g('amb') >= 2 or g('smk') >= 2) and (g('gou') or g('wod')),
            g('lea') >= 2 or (g('wod') >= 3 and g('flo') < 2),
            any(x in low for x in ('incense', 'olibanum', 'frankincense', 'myrrh')) or g('smk') >= 2,
            (g('amb') >= 2 or g('wht') >= 2 or g('gou') >= 2) and sa >= 2.4]
    for j, cnd in enumerate(cond):
        if cnd: m |= 1 << j
    s = ''
    if g('flo') or g('grn') or g('fru') or g('wht'): s += 's'
    if g('cit') or g('aqu') or g('grn'): s += 'u'
    if g('wod') or g('amb') or g('lea') or g('smk') or g('fru'): s += 'a'
    if g('amb') or g('gou') or g('smk') or g('lea'): s += 'w'
    s = s or 'suaw'
    gen = {'female': 0, 'male': 1}.get(r.gender, 2)
    pf = [perf_i(x.strip()) for x in re.split(r'\||,', r.perfumers)] if isinstance(r.perfumers, str) else []
    url = r.url.split('/perfume/')[-1].replace('.html', '')
    yr = int(r.year) if r.year == r.year else 0
    key = (norm(r.brand), norm(r.name))
    rec = [r.name, brand_i(r.brand), yr, gen, ''.join(f'{k}{v}' for k, v in fs.items()), ';'.join(layers),
           ','.join(map(str, pf)), si, round(r.longevity_avg * 10), round(r.rating_avg * 100), int(r.vote_count), url, m, s, nick.get(key, '')]
    if key in cur and cur[key] not in matched:
        matched.add(cur[key]); extras[cur[key]] = [yr, gen, rec[5], rec[8], rec[9], rec[10], url, nick.get(key, '')]
        continue
    rows.append(rec)

# prefix fallback for curated not matched exactly
for i,l in enumerate(RAW):
    if i in matched: continue
    f=l.split('|'); n,b=f[0],f[1]; db=CURB.get(b,b)
    base=norm(re.sub(r'\s+(EDT|EDP)$','',n)).replace('n5','no5')
    if not base or re.search('[\u4e00-\u9fff]',n): continue
    best=None
    for j,r in enumerate(rows):
        if brands[r[1]][0]==db and (norm(r[0]).startswith(base) or norm(r[0]).replace('replica','').startswith(base) or (len(base)>=5 and base in norm(r[0]))):
            if best is None or r[10]>rows[best][10]: best=j
    if best is not None:
        r=rows.pop(best); matched.add(i); extras[i]=[r[2],r[3],r[5],r[8],r[9],r[10],r[11],r[14]]
# nicknames for curated entries
for i,l in enumerate(RAW):
    f=l.split('|'); db=CURB.get(f[1],f[1]); nn=norm(re.sub(r'\s+(EDT|EDP)$','',f[0]))
    for b,n,a in NICK:
        if norm(b)==norm(db) and nn and (norm(n)==nn or norm(n).replace('replica','')==nn or norm(n).startswith(nn)):
            extras.setdefault(i,[0,2,'',0,0,0,'',''])[7]=a; break
for b in brands: b.append('')
for l in RAW:
    f=l.split('|'); db=CURB.get(f[1],f[1])
    if db in bidx: brands[bidx[db]][4]=f[3]
rows.sort(key=lambda x: -x[10])
rows=rows[:10000-len(RAW)]
def gloss(n):
    return ''.join(GLOSS.get(w.lower(),'').replace(' ','') for w in re.findall(r"[A-Za-zÀ-ÿ']+",n))
N2=[(b,norm(p),a) for b,p,a in NICK2]
def nick2(b,n):
    nn=norm(n); return ' '.join(a for bb,p,a in N2 if bb==b and nn.startswith(p))
DS={(b,n) for b,n in DISC}
for r in rows:
    b=brands[r[1]][0]
    r[14]=(r[14]+' '+nick2(b,r[0])).strip()
    r.append(gloss(r[0])); r.append(1 if (b,r[0]) in DS else 0)
for i,l in enumerate(RAW):
    f=l.split('|'); db=CURB.get(f[1],f[1])
    e=extras.setdefault(i,[0,2,'',0,0,0,'',''])
    e[7]=(e[7]+' '+nick2(db,f[0])).strip(); e.append(gloss(f[0]))
for b in brands:
    t=TWB.get(b[0]); b.append(t[0] if t else '')
    if t and t[2]: b[3]=[t[1],t[2]]
# pinyin map
from pypinyin import lazy_pinyin, Style
grp=collections.defaultdict(list)
for cp in range(0x4e00,0xa000):
    ch=chr(cp); py=lazy_pinyin(ch,style=Style.NORMAL,errors='ignore')
    if py and py[0]!=ch and py[0].isascii(): grp[py[0].replace('ü','v')].append(ch)
json.dump({k:''.join(v) for k,v in grp.items()},open('py.json','w'),ensure_ascii=False,separators=(',',':'))
out = {'brands': brands, 'notes': notes, 'perfumers': perf, 'rows': rows, 'extras': extras,
       'cols': 'name,brand,year,gender,fam,notes,perfumers,sillage,longevity10,rating100,votes,url,moods,seasons,nick,gloss,disc'}
json.dump(out, open('perfumes.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('rows', len(rows), 'brands', len(brands), 'notes', len(notes), 'perfumers', len(perf), 'matched', len(matched), '/', len(RAW))
print('UNMATCHED:', [RAW[i].split('|')[0] + ' / ' + RAW[i].split('|')[1] for i in range(len(RAW)) if i not in matched])
