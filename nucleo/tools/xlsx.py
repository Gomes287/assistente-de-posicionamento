"""Leitor mínimo de .xlsx só com a biblioteca padrão (para as planilhas exportadas do LinkedIn).
uso direto (inspecionar): xlsx.py <arquivo.xlsx>   → imprime cada aba e suas linhas
"""
import sys, re, zipfile, xml.etree.ElementTree as ET
from pathlib import Path

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL = '{http://schemas.openxmlformats.org/package/2006/relationships}'


def _col(ref):
    n = 0
    for ch in re.match(r'[A-Z]+', ref).group():
        n = n * 26 + ord(ch) - 64
    return n - 1


def ler(arquivo):
    """→ {nome_da_aba: [[valor, ...], ...]} (valores como texto; números ficam como texto também)."""
    z = zipfile.ZipFile(arquivo)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS):
            ss.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels')).iter(REL + 'Relationship')}
    out = {}
    for sh in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets', NS):
        alvo = rels[sh.get('{%s}id' % NS['r'])].lstrip('/')
        alvo = alvo if alvo.startswith('xl/') else 'xl/' + alvo
        linhas = []
        for row in ET.fromstring(z.read(alvo)).iter('{%s}row' % NS['m']):
            vals = {}
            for c in row.findall('m:c', NS):
                t = c.get('t'); v = c.find('m:v', NS)
                if t == 's' and v is not None: val = ss[int(v.text)]
                elif t == 'inlineStr': val = ''.join(x.text or '' for x in c.iter('{%s}t' % NS['m']))
                else: val = v.text if v is not None else ''
                vals[_col(c.get('r'))] = val
            if vals:
                linhas.append([vals.get(i, '') for i in range(max(vals) + 1)])
        out[sh.get('name')] = linhas
    return out


if __name__ == '__main__':
    for nome, linhas in ler(sys.argv[1]).items():
        print(f'=== {nome} ({len(linhas)} linhas)')
        for l in linhas[:int(sys.argv[2]) if len(sys.argv) > 2 else 15]:
            print('  ', l)
