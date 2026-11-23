"""Confere um texto antes de entregar: cacoetes de IA, voz da pessoa, formato do LinkedIn e regras do conselho.
uso: checar.py <post.md> [--carrossel | --artigo]
Mostra o trecho que aparece antes do "…ver mais", as medidas comparadas com a voz e a lista de avisos.
Não reescreve nada: quem decide é a pessoa (e o Claude, conversando com ela).
"""
import sys, re, statistics, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

OPOSICAO = re.compile(r"\bn[ãa]o (?:[ée]|se trata de|significa|basta)\b[^.!?\n]{0,60}?[,;—–-]\s*(?:mas |e sim |[ée] )", re.I)
NAO_SEJA = re.compile(r"\bn[ãa]o (?:seja|ser[áa]|est[áa]|esteja|foi|era)\b[^.!?\n]{0,80}?,\s*mas\b", re.I)
NAO_APENAS = re.compile(r"\bn[ãa]o (?:[ée] )?(?:apenas|s[óo]|somente)\b[^.!?\n]{0,140}?(?:\bmas (?:também|sim)\b|[;—–]\s*[ée]\b)", re.I)
OPOSICAO_2 = re.compile(r"\bn[ãa]o (?:[ée]|se trata de)\b[^.!?\n]{3,90}[.;]\s+(?:[ÉE]\b|Trata-se\b)")
MENOS_MAIS = re.compile(r"\bmenos (?:sobre|do que|um|uma|a|o)\b[^.!?\n]{0,90}?\be mais\b", re.I)
MAIS_DO_QUE = re.compile(r"\bmais do que [^.!?\n]{1,40}?, [ée]\b", re.I)
# cacoetes que a PRÓPRIA skill tende a criar ao fugir dos clássicos de IA (em escala, viram assinatura reconhecível).
# Se a expressão estiver em voz.md (é da pessoa), não vale o aviso.
CACOETES_SKILL = ["fica uma pergunta", "e, principalmente:", "merece destaque", "repara que", "em que situação você já viu", "em que situação vocês já viram", "e aí vem o detalhe",
                  "o detalhe que quase ninguém percebe", "e é aí que", "a pergunta que fica", "fica a pergunta",
                  "o que fica é", "no fundo,", "e tudo bem", "spoiler", "vou te contar", "deixa eu te contar",
                  "pois é", "simples assim", "faz sentido?", "parece óbvio, mas", "parece simples, mas"]
CLICHES = ["vivemos em um mundo", "vivemos num mundo", "nunca foi tão importante", "na era digital", "o futuro já chegou",
           "fora da caixa", "novo paradigma", "cada vez mais", "nos dias de hoje", "precisamos refletir",
           "a transformação começa", "em um mundo cada vez", "no cenário atual", "não é de hoje", "mundo dos negócios",
           "dinâmico e competitivo", "zona de conforto", "protagonismo", "à medida que navegamos", "complexidades do",
           "ambiente empresarial moderno", "é uma necessidade", "teste do tempo", "leitura obrigatória"]
# frases que anunciam o próximo parágrafo em vez de dizer a coisa
ANUNCIOS = ["merece destaque", "há uma pergunta", "faço uma ressalva", "o que me chama a atenção", "ganha outra dimensão",
            "é justamente por isso", "existe algo que", "é simples:", "e, principalmente", "esse movimento importa porque",
            "o que esse caso coloca", "a questão que proponho", "uma mensagem da aula", "é nesse processo que",
            "isso me fez pensar em algo", "vale destacar", "o ponto é:", "a verdade é que", "o segredo é", "a lição é"]
TRANSICOES = ["nesse contexto", "neste contexto", "diante desse cenário", "diante deste cenário", "vale ressaltar",
              "é importante destacar", "é importante ressaltar", "em suma", "dito isso", "por fim, mas não menos",
              "em última análise", "nesse sentido"]
# radicais: "naveg" pega navegar, navegamos, navegando
VOCAB_IA = ["jornada", "alavanc", "potencializ", "desbloque", "mergulh", "naveg", "galvaniz", "sinergi", "ecossistema",
            "robust", "disruptiv", "game changer", "insights valiosos", "valiosos insights", "valiosas lições",
            "fazer a diferença", "elevar o nível", "transformador", "farol de", "obra seminal", "testemunho d",
            "exploração profunda", "plano mestre", "aplicabilidade universal"]
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


