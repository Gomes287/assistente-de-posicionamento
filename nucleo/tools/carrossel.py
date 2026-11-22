"""Carrossel do LinkedIn em PDF (1080×1350, 4:5) com a identidade da pessoa, a partir de <pasta>/carrossel.json.
uso: carrossel.py <pasta>            → carrossel.pdf (para subir como documento) + previa.png (todos os slides)
     carrossel.py --demo <saida.png> → prévia com as cores/fonte do perfil (para a configuração)
Precisa do Google Chrome, Chromium, Edge ou Brave instalado (usa o modo sem janela para gerar o PDF).

carrossel.json:
{"titulo_documento": "aparece sobre o carrossel no LinkedIn",
 "slides": [
  {"tipo": "capa", "titulo": "A pergunta *errada* custa mais caro", "subtitulo": "opcional"},
  {"tipo": "texto", "titulo": "…", "texto": "…"},
  {"tipo": "lista", "titulo": "…", "itens": ["…", "…"]},
  {"tipo": "citacao", "texto": "…", "autor": "opcional"},
  {"tipo": "numero", "numero": "46%", "legenda": "…", "fonte": "OBRIGATÓRIA"},
  {"tipo": "contraste", "esquerda": {"rotulo": "Assunto", "texto": "…"}, "direita": {"rotulo": "Ideia", "texto": "…"}},
  {"tipo": "final", "pergunta": "…", "texto": "opcional"}]}
*palavra* = cor de destaque. Qualquer slide aceita "rotulo" (texto pequeno em cima).
"""
import sys, json, re, html, base64, os, shutil, subprocess, tempfile, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *
from checar import checar_texto

W, H = 1080, 1350
FONTES = NUCLEO / 'fontes'


def chrome():
    if os.environ.get('CHROME'): return os.environ['CHROME']
    cands = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium',
             '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge', '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
             r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
             r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe']
    for c in cands:
        if Path(c).exists(): return c
    for n in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge', 'brave-browser'):
        if shutil.which(n): return shutil.which(n)
    sys.exit('Não achei Chrome/Chromium/Edge/Brave. Instale o Google Chrome (ou defina CHROME=/caminho/do/navegador).')


def b64(f):
    return base64.b64encode(Path(f).read_bytes()).decode()


def css_fontes(p):
    out = [f"@font-face{{font-family:'Inter';src:url(data:font/woff2;base64,{b64(FONTES / 'Inter.woff2')}) format('woff2');font-weight:100 900}}"]
    ft = p.get('fonte_titulo', 'Inter')
    if ft == 'Playfair':
        out.append(f"@font-face{{font-family:'Playfair';src:url(data:font/woff2;base64,{b64(FONTES / 'PlayfairDisplay-Roman.woff2')}) format('woff2');font-weight:400 900}}")
        out.append(f"@font-face{{font-family:'Playfair';font-style:italic;src:url(data:font/woff2;base64,{b64(FONTES / 'PlayfairDisplay-Italic.woff2')}) format('woff2');font-weight:400 900}}")
    if ft == 'Anton':
        out.append(f"@font-face{{font-family:'Anton';src:url(data:font/woff2;base64,{b64(FONTES / 'Anton.woff2')}) format('woff2')}}")
    return '\n'.join(out)


def tit_css(p):
    ft = p.get('fonte_titulo', 'Inter')
    if ft == 'Playfair': return "font-family:'Playfair',serif;font-weight:700;letter-spacing:-0.01em"
    if ft == 'Anton': return "font-family:'Anton',sans-serif;font-weight:400;text-transform:uppercase;letter-spacing:0.01em"
    return "font-family:'Inter',sans-serif;font-weight:800;letter-spacing:-0.025em"


def md(s):
    s = html.escape(s or '')
    s = re.sub(r'\*([^*]+)\*', r'<span class="ac">\1</span>', s)
    return s.replace('\n', '<br>')


def foto_html(p, tam):
    f = p.get('foto')
    if f and Path(f).expanduser().exists():
        ext = Path(f).suffix.lower().strip('.').replace('jpg', 'jpeg')
        return f'<img class="foto" style="width:{tam}px;height:{tam}px" src="data:image/{ext};base64,{b64(Path(f).expanduser())}">'
    ini = ''.join(w[0] for w in (p.get('nome') or '?').split()[:2]).upper()
    return f'<div class="foto ini" style="width:{tam}px;height:{tam}px;font-size:{tam * 0.38:.0f}px">{ini}</div>'


