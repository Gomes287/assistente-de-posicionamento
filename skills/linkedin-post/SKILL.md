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

`SK` = a pasta deste SKILL.md. `N=$(cd -P "$SK/../../nucleo" && pwd)` · `PY=python3`.
Antes de tudo: `$PY $N/tools/perfil.py checar` (se faltar perfil, use a skill **linkedin-config**). Leia
`~/.config/assistente-de-posicionamento/voz.md`, `~/.config/assistente-de-posicionamento/notas.md` (regras dela, valem acima destas) e
`$N/referencia/autoria.md`, `anti-ia.md`, `intencao.md`, `formato.md`, `estruturas.md`, `padroes-observados.md`. Se `conselho` = CFM: `conselhos/cfm.md`. Se `sigilo` = true: `conselhos/sigilo.md` (sempre).
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
8. **O detalhe que só ela sabe** (lugar, número da experiência dela, frase dita, decisão, o que sentiu). Sem ele,
   não escreva: é o que impede o post de parecer o de outra pessoa (`estruturas.md`).
9. **Ponte:** por que essa experiência importa para o público dela e para o trabalho dela? Experiência sem ponte vira
   crônica; ponte sem experiência vira texto de qualquer um (`padroes-observados.md` §1–2). Grave em `"ponte"`.
10. **Uma ideia só.** Se aparecerem duas (um guia e um agradecimento, um argumento e uma resenha), ofereça dividir em
   dois conteúdos.
11. **Post de aula, livro ou evento:** o centro é o que ELA viveu que conversa com o tema; o agradecimento cabe numa
   linha no fim; resenha tem opinião dela e crédito em qualquer trecho de terceiros. Se ela der nome a um conceito,
   procure o conceito vizinho que já existe e cite.
12. **Estrutura:** escolha no catálogo de `estruturas.md` a que serve à ideia, evitando as dos últimos posts dela
   (`memoria.py resumo` mostra quais foram).

Crie a pasta: `$PY $N/tools/novo.py "<título de trabalho>"` e preencha `<pasta>/ideia.json` com as respostas
(`metrica_principal` coerente com a intenção, `detalhe_unico`, `ponte` e `estrutura` preenchidos).

## 2. Rascunho
Escreva `<pasta>/post.md` (só o texto do post, pronto para colar):
- Siga a **estrutura escolhida** (não o molde de sempre) e use o **detalhe único** de forma visível.
- Abertura concreta que funcione sozinha antes do "…ver mais" (`formato.md`).
- Do caso ao princípio; a ideia dita uma vez; fim que amplia (não resume).
- Só o que ela contou (autoria, regra 2). No registro dela: `voz.md` é teto, não inspiração (regra 3).
- Termine onde a ideia acaba: nada de aforismo em escada, "menos sobre X e mais sobre Y" ou parágrafos espelhados no
  fim (é onde mais aparece o molde). Varie o fim (`estruturas.md`, "Fins"). Pergunta só quando a intenção for `conversar`, e específica, com as
  palavras do assunto (não "em que situação você já viu isso?").
- Use as expressões literais dela (`voz.md`), não as suas.
- Prefira parágrafo a lista: ligue as ideias como ela falaria. Lista com marcador só para itens realmente
  paralelos (passos, critérios), e no máximo uma por texto.
- Hashtags: 0 a 3, se ela costuma usar.

## 3. Conferir
`$PY $N/tools/checar.py <pasta>/post.md`: além dos cacoetes de IA, ele aponta cacoetes da própria skill, ritmo
monótono, detalhe único ausente e trechos ou aberturas repetidos de posts anteriores dela. Corrija todo ERRO e
ATENÇÃO (ou explique a ela por que manter). Depois
releia contra `anti-ia.md` ("conferidos lendo") e, se CFM, a checagem de `cfm.md`. Pergunte-se: tem experiência dela?
Se não tem, volte à entrevista (regra 4).

## 4. Entregar
Mostre: o trecho antes do "ver mais", o post inteiro, a intenção e a métrica que vai dizer se funcionou. Peça para ela
ler em voz alta e mexer à vontade; aplique as mudanças dela. Lembre: **a skill não publica**. Ela cola no LinkedIn.
Depois de publicar: `$PY $N/tools/memoria.py registrar <pasta> --link <url>`.

## Artigo (texto longo do LinkedIn)
Quando a ideia pede mais que um post (argumento com fonte, várias etapas, texto acima de ~3.000 caracteres), ou a
pessoa trouxer um artigo pronto: mesma entrevista, mesmas regras, e `checar.py <pasta>/artigo.md --artigo` (sem o limite de 3.000 caracteres do post). Um artigo
precisa de três coisas além do texto:
1. **Título do artigo** (até ~100 caracteres): claro, com a ideia ou a pergunta central e as palavras que o público
   buscaria. Proponha 3 opções com pesos diferentes (mais direto, mais pergunta, mais provocativo) e deixe ela escolher.
2. **Capa** (1920×1080): `$PY $N/tools/capa.py <pasta> "<título curto com *destaque*>" "<linha de apoio opcional>"`
   (usa a família de layout do perfil; `--tema` troca só nesta capa).
   O título da capa pode ser mais curto que o do artigo (até ~8 palavras: é lido em miniatura). Abra a imagem e confira.
3. **Post de divulgação** (`post.md`): o artigo não se espalha sozinho. Um post curto com a abertura do argumento
   e o convite para ler, conferido com `checar.py`.
Referências do artigo vão no fim do texto, com link quando houver.

## 5. Resultado (2 a 7 dias depois)
Jeito recomendado: no LinkedIn, **Análises de publicação → Exportar** (planilha .xlsx). A pessoa entrega o arquivo e
você roda `$PY $N/tools/memoria.py importar <arquivo.xlsx>`: ele acha cada post pelo link, preenche os números, guarda
uma foto da conta (seguidores, alcance, quem viu o conteúdo) e importa também os posts feitos fora da skill.
- Post registrado sem link → peça o link e `memoria.py vincular <id> <URL>`, depois importe de novo.
- Posts importados sem intenção → pergunte a intenção de cada um (`memoria.py intencao <id> <intencao> [linha]`):
  sem isso, a comparação por intenção não funciona.
- Compare "quem viu o conteúdo" com o público do perfil: está chegando em quem ela quer?
Sem planilha: `memoria.py resultado <pasta> impressoes=… reacoes=… comentarios=… compartilhamentos=…`.
**Não** abra o painel do LinkedIn pelo navegador para ler os números: os termos do LinkedIn proíbem acesso
automatizado e a conta da pessoa pode ser restringida. A exportação é oficial e não tem esse risco.
Leia o resultado **contra a intenção** (métrica sem objetivo é só número), sem desanimar com números baixos no
começo. Pergunte o que ela leva para a próxima decisão e grave com `memoria.py aprendizado`.

## Comentários em posts de outras pessoas
Comentar no nicho costuma render alcance, mas a skill **não escreve comentários** (`autoria.md`). Se ela pedir, ajude
a escolher pessoas e posts para acompanhar e sugira um ângulo a partir do repertório dela; ela escreve.
