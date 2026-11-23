"""Edição do rascunho pela pessoa, com registro de quem escreveu cada mudança (para a voz aprender só com ela).
uso:
  edicao.py iniciar <arquivo.md>              guarda o rascunho da skill (rascunho-<nome>.md) antes de mostrar à pessoa
  edicao.py mostrar <arquivo.md> [--artigo]   parágrafos numerados (§1, §2…) com os trechos marcados pelo verificador,
                                              para a pessoa editar pela conversa ("no §3 troca X por Y")
  edicao.py marcar <arquivo.md> pessoa|skill  depois de cada mudança feita pela conversa: "pessoa" se as palavras
                                              são dela (troca literal, trecho que ela digitou, corte que ela pediu);
                                              "skill" se ela pediu e você reescreveu ("deixa mais curto")
  edicao.py pagina <arquivo.md> [--artigo]    abre uma página no navegador para ela editar direto no texto, com o
                                              verificador marcando os trechos a cada "Salvar"; fecha no "Concluir"
  edicao.py final <arquivo.md> <colado.txt>   versão que foi ao ar, se ela mexeu no LinkedIn antes de publicar
  edicao.py peso <arquivo.md>                 quanto do texto é dela (0 a 1) e se vai entrar na voz
  edicao.py aprender <pasta>                  soma à voz as versões finais da pasta, com o peso (memoria.py registrar chama)
Arquivos na pasta do conteúdo: rascunho-post.md (o que a skill entregou), .anterior-post.md e edicao.json.
"""
import sys, json, re, difflib, secrets, threading, webbrowser, html as H
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *


def _reg(arq):
    f = arq.parent / 'edicao.json'
    return f, (json.load(open(f, encoding='utf-8')) if f.exists() else {})


def _salvar_reg(f, d):
    f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')


def _anterior(arq):
    return arq.parent / f'.anterior-{arq.name}'


def iniciar(arq):
    f, d = _reg(arq); t = arq.read_text(encoding='utf-8')
    (arq.parent / f'rascunho-{arq.name}').write_text(t, encoding='utf-8')
    _anterior(arq).write_text(t, encoding='utf-8')
    d[arq.name] = {'palavras_rascunho': len(t.split()), 'pessoa_inseridas': 0, 'pessoa_removidas': 0,
                   'skill_inseridas': 0, 'mudancas': 0, 'aprendido': False}
    _salvar_reg(f, d)
    print(f'rascunho guardado ({len(t.split())} palavras). A partir daqui, registre cada mudança com edicao.py marcar.')


def marcar(arq, quem, novo=None):
    """Compara com a versão anterior e soma as palavras inseridas/removidas na conta de quem fez."""
    f, d = _reg(arq)
    if arq.name not in d: iniciar(arq); f, d = _reg(arq)
    ant = _anterior(arq).read_text(encoding='utf-8') if _anterior(arq).exists() else ''
    if novo is not None: arq.write_text(novo, encoding='utf-8')
    atual = arq.read_text(encoding='utf-8')
    a, b = ant.split(), atual.split()
    ins = rem = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op in ('replace', 'delete'): rem += i2 - i1
        if op in ('replace', 'insert'): ins += j2 - j1
    r = d[arq.name]
    if quem == 'pessoa':
        r['pessoa_inseridas'] += ins; r['pessoa_removidas'] += rem
    else:
        r['skill_inseridas'] += ins
    r['mudancas'] += 1 if (ins or rem) else 0
    _salvar_reg(f, d); _anterior(arq).write_text(atual, encoding='utf-8')
    return ins, rem


def peso(arq):
    """Quanto do texto final é dela: palavras que ela escreveu + metade do que ela cortou, sobre o tamanho do texto.
    Metade do texto dela já vale peso 1. Abaixo de PESO_MINIMO o post não entra na voz."""
    f, d = _reg(arq); r = d.get(arq.name)
    if not r: return 0.0, 'sem registro de edição (o rascunho não foi guardado com edicao.py iniciar)'
    final = max(1, len(arq.read_text(encoding='utf-8').split()))
    fr = r['pessoa_inseridas'] / final + 0.5 * r['pessoa_removidas'] / max(1, r['palavras_rascunho'])
    w = round(min(1.0, 2 * fr), 2)
    return w, (f'{r["pessoa_inseridas"]} palavras dela, {r["pessoa_removidas"]} cortadas por ela, '
               f'{r["skill_inseridas"]} reescritas pela skill a pedido')


