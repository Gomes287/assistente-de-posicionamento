"""Confere um texto antes de entregar: cacoetes de IA, voz da pessoa, formato do LinkedIn e regras do conselho.
uso: checar.py <post.md> [--carrossel | --artigo]
Mostra o trecho que aparece antes do "…ver mais", as medidas comparadas com a voz e a lista de avisos.
Não reescreve nada: quem decide é a pessoa (e o Claude, conversando com ela).
"""
import sys, re, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

OPOSICAO = re.compile(r"\bn[ãa]o (?:[ée]|se trata de|significa|basta)\b[^.!?\n]{0,60}?[,;—–-]\s*(?:mas |e sim |[ée] )", re.I)
NAO_SEJA = re.compile(r"\bn[ãa]o (?:seja|ser[áa]|est[áa]|esteja|foi|era)\b[^.!?\n]{0,80}?,\s*mas\b", re.I)
MAIS_DO_QUE = re.compile(r"\bmais do que [^.!?\n]{1,40}?, [ée]\b", re.I)
CLICHES = ["vivemos em um mundo", "vivemos num mundo", "nunca foi tão importante", "na era digital", "o futuro já chegou",
           "fora da caixa", "novo paradigma", "cada vez mais", "nos dias de hoje", "precisamos refletir",
           "a transformação começa", "em um mundo cada vez", "no cenário atual", "não é de hoje"]
TRANSICOES = ["nesse contexto", "neste contexto", "diante desse cenário", "diante deste cenário", "vale ressaltar",
              "é importante destacar", "é importante ressaltar", "em suma", "dito isso", "por fim, mas não menos",
              "em última análise", "nesse sentido"]
VOCAB_IA = ["jornada", "alavancar", "potencializar", "desbloquear", "mergulhar", "mergulho profundo", "navegar",
            "sinergia", "ecossistema", "robusto", "robusta", "disruptiv", "game changer", "insights valiosos",
            "fazer a diferença", "elevar o nível", "transformador", "transformadora"]
ABERTURAS = [r"^\s*voc[êe] j[áa] parou para pensar", r"^\s*j[áa] parou para pensar", r"^\s*imagine (?:s[óo] )?(?:um|uma|que)"]
FECHOS = [r"e voc[êe],? o que (?:acha|pensa)\??\s*$", r"concorda\??\s*$", r"deixe? (?:nos|aqui nos) coment[áa]rios",
          r"comente abaixo", r"me conta nos coment[áa]rios\s*[.!]?\s*$"]
SIGILO_RISCO = r"\b(deliber\w+|na reuni[ãa]o do conselho|no conselho d[aeo] |pauta do conselho|fato relevante|ainda n[ãa]o (?:foi |est[áa] )?(?:divulgad\w*|anunciad\w*|p[úu]blic\w*)|em primeira m[ãa]o|confidencial\w*|informa[çc][ãa]o privilegiada|antes do an[úu]ncio|vamos anunciar|ser[áa] anunciad\w*|fus[ãa]o|aquisi[çc][ãa]o|due diligence)\b"
CFM_RISCO = {"promessa de resultado": r"\b(garant\w*|cura\w*|curar|resultado certo|sem riscos?|milagr\w*|revolucion\w*)\b|(100 ?%)",
             "superlativo sobre si": r"\b(melhor m[ée]dic[oa]|refer[êe]ncia (?:em|no|na)|o [uú]nico|a [uú]nica|s[óo] eu)\b",
             "oferta de consulta/diagnóstico": r"\b(agende|agendamento|marque (?:sua|uma) consulta|whats\w*|desconto|promo[çc][ãa]o)\b",
             "medo/pânico": r"\b(perigo mortal|pode te matar|alerta m[áa]ximo|p[âa]nico|assustador)\b"}


def achar(lista, t):
    tl = t.lower()
    return [x for x in lista if x in tl]


