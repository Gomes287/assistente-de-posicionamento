"""Memória editorial: o que foi publicado, com que intenção, o que aconteceu e o que se aprendeu.
uso:
  memoria.py registrar <pasta> [--link URL]          depois de publicar ou agendar (lê ideia.json)
  memoria.py vincular <pasta|id> <URL>                 guarda o link do post (para a importação achar o post)
  memoria.py importar <planilha.xlsx>                  lê a exportação de "Análises" do LinkedIn e preenche os resultados
  memoria.py resultado <pasta|id> impressoes=N reacoes=N comentarios=N compartilhamentos=N
                       [salvamentos=N seguidores=N visitas_perfil=N]      (à mão, se não houver planilha)
  memoria.py aprendizado <pasta|id> "o que levar para a próxima decisão"
  memoria.py resumo [N]                               últimos N conteúdos, equilíbrio das linhas, aprendizados
  memoria.py pendencias                               o que espera a pessoa (publicou? link? planilha? intenção?)
  memoria.py juntar <pasta> <id-importado>            a pasta é o mesmo post que veio da planilha: junta os dois
Arquivos: ~/.config/assistente-de-posicionamento/historico.jsonl (um conteúdo por linha) e conta.jsonl (fotos da conta).
"""
import sys, json, statistics, re, unicodedata, urllib.parse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *

CONTA = CONF / 'conta.jsonl'
METRICA = {'amplificar': ('impressoes', 'seguidores'), 'compartilhar': ('salvamentos', 'compartilhamentos'),
           'conversar': ('comentarios',), 'posicionar': ('visitas_perfil', 'comentarios')}
# cabeçalhos da exportação (português e inglês) → nome usado aqui
COLUNAS = {'url da publicacao': 'url', 'post url': 'url', 'data de publicacao': 'publicado', 'post publish date': 'publicado',
           'tipo de publicacao': 'tipo', 'post type': 'tipo', 'impressoes': 'impressoes', 'impressions': 'impressoes',
           'usuarios alcancados': 'alcance', 'members reached': 'alcance', 'seguidores conquistados': 'seguidores',
           'followers gained': 'seguidores', 'visualizacoes do perfil': 'visitas_perfil', 'profile viewers from this post': 'visitas_perfil',
           'profile views': 'visitas_perfil', 'reacoes': 'reacoes', 'reactions': 'reacoes', 'comentarios': 'comentarios',
           'comments': 'comentarios', 'compartilhamentos': 'compartilhamentos', 'reposts': 'compartilhamentos',
           'shares': 'compartilhamentos', 'salvamentos': 'salvamentos', 'saves': 'salvamentos', 'envios': 'envios',
           'sends': 'envios', 'sends on linkedin': 'envios', 'visualizacoes': 'visualizacoes_video', 'video views': 'visualizacoes_video'}