def mostrar(arq, artigo):
    from checar import conferir, texto_marcado
    t, m, av, marcas = conferir(arq, artigo)
    tm, motivos = texto_marcado(t, marcas) if marcas else (t, [])
    ps = [x.strip() for x in re.split(r'\n\s*\n', tm) if x.strip()]
    for i, x in enumerate(ps, 1):
        print(f'§{i}  {x}\n')
    if motivos:
        print('trechos marcados:')
        for i, mot in enumerate(motivos, 1): print(f'  [{i}] {mot}')


def final(arq, colado):
    novo = Path(colado).read_text(encoding='utf-8').strip() + '\n'
    ins, rem = marcar(arq, 'pessoa', novo)
    print(f'versão publicada guardada: {ins} palavras novas, {rem} removidas em relação à última versão.')


def aprender(pasta):
    pasta = Path(pasta).expanduser().resolve(); f = pasta / 'edicao.json'
    if not f.exists(): print('voz: nada a aprender (sem edicao.json).'); return
    d = json.load(open(f, encoding='utf-8')); p = carregar_perfil(obrigatorio=False)
    if not p.get('voz_ancora') and p.get('voz_medidas') and not p.get('voz_publicados'):
        p['voz_ancora'] = dict(p['voz_medidas'])          # perfis de antes desta versão: a voz medida vira a âncora
    pub = p.setdefault('voz_publicados', [])
    for nome, r in d.items():
        arq = pasta / nome
        if not arq.exists(): continue
        w, expl = peso(arq)
        tipo = 'artigo' if nome.startswith('artigo') else 'post'
        chave = f'{pasta.name}/{nome}'
        pub[:] = [x for x in pub if x['id'] != chave]
        pub.append({'id': chave, 'tipo': tipo, 'peso': w, 'data': hoje(), 'medidas': medir(arq.read_text(encoding='utf-8'))})
        r['aprendido'] = True
        print(f'voz ({tipo}): {nome} entra com peso {w} ({expl})' if w >= PESO_MINIMO else
              f'voz ({tipo}): {nome} NÃO entra (peso {w}: quase tudo é da skill; {expl})')
    combinar_voz(p); salvar_perfil(p); _salvar_reg(f, d)


# ---- página de edição -----------------------------------------------------------------------------------------------
PAGINA = '''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Editar: %(nome)s</title>
<style>
:root{--papel:#fbfaf7;--tinta:#1d2329;--suave:#5b6670;--linha:#e3e0d8;--marca:#f6dc8a;--latao:#8c6118}
@media (prefers-color-scheme:dark){:root{--papel:#15191d;--tinta:#ece8df;--suave:#9aa4ad;--linha:#2c3238;--marca:#6b5418;--latao:#e0b867}}
*{box-sizing:border-box}body{margin:0;background:var(--papel);color:var(--tinta);font:17px/1.6 -apple-system,system-ui,sans-serif}
header{display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap;padding:14px 20px;border-bottom:1px solid var(--linha)}
h1{font-size:17px;margin:0}.dica{color:var(--suave);font-size:14px;margin:2px 0 0}
button{font:inherit;font-size:15px;padding:8px 16px;border-radius:8px;border:1px solid var(--linha);background:transparent;color:var(--tinta);cursor:pointer}
button.p{background:var(--tinta);color:var(--papel);border-color:var(--tinta)}
main{display:grid;grid-template-columns:1fr 1fr;min-height:calc(100vh - 70px)}
@media(max-width:860px){main{grid-template-columns:1fr}}
textarea{width:100%%;height:100%%;min-height:70vh;border:0;border-right:1px solid var(--linha);padding:20px;font:inherit;background:transparent;color:inherit;resize:none;outline:none}
#ver{padding:20px;white-space:pre-wrap}mark{background:var(--marca);color:inherit;border-radius:3px;padding:0 2px}sup{color:var(--latao);font-weight:700}
ol{font-size:14px;color:var(--suave);padding:12px 12px 12px 32px;margin:0 0 20px;border:1px solid var(--linha);border-radius:8px;white-space:normal}#cont.alto{color:#c0392b;font-weight:700}#cont{font-size:13px;color:var(--suave)}#fim{display:none;padding:40px;text-align:center}
</style>
<header><div><h1>%(nome)s</h1><p class="dica">Escreva à esquerda. "Salvar e conferir" marca à direita os trechos para olhar de novo. Marcar não é acusar: você decide.</p></div>
<div><span id="cont"></span> <button onclick="enviar('salvar')">Salvar e conferir</button> <button class="p" onclick="enviar('concluir')">Concluir</button></div></header>
<main id="area"><textarea id="t" spellcheck="true"></textarea><div id="ver"></div></main>
<div id="fim"><h1>Pronto. Pode voltar para o Claude.</h1><p class="dica">O texto foi salvo em %(nome)s.</p></div>
<script>
const T=%(token)s, t=document.getElementById('t'); t.value=%(texto)s;
const LIM=%(limite)s, conta=()=>{const c=document.getElementById('cont'),n=t.value.trim().length;c.textContent=n.toLocaleString('pt-BR')+' caracteres'+(LIM&&n>LIM?' (o LinkedIn aceita até 3.000)':'');c.className=LIM&&n>LIM?'alto':''}; t.oninput=conta; conta();
async function enviar(acao){const r=await fetch('/'+acao,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:T,texto:t.value})});
 const j=await r.json(); if(acao==='concluir'){document.getElementById('area').style.display='none';document.querySelector('header').style.display='none';document.getElementById('fim').style.display='block';return}
 document.getElementById('ver').innerHTML=(j.motivos.length?'<ol>'+j.motivos.map(m=>'<li>'+m+'</li>').join('')+'</ol>':'<p class="dica">Nenhum trecho marcado.</p>')+j.html}
enviar('salvar');
</script></html>'''


