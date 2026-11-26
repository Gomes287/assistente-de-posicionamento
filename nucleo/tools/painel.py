"""Painel no navegador: o que está pendente, o histórico com os números, as ideias para o próximo post e a voz.
Roda só no computador da pessoa (127.0.0.1, com chave na URL) e lê os arquivos dela a cada vez que a página abre,
então está sempre atualizado. Não escreve posts: para isso, os botões copiam o pedido para colar na conversa do Claude.
uso: painel.py [--sem-abrir]       fecha sozinho depois de 2 horas sem uso
"""
import sys, json, re, io, base64, secrets, threading, webbrowser, tempfile, contextlib, time, html as H
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *
import memoria

LINKEDIN = re.compile(r'^https://(www\.)?linkedin\.com/\S+$')


def e(s):
    return H.escape(str(s if s is not None else ''))


def _rodar(f, *a):
    """Roda uma função das ferramentas e devolve o que ela escreveu (ou o motivo do erro)."""
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out): f(*a)
        return True, out.getvalue().strip()
    except SystemExit as x:
        return False, (out.getvalue() + '\n' + str(x.code or '')).strip()
    except Exception as x:
        return False, f'{out.getvalue()}\nerro: {x}'.strip()


def ideias_do_banco():
    if not NOTAS.exists(): return []
    t = NOTAS.read_text(encoding='utf-8'); m = re.search(r'^## Banco de ideias\s*$(.*?)(?=^## |\Z)', t, re.M | re.S)
    if not m: return []
    out = []
    for b in re.split(r'\n(?=- )', m.group(1).strip()):
        b = b.strip()
        if not b.startswith('- '): continue
        if re.search(r'\(usada em ', b): continue
        tit = re.search(r'\*\*(.+?)\*\*', b)
        resto = re.sub(r'\s+', ' ', b[2:])
        resto = re.sub(r'^\d{4}-\d{2}-\d{2}\s*·\s*', '', resto)
        titulo = tit.group(1).rstrip('.') if tit else resto[:70]
        out.append({'titulo': titulo, 'resumo': re.sub(r'\*\*.+?\*\*\s*', '', resto, count=1)[:220]})
    return out


def _botao_copiar(pedido, rotulo='Copiar pedido para o Claude'):
    return f'<button class="copiar" data-pedido="{e(pedido)}">{e(rotulo)}</button>'


def _card(x, itens):
    t = x['tipo']; corpo = f'<p>{e(x["texto"])}</p>'
    if t == 'juntar':
        corpo += (f'<form data-acao="juntar"><input type="hidden" name="pasta" value="{e(x["id"])}">'
                  f'<input type="hidden" name="importado" value="{e(x["importado"])}"><button class="p">Sim, é o mesmo post</button></form>'
                  '<p class="dica">Não é o mesmo? Registre pelo Claude: cole o link do post certo na conversa.</p>')
    elif t == 'publicou':
        corpo += (f'<form data-acao="registrar"><input type="hidden" name="pasta" value="{e(x["id"])}">'
                  '<input name="url" type="url" placeholder="Cole aqui o link do post no LinkedIn" required>'
                  '<details><summary>Mudei o texto no LinkedIn antes de publicar</summary>'
                  '<textarea name="final" rows="6" placeholder="Cole aqui o texto como foi publicado"></textarea></details>'
                  '<button class="p">Registrar</button></form>'
                  f'<p class="dica">Ainda não publicou? {_botao_copiar("Quero revisar o rascunho " + chr(34) + x["titulo"] + chr(34) + " antes de publicar.", "Copiar pedido para revisar com o Claude")}</p>')
    elif t == 'link':
        corpo += (f'<form data-acao="vincular"><input type="hidden" name="id" value="{e(x["id"])}">'
                  '<input name="url" type="url" placeholder="Cole aqui o link do post no LinkedIn" required>'
                  '<button class="p">Guardar link</button></form>')
    elif t == 'planilha':
        corpo += ('<form data-acao="importar"><input name="arquivo" type="file" accept=".xlsx" required>'
                  '<button class="p">Enviar planilha</button></form>'
                  '<p class="dica">No LinkedIn: seu perfil → Análises de publicação (ou "Ver todas as análises") → '
                  'Exportar. Ele baixa um arquivo .xlsx; escolha esse arquivo aqui.</p>')
    elif t == 'intencao':
        ops = ''.join(f'<option value="{i}">{n}</option>' for i, n in (
            ('posicionar', 'posicionar (reforçar pelo que quero ser lembrado)'), ('amplificar', 'amplificar (chegar a mais gente)'),
            ('compartilhar', 'compartilhar (ensinar algo útil)'), ('conversar', 'conversar (gerar comentários)')))
        corpo += (f'<form data-acao="intencao"><input type="hidden" name="id" value="{e(x["id"])}">'
                  f'<select name="intencao" required><option value="">escolha…</option>{ops}</select>'
                  '<button class="p">Guardar</button></form>')
    elif t == 'aprendizado':
        corpo += (f'<form data-acao="aprendizado"><input type="hidden" name="id" value="{e(x["id"])}">'
                  '<input name="texto" placeholder="O que eu levo deste post para a próxima decisão" required>'
                  '<button class="p">Guardar</button></form>'
                  f'<p class="dica">Prefere pensar junto? {_botao_copiar("Quero ler os números do post " + chr(34) + (x["titulo"] or x["id"]) + chr(34) + " com você.", "Copiar pedido para ler com o Claude")}</p>')
    rot = {'juntar': 'Já publicado?', 'publicou': 'Publicou?', 'link': 'Falta o link', 'planilha': 'Hora dos números', 'intencao': 'Falta a intenção',
           'aprendizado': 'O que ficou'}[t]
    return f'<div class="card {t}"><span class="rot">{rot}</span>{corpo}</div>'


