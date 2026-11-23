"""Capa de artigo do LinkedIn (1920×1080, 16:9) com a identidade da pessoa.
uso: capa.py <pasta|arquivo.png> "<título com *destaque*>" ["linha de apoio opcional"] [--tema editorial|minimal|impacto|classico|foto]
     → <pasta>/capa_artigo.png (ou o arquivo .png indicado)
O título da capa pode ser mais curto que o título do artigo: é o que se lê no feed, numa miniatura.
"""
import sys, html, math, random, tempfile, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *
from carrossel import css_fontes, tit_css, md, foto_html, logo_html, rodar, paleta, tema_de, _img_uri, TEMAS

W, H = 1920, 1080


def linhas_svg(cor, semente):
    """Feixe de curvas e pontos (dados convergindo) do lado esquerdo, discreto."""
    r = random.Random(semente); out = []
    for k in range(26):
        y0 = r.uniform(-100, H + 100); y1 = H * 0.5 + r.uniform(-40, 40); y2 = r.uniform(80, H - 80)
        op = r.uniform(0.10, 0.35)
        out.append(f'<path d="M -40 {y0:.0f} C 260 {y0:.0f}, 380 {y1:.0f}, 560 {y1:.0f} S 740 {y2:.0f}, 820 {y2:.0f}" '
                   f'stroke="{cor}" stroke-opacity="{op:.2f}" stroke-width="1.6" fill="none"/>')
    for k in range(70):
        x = r.uniform(600, 820); y = H * 0.5 + (x - 560) * r.uniform(-0.9, 0.9)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(2, 5):.1f}" fill="{cor}" fill-opacity="{r.uniform(.25, .8):.2f}"/>')
    for k in range(40):
        x = r.uniform(0, 300); y = r.uniform(0, H); s = r.uniform(6, 16)
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{s:.0f}" height="{s:.0f}" fill="{cor}" fill-opacity="{r.uniform(.05, .2):.2f}"/>')
    return f'<svg class="deco" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(out)}</svg>'


def doc(p, titulo, apoio, tema=None):
    tema = tema or tema_de(p); pal = paleta(p, tema, 'texto' if tema == 'impacto' else 'capa'); c = p['cores']
    ident = p.get('identificacao') if p.get('conselho') == 'CFM' else ''
    esq, larg = 880, 930          # área do texto
    fundo = pal['grad'].replace('85% -10%', '30% 50%') if pal['grad'] != 'none' else pal['bg']
    arte = ''
    if tema == 'editorial':
        arte = linhas_svg(pal['ac'], titulo)
    elif tema == 'minimal':
        arte = f'<div class="arte" style="left:-260px;top:140px;width:900px;height:900px;border-radius:50%;border:3px solid {pal["ac"]};opacity:.5"></div>'
    elif tema == 'impacto':
        arte = f'<div class="arte" style="left:0;top:0;width:640px;height:100%;background:{c["acento"]}"></div>'; esq = 760; larg = 1060
    elif tema == 'classico':
        arte = '<div class="regua" style="top:60px"></div><div class="regua" style="bottom:60px"></div>'; esq = 260; larg = 1400
    elif tema == 'foto' and p.get('foto') and Path(p['foto']).expanduser().exists():
        arte = (f'<div class="arte" style="left:0;top:0;width:900px;height:100%;background:linear-gradient(90deg,transparent 55%,{pal["bg"]} 100%),'
                f'url({_img_uri(p["foto"])}) center/cover"></div>')
    centro = 'text-align:center;align-items:center;' if tema == 'classico' else ''
    caixa_alta = 'text-transform:uppercase;' if tema == 'impacto' else ''
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
{css_fontes(p)}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{background:{pal['bg']}}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:{fundo};color:{pal['fg']};font-family:'Inter',sans-serif;position:relative}}
.deco,.arte{{position:absolute;left:0;top:0}}
.regua{{position:absolute;left:80px;right:80px;height:12px;border-top:2px solid {pal['fg']};border-bottom:1px solid {pal['fg']};opacity:.5}}
.txt{{position:absolute;left:{esq}px;width:{larg - 110}px;top:140px;bottom:230px;display:flex;flex-direction:column;justify-content:center;gap:34px;{centro}}}
h1{{{tit_css(p)};font-size:112px;line-height:1.04;text-wrap:balance;{caixa_alta}}}
.ac{{color:{pal['ac']}}}
.apoio{{font-size:42px;line-height:1.3;opacity:.85;text-wrap:balance}}
.autor{{position:absolute;left:{esq}px;bottom:96px;display:flex;align-items:center;gap:22px}}
.foto{{border-radius:50%;object-fit:cover;border:4px solid {pal['ac']}}}
.foto.ini{{display:flex;align-items:center;justify-content:center;background:{pal['ac']};color:{pal['bg']};font-weight:800}}
.autor b{{font-size:32px;display:block}} .autor span{{font-size:24px;opacity:.75}}
.logo{{position:absolute;top:80px;right:110px;max-height:80px;max-width:300px;object-fit:contain}}
</style></head><body>{arte}{logo_html(p)}
<div class="txt"><h1 data-fit="112">{md(titulo)}</h1>{f'<p class="apoio" data-fit="42">{md(apoio)}</p>' if apoio else ''}</div>
<div class="autor">{foto_html(p, 84)}<div><b>{html.escape(p.get('nome', ''))}</b><span>{html.escape(p.get('titulo', ''))}{' · ' + html.escape(ident) if ident else ''}</span></div></div>
<script>
const a=document.querySelector('.txt'), els=[...a.querySelectorAll('[data-fit]')]; let k=1,i=0;
const est=()=>a.scrollHeight>a.clientHeight+1||els.some(e=>e.scrollWidth>e.clientWidth+1);
while(est()&&i<60){{k*=0.95;i++;els.forEach(e=>e.style.fontSize=(e.dataset.fit*k)+'px')}}
</script></body></html>'''


if __name__ == '__main__':
    if len(sys.argv) < 3: sys.exit(__doc__)
    p = carregar_perfil(); alvo = Path(sys.argv[1]).expanduser().resolve()
    if alvo.suffix.lower() != '.png': alvo.mkdir(parents=True, exist_ok=True); alvo = alvo / 'capa_artigo.png'
    titulo = sys.argv[2]; apoio = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else ''
    tema = sys.argv[sys.argv.index('--tema') + 1] if '--tema' in sys.argv else None
    if len(titulo.replace('*', '')) > 70: print('ATENÇÃO título da capa longo; na miniatura do feed, até ~8 palavras lê melhor.')
    tmp = Path(tempfile.mkdtemp()); (tmp / 'c.html').write_text(doc(p, titulo, apoio, tema), encoding='utf-8')
    rodar([f'--screenshot={alvo}', f'--window-size={W},{H}', (tmp / 'c.html').as_uri()])
    shutil.rmtree(tmp, ignore_errors=True); print('capa:', alvo)
