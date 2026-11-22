"""Perfil da pessoa (uma vez): quem é, posicionamento, linhas editoriais, cores e voz.
uso:
  perfil.py mostrar                      mostra o perfil e o que falta
  perfil.py definir '<json parcial>'     junta no perfil
  perfil.py checar                       sai com erro se faltar algo essencial
Arquivos: ~/.config/assistente-linkedin/ (perfil.json, voz.md, notas.md, historico.jsonl, exemplos/).
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *


def faltando(p):
    f = [k for k in ('nome', 'titulo', 'publico', 'posicionamento') if not p.get(k)]
    if len(p.get('linhas', [])) < 2:
        f.append('linhas editoriais (3 fixas + 1 teste)')
    if not p.get('voz_medidas'):
        f.append('voz (rode voz.py medir com posts antigos, ou pule se a pessoa nunca publicou)')
    if not VOZ.exists():
        f.append('voz.md (descrição da voz)')
    if p.get('conselho') == 'CFM' and not p.get('identificacao'):
        f.append('identificação CFM (nome, MÉDICO, CRM/UF, especialidade e RQE)')
    return f


cmd = sys.argv[1] if len(sys.argv) > 1 else 'mostrar'
if cmd == 'mostrar':
    p = carregar_perfil(obrigatorio=False)
    print(json.dumps(p, indent=1, ensure_ascii=False))
    print('\nvoz.md:', 'existe' if VOZ.exists() else 'ainda não')
    f = faltando(p); print('falta:', ', '.join(f) if f else 'nada')
elif cmd == 'definir':
    p = carregar_perfil(obrigatorio=False)
    for k, v in json.loads(sys.argv[2]).items():
        if isinstance(v, dict) and isinstance(p.get(k), dict):
            p[k].update(v)
        else:
            p[k] = v
    salvar_perfil(p); print('perfil salvo em', PERFIL)
elif cmd == 'checar':
    p = carregar_perfil(); f = faltando(p)
    print('falta:', ', '.join(f) if f else 'nada. Pronto.')
    sys.exit(1 if [x for x in f if not x.startswith('voz (')] else 0)
else:
    print(__doc__)