def _num(v):
    return f'{v:,.0f}'.replace(',', '.') if isinstance(v, (int, float)) else '·'


def montar():
    p = carregar_perfil(obrigatorio=False); itens = memoria.ler(); pend = memoria.pendencias(itens, p)
    nome = p.get('nome') or 'você'
    if not memoria.PERFIL.exists():
        return PAGINA.replace('%CORPO%', '<section><h2>Falta configurar</h2><p>Abra a aba Code do app do Claude e diga: '
                              '<b>configurar meu assistente de posicionamento</b>.</p>'
                              + _botao_copiar('configurar meu assistente de posicionamento') + '</section>')
    urg = [x for x in pend if x['tipo'] != 'aprendizado']; resto = [x for x in pend if x['tipo'] == 'aprendizado']
    s = [f'<header><h1>Painel de {e(nome.split()[0])}</h1><p class="dica">{e(p.get("posicionamento", ""))}</p></header>']
    s.append('<section><h2>Para fazer agora</h2>' + (''.join(_card(x, itens) for x in urg) if urg else
             '<p class="ok">Nada pendente. Bom momento para pensar no próximo post.</p>')
             + (''.join(_card(x, itens) for x in resto)) + '</section>')
    # próximo post
    ult = itens[-6:]; linhas = [l['nome'] for l in p.get('linhas', [])]
    sem = [l for l in linhas if l not in [i.get('linha') for i in ult]]
    ideias = ideias_do_banco()
    blocos = [f'<div class="ideia"><b>{e(i["titulo"])}</b><p>{e(i["resumo"])}</p>'
              + _botao_copiar(f'Quero um post a partir da ideia do meu banco: "{i["titulo"]}".') + '</div>' for i in ideias]
    blocos += [f'<div class="ideia"><b>Linha "{e(l)}"</b><p>Sem post nos últimos seis conteúdos.</p>'
               + _botao_copiar(f'Quero um post na linha "{l}". Me ajuda a achar a experiência certa?') + '</div>' for l in sem]
    blocos.append('<div class="ideia"><b>Não sei o que postar</b><p>O Claude começa perguntando o que você viveu esta semana.</p>'
                  + _botao_copiar('Não sei o que postar essa semana. Me entrevista?') + '</div>')
    s.append('<section><h2>Próximo post</h2><p class="dica">O botão copia o pedido. Cole numa conversa nova da aba Code '
             'do Claude.</p><div class="grade">' + ''.join(blocos) + '</div></section>')
    # histórico
    linhas_h = []
    for i in sorted(itens, key=lambda i: str(i.get('data', '')), reverse=True):
        r = i.get('resultado') or {}; t = memoria.taxa(r)
        tit = i.get('ideia') or i.get('titulo_trabalho') or i['id']
        link = f'<a href="{e(i["link"])}" target="_blank" rel="noopener">abrir</a>' if i.get('link') else '<span class="falta">sem link</span>'
        linhas_h.append(f'<tr><td>{e(memoria.data_br(i.get("data")))}</td><td class="tit">{e(tit[:120])}'
                        + (f'<div class="apr">Aprendi: {e(i["aprendizado"])}</div>' if i.get('aprendizado') else '')
                        + f'</td><td>{e(i.get("formato") or "·")}</td><td>{e(i.get("intencao") or "·")}</td>'
                        f'<td class="n">{_num(r.get("impressoes"))}</td><td class="n">{_num(r.get("comentarios"))}</td>'
                        f'<td class="n">{f"{100 * t:.1f}%".replace(".", ",") if t is not None else "·"}</td><td>{link}</td></tr>')
    s.append('<section><h2>O que já foi publicado</h2>' + (
        '<div class="tabela"><table><thead><tr><th>Data</th><th>Ideia</th><th>Formato</th><th>Intenção</th>'
        '<th class="n">Impressões</th><th class="n">Coment.</th><th class="n">Engaj.</th><th></th></tr></thead><tbody>'
        + ''.join(linhas_h) + '</tbody></table></div>' if itens else '<p class="dica">Nada registrado ainda.</p>') + '</section>')
    # voz
    vm = p.get('voz_medidas') or {}; pub = p.get('voz_publicados') or []
    entram = [x for x in pub if x['peso'] >= PESO_MINIMO]
    v = [f'<p>Sua voz vem de <b>{vm.get("textos_proprios", vm.get("posts_medidos", 0))} textos seus</b>'
         + (f' e de <b>{len(entram)} {"publicado" if len(entram) == 1 else "publicados"} com a skill</b>, que pesam {round(100 * vm.get("peso_dos_publicados", 0))}% '
            'na mistura.' if entram else '. Cada post que você editar e publicar se soma a ela, com mais peso quanto mais o texto for seu.') + '</p>']
    if pub:
        v.append('<ul class="voz">' + ''.join(f'<li>{e(x["id"].split("/")[0])} · {e(x["tipo"])} · peso {x["peso"]:.2f}'
                                              + ('' if x['peso'] >= PESO_MINIMO else ' (não entrou: quase todo da skill)') + '</li>' for x in pub[-8:]) + '</ul>')
    if vm and 'passiva_por_1000' not in vm:
        v.append('<p class="dica">Sua voz foi medida por uma versão antiga. '
                 + _botao_copiar('Quero atualizar minha voz com textos meus.', 'Copiar pedido para atualizar') + '</p>')
    s.append('<section><h2>Sua voz</h2>' + ''.join(v) + '</section>')
    s.append('<footer>Este painel roda só no seu computador e lê seus arquivos em '
             f'{e(str(CONF).replace(str(Path.home()), "~"))}. Nada é enviado para fora. Atualizado em {time.strftime("%d/%m %H:%M")}.</footer>')
    return PAGINA.replace('%CORPO%', '\n'.join(s))


