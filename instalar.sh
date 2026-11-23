#!/bin/bash
# Instala (ou atualiza) o Assistente de posicionamento para o Claude Code / app do Claude, sem precisar de git.
# uso: curl -fsSL https://raw.githubusercontent.com/Gomes287/assistente-de-posicionamento/main/instalar.sh | bash
set -e
REPO="Gomes287/assistente-de-posicionamento"
DEST="$HOME/.claude/assistente-de-posicionamento"
SKILLS="$HOME/.claude/skills"
TMP="$(mktemp -d)"

echo "Baixando o Assistente de posicionamento…"
curl -fsSL "https://github.com/$REPO/archive/refs/heads/main.zip" -o "$TMP/a.zip"
unzip -q "$TMP/a.zip" -d "$TMP"
rm -rf "$DEST"; mkdir -p "$(dirname "$DEST")"
mv "$TMP/assistente-de-posicionamento-main" "$DEST"
rm -rf "$TMP"

mkdir -p "$SKILLS"
for s in linkedin-config linkedin-post linkedin-carrossel; do
  rm -rf "$SKILLS/$s"
  ln -s "$DEST/skills/$s" "$SKILLS/$s"
done
echo "Instalado em $DEST"
echo

if command -v python3 >/dev/null 2>&1; then
  python3 "$DEST/nucleo/tools/verificar.py" || true
else
  echo "Falta o Python 3. No Mac, rode 'python3' no Terminal e aceite instalar as ferramentas de desenvolvedor,"
  echo "ou baixe em python.org/downloads. Depois rode este instalador de novo."
fi
echo
echo "Agora abra o Claude (aba Code) e diga: configurar meu assistente de posicionamento"
