"""Carrossel do LinkedIn em PDF (1080×1350, 4:5) com a identidade da pessoa, a partir de <pasta>/carrossel.json.
uso: carrossel.py <pasta>               → carrossel.pdf (para subir como documento) + previa.png (todos os slides)
     carrossel.py --demo <saida.png>    → prévia com o visual do perfil (para a configuração)
     carrossel.py --temas <saida.png>   → a capa em cada família de layout, lado a lado (para a pessoa escolher)
Precisa do Google Chrome, Chromium, Edge ou Brave instalado (usa o modo sem janela para gerar o PDF).

Famílias de layout (perfil.tema): editorial (padrão) · minimal · impacto · classico · foto
Fontes do título (perfil.fonte_titulo): Inter · SpaceGrotesk · ArchivoBlack · Anton · Playfair · DMSerif
Variações por pessoa (lado da faixa, desenho de fundo) saem do nome, para dois perfis parecidos não ficarem iguais.

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
import sys, json, re, html, base64, os, shutil, subprocess, tempfile, math, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *
from checar import checar_texto

W, H = 1080, 1350
FONTES = NUCLEO / 'fontes'
TEMAS = ('editorial', 'minimal', 'impacto', 'classico', 'foto')
# nome → (arquivos, formato, pesos, css do título)
FONTE_TIT = {
    'Inter': ([('Inter.woff2', 'normal')], 'woff2', '100 900', "font-family:'Inter';font-weight:800;letter-spacing:-0.025em"),
    'SpaceGrotesk': ([('SpaceGrotesk.woff2', 'normal')], 'woff2', '300 700', "font-family:'SpaceGrotesk';font-weight:700;letter-spacing:-0.02em"),
    'ArchivoBlack': ([('ArchivoBlack.woff2', 'normal')], 'woff2', '400', "font-family:'ArchivoBlack';font-weight:400;letter-spacing:-0.01em"),
    'Anton': ([('Anton.woff2', 'normal')], 'woff2', '400', "font-family:'Anton';font-weight:400;text-transform:uppercase;letter-spacing:0.01em"),
    'Playfair': ([('PlayfairDisplay-Roman.woff2', 'normal'), ('PlayfairDisplay-Italic.woff2', 'italic')], 'woff2', '400 900', "font-family:'Playfair';font-weight:700;letter-spacing:-0.01em"),
    'DMSerif': ([('DMSerifDisplay.ttf', 'normal')], 'truetype', '400', "font-family:'DMSerif';font-weight:400;letter-spacing:-0.01em"),
}


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


def fonte_titulo(p):
    f = p.get('fonte_titulo') or 'Inter'
    return f if f in FONTE_TIT else 'Inter'


def css_fontes(p):
    out = []
    for nome in sorted({'Inter', fonte_titulo(p)}):
        arqs, fmt, pesos, _ = FONTE_TIT[nome]
        for arq, estilo in arqs:
            out.append(f"@font-face{{font-family:'{nome}';font-style:{estilo};src:url(data:font/{fmt};base64,{b64(FONTES / arq)}) format('{fmt}');font-weight:{pesos}}}")
    return '\n'.join(out)


def tit_css(p):
    return FONTE_TIT[fonte_titulo(p)][3]


def md(s):
    s = html.escape(s or '')
    s = re.sub(r'\*([^*]+)\*', r'<span class="ac">\1</span>', s)
    return s.replace('\n', '<br>')


# ---- cor --------------------------------------------------------------------------------------------------------
def _rgb(h):
    h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def _lum(h):
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = [x / 255 for x in _rgb(h)]
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contraste(a, b):
    la, lb = sorted([_lum(a), _lum(b)], reverse=True); return (la + 0.05) / (lb + 0.05)


def _mistura(a, b, t):
    ra, rb = _rgb(a), _rgb(b); return '#%02X%02X%02X' % tuple(round(x + (y - x) * t) for x, y in zip(ra, rb))


def semente(p):
    return int(hashlib.sha1((p.get('nome') or 'x').encode()).hexdigest(), 16)


def tema_de(p):
    return p.get('tema') if p.get('tema') in TEMAS else 'editorial'


def paleta(p, tema, tipo):
    """Cores do slide conforme a família de layout: bg, fg, ac (destaque), card, linha, grad."""
    c = p['cores']; escuro, claro = c['fundo'], c['texto']
    if _lum(escuro) > _lum(claro): escuro, claro = claro, escuro
    ac = c['acento']
    if tema in ('minimal', 'classico'):
        papel = _mistura(claro, '#FFFFFF', 0.35) if tema == 'minimal' else _mistura(claro, '#F3E9D8', 0.25)
        acl, k = ac, 0.0
        while contraste(acl, papel) < 3.2 and k < 0.9:  # escurece o destaque mantendo o tom (bege vira bronze)
            k += 0.05; acl = _mistura(ac, '#000000', k)
        return dict(bg=papel, fg=escuro, ac=acl, card=_mistura(papel, escuro, 0.06), linha=_mistura(papel, escuro, 0.25), grad='none')
    if tema == 'impacto' and tipo in ('capa', 'final'):
        fg = escuro if contraste(escuro, ac) >= contraste(claro, ac) else claro
        return dict(bg=ac, fg=fg, ac=fg, card='rgba(0,0,0,.08)', linha=_mistura(ac, fg, 0.3), grad='none')
    grad = 'none' if tema == 'impacto' else f"radial-gradient(1200px 900px at 85% -10%, {c['suave']} 0%, {escuro} 60%)"
    return dict(bg=escuro, fg=claro, ac=ac, card='rgba(255,255,255,.06)', linha=_mistura(escuro, claro, 0.15), grad=grad)


def deco(p, tema, pal):
    if tema == 'classico':
        return '<div class="regua cima"></div><div class="regua baixo"></div>'
    if tema in ('impacto', 'minimal'):
        return ''
    estilo = semente(p) % 4
    if estilo == 1:  # grade de pontos
        return f'<div class="deco" style="background-image:radial-gradient({pal["linha"]} 2.5px, transparent 2.6px);background-size:44px 44px;opacity:.55"></div>'
    if estilo == 2:  # diagonais
        return f'<div class="deco" style="background-image:repeating-linear-gradient(135deg,{pal["linha"]} 0 2px,transparent 2px 38px);opacity:.35"></div>'
    if estilo == 3:  # círculo no canto
        return f'<div class="deco circ" style="border-color:{pal["ac"]}"></div>'
    return ''


def _img_uri(f):
    ext = Path(f).suffix.lower().strip('.').replace('jpg', 'jpeg').replace('svg', 'svg+xml')
    return f'data:image/{ext};base64,{b64(Path(f).expanduser())}'


def foto_html(p, tam):
    f = p.get('foto')
    if f and Path(f).expanduser().exists():
        return f'<img class="foto" style="width:{tam}px;height:{tam}px" src="{_img_uri(f)}">'
    ini = ''.join(w[0] for w in (p.get('nome') or '?').split()[:2]).upper()
    return f'<div class="foto ini" style="width:{tam}px;height:{tam}px;font-size:{tam * 0.38:.0f}px">{ini}</div>'


def logo_html(p):
    f = p.get('logo')
    return f'<img class="logo" src="{_img_uri(f)}">' if f and Path(f).expanduser().exists() else ''


def rodape(p, i, n, grande=False, tema='editorial'):
    ident = p.get('identificacao') if p.get('conselho') == 'CFM' else ''
    seta = '' if i == n else '<span class="seta">→</span>'
    tam = 104 if grande else 64
    mostrar_foto = not (tema == 'foto' and grande and p.get('foto'))
    return f'''<div class="rod {'grande' if grande else ''}">{foto_html(p, tam) if mostrar_foto else ''}<div class="quem"><b>{html.escape(p.get('nome', ''))}</b>
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


def slide_html(p, s, i, n, tema):
    tipo = s.get('tipo'); grande = tipo in ('capa', 'final'); pal = paleta(p, tema, tipo)
    if tema in ('editorial', 'foto'): lado = ('esq', 'dir', 'topo')[semente(p) // 7 % 3]
    else: lado = 'topo' if tema == 'minimal' else 'nenhum'
    fundo_foto = ''
    if tema == 'foto' and grande and p.get('foto') and Path(p['foto']).expanduser().exists():
        fundo_foto = (f'<div class="fotobg" style="background-image:linear-gradient(90deg,{pal["bg"]} 34%,{pal["bg"]}cc 58%,transparent 88%),'
                      f'url({_img_uri(p["foto"])})"></div>')
    st = f"--bg:{pal['bg']};--fg:{pal['fg']};--ac:{pal['ac']};--card:{pal['card']};--linha:{pal['linha']};background:{pal['grad'] if pal['grad'] != 'none' else pal['bg']}"
    logo = logo_html(p) if grande else ''
    return f'<section class="slide t-{tipo} tema-{tema} faixa-{lado}" style="{st}">{fundo_foto}{deco(p, tema, pal)}{logo}{corpo(s)}{rodape(p, i, n, grande, tema)}</section>'


def css_base(p):
    tc = tit_css(p)
    return f'''{css_fontes(p)}
@page{{size:{W}px {H}px;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.slide{{width:{W}px;height:{H}px;position:relative;overflow:hidden;display:flex;flex-direction:column;padding:96px 92px 0;
 color:var(--fg);font-family:'Inter',sans-serif;page-break-after:always;break-after:page}}
.slide>*{{position:relative;z-index:1}}
.slide>.deco,.slide>.fotobg{{position:absolute;inset:0;z-index:0}}
.fotobg{{background-size:cover;background-position:right center}}
.slide>.deco.circ{{inset:auto -260px -260px auto;width:720px;height:720px;border-radius:50%;border:3px solid;opacity:.25}}
.faixa-esq::after,.faixa-dir::after,.faixa-topo::after{{content:'';position:absolute;background:var(--ac);z-index:2}}
.faixa-esq::after{{left:0;top:0;width:14px;height:100%}} .faixa-dir::after{{right:0;top:0;width:14px;height:100%}}
.faixa-topo::after{{left:0;top:0;height:12px;width:100%}}
.ac{{color:var(--ac)}}
.rot{{font-size:26px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--ac);margin-bottom:28px}}
.area{{flex:1;min-height:0;display:flex;flex-direction:column;justify-content:center;gap:34px;overflow:hidden}}
h1,h2{{{tc};line-height:1.06;text-wrap:balance}}
h1{{font-size:118px}} h2{{font-size:72px}}
.sub{{font-size:40px;line-height:1.3;opacity:.85;font-weight:400;text-wrap:balance}}
.barra{{width:120px;height:8px;background:var(--ac);border-radius:4px}}
.txt{{font-size:42px;line-height:1.38;font-weight:400;text-wrap:pretty}}
ol{{list-style:none;display:flex;flex-direction:column;gap:30px}}
li{{display:flex;gap:30px;align-items:flex-start;font-size:40px;line-height:1.3}}
.num{{flex:none;width:74px;height:74px;border-radius:50%;background:var(--ac);color:var(--bg);display:flex;align-items:center;
 justify-content:center;font-weight:800;font-size:36px}}
.cit .aspas{{{tc};font-size:220px;line-height:.6;color:var(--ac);height:110px;text-transform:none}}
.q{{{tc};font-size:62px;line-height:1.18;text-transform:none}}
.autor{{font-size:32px;opacity:.75}}
.numa .big{{{tc};font-size:260px;line-height:1;color:var(--ac)}}
.leg{{font-size:48px;line-height:1.25;font-weight:500}}
.fonte{{font-size:26px;opacity:.7}}
.cx{{display:flex;flex-direction:column;gap:30px}}
.lado{{background:var(--card);border-left:10px solid var(--linha);border-radius:18px;padding:36px 40px}}
.lado.dir{{border-left-color:var(--ac)}}
.lr{{font-size:26px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:16px;opacity:.8}}
.lado p{{font-size:40px;line-height:1.3}}
.rod{{flex:none;display:flex;align-items:center;gap:24px;height:150px;border-top:2px solid var(--linha);margin-top:30px}}
.rod.grande{{height:210px}}
.foto{{border-radius:50%;object-fit:cover;flex:none;border:4px solid var(--ac)}}
.foto.ini{{display:flex;align-items:center;justify-content:center;background:var(--ac);color:var(--bg);font-weight:800}}
.quem{{display:flex;flex-direction:column;gap:4px;flex:1;min-width:0}}
.quem b{{font-size:30px}} .quem span{{font-size:23px;opacity:.75}}
.rod.grande .quem b{{font-size:38px}} .rod.grande .quem span{{font-size:26px}}
.quem .ident{{font-size:21px!important;opacity:.9!important;color:var(--ac)}}
.pag{{font-size:26px;opacity:.7;font-weight:600;white-space:nowrap}}
.seta{{margin-left:16px;color:var(--ac);opacity:1;font-size:40px}}
.slide>.logo{{position:absolute;top:84px;right:92px;max-height:72px;max-width:260px;object-fit:contain;z-index:3}}
.tema-minimal h1,.tema-minimal h2{{font-weight:700}}
.tema-minimal .barra{{height:4px;width:80px}} .tema-minimal .num{{border-radius:8px}}
.tema-minimal .lado{{border-left-width:4px;border-radius:0}}
.tema-impacto h1{{font-size:140px;text-transform:uppercase;line-height:.98}} .tema-impacto h2{{text-transform:uppercase}}
.tema-impacto .num{{border-radius:0}}
.tema-impacto .rot{{background:var(--ac);color:var(--bg);display:inline-block;padding:10px 18px;align-self:flex-start}}
.tema-impacto .lado{{border-radius:0;border-left-width:18px}} .tema-impacto .barra{{height:18px;width:180px;border-radius:0}}
.tema-classico{{text-align:center}} .tema-classico .area{{align-items:center}} .tema-classico .barra{{height:2px;width:160px}}
.tema-classico ol{{text-align:left}} .tema-classico .rod{{justify-content:center;text-align:left}}
.slide>.regua{{position:absolute;left:60px;right:60px;height:10px;border-top:2px solid var(--fg);border-bottom:1px solid var(--fg);opacity:.5;z-index:0}}
.slide>.regua.cima{{top:46px}} .slide>.regua.baixo{{bottom:26px}}
.tema-classico .rod{{margin-bottom:44px}}
.tema-classico .lado{{border-left:none;border-top:4px solid var(--linha);border-radius:0;text-align:left}}
.tema-classico .lado.dir{{border-top-color:var(--ac)}}
.tema-foto.t-capa .area,.tema-foto.t-final .area{{max-width:64%}}
'''


JS_FIT = '''<script>
document.querySelectorAll('.area').forEach(a=>{
  const els=[...a.querySelectorAll('[data-fit]')];
  els.forEach(e=>e.style.fontSize=e.dataset.fit+'px');
  let k=1, it=0;
  const estoura=()=>a.scrollHeight>a.clientHeight+1||els.some(e=>e.scrollWidth>e.clientWidth+1);
  while(estoura()&&it<60){k*=0.95;it++;els.forEach(e=>e.style.fontSize=(e.dataset.fit*k)+'px')}
});
</script>'''


def documento(p, slides, previa=False, escala=0.4, colunas=4, temas=None):
    tema = tema_de(p); n = len(slides)
    secs = [slide_html(p, s, i, n, (temas[i - 1] if temas else tema)) for i, s in enumerate(slides, 1)]
    if previa:
        cel = ''.join(f'<div class="cel" style="width:{W * escala}px;height:{H * escala}px">{x}</div>' for x in secs)
        body = f'<div class="grade" style="grid-template-columns:repeat({colunas},{W * escala}px)">{cel}</div>'
        extra = f'.cel{{overflow:hidden;border-radius:10px}} .cel .slide{{transform:scale({escala});transform-origin:0 0}} body{{background:#d9d9d9;padding:24px}} .grade{{display:grid;gap:24px}}'
    else:
        body = ''.join(secs); extra = ''
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{css_base(p)}{extra}</style></head><body>{body}{JS_FIT}</body></html>'


def rodar(args):
    subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--hide-scrollbars',
                    '--virtual-time-budget=4000', '--force-device-scale-factor=1', *args], check=True, capture_output=True, timeout=120)


def previa_png(p, slides, alvo, colunas=4, escala=0.4, temas=None):
    col = min(colunas, len(slides)); lin = math.ceil(len(slides) / col)
    tmp = Path(tempfile.mkdtemp())
    (tmp / 'p.html').write_text(documento(p, slides, previa=True, escala=escala, colunas=col, temas=temas), encoding='utf-8')
    rodar([f'--screenshot={alvo}', f'--window-size={int(col * W * escala + (col - 1) * 24 + 48)},{int(lin * H * escala + (lin - 1) * 24 + 48)}', (tmp / 'p.html').as_uri()])
    shutil.rmtree(tmp, ignore_errors=True)
    return alvo


def render(p, slides, pasta, so_previa=False):
    pasta = Path(pasta); pasta.mkdir(parents=True, exist_ok=True)
    if not so_previa:
        tmp = Path(tempfile.mkdtemp())
        (tmp / 'c.html').write_text(documento(p, slides), encoding='utf-8')
        rodar(['--no-pdf-header-footer', f'--print-to-pdf={pasta / "carrossel.pdf"}', (tmp / 'c.html').as_uri()])
        shutil.rmtree(tmp, ignore_errors=True)
    return previa_png(p, slides, pasta / 'previa.png')


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
    if sys.argv[1] in ('--demo', '--temas'):
        nome = (p.get('nome') or 'Seu Nome').split()[0]
        out = Path(sys.argv[2] if len(sys.argv) > 2 else 'previa_carrossel.png').expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        if sys.argv[1] == '--temas':
            capas = [{"tipo": "capa", "rotulo": t, "titulo": "Assim fica a *capa* do seu carrossel",
                      "subtitulo": "Mesmas cores e fonte, outra família de layout."} for t in TEMAS]
            previa_png(p, capas, out, colunas=5, escala=0.3, temas=list(TEMAS)); print('famílias:', ', '.join(TEMAS), '→', out); sys.exit()
        demo = [{"tipo": "capa", "rotulo": "prévia", "titulo": "Assim fica a *capa* do seu carrossel", "subtitulo": "Cores, fonte, foto e layout vêm do perfil."},
                {"tipo": "lista", "titulo": "Três coisas para conferir", "itens": ["O contraste está confortável?", "A fonte combina com você?", f"A foto e o nome de {nome} estão certos?"]},
                {"tipo": "final", "pergunta": "Quer mudar *alguma* cor, a fonte ou o layout?"}]
        previa_png(p, demo, out); print('prévia:', out); sys.exit()
    P = Path(sys.argv[1]).expanduser().resolve(); d = json.load(open(P / 'carrossel.json', encoding='utf-8'))
    erros, av = validar(p, d)
    for a in av: print('ATENÇÃO', a)
    if erros:
        for e in erros: print('ERRO   ', e)
        sys.exit(1)
    prev = render(p, d['slides'], P)
    print('PDF:', P / 'carrossel.pdf'); print('prévia (confira antes de entregar):', prev)
    print('título do documento no LinkedIn:', d['titulo_documento'])