def agir(d):
    itens = memoria.ler(); a = d.get('acao')
    url = (d.get('url') or '').strip()
    if a in ('registrar', 'vincular') and not LINKEDIN.match(url):
        return False, 'Esse não parece um link do LinkedIn. No post, clique nos três pontinhos → "Copiar link para a publicação".'
    if a == 'registrar':
        P = Path(d['pasta']); base = Path(carregar_perfil(obrigatorio=False).get('pasta_saida') or '').expanduser().resolve()
        if base not in P.resolve().parents: return False, 'pasta fora da sua pasta de conteúdos.'
        msgs = []
        if (d.get('final') or '').strip():
            from edicao import final
            ide = json.load(open(P / 'ideia.json', encoding='utf-8'))
            alvo = P / ('artigo.md' if ide.get('formato') == 'artigo' and (P / 'artigo.md').exists() else 'post.md')
            if alvo.exists():
                with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8') as f: f.write(d['final'])
                ok, m = _rodar(final, alvo, f.name); Path(f.name).unlink(); msgs.append(m)
        ok, m = _rodar(memoria.registrar, P, url, itens); msgs.append(m)
        return ok, '\n'.join(x for x in msgs if x)
    if a == 'juntar':
        P = Path(d['pasta']); base = Path(carregar_perfil(obrigatorio=False).get('pasta_saida') or '').expanduser().resolve()
        if base not in P.resolve().parents: return False, 'pasta fora da sua pasta de conteúdos.'
        return _rodar(memoria.juntar, P, d.get('importado', ''), itens)
    if a == 'vincular':
        return _rodar(lambda: (memoria.achar(itens, d['id']).__setitem__('link', url), memoria.gravar(itens), print('Link guardado.')))
    if a == 'intencao':
        if d.get('intencao') not in INTENCOES: return False, 'escolha uma intenção.'
        return _rodar(lambda: (memoria.achar(itens, d['id']).__setitem__('intencao', d['intencao']), memoria.gravar(itens), print('Intenção guardada.')))
    if a == 'aprendizado':
        txt = (d.get('texto') or '').strip()
        if not txt: return False, 'escreva o que ficou.'
        return _rodar(lambda: (memoria.achar(itens, d['id']).__setitem__('aprendizado', txt), memoria.gravar(itens), print('Guardado.')))
    if a == 'importar':
        try: dados = base64.b64decode(d.get('arquivo', '').split(',', 1)[-1])
        except Exception: return False, 'não consegui ler o arquivo.'
        if not dados.startswith(b'PK'): return False, 'esse arquivo não é uma planilha .xlsx.'
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f: f.write(dados)
        ok, m = _rodar(memoria.importar, f.name, itens); Path(f.name).unlink()
        return ok, m
    return False, 'ação desconhecida.'