def paralelas(t):
    """Sequências de frases curtas com o mesmo molde: 'Planos mostram X. Recursos mostram Y.' (mesmo verbo na mesma
    posição) ou 3+ frases curtas seguidas começando igual."""
    achados = []
    for p in paragrafos(t):
        fs = [re.sub(r'[^\wÀ-ú ]', '', f).lower().split() for f in frases(p)]
        orig = frases(p)
        for i in range(len(fs) - 1):
            a, b = fs[i], fs[i + 1]
            if 2 <= len(a) <= 7 and 2 <= len(b) <= 7 and a[1] == b[1] and a[0] != b[0] and len(a[1]) > 2:
                achados.append(orig[i] + ' ' + orig[i + 1])
        for i in range(len(fs) - 2):
            trio = fs[i:i + 3]
            if all(2 <= len(x) <= 8 for x in trio) and len({x[0] for x in trio}) == 1:
                achados.append(' '.join(orig[i:i + 3]))
    return achados


def ver_mais(t, n=210):
    linhas = [l for l in t.strip().split('\n')]
    vis = '\n'.join(linhas[:3])
    return vis[:n] + ('…' if len(vis) > n or len(linhas) > 3 else '')


def checar_texto(t, p, carrossel=False, artigo=False):
    av = []  # (nivel, msg)  nivel: ERRO | ATENÇÃO | nota
    m = medir(t); v = p.get('voz_medidas') or {}
    n_op = len(OPOSICAO.findall(t)) + len(MAIS_DO_QUE.findall(t)) + len(NAO_SEJA.findall(t))
    if n_op >= 2: av.append(('ATENÇÃO', f'oposição "não é X, é Y" {n_op}x: cacoete de IA. Deixe no máximo uma.'))
    elif n_op == 1: av.append(('nota', 'uma oposição "não é X, é Y": ok se for a ideia central; não repita.'))
    for nome, lista in (('clichê', CLICHES), ('transição mecânica', TRANSICOES), ('vocabulário de IA', VOCAB_IA)):
        a = achar(lista, t)
        if a: av.append(('ATENÇÃO', f'{nome}: ' + ', '.join(f'"{x}"' for x in a)))
    if any(re.search(r, t, re.I) for r in ABERTURAS): av.append(('ATENÇÃO', 'abertura genérica ("você já parou para pensar"/"imagine"). Abra com a cena ou observação concreta.'))
    if any(re.search(r, t.strip(), re.I | re.M) for r in FECHOS): av.append(('ATENÇÃO', 'fecho genérico ("e você, o que acha?"/"concorda?"). Pergunta específica, que só a pessoa faria.'))
    triades = len(re.findall(r'\b[\wÀ-ú]+(?: [\wÀ-ú]+)?, [\wÀ-ú]+(?: [\wÀ-ú]+)? e [\wÀ-ú]+(?: [\wÀ-ú]+)?[.!]', t))
    if triades >= 2: av.append(('ATENÇÃO', f'{triades} tríades "X, Y e Z." para dar ritmo: cacoete de IA.'))
    par = paralelas(t)
    if par: av.append(('ATENÇÃO', 'frases paralelas em série (molde de IA): ' + ' | '.join(f'"{x}"' for x in par[:2])))
    emo_lista = len(re.findall(r'^\s*' + EMOJI.pattern, t, re.M))
    if emo_lista >= 2: av.append(('ATENÇÃO', f'{emo_lista} linhas começando com emoji (lista com emoji é marca de IA).'))
    lim_trav = max(3.0, 2 * v.get('travessoes_por_1000', 0))
    if m['travessoes_por_1000'] > lim_trav: av.append(('ATENÇÃO', f'travessões demais ({m["travessoes_por_1000"]}/1000 palavras; a voz da pessoa usa {v.get("travessoes_por_1000", "?")}).'))
    if m['hashtags'] > 5: av.append(('ATENÇÃO', f'{m["hashtags"]} hashtags; use até 3–5 específicas (ou nenhuma).'))
    ps = paragrafos(t)
    if len(ps) >= 5:
        tam = [len(x.split()) for x in ps]
        if statistics.pstdev(tam) / max(1, statistics.mean(tam)) < 0.25:
            av.append(('ATENÇÃO', 'parágrafos todos do mesmo tamanho (molde visível). Varie.'))
    # voz
    if v:
        if m['palavras_por_frase'] > 1.35 * v['palavras_por_frase'] + 1:
            av.append(('ATENÇÃO', f'frases mais longas que a voz da pessoa ({m["palavras_por_frase"]} vs {v["palavras_por_frase"]} palavras): mais sofisticado do que a pessoa fala?'))
        if v.get('emojis', 0) < 1 and m['emojis'] > 1:
            av.append(('ATENÇÃO', f'{m["emojis"]} emojis; a pessoa quase não usa.'))
        if not carrossel and not artigo and v.get('caracteres') and m['caracteres'] > 1.8 * v['caracteres']:
            av.append(('nota', f'bem mais longo que os posts da pessoa ({m["caracteres"]} vs ~{int(v["caracteres"])} caracteres).'))
    if m['primeira_pessoa_por_100'] < 0.5 and not carrossel:
        av.append(('ATENÇÃO', 'quase nada em primeira pessoa: onde está a experiência da pessoa? (autoria, regra 4)'))
    # formato
    if not carrossel and not artigo and m['caracteres'] > 3000: av.append(('ERRO', f'{m["caracteres"]} caracteres: o LinkedIn aceita até 3.000.'))
    if re.search(r'\d+(?:[.,]\d+)?\s?%|\b\d{2,}(?:[.,]\d+)? (?:mil|milh[õo]es|bilh[õo]es)\b', t):
        av.append(('nota', 'tem número/percentual: confira que a fonte está citada e o número é igual ao da fonte.'))
    if re.search(r'https?://', t): av.append(('nota', 'link no corpo: não há regra confiável sobre alcance; a memória vai mostrar se pesa para a pessoa.'))
    # conselho
    if p.get('conselho') == 'CFM':
        for nome, r in CFM_RISCO.items():
            a = sorted(set(y for x in re.findall(r, t, re.I) for y in ((x,) if isinstance(x, str) else x) if y))
            if a: av.append(('ATENÇÃO', f'CFM, {nome}: ' + ', '.join(f'"{x}"' for x in a) + ' (referencia/conselhos/cfm.md)'))
        if not p.get('identificacao_no_perfil') and not carrossel:
            av.append(('ATENÇÃO', 'CFM Art. 4º/6º: confirme que nome, MÉDICO, CRM/UF e RQE estão no título ou Sobre do perfil.'))
    if p.get('sigilo'):
        a = sorted(set(x.lower() for x in re.findall(SIGILO_RISCO, t, re.I)))
        if a: av.append(('ATENÇÃO', 'sigilo de conselho/administração: ' + ', '.join(f'"{x}"' for x in a) +
                         '. Dá para deduzir a empresa? A informação já é pública? (referencia/conselhos/sigilo.md)'))
    if p.get('conselho') == 'CFM':
        pass
    elif p.get('conselho') not in ('', 'nenhum', None):
        av.append(('nota', f'conselho {p["conselho"]}: confira as regras de publicidade da profissão (a skill não tem módulo dele).'))
    return m, av


if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    t = Path(sys.argv[1]).read_text(encoding='utf-8'); p = carregar_perfil(obrigatorio=False)
    m, av = checar_texto(t, p, '--carrossel' in sys.argv, '--artigo' in sys.argv)
    print('ANTES DO "…VER MAIS" (o que decide se abrem):\n' + '-' * 60 + '\n' + ver_mais(t) + '\n' + '-' * 60)
    v = p.get('voz_medidas') or {}
    print('\nmedidas (texto · voz da pessoa):')
    for k in ('caracteres', 'palavras_por_frase', 'paragrafos', 'primeira_pessoa_por_100', 'emojis', 'hashtags', 'perguntas', 'travessoes_por_1000'):
        print(f'  {k:26} {m[k]!s:>7} · {v.get(k, "-")}')
    print()
    for n, msg in sorted(av, key=lambda x: ['ERRO', 'ATENÇÃO', 'nota'].index(x[0])):
        print(f'{n:8} {msg}')
    if not [a for a in av if a[0] != 'nota']:
        print('OK: nenhum cacoete detectado. Agora leia em voz alta: soa como ela?')
    sys.exit(1 if any(a[0] == 'ERRO' for a in av) else 0)
