# Texto sem cara de IA

Leitores de LinkedIn reconhecem texto de IA e rejeitam ("people can tell"). Estes padrões denunciam. `checar.py`
detecta os que dá para detectar; os outros você confere lendo.

## Detectados por `checar.py`
- **Oposição fabricada em série:** "não é X, é Y", "não se trata de X, mas de Y", "mais do que X, é Y". Uma vez pode;
  duas já é cacoete.
- **Clichês:** "vivemos em um mundo", "nunca foi tão importante", "na era digital", "o futuro já chegou",
  "pensar fora da caixa", "novo paradigma", "cada vez mais", "nos dias de hoje", "precisamos refletir".
- **Transições mecânicas:** "nesse contexto", "diante desse cenário", "vale ressaltar", "é importante destacar",
  "em suma", "dito isso", "além disso" em toda frase.
- **Vocabulário de IA/corporativês:** jornada, alavancar, potencializar, desbloquear, mergulhar, navegar (em sentido
  figurado), sinergia, ecossistema, robusto, disruptivo, game changer, insights valiosos.
- **Aberturas e fechos genéricos:** "Você já parou para pensar…", "E você, o que acha?", "Concorda?",
  "Deixe nos comentários". A pergunta final, se houver, é específica e só ela poderia fazer.
- **Travessões em excesso** (—) e **emojis como marcadores** de lista.
- **Tríades em série:** "X, Y e Z." repetido para dar ritmo.
- **Frases paralelas em série:** "Planos mostram intenção. Recursos mostram possibilidade." (mesmo molde, frase atrás de frase).
- **Parágrafos simétricos:** todos com o mesmo tamanho, como se saíssem do mesmo molde.
- **Hashtags demais** (mais de 3–5).

## Detectados desde a leitura de sete textos reais (`padroes-observados.md`)
- **Frases que anunciam** o próximo parágrafo ("merece destaque:", "há uma pergunta que…", "é simples:") e muitas
  linhas terminando em dois-pontos.
- **Começos (ou finais) iguais em série:** "Não controlamos… Não controlamos…", "Se…, Se…, Se…", "Governos mudam.
  Regras mudam."
- **Oposição dividida em duas frases** ("não é X. É Y.") e **"não apenas…, mas também…"**, "menos sobre X e mais sobre Y".
- **Enumerações de 4+ itens** repetidas, e **listas com marcador** onde um parágrafo bastaria: enumerar tudo em
  tópicos é uma das marcas mais fortes de texto gerado. Lista só quando os itens são mesmo paralelos e independentes
  (passos, critérios); o resto vira parágrafo, com as ideias ligadas.
- **Cautela em excesso** ("pode", "talvez" em quase toda frase).
- **Intertítulos Em Maiúscula Em Cada Palavra** e **marcação em massa** de pessoas.
- **O fim acumulando recursos de efeito.**

## Comparados com a voz da pessoa (literatura de detecção)
As revisões de Wu et al. (2025, *Computational Linguistics*) e Yang et al. (2024, *Findings of EMNLP*) resumem o que
separa texto gerado de texto humano: mais longo, mais voz passiva, menos pontuação expressiva, mais formal e menos
emotivo, com vocabulário diferente do de quem fala. `checar.py` mede três desses sinais e só compara com a voz da
própria pessoa, nunca com número fixo (os estudos são em inglês e em textos longos; post em português é outro mundo):
- **Voz passiva** ("foi decidido", "são observados") bem acima da dela: diga quem fez.
- **Pontuação "limpa" demais** (menos ?, !, parênteses e reticências que ela usa): o texto perdeu a fala.
- **Vocabulário** muito mais rebuscado ou muito mais repetitivo que o dela (MTLD, McCarthy e Jarvis 2010). No nosso
  caso real, o texto escrito com IA tinha vocabulário **mais** variado que o do autor, não menos: o sinal vale nos
  dois sentidos.

## Mostrar no texto, não só listar
`checar.py` devolve o **texto marcado** (trecho em negrito e número do motivo) e, com `--html`, uma `revisao.html`
colorida. No GLTR (Gehrmann, Strobelt e Rush, 2019), ver os trechos marcados no texto levou leitores de 54% para 72%
de acerto, sem treino. A pessoa aprende a ver o padrão sozinha, que é o objetivo.

## Por que isto não é um "detector de IA"
Sadasivan et al. (2023–2025) mostram que paráfrase derruba qualquer detector de autoria e que, quanto mais o modelo
imita a escrita humana, mais o melhor detector possível se aproxima do acaso. Os detectores também erram mais em texto
curto, fora do inglês e de quem escreve fora do padrão. O verificador não tenta dizer quem escreveu: aponta o que
faz o **leitor** desconfiar. Nunca diga à pessoa (nem sobre texto de outra) que "foi IA".

## Cacoetes da própria skill
Ao fugir dos vícios clássicos, a skill cria os dela ("Repara que…", "Em que situação você já viu…?", "e é aí que…").
Com mil pessoas usando, isso vira uma assinatura reconhecível. `checar.py` tem a lista (`CACOETES_SKILL`); quando
aparecer um novo, acrescente. Se a expressão estiver em `voz.md`, é da pessoa e pode ficar.

## Conferidos lendo
- Frase de efeito no fim de cada parágrafo.
- Resumo no final repetindo o que já foi dito (o fim deve ampliar, não resumir).
- Parágrafo que só reformula o anterior.
- Autoridade afirmada ("sem dúvida", "todos sabem") em vez de construída pelo raciocínio.
- Abstração sem objeto concreto; explicar o óbvio para o público dela.
- Texto neutro demais, escondendo a posição dela.

## O que preservar
O ritmo dela (frases curtas e médias como ela usa), a passagem do caso ao princípio, as expressões que ela realmente
usa. Uma irregularidade escolhida pela pessoa fica; erro de digitação não é estilo.
