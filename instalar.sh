#!/bin/bash
# Instala (ou atualiza) o Assistente de posicionamento para o Claude Code / app do Claude, sem precisar de git.
# Duas formas:
#   pelo zip:      descompacte e rode  bash instalar.sh  de dentro da pasta (não precisa de internet)
#   pela internet: curl -fsSL https://raw.githubusercontent.com/Gomes287/assistente-de-posicionamento/main/instalar.sh | bash
# Seus dados (perfil, voz, histórico) ficam em ~/.config/assistente-de-posicionamento e nunca são apagados aqui.
set -e
REPO="Gomes287/assistente-de-posicionamento"
DEST="$HOME/.claude/assistente-de-posicionamento"
SKILLS="$HOME/.claude/skills"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# rodando de dentro de uma pasta descompactada? (no "curl | bash" não existe pasta de origem)
ORIGEM=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
  if [ -d "$AQUI/skills/linkedin-post" ] && [ -d "$AQUI/nucleo/tools" ]; then ORIGEM="$AQUI"; fi
fi

if [ -n "$ORIGEM" ]; then
  if [ "$ORIGEM" = "$(cd "$DEST" 2>/dev/null && pwd -P)" ]; then
    echo "Esta já é a pasta instalada. Rode o instalador de dentro da pasta do zip."; exit 1
  fi
  echo "Instalando a partir de $ORIGEM…"
  mkdir -p "$TMP/novo"
  cp -R "$ORIGEM/." "$TMP/novo/"
else
  echo "Baixando o Assistente de posicionamento…"
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/main.zip" -o "$TMP/a.zip"
  unzip -q "$TMP/a.zip" -d "$TMP"
  mv "$TMP/assistente-de-posicionamento-main" "$TMP/novo"
fi

rm -rf "$DEST"; mkdir -p "$(dirname "$DEST")"
mv "$TMP/novo" "$DEST"
find "$DEST" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true

mkdir -p "$SKILLS"
for s in linkedin-config linkedin-post linkedin-carrossel; do
  rm -rf "$SKILLS/$s"
  ln -s "$DEST/skills/$s" "$SKILLS/$s"
done
VERSAO="$(grep -o '"version": *"[^"]*"' "$DEST/.claude-plugin/plugin.json" 2>/dev/null | grep -o '[0-9][0-9.]*' || true)"
echo "Instalado em $DEST${VERSAO:+ (versão $VERSAO)}"
echo

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(sys.version_info < (3, 9))' 2>/dev/null; then PY="$c"; break; fi
done
if [ -n "$PY" ]; then
  "$PY" "$DEST/nucleo/tools/verificar.py" || true
else
  echo "Falta o Python 3 (3.9 ou mais novo). No Mac, rode 'python3' no Terminal e aceite instalar as ferramentas de"
  echo "desenvolvedor, ou baixe em python.org/downloads. Depois rode este instalador de novo."
fi
echo
if [ -f "$HOME/.config/assistente-de-posicionamento/perfil.json" ]; then
  echo "Seu perfil e sua voz continuam lá. Comece uma conversa nova no Claude e peça um post."
else
  echo "Agora comece uma conversa nova no Claude (aba Code) e diga: configurar meu assistente de posicionamento"
fi
