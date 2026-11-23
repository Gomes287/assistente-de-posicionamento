"""Tira as cores principais de uma imagem (logo, banner, print do perfil) usando o Chrome; nada para instalar.
uso: cores.py <imagem>     → lista as cores (da mais presente para a menos) e sugere fundo/texto/acento/suave
     cores.py --curadas "<nome>"  → 3 paletas prontas (para quem não tem identidade visual)
O Claude confere a sugestão olhando a imagem e ajusta com a pessoa antes de gravar no perfil.
"""
import sys, json, base64, tempfile, shutil, re, html
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from carrossel import chrome
import subprocess

JS = r"""
const img=new Image();
img.onload=()=>{
  const c=document.createElement('canvas'), W=160, H=Math.max(1,Math.round(160*img.height/img.width));
  c.width=W;c.height=H;const g=c.getContext('2d');g.drawImage(img,0,0,W,H);
  const d=g.getImageData(0,0,W,H).data, px=[];
  for(let i=0;i<d.length;i+=4){if(d[i+3]>200)px.push([d[i],d[i+1],d[i+2]]);}
  let K=10, cent=[];for(let k=0;k<K;k++)cent.push(px[Math.floor((k+0.5)*px.length/K)]);
  let lab=new Array(px.length).fill(0);
  for(let it=0;it<25;it++){
    for(let i=0;i<px.length;i++){let b=0,bd=1e18;for(let k=0;k<K;k++){const a=px[i],q=cent[k];const dd=(a[0]-q[0])**2+(a[1]-q[1])**2+(a[2]-q[2])**2;if(dd<bd){bd=dd;b=k}}lab[i]=b}
    const s=cent.map(()=>[0,0,0,0]);for(let i=0;i<px.length;i++){const s2=s[lab[i]];s2[0]+=px[i][0];s2[1]+=px[i][1];s2[2]+=px[i][2];s2[3]++}
    cent=s.map((v,k)=>v[3]?[v[0]/v[3],v[1]/v[3],v[2]/v[3]]:cent[k]);
  }
  const cnt=cent.map(()=>0);lab.forEach(l=>cnt[l]++);
  document.getElementById('out').textContent=JSON.stringify(cent.map((q,k)=>({rgb:q.map(Math.round),parte:cnt[k]/px.length})));
};
img.src=document.getElementById('src').textContent;
"""


def lum(rgb):
    r, g, b = [x / 255 for x in rgb]
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contraste(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def hexa(rgb):
    return '#%02X%02X%02X' % tuple(rgb)


def sat(rgb):
    mx, mn = max(rgb), min(rgb)
    return (mx - mn) / (mx + 1e-6)


if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    if sys.argv[1] == '--curadas':
        import hashlib
        from comum import CURADAS
        nomes = sorted(CURADAS); s = int(hashlib.sha1((sys.argv[2] if len(sys.argv) > 2 else 'x').encode()).hexdigest(), 16)
        escolha = [nomes[(s + k * 3) % len(nomes)] for k in range(3)]
        print('três paletas para oferecer (mostre com carrossel.py --demo depois de gravar a escolhida):')
        for n in escolha: print(f'  {n}: {json.dumps(CURADAS[n])}')
        sys.exit()
    f = Path(sys.argv[1]).expanduser()
    tipo = {'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png', 'webp': 'webp', 'gif': 'gif'}.get(f.suffix.lower().strip('.'), 'png')
    uri = f'data:image/{tipo};base64,' + base64.b64encode(f.read_bytes()).decode()
    tmp = Path(tempfile.mkdtemp()); pg = tmp / 'c.html'
    pg.write_text(f'<!doctype html><pre id="src">{uri}</pre><pre id="out"></pre><script>{JS}</script>', encoding='utf-8')
    r = subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--virtual-time-budget=8000', '--dump-dom', pg.as_uri()],
                       capture_output=True, text=True, timeout=120)
    shutil.rmtree(tmp, ignore_errors=True)
    m = re.search(r'<pre id="out">(.*?)</pre>', r.stdout, re.S)
    if not m or not m.group(1).strip(): sys.exit('não consegui ler a imagem (formato aceito: png, jpg, webp, gif).')
    cs = sorted(json.loads(html.unescape(m.group(1))), key=lambda c: -c['parte'])
    print('cores da imagem (da mais presente para a menos):')
    for c in cs: print(f"  {hexa(c['rgb'])}  {100 * c['parte']:4.0f}%  luminância {lum(c['rgb']):.2f}  saturação {sat(c['rgb']):.2f}")
    fundo = cs[0]['rgb']
    escuro = lum(fundo) < 0.2
    resto = cs[1:]
    texto = max(resto, key=lambda c: contraste(c['rgb'], fundo))['rgb'] if resto else ([245, 241, 234] if escuro else [20, 24, 28])
    if contraste(texto, fundo) < 7: texto = [245, 243, 238] if escuro else [18, 22, 28]
    cand = [c['rgb'] for c in resto if c['rgb'] != texto and contraste(c['rgb'], fundo) >= 3]
    acento = max(cand, key=lambda x: sat(x) + 0.5 * min(contraste(x, fundo), 6) / 6) if cand else ([227, 178, 91] if escuro else [14, 94, 111])
    suave = [min(255, round(v + (28 if escuro else -18))) for v in fundo]
    sug = {'fundo': hexa(fundo), 'texto': hexa(texto), 'acento': hexa(acento), 'suave': hexa(suave)}
    print('\nsugestão:', json.dumps(sug))
    print(f'contraste texto/fundo {contraste(texto, fundo):.1f}:1 (bom ≥ 7) · acento/fundo {contraste(acento, fundo):.1f}:1 (bom ≥ 3)')
