#!/bin/bash
# Gera o zip para entregar a quem vai instalar sem GitHub (só o que a skill precisa; sem docs/ e exemplo/).
# uso: bash empacotar.sh [pasta_de_saida]   → assistente-de-posicionamento-<versão>.zip
set -e
cd "$(dirname "$0")"
SAIDA="${1:-$HOME/Desktop}"
V="$(grep -o '"version": *"[^"]*"' .claude-plugin/plugin.json | grep -o '[0-9][0-9.]*')"
Z="$SAIDA/assistente-de-posicionamento-$V.zip"
[ -n "$(git status --porcelain)" ] && echo "Aviso: há mudanças não commitadas; o zip usa o último commit."
mkdir -p "$SAIDA"; rm -f "$Z"
git archive --format=zip --prefix=assistente-de-posicionamento/ -o "$Z" HEAD \
  .claude-plugin nucleo skills instalar.sh LEIA-ME.md README.md LICENSE
echo "$Z ($(du -h "$Z" | cut -f1))"