def norm(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower().strip()


def num(v):
    v = str(v).strip().replace('.', '').replace(',', '.') if re.fullmatch(r'[\d.,]+', str(v).strip() or 'x') else v
    try:
        return int(v) if float(v) == int(float(v)) else float(v)
    except (ValueError, TypeError):
        return None


def id_post(url):
    m = re.search(r'(\d{16,})', url or '')
    return m.group(1) if m else ''


def ler():
    return [json.loads(l) for l in open(HIST, encoding='utf-8')] if HIST.exists() else []


def gravar(itens):
    CONF.mkdir(parents=True, exist_ok=True)
    with open(HIST, 'w', encoding='utf-8') as f:
        for i in itens: f.write(json.dumps(i, ensure_ascii=False) + '\n')


def achar(itens, ref):
    for i in itens:
        if i['id'] == ref or (i.get('pasta') and Path(i['pasta']).resolve() == Path(ref).expanduser().resolve()):
            return i
    sys.exit(f'não achei "{ref}" no histórico (registre antes com: memoria.py registrar <pasta>)')


def taxa(r):
    imp = r.get('impressoes') or 0
    return (r.get('reacoes', 0) + r.get('comentarios', 0) + r.get('compartilhamentos', 0)) / imp if imp else None


def leitura(it, itens):
    r = it['resultado']; intc = it.get('intencao') or '?'; t = taxa(r)
    print(f'{it["id"]} · intenção: {intc} · métrica principal: {it.get("metrica_principal") or ", ".join(METRICA.get(intc, ())) or "?"}')
    if t is not None:
        print(f'  {r["impressoes"]} impressões · engajamento {100 * t:.1f}% · comentários por mil impressões: {1000 * r.get("comentarios", 0) / r["impressoes"]:.1f}')
    pares = [i for i in itens if i is not it and i.get('resultado')]
    mesmos = [i for i in pares if i.get('intencao') == intc]
    for k in METRICA.get(intc, ()):
        if k not in r: print(f'  falta {k} (é a métrica dessa intenção)'); continue
        base = [i['resultado'][k] for i in mesmos if k in i['resultado']]
        if len(base) >= 3:
            md = statistics.median(base)
            print(f'  {k}: {r[k]} · mediana dos seus posts "{intc}": {md:g} → {"acima" if r[k] > md else "abaixo" if r[k] < md else "igual"}')
        else:
            todos = [i['resultado'][k] for i in pares if k in i['resultado']]
            extra = f' · mediana de todos os seus posts: {statistics.median(todos):g}' if len(todos) >= 3 else ''
            print(f'  {k}: {r[k]} (ainda poucos posts "{intc}" para comparar{extra})')
    if len(pares) < 8:
        print('  base pequena: números baixos no começo são normais (muita gente lê e não interage). '
              'Compare consigo mesmo depois de 8–10 posts; julgue a estratégia em meses, não em dias.')
    print('  Pergunte à pessoa: o resultado combina com o que ela queria provocar? O que levar para a próxima decisão?'
          '\n  Grave com: memoria.py aprendizado', it['id'], '"..."')


def importar(arq, itens):
    from xlsx import ler as ler_xlsx
    abas = ler_xlsx(arq); posts = []
    for nome, linhas in abas.items():
        for k, l in enumerate(linhas):
            cab = [COLUNAS.get(norm(c), '') for c in l]
            if 'url' in cab and 'impressoes' in cab and cab.count('url') == 1:  # tabela por post (não a de "em alta")
                for row in linhas[k + 1:]:
                    d = {cab[j]: row[j] for j in range(min(len(cab), len(row))) if cab[j] and row[j] != ''}
                    if d.get('url'): posts.append(d)
                break
    if not posts: sys.exit('não achei a tabela de publicações (aba "Publicações mais recentes" / "Recent posts").')
    novos = atual = 0; vinc = []
    por_id = {id_post(i.get('link')): i for i in itens if id_post(i.get('link'))}
    for d in posts:
        res = {k: num(v) for k, v in d.items() if k not in ('url', 'publicado', 'tipo') and num(v) is not None}
        it = por_id.get(id_post(d['url']))
        if it:
            it['resultado'].update(res); it['resultado']['fonte'] = f'exportação {hoje()}'; atual += 1; vinc.append(it)
        else:
            slug_url = urllib.parse.unquote(d['url'].rstrip('/').split('/')[-1]).split('-share-')[0].split('-ugcPost-')[0].split('-activity-')[0].split('_', 1)[-1]
            pub = d.get('publicado', ''); m = re.fullmatch(r'(\d{2})/(\d{2})/(\d{4})', pub.strip())
            pub = f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else pub
            itens.append({'id': 'li-' + id_post(d['url']), 'pasta': '', 'data': pub, 'link': d['url'],
                          'titulo_trabalho': slug_url.replace('-', ' ')[:80] if slug_url else '',
                          'ideia': '', 'intencao': '', 'linha': '', 'formato': norm(d.get('tipo', '')), 'metrica_principal': '',
                          'origem': 'importado', 'resultado': {**res, 'fonte': f'exportação {hoje()}'}, 'aprendizado': ''})
            por_id[id_post(d['url'])] = itens[-1]; novos += 1
    # foto da conta: total de seguidores, impressões e alcance do período
    foto = {'data': hoje(), 'arquivo': Path(arq).name}
    for nome, linhas in abas.items():
        for l in linhas:
            if len(l) >= 2 and norm(l[0]).startswith(('total de seguidores', 'total followers')): foto['seguidores_total'] = num(l[1])
            if len(l) >= 2 and norm(l[0]) in ('impressoes', 'impressions'): foto['impressoes_periodo'] = num(l[1])
            if len(l) >= 2 and norm(l[0]) in ('usuarios alcancados', 'members reached'): foto['alcance_periodo'] = num(l[1])
            if len(l) >= 2 and norm(l[0]) in ('desempenho geral', 'overall performance'): foto['periodo'] = l[1]
        if norm(nome).startswith(('dados demograficos do conteudo', 'content demographics')):
            foto['quem_viu'] = [f'{l[0]}: {l[1]} ({l[2]})' for l in linhas[1:] if len(l) >= 3]
    with open(CONTA, 'a', encoding='utf-8') as f: f.write(json.dumps(foto, ensure_ascii=False) + '\n')
    gravar(itens)
    print(f'{len(posts)} publicações na planilha · {atual} atualizadas no histórico · {novos} novas (feitas fora da skill, marcadas "importado")')
    if foto.get('seguidores_total') is not None:
        print(f'conta: {foto.get("seguidores_total")} seguidores · {foto.get("impressoes_periodo", "?")} impressões e '
              f'{foto.get("alcance_periodo", "?")} pessoas alcançadas em {foto.get("periodo", "?")}')
    if foto.get('quem_viu'):
        print('quem viu o conteúdo (compare com o público que a pessoa quer):'); [print('  ' + x) for x in foto['quem_viu']]
    for it in vinc:
        print(); leitura(it, itens)
    sem = [i for i in itens if i.get('origem') == 'importado' and not i.get('intencao')]
    if sem:
        print(f'\n{len(sem)} posts importados sem intenção. Pergunte à pessoa a intenção de cada um (melhora a comparação):')
        for i in sem: print(f'  {i["id"]} · {i["data"]} · {i["formato"]} · {i["titulo_trabalho"][:60]} · {i["resultado"].get("impressoes", "?")} impr')
    pend = [i for i in itens if i.get('pasta') and not i.get('link')]
    if pend:
        print('\nregistrados sem link (não dá para achar na planilha): ' + ', '.join(i['id'] for i in pend)
              + '. Peça o link e use: memoria.py vincular <id> <URL>')


def registrar(P, link, itens):
    P = Path(P).expanduser().resolve(); ide = json.load(open(P / 'ideia.json', encoding='utf-8'))
    if any(i.get('pasta') and Path(i['pasta']) == P for i in itens): sys.exit('já registrado.')
    if not ide.get('ideia') or ide.get('intencao') not in INTENCOES:
        sys.exit('ideia.json sem "ideia" ou sem "intencao" válida (' + ', '.join(INTENCOES) + '). Preencha antes de registrar.')
    it = {'id': P.name, 'pasta': str(P), 'data': hoje(), 'link': link,
          **{k: ide.get(k, '') for k in ('titulo_trabalho', 'ideia', 'intencao', 'linha', 'formato', 'metrica_principal', 'estrutura')},
          'resultado': {}, 'aprendizado': ''}
    itens.append(it); gravar(itens); print('registrado:', it['id'], '·', it['intencao'], '·', it['linha'])
    if not link: print('sem link ainda: quando publicar, use memoria.py vincular', it['id'], '<URL>')
    if (P / 'edicao.json').exists():                     # a voz aprende com a versão final, na medida em que é dela
        from edicao import aprender; aprender(P)
    return it


def _dias(data):
    try: return (datetime.date.today() - datetime.date.fromisoformat(str(data)[:10])).days
    except ValueError: return None


def prontos_sem_registro(itens, p=None):
    """Pastas de conteúdo com texto pronto que ainda não foram registradas (talvez já publicadas)."""
    p = p or carregar_perfil(obrigatorio=False); base = Path(p.get('pasta_saida') or '').expanduser()
    reg = {str(Path(i['pasta']).resolve()) for i in itens if i.get('pasta')}; out = []
    if not base.is_dir(): return out
    for d in sorted(base.iterdir()):
        j = d / 'ideia.json'
        if not j.exists() or str(d.resolve()) in reg: continue
        if not any((d / x).exists() for x in ('post.md', 'artigo.md', 'carrossel.pdf')): continue
        try: ide = json.load(open(j, encoding='utf-8'))
        except Exception: continue
        if not ide.get('ideia'): continue
        m = re.match(r'(\d{4}-\d{2}-\d{2})', d.name)
        out.append({'pasta': str(d), 'titulo': ide.get('titulo_trabalho') or d.name, 'data': m.group(1) if m else '',
                    'formato': ide.get('formato', ''), 'pronto_para_registrar': ide.get('intencao') in INTENCOES})
    return out


def data_br(d):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', str(d or ''))
    return f'{m.group(3)}/{m.group(2)}' if m else (d or '?')


def _palavras(s):
    return re.findall(r'[a-z0-9]+', norm(s))


def importado_igual(pasta, itens):
    """O post desta pasta já veio da planilha (publicado sem registrar)? Compara o começo do texto com o título do link."""
    pasta = Path(pasta)
    for nome in ('post.md', 'artigo.md'):
        if (pasta / nome).exists():
            ini = _palavras((pasta / nome).read_text(encoding='utf-8')[:400]); break
    else:
        return None
    for i in itens:
        tit = _palavras(i.get('titulo_trabalho', ''))
        if i.get('origem') == 'importado' and not i.get('pasta') and len(tit) >= 4 and ini[:min(len(tit), 8)] == tit[:8]:
            return i
    return None


def juntar(P, ref, itens):
    """A pasta P é o mesmo post que veio da planilha como "importado": passa a ideia da pasta para ele."""
    P = Path(P).expanduser().resolve(); ide = json.load(open(P / 'ideia.json', encoding='utf-8')); it = achar(itens, ref)
    if it.get('pasta'): sys.exit('esse post já está ligado a uma pasta.')
    it['pasta'] = str(P); it['origem'] = 'skill'
    for k in ('titulo_trabalho', 'ideia', 'linha', 'formato', 'metrica_principal', 'estrutura'):
        if ide.get(k): it[k] = ide[k]
    if not it.get('intencao'): it['intencao'] = ide.get('intencao', '')
    gravar(itens); print(f'juntei a pasta {P.name} ao post publicado em {data_br(it.get("data"))}.')
    if (P / 'edicao.json').exists():
        from edicao import aprender; aprender(P)
    return it


def pendencias(itens, p=None):
    """Lista do que espera a pessoa, da mais urgente para a menos. Cada item: tipo, id, texto."""
    out = []
    for x in prontos_sem_registro(itens, p):
        imp = importado_igual(x['pasta'], itens)
        if imp:
            out.append({'tipo': 'juntar', 'id': x['pasta'], 'importado': imp['id'], 'titulo': x['titulo'],
                        'texto': f'"{x["titulo"]}" parece ser o post publicado em {data_br(imp.get("data"))}, que veio da '
                                 'planilha. Juntar os dois? Assim a ideia e a sua edição entram no histórico e na voz.'})
        else:
            out.append({'tipo': 'publicou', 'id': x['pasta'], 'titulo': x['titulo'],
                        'texto': f'"{x["titulo"]}" está pronto desde {data_br(x["data"])}. Já publicou? Registre com o link.'})
    for i in itens:
        if i.get('pasta') and not i.get('link'):
            out.append({'tipo': 'link', 'id': i['id'], 'titulo': i.get('titulo_trabalho', ''),
                        'texto': f'"{i.get("titulo_trabalho") or i["id"]}" foi registrado sem link. Cole o link do post.'})
    esperando = [i for i in itens if i.get('link') and not (i.get('resultado') or {}).get('impressoes')
                 and (_dias(i.get('data')) or 0) >= 2]
    if esperando:
        nomes = ', '.join(f'"{(i.get("titulo_trabalho") or i["id"])[:40]}"' for i in esperando[:4]) + ('…' if len(esperando) > 4 else '')
        out.append({'tipo': 'planilha', 'id': '', 'titulo': '', 'posts': [i['id'] for i in esperando],
                    'texto': f'{len(esperando)} post(s) com 2 dias ou mais sem números: {nomes}. Exporte a planilha do '
                             'LinkedIn (Análises de publicação → Exportar) e entregue aqui.'})
    for i in itens:
        if i.get('origem') == 'importado' and not i.get('intencao'):
            out.append({'tipo': 'intencao', 'id': i['id'], 'titulo': i.get('titulo_trabalho', ''),
                        'texto': f'Post de {data_br(i.get("data"))} ("{i.get("titulo_trabalho", "")[:50]}") sem intenção: '
                                 'qual era a ideia dele?'})
    for i in itens:
        if (i.get('resultado') or {}).get('impressoes') and not i.get('aprendizado') and i.get('origem') != 'importado':
            out.append({'tipo': 'aprendizado', 'id': i['id'], 'titulo': i.get('titulo_trabalho', ''),
                        'texto': f'"{i.get("titulo_trabalho") or i["id"]}" já tem números. O que você leva dele para o próximo?'})
    return out


def main():
    itens = ler()
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'resumo'
    if cmd == 'registrar':
        link = sys.argv[sys.argv.index('--link') + 1] if '--link' in sys.argv else ''
        registrar(sys.argv[2], link, itens)
    elif cmd == 'vincular':
        it = achar(itens, sys.argv[2]); it['link'] = sys.argv[3]; gravar(itens); print('link guardado.')
    elif cmd == 'importar':
        importar(sys.argv[2], itens)
    elif cmd == 'resultado':
        it = achar(itens, sys.argv[2])
        for kv in sys.argv[3:]:
            k, v = kv.split('='); it['resultado'][k] = float(v) if '.' in v else int(v)
        gravar(itens); leitura(it, itens)
    elif cmd == 'intencao':
        it = achar(itens, sys.argv[2]); it['intencao'] = sys.argv[3]
        if len(sys.argv) > 4: it['linha'] = sys.argv[4]
        gravar(itens); print('ok')
    elif cmd == 'aprendizado':
        it = achar(itens, sys.argv[2]); it['aprendizado'] = sys.argv[3]; gravar(itens); print('aprendizado gravado.')
    elif cmd == 'resumo':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
        if not itens: print('memória vazia (nenhum conteúdo registrado ainda).'); sys.exit()
        for i in itens[-n:]:
            r = i.get('resultado') or {}; t = taxa(r)
            res = (f'{r.get("impressoes", "?")} impr · {r.get("comentarios", "?")} coment' + (f' · {100 * t:.1f}%' if t else '')) if r.get('impressoes') is not None else 'sem resultado'
            print(f'{i["data"]}  {(i.get("intencao") or "?"):12} {(i.get("linha") or "?")[:18]:18} {(i.get("formato") or "?")[:10]:10} {res}')
            print(f'            {("ideia: " + i["ideia"]) if i.get("ideia") else i.get("titulo_trabalho", "")[:100]}')
            if i.get('aprendizado'): print(f'            aprendi: {i["aprendizado"]}')
        from collections import Counter
        print('\nlinhas:', dict(Counter(i.get('linha') or '?' for i in itens)), '· intenções:', dict(Counter(i.get('intencao') or '?' for i in itens)))
        p = carregar_perfil(obrigatorio=False); nomes = [l['nome'] for l in p.get('linhas', [])]
        faltam = [x for x in nomes if x not in [i.get('linha') for i in itens[-6:]]]
        if faltam: print('linhas sem post nos últimos 6:', ', '.join(faltam))
        usadas = [i.get('estrutura') for i in itens[-5:] if i.get('estrutura')]
        if usadas:
            print('estruturas dos últimos 5:', ', '.join(usadas), '→ prefira outra:', ', '.join(e for e in ESTRUTURAS if e not in usadas))
    elif cmd == 'juntar':
        juntar(sys.argv[2], sys.argv[3], itens)
    elif cmd == 'pendencias':
        ps = pendencias(itens)
        if not ps: print('nada pendente.')
        for x in ps: print(f'- [{x["tipo"]}] {x["texto"]}' + (f' (id: {x["id"]})' if x['id'] and x['tipo'] not in ('publicou', 'juntar') else '')
                  + (f' → memoria.py juntar "{x["id"]}" {x["importado"]}' if x['tipo'] == 'juntar' else ''))
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
