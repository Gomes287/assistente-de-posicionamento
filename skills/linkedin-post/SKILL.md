---
name: linkedin-post
description: >-
  Post de LinkedIn em português com a voz da própria pessoa e sem cara de IA: começa por uma entrevista curta (da
  experiência à ideia, e da ideia à intenção), escreve o rascunho respeitando regras de autoria, confere cacoetes de IA,
  a voz medida e as regras do conselho profissional (CFM para médicos), e depois registra o que aconteceu para aprender
  com os números. Use quando pedirem "post para o LinkedIn", "escreve um post sobre…", "transforma isso num post",
  "o que eu posto essa semana?", "não sei sobre o que postar", ou quando trouxerem os números de um post publicado.
---

# Post de LinkedIn: da experiência à publicação

`SK` = a pasta deste SKILL.md. `N="$SK/../../nucleo"` · `PY=python3`.
Antes de tudo: `$PY $N/tools/perfil.py checar` (se faltar perfil, use a skill **linkedin-config**). Leia
`~/.config/assistente-linkedin/voz.md`, `~/.config/assistente-linkedin/notas.md` (regras dela, valem acima destas) e
`$N/referencia/autoria.md`, `anti-ia.md`, `intencao.md`, `formato.md`. Se `conselho` = CFM: `conselhos/cfm.md`.
`$PY $N/tools/memoria.py resumo` mostra o que já foi publicado (não repita ideia; veja que linha está sem post).

## 1. Entrevista (antes de escrever qualquer coisa)
Converse, uma ou duas perguntas por vez (`intencao.md` §1). Se ela já trouxe um texto, artigo ou anotação, extraia
dele e pergunte só o que faltar.
1. **Experiência:** que situação viveu, percebeu, aprendeu? Se ela trouxe só um tema, peça uma situação concreta ligada
   a ele. Se não tiver nenhuma, ofereça o banco de ideias (`notas.md`) ou uma das linhas editoriais.
2. **O que percebeu** e a **segunda leitura** ("mas será que era isso mesmo?").
3. **A ideia em uma frase:** o que alguém deve levar daqui. Se só houver assunto, devolva "e daí?". Sem essa frase,
   não escreva.
4. **Ponto de vista:** o que ela pensa / aprendeu / vê que outros não veem. Se precisa de uma posição e ela não deu,
   pergunte (autoria, regra 1).
5. **Para quem** e **intenção** (`amplificar`, `compartilhar`, `conversar`, `posicionar`): o que quer provocar?
6. **Formato:** proponha pelo quadro de `intencao.md` §3 e diga por quê. Carrossel → skill **linkedin-carrossel**
   (mesma pasta e mesmo ideia.json).
7. Fontes de todo número.

Crie a pasta: `$PY $N/tools/novo.py "<título de trabalho>"` e preencha `<pasta>/ideia.json` com as respostas
(`metrica_principal` coerente com a intenção).

## 2. Rascunho
Escreva `<pasta>/post.md` (só o texto do post, pronto para colar):
- Abertura concreta que funcione sozinha antes do "…ver mais" (`formato.md`).
- Do caso ao princípio; a ideia dita uma vez; fim que amplia (não resume).
- Só o que ela contou (autoria, regra 2). No registro dela: `voz.md` é teto, não inspiração (regra 3).
- `conversar`: termine com uma pergunta específica, de preferência pedindo a experiência do leitor.
- Hashtags: 0 a 3, se ela costuma usar.

## 3. Conferir
`$PY $N/tools/checar.py <pasta>/post.md`. Corrija todo ERRO e ATENÇÃO (ou explique a ela por que manter). Depois
releia contra `anti-ia.md` ("conferidos lendo") e, se CFM, a checagem de `cfm.md`. Pergunte-se: tem experiência dela?
Se não tem, volte à entrevista (regra 4).

## 4. Entregar
Mostre: o trecho antes do "ver mais", o post inteiro, a intenção e a métrica que vai dizer se funcionou. Peça para ela
ler em voz alta e mexer à vontade; aplique as mudanças dela. Lembre: **a skill não publica**. Ela cola no LinkedIn.
Depois de publicar: `$PY $N/tools/memoria.py registrar <pasta> --link <url>`.

## 5. Resultado (quando ela trouxer os números, ~48 h ou 7 dias depois)
`$PY $N/tools/memoria.py resultado <pasta> impressoes=… reacoes=… comentarios=… compartilhamentos=… [salvamentos=…
seguidores=… visitas_perfil=…]`. Leia o resultado **contra a intenção** (métrica sem objetivo é só número), sem
desanimar com números baixos no começo. Pergunte o que ela leva para a próxima decisão e grave com
`memoria.py aprendizado`.

## Comentários em posts de outras pessoas
Comentar no nicho costuma render alcance, mas a skill **não escreve comentários** (`autoria.md`). Se ela pedir, ajude
a escolher pessoas e posts para acompanhar e sugira um ângulo a partir do repertório dela; ela escreve.
