"""Cria a pasta de um conteúdo novo com o ideia.json para preencher na entrevista.
uso: novo.py "<título de trabalho>"   → <pasta_saida>/AAAA-MM-DD-slug/ (pasta_saida vem do perfil)
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

if len(sys.argv) < 2: sys.exit(__doc__)
p = carregar_perfil()
P = Path(p['pasta_saida']).expanduser() / f'{hoje()}-{slug(sys.argv[1])}'
P.mkdir(parents=True, exist_ok=True)
f = P / 'ideia.json'
if not f.exists():
    json.dump({
        "titulo_trabalho": sys.argv[1],
        "experiencia": "", "o_que_percebeu": "", "segunda_leitura": "",
        "ideia": "", "ponto_de_vista": "", "para_quem": "",
        "intencao": "", "linha": "", "formato": "", "por_que_formato": "", "metrica_principal": "",
        "fontes": [], "pergunta_final": ""
    }, open(f, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(P)
