"""Capa de artigo do LinkedIn (1920×1080, 16:9) com a identidade da pessoa.
uso: capa.py <pasta|arquivo.png> "<título com *destaque*>" ["linha de apoio opcional"]
     → <pasta>/capa_artigo.png (ou o arquivo .png indicado)
O título da capa pode ser mais curto que o título do artigo: é o que se lê no feed, numa miniatura.
"""
import sys, html, math, random, tempfile, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import *
from carrossel import css_fontes, tit_css, md, foto_html, rodar

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


def doc(p, titulo, apoio):
    c = p['cores']
    ident = p.get('identificacao') if p.get('conselho') == 'CFM' else ''
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
{css_fontes(p)}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{background:{c['fundo']}}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:radial-gradient(1400px 900px at 30% 50%, {c['suave']} 0%, {c['fundo']} 65%);
 color:{c['texto']};font-family:'Inter',sans-serif;position:relative}}
.deco{{position:absolute;left:0;top:0}}
.txt{{position:absolute;left:880px;right:110px;top:140px;bottom:230px;display:flex;flex-direction:column;justify-content:center;gap:34px}}
h1{{{tit_css(p)};font-size:112px;line-height:1.04;text-wrap:balance}}
.ac{{color:{c['acento']}}}
.apoio{{font-size:42px;line-height:1.3;opacity:.85;text-wrap:balance}}
.autor{{position:absolute;left:880px;bottom:96px;display:flex;align-items:center;gap:22px}}
.foto{{border-radius:50%;object-fit:cover;border:4px solid {c['acento']}}}
.foto.ini{{display:flex;align-items:center;justify-content:center;background:{c['acento']};color:{c['fundo']};font-weight:800}}
.autor b{{font-size:32px;display:block}} .autor span{{font-size:24px;opacity:.75}}
</style></head><body>{linhas_svg(c['acento'], titulo)}
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
    titulo = sys.argv[2]; apoio = sys.argv[3] if len(sys.argv) > 3 else ''
    if len(titulo.replace('*', '')) > 70: print('ATENÇÃO título da capa longo; na miniatura do feed, até ~8 palavras lê melhor.')
    tmp = Path(tempfile.mkdtemp()); (tmp / 'c.html').write_text(doc(p, titulo, apoio), encoding='utf-8')
    rodar([f'--screenshot={alvo}', f'--window-size={W},{H}', (tmp / 'c.html').as_uri()])
    shutil.rmtree(tmp, ignore_errors=True); print('capa:', alvo)