def servir(abrir=True, horas_ociosas=2):
    token = secrets.token_hex(16); visto = [time.time()]

    class H_(BaseHTTPRequestHandler):
        def log_message(self, *a): pass

        def _env(self, cod, tipo, corpo):
            b = corpo.encode(); self.send_response(cod); self.send_header('Content-Type', tipo)
            self.send_header('Content-Length', str(len(b))); self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(b)

        def do_GET(self):
            visto[0] = time.time()
            if self.path != '/?k=' + token: return self._env(404, 'text/plain; charset=utf-8', 'não encontrado')
            try: pag = montar()
            except Exception as x: pag = PAGINA.replace('%CORPO%', f'<section><h2>Algo deu errado</h2><pre>{e(x)}</pre></section>')
            self._env(200, 'text/html; charset=utf-8', pag.replace('%TOKEN%', json.dumps(token)))

        def do_POST(self):
            visto[0] = time.time()
            try: d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
            except Exception: return self._env(400, 'text/plain; charset=utf-8', 'pedido inválido')
            if d.get('token') != token or self.path != '/acao': return self._env(403, 'text/plain; charset=utf-8', 'proibido')
            ok, msg = agir(d)
            self._env(200, 'application/json', json.dumps({'ok': ok, 'msg': msg}))

    srv = ThreadingHTTPServer(('127.0.0.1', 0), H_)
    url = f'http://127.0.0.1:{srv.server_address[1]}/?k={token}'
    print('painel:', url, flush=True)
    print('Pode minimizar esta janela. Fechar a janela fecha o painel (ele também fecha sozinho depois de 2 horas sem uso).', flush=True)
    if abrir: webbrowser.open(url)

    def vigia():
        while time.time() - visto[0] < horas_ociosas * 3600: time.sleep(60)
        srv.shutdown()
    threading.Thread(target=vigia, daemon=True).start()
    srv.serve_forever()


