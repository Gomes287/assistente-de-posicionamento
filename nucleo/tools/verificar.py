"""Confere se o computador tem o que a skill precisa e diz, em português simples, o que falta.
uso: verificar.py
"""
import sys, platform, os
from pathlib import Path

ok = True
print('Conferindo o seu computador…\n')
v = sys.version_info
if v >= (3, 9):
    print(f'  ✔ Python {v.major}.{v.minor}')
else:
    ok = False
    print(f'  ✘ Python {v.major}.{v.minor} é antigo. Instale o Python 3.9 ou mais novo em python.org/downloads.')

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import comum, carrossel
    try:
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            c = carrossel.chrome()
        print(f'  ✔ Navegador para gerar PDF e imagens: {Path(c).name}')
    except SystemExit:
        ok = False
        print('  ✘ Não achei Google Chrome, Edge, Brave ou Chromium. Instale o Google Chrome (google.com/chrome);'
              ' sem ele a skill escreve, mas não gera carrossel nem capa.')
    fontes = list((comum.NUCLEO / 'fontes').glob('*.woff2'))
    print(f'  ✔ Fontes ({len(fontes)})' if fontes else '  ✘ Fontes não encontradas: reinstale a skill.')
    try:
        comum.CONF.mkdir(parents=True, exist_ok=True); t = comum.CONF / '.teste'; t.write_text('ok'); t.unlink()
        print(f'  ✔ Pasta dos seus dados: {comum.CONF}')
    except Exception as e:
        ok = False; print(f'  ✘ Não consegui gravar em {comum.CONF} ({e}).')
except Exception as e:
    ok = False; print(f'  ✘ Arquivos da skill incompletos ({e}). Reinstale.')

print('\nTudo pronto.' if ok else '\nArrume os itens com ✘ e rode de novo.')
if platform.system() == 'Windows':
    print('(Windows ainda não foi testado; se algo falhar, conte o que apareceu.)')
sys.exit(0 if ok else 1)