def achar_radical(lista, t):
    tl = t.lower()
    return sorted({m.group(0) for x in lista for m in re.finditer(r'\b' + re.escape(x) + r'[\wÀ-ú]*', tl)})


def anaforas(t):
    """3+ frases seguidas (de qualquer tamanho) começando pela mesma palavra: "Não controlamos… Não controlamos…",
    "Se…, Se…, Se…", "Será que…? Será que…?". E frases curtas seguidas terminando igual ("Governos mudam. Regras mudam.")."""
    fs = [f for p in paragrafos(t) for f in frases(p)]
    w = [re.sub(r'[^\wÀ-ú ]', '', f).lower().split() for f in fs]
    achados, i = [], 0
    while i < len(w) - 2:
        if w[i] and w[i][0] not in ('o', 'a', 'os', 'as', 'e', 'de', 'em', 'um', 'uma') and all(w[k] and w[k][0] == w[i][0] for k in (i + 1, i + 2)):
            j = i + 3
            while j < len(w) and w[j] and w[j][0] == w[i][0]: j += 1
            achados.append(f'{j - i}x "{w[i][0].capitalize()}…"'); i = j
        else:
            i += 1
    for i in range(len(w) - 1):
        a, b = w[i], w[i + 1]
        if 2 <= len(a) <= 4 and 2 <= len(b) <= 4 and a[-1] == b[-1] and len(a[-1]) > 3:
            achados.append(f'"{fs[i]} {fs[i + 1]}"')
    return achados


def titulos_ingles(t):
    """Intertítulos com Maiúscula Em Cada Palavra (padrão do inglês, comum em texto gerado ou traduzido)."""
    n = 0
    for l in t.split('\n'):
        l = l.strip().lstrip('#*•-– ').strip()
        ws = l.split()
        if not 3 <= len(ws) <= 10 or l[-1:] in '.?!:;,' or l.isupper(): continue
        cont = [x for x in ws if x.lower() not in ('de', 'da', 'do', 'das', 'dos', 'e', 'a', 'o', 'para', 'em', 'no', 'na', 'com', 'por')]
        if len(cont) >= 3 and sum(1 for x in cont if x[:1].isupper()) / len(cont) >= 0.8: n += 1
    return n


def marcadores_de_efeito(t):
    return (len(OPOSICAO.findall(t)) + len(OPOSICAO_2.findall(t)) + len(NAO_APENAS.findall(t)) + len(NAO_SEJA.findall(t))
            + len(MENOS_MAIS.findall(t)) + len(anaforas(t)) + _pares_iguais(t)
            + len(re.findall(r'^\s*(?:afinal|no fim das contas|em resumo)[, ]', t, re.I | re.M)))


def _pares_iguais(t):
    w = [re.sub(r'[^\wÀ-ú ]', '', f).lower().split()[:1] for p in paragrafos(t) for f in frases(p)]
    return sum(1 for a, b in zip(w, w[1:]) if a and a == b and a[0] not in ('o', 'a', 'os', 'as', 'e', 'de', 'em', 'um', 'uma'))


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


def _pal(t):
    return re.findall(r'[\wÀ-ú]+', t.lower())


def repetidos(a, b, n=7):
    """Primeira sequência de n palavras que aparece igual nos dois textos (repetir a si mesmo também é molde)."""
    pa, pb = _pal(a), _pal(b)
    gb = {tuple(pb[i:i + n]) for i in range(len(pb) - n + 1)}
    for i in range(len(pa) - n + 1):
        if tuple(pa[i:i + n]) in gb: return ' '.join(pa[i:i + n])
    return ''


def abertura(t, n=5):
    return ' '.join(_pal(t)[:n])


def anteriores_da_memoria(atual):
    """Textos de posts/artigos já registrados (menos o atual), para não se repetir."""
    hist = HIST
    if not hist.exists(): return []
    out = []
    for l in open(hist, encoding='utf-8'):
        i = json.loads(l)
        for nome in ('post.md', 'artigo.md'):
            f = Path(i.get('pasta') or '/nao/existe') / nome
            if f.exists() and f.resolve().parent != Path(atual).resolve().parent:  # mesma pasta = mesmo conteúdo (post de divulgação do artigo)
                out.append((f'{i["id"]}/{nome}', f.read_text(encoding='utf-8')))
    return out


