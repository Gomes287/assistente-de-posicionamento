# Estruturas de post (para não ficar tudo igual)

Mil pessoas usando o mesmo molde viram um padrão reconhecível, mesmo com conteúdos diferentes. Escolha a estrutura
**depois** da ideia, pela ideia, e evite repetir as que a pessoa usou nos últimos posts (`memoria.py resumo` mostra).
Grave a escolhida em `ideia.json` → `"estrutura"`. Os nomes abaixo são os valores aceitos.

| estrutura | como funciona | serve bem para |
|---|---|---|
| `cena` | abre no meio de uma situação ("Sexta, 18h, a reunião já tinha passado da hora…") e só depois diz o que ela ensinou | posicionar, conversar |
| `numero` | abre com um número que surpreende (com fonte) e explica por que ele importa | amplificar, compartilhar |
| `confissao` | abre admitindo um erro ou uma crença antiga ("Durante anos eu achei que…") | posicionar, conversar |
| `contraintuitivo` | afirma algo que vai contra o senso comum do público e sustenta com o caso | amplificar, conversar |
| `pergunta` | abre com a pergunta que a pessoa se fez (não "você já parou para pensar") e mostra como respondeu | conversar |
| `antes_depois` | como ela fazia/pensava, o que aconteceu, como faz/pensa hoje | posicionar, compartilhar |
| `lista_curta` | 3 a 5 itens concretos tirados da experiência dela, cada um com um exemplo | compartilhar |
| `carta` | escrito para uma pessoa ou um cargo ("Para quem vai sentar num conselho pela primeira vez") | posicionar, compartilhar |
| `dialogo` | reconstrói uma conversa curta (sem identificar ninguém) e comenta | conversar, posicionar |
| `bastidor` | mostra como ela trabalha: método, ferramenta, rotina, decisão | posicionar, compartilhar |
| `leitura` | parte de uma notícia, relatório ou livro (com fonte) e dá a leitura dela | posicionar, amplificar |

## Fins (varie também)
Nem todo post termina em pergunta. Alterne entre: uma implicação prática, uma pergunta específica (quando a intenção é
`conversar`), uma frase que abre outro ângulo, um convite concreto (ler o artigo, ver o carrossel), ou simplesmente
parar quando a ideia acabou.

## O detalhe que só ela sabe
Todo conteúdo precisa de pelo menos um detalhe concreto que só a pessoa conhece: um lugar, um número da própria
experiência, uma frase que alguém disse, a decisão que ela tomou, o que ela sentiu. Grave em `ideia.json` →
`"detalhe_unico"`. Sem ele, não escreva: é o que torna o post impossível de confundir com o de outra pessoa.
`checar.py` confere se o detalhe aparece no texto.

**A palavra que o modelo não previa.** Texto humano usa 2,4 vezes mais palavras fora das cem que um modelo de
linguagem esperaria naquele ponto (GLTR, Gehrmann et al. 2019); o texto gerado escolhe sempre a palavra mais provável.
Ao escrever, confira cada parágrafo: tem pelo menos uma palavra, número, nome ou expressão dela que você (o modelo)
**não** teria escolhido sozinho? Se o parágrafo inteiro é o que você escreveria para qualquer pessoa, troque uma
abstração pelo concreto que ela contou ("um colchão enorme de recursos", "o painel da UTI"), ou corte o parágrafo.
Não invente esse detalhe: se não houver, pergunte a ela.
