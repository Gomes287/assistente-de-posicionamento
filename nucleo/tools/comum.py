"""Peças comuns do assistente-de-posicionamento: caminhos, perfil e medidas de texto. Só biblioteca padrão do Python."""
import json, os, re, sys, statistics, datetime
from pathlib import Path

NUCLEO = Path(__file__).resolve().parent.parent
CONF = Path(os.environ.get('ASSISTENTE_POSICIONAMENTO_CONF', Path.home() / '.config/assistente-de-posicionamento'))
PERFIL = CONF / 'perfil.json'
VOZ = CONF / 'voz.md'
NOTAS = CONF / 'notas.md'
HIST = CONF / 'historico.jsonl'

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

INTENCOES = ('amplificar', 'compartilhar', 'conversar', 'posicionar')
ESTRUTURAS = ('cena', 'numero', 'confissao', 'contraintuitivo', 'pergunta', 'antes_depois', 'lista_curta', 'carta',
              'dialogo', 'bastidor', 'leitura')
CORES_PADRAO = {"fundo": "#0F2A3D", "texto": "#F4F1EA", "acento": "#E3B25B", "suave": "#16384F"}
# paletas curadas (fundo escuro, texto claro, destaque, suave). A configuração oferece 3, escolhidas a partir do nome,
# para quem não tem identidade visual; ninguém fica com a padrão sem escolher.
CURADAS = {
    "petroleo-ambar":  {"fundo": "#0F2A3D", "texto": "#F4F1EA", "acento": "#E3B25B", "suave": "#16384F"},
    "grafite-coral":   {"fundo": "#1E2124", "texto": "#F5F2EE", "acento": "#FF7A59", "suave": "#2C3135"},
    "verde-musgo":     {"fundo": "#16281F", "texto": "#F1EFE6", "acento": "#C9D46B", "suave": "#21392D"},
    "vinho-areia":     {"fundo": "#3A1420", "texto": "#F6EEE6", "acento": "#E8B98F", "suave": "#4D1D2B"},
    "marinho-ciano":   {"fundo": "#0B1D3A", "texto": "#EEF3F8", "acento": "#3CC6D8", "suave": "#13294F"},
    "terracota":       {"fundo": "#2B1A14", "texto": "#F7EFE7", "acento": "#E07A4F", "suave": "#3B251C"},
    "berinjela-lima":  {"fundo": "#241A33", "texto": "#F3F0F7", "acento": "#B8E06A", "suave": "#33264A"},
    "carvao-ouro":     {"fundo": "#121212", "texto": "#F2EEE6", "acento": "#D4AF37", "suave": "#222222"},
}
PERFIL_PADRAO = {
    "nome": "", "titulo": "", "profissao": "", "arroba": "",
    "conselho": "nenhum",                 # "CFM" liga o módulo de médicos; outro nome = só lembrete
    "identificacao": "",                  # linha do conselho, ex. "MÉDICO · CRM-SP 123456 · Cardiologia · RQE 9876"
    "identificacao_no_perfil": False,     # a identificação já está no título/Sobre do perfil do LinkedIn?
    "sigilo": False,                      # conselheira/administradora com acesso a informação estratégica (módulo de sigilo)
    "situacao": "",                       # "ja_publica" | "nao_publica"
    "publico": "",
    "lembrado_por": "",                   # conhecimento | experiencia | visao | causa
    "posicionamento": "",                 # uma frase: pelo que quero ser lembrado
    "linhas": [],                         # [{"nome": "...", "descricao": "..."}], 3 fixas + 1 "teste"
    "cores": CORES_PADRAO, "cores_escolhidas": False, "tema": "editorial", "fonte_titulo": "Inter", "foto": "", "logo": "",
    "pasta_saida": str(Path.home() / 'Documents/LinkedIn'),
    "voz_medidas": {},
}