PAGINA = '''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Meu painel do LinkedIn</title>
<style>
:root{--papel:#fbfaf7;--tinta:#1d2329;--suave:#5b6670;--linha:#e3e0d8;--card:#ffffff;--latao:#8c6118;--alerta:#b5541c;--ok:#2f7a4a}
@media (prefers-color-scheme:dark){:root{--papel:#15191d;--tinta:#ece8df;--suave:#9aa4ad;--linha:#2c3238;--card:#1c2126;--latao:#e0b867;--alerta:#f0a06a;--ok:#7ccf98}}
*{box-sizing:border-box}body{margin:0;background:var(--papel);color:var(--tinta);font:16px/1.55 -apple-system,system-ui,sans-serif}
main{max-width:1040px;margin:0 auto;padding:28px 16px 60px}header h1{font-size:28px;margin:0}
h2{font-size:19px;margin:36px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--linha)}
.dica{color:var(--suave);font-size:14px;margin:4px 0}.ok{color:var(--ok)}.falta{color:var(--alerta);font-size:14px}
.card{background:var(--card);border:1px solid var(--linha);border-left:4px solid var(--latao);border-radius:10px;padding:14px 16px;margin:0 0 12px}
.card.aprendizado{border-left-color:var(--linha)}.card p{margin:4px 0 10px}
.rot{font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--latao)}
form{display:flex;flex-wrap:wrap;gap:8px;align-items:flex-start}form details{flex-basis:100%;font-size:14px;color:var(--suave)}
input,select,textarea{font:inherit;font-size:15px;padding:8px 10px;border:1px solid var(--linha);border-radius:8px;background:var(--papel);color:var(--tinta);min-width:0}
input[type=url],input[name=texto]{flex:1 1 320px}textarea{width:100%;margin-top:6px}
button{font:inherit;font-size:14px;padding:8px 14px;border-radius:8px;border:1px solid var(--linha);background:transparent;color:var(--tinta);cursor:pointer}
button.p{background:var(--tinta);color:var(--papel);border-color:var(--tinta)}button.copiar{margin-top:6px}
.grade{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.ideia{background:var(--card);border:1px solid var(--linha);border-radius:10px;padding:14px 16px}.ideia p{color:var(--suave);font-size:14px;margin:6px 0}
.tabela{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:8px 6px;border-bottom:1px solid var(--linha);vertical-align:top}
th{color:var(--suave);font-weight:600}td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}td.tit{min-width:240px}.apr{color:var(--suave);font-size:13px;margin-top:4px}
a{color:var(--latao)}ul.voz{font-size:14px;color:var(--suave)}footer{margin-top:48px;color:var(--suave);font-size:13px}
#aviso{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);max-width:min(640px,calc(100% - 32px));background:var(--tinta);color:var(--papel);
padding:12px 16px;border-radius:10px;font-size:14px;white-space:pre-wrap;display:none;z-index:9;max-height:70vh;overflow:auto}
</style><main>%CORPO%</main><div id="aviso"></div>
<script>
const T=%TOKEN%, av=document.getElementById('aviso');
function aviso(m,ms){av.textContent=m;av.style.display='block';clearTimeout(av._t);av._t=setTimeout(()=>av.style.display='none',ms||4000)}
document.querySelectorAll('.copiar').forEach(b=>b.onclick=async()=>{const t=b.dataset.pedido;
 try{await navigator.clipboard.writeText(t)}catch(_){const x=document.createElement('textarea');x.value=t;document.body.appendChild(x);x.select();document.execCommand('copy');x.remove()}
 aviso('Copiado. Abra uma conversa nova na aba Code do Claude e cole (⌘V ou Ctrl+V).')});
const ler=f=>new Promise((ok,erro)=>{const r=new FileReader();r.onload=()=>ok(r.result);r.onerror=erro;r.readAsDataURL(f)});
document.querySelectorAll('form[data-acao]').forEach(f=>f.onsubmit=async ev=>{ev.preventDefault();
 const d={token:T,acao:f.dataset.acao};for(const el of f.elements){if(!el.name)continue;d[el.name]=el.type==='file'?(el.files[0]?await ler(el.files[0]):''):el.value}
 const b=f.querySelector('button.p');b.disabled=true;b.textContent='Um momento…';
 try{const r=await(await fetch('/acao',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)})).json();
  const m=r.msg||(r.ok?'Feito.':'Não deu certo.');
  if(r.ok&&m.length>90){av.textContent=m+'\\n\\nClique aqui para fechar.';av.style.display='block';av.style.cursor='pointer';av.onclick=()=>location.reload()}
  else{aviso(m,r.ok?3000:9000);if(r.ok)setTimeout(()=>location.reload(),1500);else{b.disabled=false;b.textContent='Tentar de novo'}}}
 catch(_){aviso('O painel foi fechado. Abra de novo pelo atalho.',8000)}});
</script></html>'''

if __name__ == '__main__':
    servir(abrir='--sem-abrir' not in sys.argv)
