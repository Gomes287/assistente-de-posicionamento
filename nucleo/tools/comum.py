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
CORES_PADRAO = {"fundo": "#0F2A3D", "texto": "#F4F1EA", "acento": "#E3B25B", "suave": "#16384F"}
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
    "cores": CORES_PADRAO, "fonte_titulo": "Inter", "foto": "",
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
PRIMEIRA_VERBO = re.compile(r'\b(?:\w{2,}(?:amos|emos|imos)|somos|\w{3,}ei)\b', re.I)


def frases(t):
    t = re.sub(r'\s+', ' ', t)
    return [f for f in re.split(r'(?<=[.!?…])\s+', t) if len(f.split()) >= 2]


def paragrafos(t):
    return [p.strip() for p in re.split(r'\n\s*\n', t) if p.strip()]


def medir(t):
    fs = frases(t); ps = paragrafos(t); pal = t.split()
    tam = [len(f.split()) for f in fs] or [0]
    return {
        'caracteres': len(t.strip()),
        'palavras': len(pal),
        'frases': len(fs),
        'palavras_por_frase': round(statistics.mean(tam), 1),
        'frase_longa_p90': sorted(tam)[int(0.9 * (len(tam) - 1))],
        'paragrafos': len(ps),
        'palavras_por_paragrafo': round(statistics.mean([len(p.split()) for p in ps]), 1) if ps else 0,
        'primeira_pessoa_por_100': round(100 * (len(PRIMEIRA.findall(t)) + len(PRIMEIRA_VERBO.findall(t))) / max(1, len(pal)), 1),
        'emojis': len(EMOJI.findall(t)),
        'hashtags': len(re.findall(r'(?<!\w)#\w+', t)),
        'perguntas': t.count('?'),
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