def rodape(p, i, n, grande=False):
    ident = p.get('identificacao') if p.get('conselho') == 'CFM' else ''
    seta = '' if i == n else '<span class="seta">→</span>'
    tam = 104 if grande else 64
    return f'''<div class="rod {'grande' if grande else ''}">{foto_html(p, tam)}<div class="quem"><b>{html.escape(p.get('nome', ''))}</b>
<span>{html.escape(p.get('titulo', ''))}</span>{f'<span class="ident">{html.escape(ident)}</span>' if grande and ident else ''}</div>
<div class="pag">{i}/{n}{seta}</div></div>'''


def corpo(s):
    t = s.get('tipo')
    rot = f'<div class="rot">{md(s["rotulo"])}</div>' if s.get('rotulo') else ''
    if t == 'capa':
        return f'{rot}<div class="area capa"><h1 data-fit="118">{md(s.get("titulo"))}</h1>' + \
               (f'<p class="sub" data-fit="40">{md(s["subtitulo"])}</p>' if s.get('subtitulo') else '') + '</div>'
    if t == 'texto':
        return f'{rot}<div class="area"><h2 data-fit="76">{md(s.get("titulo"))}</h2><div class="barra"></div><p class="txt" data-fit="42">{md(s.get("texto"))}</p></div>'
    if t == 'lista':
        its = ''.join(f'<li><span class="num">{k + 1}</span><span data-fit="40">{md(x)}</span></li>' for k, x in enumerate(s.get('itens', [])))
        return f'{rot}<div class="area"><h2 data-fit="68">{md(s.get("titulo"))}</h2><ol>{its}</ol></div>'
    if t == 'citacao':
        return f'{rot}<div class="area cit"><div class="aspas">“</div><p class="q" data-fit="62">{md(s.get("texto"))}</p>' + \
               (f'<p class="autor">{md(s["autor"])}</p>' if s.get('autor') else '') + '</div>'
    if t == 'numero':
        return f'{rot}<div class="area numa"><div class="big" data-fit="260">{md(s.get("numero"))}</div><p class="leg" data-fit="48">{md(s.get("legenda"))}</p>' \
               f'<p class="fonte">Fonte: {md(s.get("fonte"))}</p></div>'
    if t == 'contraste':
        e, d = s.get('esquerda', {}), s.get('direita', {})
        return f'{rot}<div class="area">' + (f'<h2 data-fit="64">{md(s["titulo"])}</h2>' if s.get('titulo') else '') + \
               f'<div class="cx"><div class="lado"><div class="lr">{md(e.get("rotulo"))}</div><p data-fit="40">{md(e.get("texto"))}</p></div>' \
               f'<div class="lado dir"><div class="lr">{md(d.get("rotulo"))}</div><p data-fit="40">{md(d.get("texto"))}</p></div></div></div>'
    if t == 'final':
        return f'{rot}<div class="area capa"><h2 class="perg" data-fit="84">{md(s.get("pergunta"))}</h2>' + \
               (f'<p class="sub" data-fit="38">{md(s["texto"])}</p>' if s.get('texto') else '') + '</div>'
    sys.exit(f'tipo de slide desconhecido: {t}')