def ver_mais(t, n=210):
    linhas = [l for l in t.strip().split('\n')]
    vis = '\n'.join(linhas[:3])
    return vis[:n] + ('…' if len(vis) > n or len(linhas) > 3 else '')


def checar_texto(t, p, carrossel=False, artigo=False, ideia=None, anteriores=None):
    av = []  # (nivel, msg)  nivel: ERRO | ATENÇÃO | nota
    m = medir(t); v = p.get('voz_medidas') or {}
    n_op = (len(OPOSICAO.findall(t)) + len(MAIS_DO_QUE.findall(t)) + len(NAO_SEJA.findall(t))
            + len(NAO_APENAS.findall(t)) + len(OPOSICAO_2.findall(t)) + len(MENOS_MAIS.findall(t)))
    if n_op >= 2: av.append(('ATENÇÃO', f'oposição "não é X, é Y" {n_op}x: cacoete de IA. Deixe no máximo uma.'))
    elif n_op == 1: av.append(('nota', 'uma oposição "não é X, é Y": ok se for a ideia central; não repita.'))
    for nome, lista in (('clichê', CLICHES), ('transição mecânica', TRANSICOES)):
        a = achar(lista, t)
        if a: av.append(('ATENÇÃO', f'{nome}: ' + ', '.join(f'"{x}"' for x in a)))
    a = achar_radical(VOCAB_IA, t)
    if a: av.append(('ATENÇÃO', 'vocabulário de IA: ' + ', '.join(f'"{x}"' for x in a)))
    an = anaforas(t)
    if an: av.append(('ATENÇÃO', 'frases começando ou terminando do mesmo jeito em série: ' + '; '.join(an[:3])))
    tri_longa = len(re.findall(r'(?:[\wÀ-ú]+ ){0,4}[\wÀ-ú]+, (?:[\wÀ-ú]+ ){0,4}[\wÀ-ú]+,? e (?:[\wÀ-ú]+ ){0,4}[\wÀ-ú]+[.!;:?]', t))
    enum = len(re.findall(r'(?:[\wÀ-ú]+(?: [\wÀ-ú]+){0,4}, ){3,}(?:[\wÀ-ú]+ ){0,4}[\wÀ-ú]+,? e ', t))
    if enum >= 2: av.append(('ATENÇÃO', f'{enum} enumerações de 4+ itens: escolha os que importam.'))
    anun = achar(ANUNCIOS, t); dois_pontos = len(re.findall(r'[^\n]{8,}:\s*$', t, re.M))
    if len(anun) >= 2 or dois_pontos >= 3:
        av.append(('ATENÇÃO', 'frases que anunciam o próximo parágrafo em vez de dizer a coisa' +
                   (': ' + ', '.join(f'"{x}"' for x in anun) if anun else '') + (f' ({dois_pontos} linhas terminando em ":")' if dois_pontos >= 3 else '')))
    cautela = len(re.findall(r'\b(?:pode|podem|poderia|poderiam|talvez|possivelmente|eventualmente)\b', t, re.I))
    if m['palavras'] >= 150 and 100 * cautela / m['palavras'] > 1.3:
        av.append(('ATENÇÃO', f'cautela em excesso: {cautela}x "pode/talvez". Afirme o que você sustenta.'))
    if titulos_ingles(t) >= 2: av.append(('ATENÇÃO', 'intertítulos com Maiúscula Em Cada Palavra (padrão do inglês): em português, só a primeira.'))
    marc = len(re.findall(r'linkedin\.com/in/|(?<![\w.])@[\wÀ-ú]', t))
    if marc > 3: av.append(('ATENÇÃO', f'{marc} pessoas marcadas: marcação em massa é lida como tática de alcance. Marque só quem está no texto.'))
    if re.search(r'\b(?:na aula|da aula|o m[óo]dulo|na turma|programa de forma[çc][ãa]o|forma[çc][ãa]o de|facilitador|professora? )', t, re.I):
        av.append(('nota', 'post de aula: os colegas vão publicar sobre a mesma aula. O que VOCÊ viveu que conversa com ela? '
                           'Conte isso; o agradecimento cabe numa linha no fim.'))
    if re.search(r'\b(?:chamo isso de|batizei (?:isso )?de|dei o nome de|que chamo de)\b', t, re.I):
        av.append(('nota', 'conceito com nome próprio: confira se já existe com outro nome (ex.: custo do atraso, opções reais) e cite; reforça, não enfraquece.'))
    fs_all = [f for p in paragrafos(t) for f in frases(p)]
    if len(fs_all) >= 12:
        corte = int(len(fs_all) * 0.75)
        fim, ini = ' '.join(fs_all[corte:]), ' '.join(fs_all[:corte])
        mf, mi = marcadores_de_efeito(fim), marcadores_de_efeito(ini)
        if mf >= 2 and mf > mi / 3:
            av.append(('ATENÇÃO', f'o fim acumula recursos de efeito ({mf} no último quarto): termine onde a ideia acaba, sem aforismo em cascata.'))
    if any(re.search(r, t, re.I) for r in ABERTURAS): av.append(('ATENÇÃO', 'abertura genérica ("você já parou para pensar"/"imagine"). Abra com a cena ou observação concreta.'))
    if any(re.search(r, t.strip(), re.I | re.M) for r in FECHOS): av.append(('ATENÇÃO', 'fecho genérico ("e você, o que acha?"/"concorda?"). Pergunta específica, que só a pessoa faria.'))
    triades = len(re.findall(r'\b[\wÀ-ú]+(?: [\wÀ-ú]+)?, [\wÀ-ú]+(?: [\wÀ-ú]+)? e [\wÀ-ú]+(?: [\wÀ-ú]+)?[.!]', t))
    if triades < 2 and tri_longa >= 3: triades = tri_longa
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
    voz_txt = VOZ.read_text(encoding='utf-8').lower() if VOZ.exists() else ''
    cs = [x for x in achar(CACOETES_SKILL, t) if x not in voz_txt]
    if cs: av.append(('ATENÇÃO', 'cacoete da própria skill (em escala vira assinatura): ' + ', '.join(f'"{x}"' for x in cs)))
    if ideia is not None and not carrossel:
        det = (ideia.get('detalhe_unico') or '').strip()
        if not det:
            av.append(('ATENÇÃO', 'ideia.json sem "detalhe_unico": falta o detalhe que só a pessoa sabe (estruturas.md).'))
        else:
            chave = [w for w in re.findall(r'[\wÀ-ú]{5,}', det.lower())]
            achou = [w for w in chave if w in t.lower()]
            if chave and len(achou) < max(1, len(chave) // 3):
                av.append(('ATENÇÃO', f'o detalhe único ("{det[:60]}") não aparece no texto. É ele que diferencia o post.'))
        if 'ponte' in ideia and not (ideia.get('ponte') or '').strip():
            av.append(('ATENÇÃO', 'ideia.json sem "ponte": por que essa experiência importa para o seu público e para o seu trabalho?'))
        if ideia.get('estrutura') and ideia['estrutura'] not in ESTRUTURAS:
            av.append(('nota', f'estrutura "{ideia["estrutura"]}" fora do catálogo (estruturas.md).'))
    for nome, ant in (anteriores or []):
        rep = repetidos(t, ant)
        if rep: av.append(('ATENÇÃO', f'repete trecho de "{nome}": "{rep}"'))
        if abertura(t) and abertura(t) == abertura(ant):
            av.append(('ATENÇÃO', f'mesma abertura de "{nome}".'))
    # voz
    if v:
        if m['palavras_por_frase'] > 1.35 * v['palavras_por_frase'] + 1:
            av.append(('ATENÇÃO', f'frases mais longas que a voz da pessoa ({m["palavras_por_frase"]} vs {v["palavras_por_frase"]} palavras): mais sofisticado do que a pessoa fala?'))
        if v.get('variacao_frase') and m['frases'] >= 6 and m['variacao_frase'] < 0.6 * v['variacao_frase']:
            av.append(('ATENÇÃO', f'ritmo monótono: frases todas parecidas em tamanho (variação {m["variacao_frase"]} vs {v["variacao_frase"]} da voz da pessoa).'))
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
    fi = Path(sys.argv[1]).parent / 'ideia.json'
    ideia = json.load(open(fi, encoding='utf-8')) if fi.exists() else None
    m, av = checar_texto(t, p, '--carrossel' in sys.argv, '--artigo' in sys.argv, ideia, anteriores_da_memoria(sys.argv[1]))
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
