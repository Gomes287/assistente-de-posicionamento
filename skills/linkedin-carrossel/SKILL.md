---
name: linkedin-carrossel
description: >-
  Carrossel de LinkedIn em PDF (1080×1350, pronto para subir como documento) com as cores, fonte, foto e identificação
  da pessoa: parte da mesma entrevista do post (experiência → ideia → intenção), escreve 6–10 slides curtos na voz dela,
  confere cacoetes de IA e regras do conselho (CFM para médicos), gera o PDF e uma prévia, e escreve o texto que
  acompanha o carrossel. Use quando pedirem "carrossel para o LinkedIn", "transforma esse artigo/post em carrossel",
  "documento em PDF para o LinkedIn", "slides para o LinkedIn".
---

# Carrossel de LinkedIn

`SK` = a pasta deste SKILL.md. `N=$(cd -P "$SK/../../nucleo" && pwd)` · `PY=python3`. Precisa de Chrome, Edge, Brave ou Chromium.
Antes: `$PY $N/tools/perfil.py checar` (sem perfil → **linkedin-config**). Leia `voz.md`, `notas.md`
(em `~/.config/assistente-de-posicionamento/`), e `$N/referencia/autoria.md`, `anti-ia.md`, `intencao.md`, `formato.md`
(+ `conselhos/cfm.md` se CFM, `conselhos/sigilo.md` se `sigilo`).

## 1. Ideia antes de slide
Faça a entrevista do **linkedin-post**, passo 1 (experiência, ideia em uma frase, ponto de vista, para quem, intenção).
Se já existe a pasta com `ideia.json` (porque começou como post), use a mesma. Senão: `$PY $N/tools/novo.py "<título>"`.
Carrossel combina com `compartilhar` e `amplificar`: conhecimento em passos, contraste, erro comum, lista curta. Se a
ideia for uma opinião que pede conversa, sugira post de texto.

## 2. Roteiro dos slides (`<pasta>/carrossel.json`, tipos em `$N/tools/carrossel.py`)
- **Capa** (`capa`): a ideia como promessa de leitura, até ~8 palavras; `*palavra*` destaca. É o que faz parar no feed.
- **Miolo** (4–8 slides): **uma ideia por slide**, frases curtas, a progressão do caso ao princípio. Varie os tipos:
  `texto`, `lista`, `citacao` (uma frase dela que merece destaque), `numero` (**sempre com fonte**), `contraste`
  (assunto × ideia, antes × depois, mito × fato).
- **Final** (`final`): pergunta específica ou a ideia que fica. Sem "curta e compartilhe".
- `titulo_documento`: o título que o LinkedIn mostra sobre o carrossel (curto, claro, sem clickbait).
- Só o que ela contou; no registro dela (autoria). Slide não é parágrafo: se passou de ~40 palavras, divida.

## 3. Gerar e conferir
`$PY $N/tools/carrossel.py <pasta>` valida (ERRO para: número sem fonte, falta de título do documento, CFM sem
identificação) e avisa cacoetes de IA. Corrija e rode de novo. **Abra `previa.png` e olhe**: texto apertado, slide
vazio demais, quebra feia, destaque no lugar errado. Ajuste o JSON até ficar bom.
Se CFM: a identificação sai no rodapé da capa e do último slide; confira também `cfm.md`.

## 4. Texto que acompanha
Escreva `<pasta>/post.md` curto (o carrossel faz o trabalho): abertura concreta, por que esse carrossel existe, e a
pergunta se a intenção for `conversar`. Rode `$PY $N/tools/checar.py <pasta>/post.md`.

## 5. Entregar
Mostre a prévia, o título do documento e o texto. Passo a passo para ela: no LinkedIn, começar publicação → adicionar
documento → `carrossel.pdf` → título do documento → colar o texto → publicar. A skill não publica.
Depois: `$PY $N/tools/memoria.py registrar <pasta> --link <url>` e, com os números, `memoria.py resultado …`
(ver **linkedin-post**, passo 5).
