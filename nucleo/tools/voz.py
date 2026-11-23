"""Mede a voz da pessoa a partir de posts antigos (o teto que o texto novo não deve passar).
uso:
  voz.py medir <arquivo> [arquivo...]    posts separados por uma linha '---'; grava a mediana no perfil como
                                         ÂNCORA da voz (os posts publicados com a skill se somam depois, edicao.py)
                                         (não guarda cópia dos textos: só as medidas)
O que é medido: tamanho de frase e de parágrafo, primeira pessoa, emojis, hashtags, perguntas, travessões,
diversidade de vocabulário (MTLD), voz passiva e pontuação expressiva (? ! ( …).
A descrição qualitativa (vocabulário, expressões, o que ela nunca faz) o Claude escreve em voz.md.
"""
import sys, json, statistics, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

if len(sys.argv) < 3 or sys.argv[1] != 'medir':
    sys.exit(__doc__)
textos = ler_textos(sys.argv[2:])
if not textos:
    sys.exit('não achei posts com 25+ palavras (separe os posts com uma linha "---").')
ms = [medir(t) for t in textos]
med = {k: round(statistics.median(vs), 1) for k in ms[0] if (vs := [m[k] for m in ms if m[k] is not None])}
med['posts_medidos'] = len(textos)
p = carregar_perfil(obrigatorio=False); p['voz_ancora'] = med; p['voz_medidas'] = med
combinar_voz(p); salvar_perfil(p)   # textos próprios = âncora; os posts publicados com a skill entram por cima (edicao.py)
print(f'{len(textos)} posts medidos (mediana):')
for k, v in med.items():
    print(f'  {k:26} {v}')
# expressões recorrentes: candidatas para o voz.md (o Claude confere quais são mesmo da pessoa)
from collections import Counter
STOP = set("a o as os e de da do das dos em no na nos nas um uma uns umas que se por para pra com sem é foi ser ao à "
           "mas ou como mais muito já não sim eu me meu minha você ele ela isso esse essa este esta aquilo lá aqui "
           "tá tem ter vai vou era são está estou".split())
cont = Counter(); onde = Counter()
for tx in textos:
    w = re.findall(r'[\wÀ-ú]+', tx.lower()); vistos = set()
    for n in (2, 3, 4):
        for i in range(len(w) - n + 1):
            g = tuple(w[i:i + n])
            if all(x in STOP for x in g) or g[0] in STOP and g[-1] in STOP: continue
            cont[g] += 1; vistos.add(g)
    for g in vistos: onde[g] += 1
cand = [(' '.join(g), c) for g, c in cont.most_common(400) if onde[g] >= 2]
cand = [x for x in cand if not any(x[0] != y[0] and x[0] in y[0] and y[1] >= x[1] for y in cand)][:20]
if cand:
    print('\nexpressões que se repetem (candidatas para voz.md, confira quais são mesmo da pessoa):')
    print('  ' + ' · '.join(f'"{e}" ({c}x)' for e, c in cand))
if len(textos) < 5:
    print('ATENÇÃO: menos de 5 posts. A voz vai ficar aproximada; diga isso à pessoa e peça mais quando der.')