def documento(p, slides, previa=False, escala=0.4, colunas=4):
    c = p['cores']; n = len(slides)
    secs = []
    for i, s in enumerate(slides, 1):
        grande = s.get('tipo') in ('capa', 'final')
        secs.append(f'<section class="slide t-{s.get("tipo")}">{corpo(s)}{rodape(p, i, n, grande)}</section>')
    if previa:
        cel = ''.join(f'<div class="cel" style="width:{W * escala}px;height:{H * escala}px">{x}</div>' for x in secs)
        body = f'<div class="grade" style="grid-template-columns:repeat({colunas},{W * escala}px)">{cel}</div>'
        extra = f'.cel{{overflow:hidden;border-radius:10px}} .cel .slide{{transform:scale({escala});transform-origin:0 0}} body{{background:#d9d9d9;padding:24px}} .grade{{display:grid;gap:24px}}'
    else:
        body = ''.join(secs); extra = ''
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
{css_fontes(p)}
@page{{size:{W}px {H}px;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.slide{{width:{W}px;height:{H}px;position:relative;overflow:hidden;display:flex;flex-direction:column;padding:96px 92px 0;
 background:radial-gradient(1200px 900px at 85% -10%, {c['suave']} 0%, {c['fundo']} 60%);color:{c['texto']};
 font-family:'Inter',sans-serif;page-break-after:always;break-after:page}}
.slide::after{{content:'';position:absolute;left:0;top:0;width:14px;height:100%;background:{c['acento']}}}
.ac{{color:{c['acento']}}}
.rot{{font-size:26px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:{c['acento']};margin-bottom:28px}}
.area{{flex:1;min-height:0;display:flex;flex-direction:column;justify-content:center;gap:34px;overflow:hidden}}
h1,h2{{{tit_css(p)};line-height:1.06}}
h1{{font-size:118px}} h2{{font-size:72px}}
.sub{{font-size:40px;line-height:1.3;opacity:.85;font-weight:400}}
.barra{{width:120px;height:8px;background:{c['acento']};border-radius:4px}}
.txt{{font-size:42px;line-height:1.38;font-weight:400}}
ol{{list-style:none;display:flex;flex-direction:column;gap:30px}}
li{{display:flex;gap:30px;align-items:flex-start;font-size:40px;line-height:1.3}}
.num{{flex:none;width:74px;height:74px;border-radius:50%;background:{c['acento']};color:{c['fundo']};display:flex;align-items:center;
 justify-content:center;font-weight:800;font-size:36px}}
.cit .aspas{{{tit_css(p)};font-size:220px;line-height:.6;color:{c['acento']};height:110px}}
.q{{{tit_css(p)};font-size:62px;line-height:1.18;text-transform:none}}
.autor{{font-size:32px;opacity:.75}}
.numa .big{{{tit_css(p)};font-size:260px;line-height:1;color:{c['acento']}}}
.leg{{font-size:48px;line-height:1.25;font-weight:500}}
.fonte{{font-size:26px;opacity:.7}}
.cx{{display:flex;flex-direction:column;gap:30px}}
.lado{{background:rgba(255,255,255,.06);border-left:10px solid {c['texto']}55;border-radius:18px;padding:36px 40px}}
.lado.dir{{border-left-color:{c['acento']}}}
.lr{{font-size:26px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:16px;opacity:.8}}
.lado p{{font-size:40px;line-height:1.3}}
.rod{{flex:none;display:flex;align-items:center;gap:24px;height:150px;border-top:2px solid {c['texto']}22;margin-top:30px}}
.rod.grande{{height:210px}}
.foto{{border-radius:50%;object-fit:cover;flex:none;border:4px solid {c['acento']}}}
.foto.ini{{display:flex;align-items:center;justify-content:center;background:{c['acento']};color:{c['fundo']};font-weight:800}}
.quem{{display:flex;flex-direction:column;gap:4px;flex:1;min-width:0}}
.quem b{{font-size:30px}} .quem span{{font-size:23px;opacity:.75}}
.rod.grande .quem b{{font-size:38px}} .rod.grande .quem span{{font-size:26px}}
.quem .ident{{font-size:21px!important;opacity:.9!important;color:{c['acento']}}}
.pag{{font-size:26px;opacity:.7;font-weight:600;white-space:nowrap}}
.seta{{margin-left:16px;color:{c['acento']};opacity:1;font-size:40px}}
{extra}
</style></head><body>{body}
<script>
document.querySelectorAll('.area').forEach(a=>{{
  const els=[...a.querySelectorAll('[data-fit]')];
  els.forEach(e=>e.style.fontSize=e.dataset.fit+'px');
  let k=1, it=0;
  const estoura=()=>a.scrollHeight>a.clientHeight+1||els.some(e=>e.scrollWidth>e.clientWidth+1);
  while(estoura()&&it<60){{k*=0.95;it++;els.forEach(e=>e.style.fontSize=(e.dataset.fit*k)+'px')}}
  if(k<0.6) a.dataset.apertado='1';
}});
</script></body></html>'''


def rodar(args):
    subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--hide-scrollbars',
                    '--virtual-time-budget=4000', *args], check=True, capture_output=True, timeout=120)


def render(p, slides, pasta, so_previa=False):
    pasta = Path(pasta); pasta.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    if not so_previa:
        (tmp / 'c.html').write_text(documento(p, slides), encoding='utf-8')
        rodar(['--no-pdf-header-footer', f'--print-to-pdf={pasta / "carrossel.pdf"}', (tmp / 'c.html').as_uri()])
    col = min(4, len(slides)); lin = math.ceil(len(slides) / col); e = 0.4
    (tmp / 'p.html').write_text(documento(p, slides, previa=True, escala=e, colunas=col), encoding='utf-8')
    alvo = pasta / ('previa.png')
    rodar([f'--screenshot={alvo}', f'--window-size={int(col * W * e + (col - 1) * 24 + 48)},{int(lin * H * e + (lin - 1) * 24 + 48)}', (tmp / 'p.html').as_uri()])
    shutil.rmtree(tmp, ignore_errors=True)
    return alvo


def validar(p, d):
    sl = d.get('slides', []); erros = []; av = []
    if not d.get('titulo_documento'): erros.append('falta "titulo_documento" (o LinkedIn pede ao subir o PDF).')
    if not 5 <= len(sl) <= 12: av.append(f'{len(sl)} slides; o usual é 6–10.')
    if sl and sl[0].get('tipo') != 'capa': av.append('o primeiro slide deveria ser "capa".')
    if sl and sl[-1].get('tipo') != 'final': av.append('o último slide deveria ser "final" (pergunta específica ou convite).')
    for i, s in enumerate(sl, 1):
        if s.get('tipo') == 'numero' and not s.get('fonte'): erros.append(f'slide {i}: número sem fonte.')
        txt = ' '.join(str(s.get(k, '')) for k in ('titulo', 'texto', 'pergunta', 'legenda'))
        if len(txt) > 380: av.append(f'slide {i}: {len(txt)} caracteres; slide bom tem uma ideia curta (corte ou divida).')
    if p.get('conselho') == 'CFM' and not p.get('identificacao'):
        erros.append('CFM: falta a identificação no perfil (vai no rodapé da capa e do slide final).')
    tudo = '\n\n'.join(' '.join([str(s.get(k, '')) for k in ('titulo', 'subtitulo', 'texto', 'pergunta', 'legenda')] +
                                [str(x) for x in s.get('itens', [])]) for s in sl).replace('*', '')
    _, avt = checar_texto(tudo, p, carrossel=True)
    av += [f'{n}: {m}' for n, m in avt if n != 'nota']
    return erros, av


if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    p = carregar_perfil()
    if sys.argv[1] == '--demo':
        nome = (p.get('nome') or 'Seu Nome').split()[0]
        demo = [{"tipo": "capa", "rotulo": "prévia", "titulo": "Assim fica a *capa* do seu carrossel", "subtitulo": "Cores, fonte, foto e identificação vêm do perfil."},
                {"tipo": "lista", "titulo": "Três coisas para conferir", "itens": ["O contraste está confortável?", "A fonte combina com você?", f"A foto e o nome de {nome} estão certos?"]},
                {"tipo": "final", "pergunta": "Quer mudar *alguma* cor ou a fonte?"}]
        out = Path(sys.argv[2] if len(sys.argv) > 2 else 'previa_carrossel.png').expanduser().resolve()
        a = render(p, demo, out.parent, so_previa=True); a.rename(out); print('prévia:', out); sys.exit()
    P = Path(sys.argv[1]).expanduser().resolve(); d = json.load(open(P / 'carrossel.json', encoding='utf-8'))
    erros, av = validar(p, d)
    for a in av: print('ATENÇÃO', a)
    if erros:
        for e in erros: print('ERRO   ', e)
        sys.exit(1)
    prev = render(p, d['slides'], P)
    print('PDF:', P / 'carrossel.pdf'); print('prévia (confira antes de entregar):', prev)
    print('título do documento no LinkedIn:', d['titulo_documento'])