def carregar_perfil(obrigatorio=True):
    p = json.loads(json.dumps(PERFIL_PADRAO))
    if not PERFIL.exists():
        if obrigatorio:
            sys.exit('Sem perfil ainda. Rode a configuração (skill linkedin-config).')
        return p
    for k, v in json.load(open(PERFIL, encoding='utf-8')).items():
        if isinstance(v, dict) and isinstance(p.get(k), dict):
            p[k].update(v)
        else:
            p[k] = v
    return p


def salvar_perfil(p):
    CONF.mkdir(parents=True, exist_ok=True)
    json.dump(p, open(PERFIL, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


def hoje():
    return datetime.date.today().isoformat()


def slug(s, n=50):
    import unicodedata
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:n].strip('-') or 'post'


# ---- medidas de texto ---------------------------------------------------------------------------------------------
EMOJI = re.compile('[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF⭐⬆↔-⇿✅❌]')
PRIMEIRA = re.compile(r'\b(eu|meu|minha|meus|minhas|me|comigo|mim|a gente|n[óo]s|nosso|nossa|nossos|nossas)\b', re.I)
# verbos na 1ª pessoa (o português omite o pronome): -amos/-emos/-imos, 'somos' e pretérito em -ei (falei, pensei)
PRIMEIRA_VERBO = re.compile(r'\b(?:\w{2,}(?:amos|emos|imos)|somos|\w{3,}ei|acho|acredito|considero|penso|vejo|proponho|'
                            r'faço|chamo|sigo|quero|sei|tenho|digo|olho|vou|estou|sou|percebo|entendo|defendo|prefiro|'
                            r'aprendi|percebi|vivi|senti|decidi|escrevi|fui|fiz|tive|pude|quis|li|ouvi|perdi|errei)\b', re.I)


# voz passiva analítica: "foi decidido", "são observados", "tinha sido feito" (texto gerado usa mais)
PASSIVA = re.compile(r'\b(?:é|são|foi|foram|era|eram|será|serão|seria|seriam|sendo|sido|ser|está sendo|estão sendo)\s+'
                     r'(?:\w+mente\s+)?(?!(?:casad|cansad|obrigad|preocupad|furad|acostumad|interessad|ocupad|atrasad|'
                     r'errad|lotad|complicad|delicad|sofisticad|avançad|adequad|apropriad|conhecid|querid)\w*\b)'
                     r'[\wÀ-ú]{3,}(?:ado|ada|ados|adas|ido|ida|idos|idas|ito|ita|itos|itas|osto|osta|ostos|ostas)\b', re.I)
# pontuação de quem fala: pergunta, exclamação, parênteses, reticências (texto gerado usa menos)
EXPRESSIVA = re.compile(r'[?!(…]|\.\.\.')


def mtld(palavras, limiar=0.72):
    """Diversidade de vocabulário que não depende do tamanho do texto (McCarthy e Jarvis, 2010): quantas palavras,
    em média, até o vocabulário começar a se repetir. Maior = vocabulário mais variado. None se o texto for curto."""
    if len(palavras) < 100: return None
    def passada(ws):
        fatores, tipos, n = 0.0, set(), 0
        for w in ws:
            tipos.add(w); n += 1
            if len(tipos) / n <= limiar:
                fatores += 1; tipos, n = set(), 0
        if n: fatores += (1 - len(tipos) / n) / (1 - limiar)
        return len(ws) / fatores if fatores else len(ws)
    return round((passada(palavras) + passada(palavras[::-1])) / 2, 1)


def frases(t):
    t = re.sub(r'\s+', ' ', t)
    return [f for f in re.split(r'(?<=[.!?…])\s+', t) if len(f.split()) >= 2]


def paragrafos(t):
    ps = [p.strip() for p in re.split(r'\n\s*\n', t) if p.strip()]
    if len(ps) <= 1 and t.strip().count('\n') >= 3:   # texto colado do LinkedIn costuma vir com quebra simples
        ps = [l.strip() for l in t.split('\n') if l.strip()]
    return ps


def medir(t):
    fs = frases(t); ps = paragrafos(t); pal = t.split()
    tam = [len(f.split()) for f in fs] or [0]
    return {
        'caracteres': len(t.strip()),
        'palavras': len(pal),
        'frases': len(fs),
        'palavras_por_frase': round(statistics.mean(tam), 1),
        'frase_longa_p90': sorted(tam)[int(0.9 * (len(tam) - 1))],
        'variacao_frase': round(statistics.pstdev(tam), 1),
        'frases_curtas_pct': round(100 * sum(1 for x in tam if x <= 6) / len(tam)),
        'paragrafos': len(ps),
        'palavras_por_paragrafo': round(statistics.mean([len(p.split()) for p in ps]), 1) if ps else 0,
        'primeira_pessoa_por_100': round(100 * (len(PRIMEIRA.findall(t)) + len(PRIMEIRA_VERBO.findall(t))) / max(1, len(pal)), 1),
        'emojis': len(EMOJI.findall(t)),
        'hashtags': len(re.findall(r'(?<!\w)#\w+', t)),
        'perguntas': t.count('?'),
        'vocabulario_mtld': mtld(re.findall(r'[\wÀ-ú]+', t.lower())),
        'passiva_por_1000': round(1000 * len(PASSIVA.findall(t)) / max(1, len(pal)), 1),
        'pontuacao_expressiva_por_1000': round(1000 * len(EXPRESSIVA.findall(t)) / max(1, len(pal)), 1),
        'travessoes_por_1000': round(1000 * (t.count('—') + t.count(' – ')) / max(1, len(pal)), 1),
    }


def ler_textos(arquivos):
    """Um arquivo pode ter vários posts separados por uma linha com '---'."""
    out = []
    for a in arquivos:
        for bloco in re.split(r'\n\s*---+\s*\n', Path(a).read_text(encoding='utf-8')):
            if len(bloco.split()) >= 25:
                out.append(bloco.strip())
    return out


# ---- voz que aprende com o que a pessoa publica ------------------------------------------------------------------
# A voz é a mistura de duas fontes: a ÂNCORA (textos que a pessoa escreveu sem a skill, medidos na configuração) e os
# PUBLICADOS (versões finais dos posts feitos com a skill), cada um com peso = quanto do texto é dela. Post que ela
# quase não editou não entra: senão a skill aprende a própria voz e o verificador para de apontar os cacoetes.
# A âncora vale pelo menos metade enquanto existir. Posts e artigos têm vozes separadas.
PESO_MINIMO = 0.1
JANELA = 15


def _mediana_ponderada(pares):
    pares = sorted(pares); total = sum(w for _, w in pares); acc = 0
    for v, w in pares:
        acc += w
        if acc >= total / 2: return v
    return pares[-1][0]


def combinar_voz(p):
    """Recalcula p['voz_medidas'] (posts) e p['voz_medidas_artigo'] a partir da âncora e dos publicados."""
    ancora = p.get('voz_ancora') or {}
    for tipo, chave in (('post', 'voz_medidas'), ('artigo', 'voz_medidas_artigo')):
        pub = [x for x in p.get('voz_publicados', []) if x['tipo'] == tipo and x['peso'] >= PESO_MINIMO][-JANELA:]
        base = ancora if tipo == 'post' else {}
        soma = sum(x['peso'] for x in pub)
        if not pub:
            if base: p[chave] = dict(base)
            continue
        w = 0.5 * min(1, soma / 3) if base else 1.0
        out = {}
        for k in set(base) | {k for x in pub for k in x['medidas']}:
            vals = [(x['medidas'][k], x['peso']) for x in pub if x['medidas'].get(k) is not None]
            mp = _mediana_ponderada(vals) if vals else None
            if k in base and base[k] is not None and mp is not None:
                out[k] = round((1 - w) * base[k] + w * mp, 1)
            elif mp is not None and (not base or k not in base):
                out[k] = round(mp, 1)
            elif k in base:
                out[k] = base[k]
        out['textos_proprios'] = ancora.get('posts_medidos', 0) if tipo == 'post' else 0
        out['publicados_considerados'] = len(pub)
        out['peso_dos_publicados'] = round(w, 2)
        p[chave] = out
    return p
