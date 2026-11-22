"""Memória editorial: o que foi publicado, com que intenção, o que aconteceu e o que se aprendeu.
uso:
  memoria.py registrar <pasta> [--link URL]          depois de publicar (lê ideia.json)
  memoria.py resultado <pasta|id> impressoes=N reacoes=N comentarios=N compartilhamentos=N
                       [salvamentos=N seguidores=N visitas_perfil=N horas=48]
  memoria.py aprendizado <pasta|id> "o que levar para a próxima decisão"
  memoria.py resumo [N]                               últimos N conteúdos, equilíbrio das linhas, aprendizados
Arquivo: ~/.config/assistente-linkedin/historico.jsonl (uma linha por conteúdo).
"""
import sys, json, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

METRICA = {'amplificar': ('impressoes', 'seguidores'), 'compartilhar': ('salvamentos', 'compartilhamentos'),
           'conversar': ('comentarios',), 'posicionar': ('visitas_perfil', 'comentarios')}


def ler():
    return [json.loads(l) for l in open(HIST, encoding='utf-8')] if HIST.exists() else []


def gravar(itens):
    CONF.mkdir(parents=True, exist_ok=True)
    with open(HIST, 'w', encoding='utf-8') as f:
        for i in itens: f.write(json.dumps(i, ensure_ascii=False) + '\n')


def achar(itens, ref):
    for i in itens:
        if i['id'] == ref or Path(i['pasta']).resolve() == Path(ref).expanduser().resolve():
            return i
    sys.exit(f'não achei "{ref}" no histórico (registre antes com: memoria.py registrar <pasta>)')


def taxa(r):
    imp = r.get('impressoes') or 0
    return (r.get('reacoes', 0) + r.get('comentarios', 0) + r.get('compartilhamentos', 0)) / imp if imp else None


cmd = sys.argv[1] if len(sys.argv) > 1 else 'resumo'
itens = ler()
if cmd == 'registrar':
    P = Path(sys.argv[2]).expanduser().resolve(); ide = json.load(open(P / 'ideia.json', encoding='utf-8'))
    if any(Path(i['pasta']) == P for i in itens): sys.exit('já registrado.')
    if not ide.get('ideia') or ide.get('intencao') not in INTENCOES:
        sys.exit('ideia.json sem "ideia" ou sem "intencao" válida (' + ', '.join(INTENCOES) + '). Preencha antes de registrar.')
    link = sys.argv[sys.argv.index('--link') + 1] if '--link' in sys.argv else ''
    it = {'id': P.name, 'pasta': str(P), 'data': hoje(), 'link': link,
          **{k: ide.get(k, '') for k in ('titulo_trabalho', 'ideia', 'intencao', 'linha', 'formato', 'metrica_principal')},
          'resultado': {}, 'aprendizado': ''}
    itens.append(it); gravar(itens); print('registrado:', it['id'], '·', it['intencao'], '·', it['linha'])
elif cmd == 'resultado':
    it = achar(itens, sys.argv[2])
    for kv in sys.argv[3:]:
        k, v = kv.split('='); it['resultado'][k] = float(v) if '.' in v else int(v)
    gravar(itens); r = it['resultado']; intc = it.get('intencao') or '?'
    t = taxa(r)
    print(f'{it["id"]} · intenção: {intc} · métrica principal: {it.get("metrica_principal") or ", ".join(METRICA.get(intc, ()))}')
    if t is not None: print(f'  engajamento: {100 * t:.1f}% · comentários por mil impressões: {1000 * r.get("comentarios", 0) / r["impressoes"]:.1f}')
    pares = [i for i in itens if i is not it and i.get('resultado')]
    mesmos = [i for i in pares if i.get('intencao') == intc]
    for k in METRICA.get(intc, ()):
        if k not in r: print(f'  falta {k} (é a métrica dessa intenção)'); continue
        base = [i['resultado'][k] for i in mesmos if k in i['resultado']]
        if len(base) >= 3:
            md = statistics.median(base)
            print(f'  {k}: {r[k]} · mediana dos seus posts "{intc}": {md:g} → {"acima" if r[k] > md else "abaixo" if r[k] < md else "igual"}')
        else:
            print(f'  {k}: {r[k]} (ainda poucos posts "{intc}" para comparar)')
    if len(pares) < 8:
        print('  base pequena: números baixos no começo são normais (muita gente lê e não interage). '
              'Compare consigo mesmo depois de 8–10 posts; julgue a estratégia em meses, não em dias.')
    print('  Pergunte à pessoa: o resultado combina com o que ela queria provocar? O que levar para a próxima decisão?'
          '\n  Grave com: memoria.py aprendizado', it['id'], '"..."')
elif cmd == 'aprendizado':
    it = achar(itens, sys.argv[2]); it['aprendizado'] = sys.argv[3]; gravar(itens); print('aprendizado gravado.')
elif cmd == 'resumo':
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    if not itens: print('memória vazia (nenhum conteúdo registrado ainda).'); sys.exit()
    for i in itens[-n:]:
        r = i.get('resultado') or {}; t = taxa(r)
        res = f'{r.get("impressoes", "?")} impr · {r.get("comentarios", "?")} coment' + (f' · {100 * t:.1f}%' if t else '') if r else 'sem resultado'
        print(f'{i["data"]}  {(i.get("intencao") or "?"):12} {(i.get("linha") or "?")[:18]:18} {(i.get("formato") or "?")[:10]:10} {res}')
        print(f'            ideia: {i.get("ideia", "")[:100]}')
        if i.get('aprendizado'): print(f'            aprendi: {i["aprendizado"]}')
    from collections import Counter
    print('\nlinhas:', dict(Counter(i.get('linha', '?') for i in itens)), '· intenções:', dict(Counter(i.get('intencao', '?') for i in itens)))
    p = carregar_perfil(obrigatorio=False); nomes = [l['nome'] for l in p.get('linhas', [])]
    faltam = [x for x in nomes if x not in [i.get('linha') for i in itens[-6:]]]
    if faltam: print('linhas sem post nos últimos 6:', ', '.join(faltam))
else:
    print(__doc__)