def _html_marcado(t, marcas):
    motivos, ult, out, fim = [], {}, [], 0
    for a, b, mot in sorted(marcas, key=lambda x: (x[0], -(x[1] - x[0]))):
        if a < fim: continue
        if mot not in ult: motivos.append(mot); ult[mot] = len(motivos)
        out.append(H.escape(t[fim:a])); out.append(f'<mark title="{H.escape(mot)}">{H.escape(t[a:b])}<sup>{ult[mot]}</sup></mark>'); fim = b
    out.append(H.escape(t[fim:]))
    return ''.join(out), [H.escape(m) for m in motivos]


def pagina(arq, artigo):
    from checar import conferir
    if arq.name not in _reg(arq)[1]: iniciar(arq)
    token = secrets.token_hex(16)
    corpo = (PAGINA % {'nome': H.escape(arq.name), 'token': json.dumps(token), 'limite': 0 if artigo else 3000,
                       'texto': json.dumps(arq.read_text(encoding='utf-8'))}).encode()

    class H_(BaseHTTPRequestHandler):
        def log_message(self, *a): pass

        def _json(self, d):
            b = json.dumps(d).encode(); self.send_response(200)
            self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)

        def do_GET(self):
            if self.path != '/?k=' + token: self.send_response(404); self.end_headers(); return
            self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.end_headers(); self.wfile.write(corpo)

        def do_POST(self):
            d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
            if d.get('token') != token: self.send_response(403); self.end_headers(); return
            texto = d.get('texto', '').rstrip() + '\n'
            if texto != arq.read_text(encoding='utf-8'): marcar(arq, 'pessoa', texto)
            if self.path == '/concluir':
                self._json({'ok': True}); threading.Thread(target=srv.shutdown).start(); return
            _, m, av, marcas = conferir(arq, artigo)
            h, mot = _html_marcado(texto, marcas); self._json({'html': h, 'motivos': mot})

    srv = ThreadingHTTPServer(('127.0.0.1', 0), H_)
    url = f'http://127.0.0.1:{srv.server_address[1]}/?k={token}'
    print('página de edição:', url, flush=True); webbrowser.open(url)
    threading.Timer(3 * 3600, srv.shutdown).start()   # fecha sozinha em 3 horas se ninguém clicar em Concluir
    srv.serve_forever()
    w, expl = peso(arq)
    print(f'edição concluída: {arq}\nquanto do texto é dela: {w} ({expl})', flush=True)
    import os; os._exit(0)


if __name__ == '__main__':
    if len(sys.argv) < 3: sys.exit(__doc__)
    cmd, alvo = sys.argv[1], Path(sys.argv[2]).expanduser().resolve()
    if cmd == 'iniciar': iniciar(alvo)
    elif cmd == 'mostrar': mostrar(alvo, '--artigo' in sys.argv or alvo.name.startswith('artigo'))
    elif cmd == 'marcar':
        ins, rem = marcar(alvo, sys.argv[3]); print(f'{sys.argv[3]}: +{ins} palavras, -{rem}')
    elif cmd == 'pagina': pagina(alvo, '--artigo' in sys.argv or alvo.name.startswith('artigo'))
    elif cmd == 'final': final(alvo, sys.argv[3])
    elif cmd == 'peso':
        w, expl = peso(alvo); print(f'{w} ({expl}); ' + ('entra na voz.' if w >= PESO_MINIMO else 'não entra na voz.'))
    elif cmd == 'aprender': aprender(alvo)
    else: sys.exit(__doc__)
