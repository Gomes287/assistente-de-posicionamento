"""Mede a voz da pessoa a partir de posts antigos (o teto que o texto novo não deve passar).
uso:
  voz.py medir <arquivo> [arquivo...]    posts separados por uma linha '---'; grava a média no perfil
                                         (não guarda cópia dos textos: só as medidas)
O que é medido: tamanho de frase e de parágrafo, primeira pessoa, emojis, hashtags, perguntas, travessões.
A descrição qualitativa (vocabulário, expressões, o que ela nunca faz) o Claude escreve em voz.md.
"""
import sys, json, statistics, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

if len(sys.argv) < 3 or sys.argv[1] != 'medir':
    sys.exit(__doc__)
textos = ler_textos(sys.argv[2:])
if not textos:
    sys.exit('não achei posts com 25+ palavras (separe os posts com uma linha "---").')
ms = [medir(t) for t in textos]
med = {k: round(statistics.median([m[k] for m in ms]), 1) for k in ms[0]}
med['posts_medidos'] = len(textos)
p = carregar_perfil(obrigatorio=False); p['voz_medidas'] = med; salvar_perfil(p)
print(f'{len(textos)} posts medidos (mediana):')
for k, v in med.items():
    print(f'  {k:26} {v}')
if len(textos) < 5:
    print('ATENÇÃO: menos de 5 posts. A voz vai ficar aproximada; diga isso à pessoa e peça mais quando der.')
