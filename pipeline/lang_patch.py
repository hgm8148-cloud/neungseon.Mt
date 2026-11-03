"""산이 있는 나라 말 더하기 (2026-11-03)

모든 산: 한국어·영어·일본어·중국어. 해외 산 페이지에는 그 나라 말을 더해요.
  마터호른 독일어·프랑스어·이탈리아어 · 몽블랑 프랑스어·이탈리아어 · 트레치메 이탈리아어
  토레스 델 파이네 스페인어 · 에베레스트 네팔어 · 킬리만자로 스와힐리어
  (후지산 일본어, 황산 중국어, 하프돔·통가리로 영어는 이미 있어요)
번역은 i18n/<언어>.tsv (i18n/keys.json 의 한국어 문장 순서). 표에 없는 문장은 영어로 보여요.
번역 원문을 바꾸면 keys.json 과 줄 번호가 맞는지 확인해 주세요 (python3 lang_patch.py 로 점검).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, 'i18n')
NAMES = {'de': 'Deutsch', 'fr': 'Français', 'it': 'Italiano', 'es': 'Español', 'ne': 'नेपाली', 'sw': 'Kiswahili'}
PAGE_LANGS = {'matterhorn': ['de', 'fr', 'it'], 'montblanc': ['fr', 'it'], 'trecime': ['it'], 'torresdelpaine': ['es'],
              'everest': ['ne'], 'kilimanjaro': ['sw']}
# 템플릿 PAT 11개와 같은 순서: {T1}=번역한 첫 이름, {1}·{2}=숫자 그대로
PATX = {
    'de': ['{T1} hat gewinkt', 'Zurück zu {T1}', 'Du rastest kurz: {T1}', '{2} km bis {T1}', '{T1} passiert', '{1} km gegangen', 'Höhe {1} m', '{1} Std. {2} Min.', '{1} Min.', '{1}', '{1} steil'],
    'fr': ['{T1} vous a salué', 'Retour à {T1}', 'Petite pause : {T1}', '{2} km jusqu’à {T1}', '{T1} passé', '{1} km parcourus', 'Alt. {1} m', '{1} h {2} min', '{1} min', '{1}', '{1} raide'],
    'it': ['{T1} ti ha salutato', 'Di nuovo a {T1}', 'Una breve sosta: {T1}', '{2} km a {T1}', 'Superato {T1}', '{1} km percorsi', 'Alt. {1} m', '{1} h {2} min', '{1} min', '{1}', '{1} ripido'],
    'es': ['{T1} te saludó', 'De vuelta en {T1}', 'Un breve descanso: {T1}', '{2} km hasta {T1}', 'Pasado {T1}', '{1} km recorridos', 'Alt. {1} m', '{1} h {2} min', '{1} min', '{1}', '{1} empinado'],
    'ne': ['{T1} ले हात हल्लाउनुभयो', '{T1} मा फर्कनुभयो', 'केहीबेर आराम: {T1}', '{T1} सम्म {2} कि.मि.', '{T1} पार गरियो', '{1} कि.मि. हिँडियो', 'उचाइ {1} मि.', '{1} घण्टा {2} मिनेट', '{1} मिनेट', '{1} पटक', '{1} ठाडो'],
    'sw': ['{T1} amekupungia mkono', 'Umerudi {T1}', 'Pumziko fupi: {T1}', 'km {2} hadi {T1}', 'Umepita {T1}', 'km {1} umetembea', 'Mwinuko m {1}', 'saa {1} dakika {2}', 'dakika {1}', 'mara {1}', '{1} mkali'],
}
NOUN_FIRST = ['fr', 'it', 'es']   # 별명: 형용사 뒤에 명사 → 명사 앞에


def table(lang):
    keys = json.load(open(os.path.join(D, 'keys.json'), encoding='utf-8'))
    out = {}
    for line in open(os.path.join(D, lang + '.tsv'), encoding='utf-8'):
        if not line.strip(): continue
        i, tr = line.rstrip('\n').split('\t', 1)
        out[keys[int(i)]] = tr
    return out


I18N_JS = r'''
  const X = __X__, XP = __XP__, NOUN_FIRST = __NF__;
  const col = (r, k) => IDX[LANG] != null ? r[IDX[LANG]] : ((X[LANG] && X[LANG][k]) || r[1]);
  const patTr = (f, m, i) => { const o = f(m); if(o[LANG]) return o[LANG]; const t = XP[LANG] && XP[LANG][i]; return t ? t.replace(/\{T1\}/g, T(m[1])).replace(/\{(\d)\}/g, (_, d) => m[d]) : o.en; };'''


def patch_lang(P, m):
    langs = PAGE_LANGS.get(m['id'])
    if not langs: return
    X = {l: table(l) for l in langs}
    P.rep("const LANGS = { ko:'한국어', en:'English', ja:'日本語', zh:'中文' };",
          "const LANGS = { ko:'한국어', en:'English', ja:'日本語', zh:'中文', " + ', '.join(f"{l}:'{NAMES[l]}'" for l in langs) + " };", 1)
    P.rep("const IDX = { en:1, ja:2, zh:3 };", "const IDX = { en:1, ja:2, zh:3 };" + I18N_JS
          .replace('__X__', json.dumps(X, ensure_ascii=False)).replace('__XP__', json.dumps({l: PATX[l] for l in langs}, ensure_ascii=False))
          .replace('__NF__', json.dumps(NOUN_FIRST)), 1)
    P.rep("const r = DICT.get(k); if(r) return lead + r[IDX[LANG]] + trail;", "const r = DICT.get(k); if(r) return lead + col(r, k) + trail;", 1)
    P.rep("for(const [re, f] of PAT){ const m = k.match(re); if(m) return lead + f(m)[LANG] + trail; }",
          "for(let pi = 0; pi < PAT.length; pi++){ const [re, f] = PAT[pi]; const m = k.match(re); if(m) return lead + patTr(f, m, pi) + trail; }", 1)
    P.rep("(LANG==='en' ? ra[1]+' '+rb[1] : ra[IDX[LANG]] + rb[IDX[LANG]])",
          "(LANG==='en' ? ra[1]+' '+rb[1] : IDX[LANG] == null ? (NOUN_FIRST.includes(LANG) ? col(rb, b)+' '+col(ra, a) : col(ra, a)+' '+col(rb, b)) : ra[IDX[LANG]] + rb[IDX[LANG]])", 1)
    P.rep("if(g !== k && DICT.get(g)) return lead + DICT.get(g)[IDX[LANG]] + trail;", "if(g !== k && DICT.get(g)) return lead + col(DICT.get(g), g) + trail;", 1)
    # 기기가 있는 나라
    P.rep("for(const l of (navigator.languages && navigator.languages.length",
          "if(LANGS.ne && /^Asia\\/(Kathmandu|Katmandu)$/.test(tz)) return 'ne'; if(LANGS.sw && /^Africa\\/(Dar_es_Salaam|Nairobi|Kampala)$/.test(tz)) return 'sw';\n"
          "    for(const l of (navigator.languages && navigator.languages.length", 1)
    if 'ne' in langs:   # 데바나가리 글꼴 (휴대폰마다 기본 글꼴이 달라 글자가 깨지지 않게)
        P.rep('family=Gowun+Dodum&display=swap', 'family=Gowun+Dodum&family=Noto+Sans+Devanagari:wght@400;700&display=swap', 1)
        P.rep('--display:"Gowun Batang","Noto Serif KR",serif;', '--display:"Gowun Batang","Noto Serif KR","Noto Sans Devanagari",serif;', 1)
        P.rep('--body:"Gowun Dodum","Pretendard",', '--body:"Gowun Dodum","Noto Sans Devanagari","Pretendard",', 1)
    P.rep('<option value="zh">中文</option></select>', '<option value="zh">中文</option>' + ''.join(f'<option value="{l}">{NAMES[l]}</option>' for l in langs) + '</select>')


if __name__ == '__main__':
    keys = json.load(open(os.path.join(D, 'keys.json'), encoding='utf-8'))
    for l in NAMES:
        t = table(l); assert len(t) == len(keys), (l, len(t))
        print(l, len(t), 'OK')
