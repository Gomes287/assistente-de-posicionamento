---
name: linkedin-config
description: >-
  Configuração do Assistente de posicionamento para LinkedIn (uma vez por pessoa, ou para mudar depois): quem a pessoa é, pelo que quer ser
  lembrada, público, linhas editoriais, voz medida a partir de posts antigos, cores/fonte/foto do carrossel e regras do
  conselho profissional (sigilo para conselheiros e administradores; CFM para médicos). Use quando a pessoa disser "configurar o assistente de posicionamento" ou "configurar o assistente de LinkedIn",
  "mudar minhas cores do carrossel", "atualizar minha voz", "mudar minhas linhas editoriais", ou quando linkedin-post ou
  linkedin-carrossel disserem que falta perfil.
---

# Configuração do Assistente de posicionamento

`SK` = a pasta deste SKILL.md (o Claude Code mostra como "Base directory"). `N=$(cd -P "$SK/../../nucleo" && pwd)` ·
`PY=python3` (3.9+, só biblioteca padrão). Dados da pessoa: `~/.config/assistente-de-posicionamento/` (só no computador dela).
Leia `$N/referencia/autoria.md` antes de começar: ela explica por que a skill pergunta antes de escrever.

**Antes de tudo:** `$PY $N/tools/verificar.py`. Se faltar algo, explique em português simples como resolver
(o próprio script diz) e só siga quando estiver ok. Sem Chrome dá para seguir, avisando que carrossel e capa não vão sair.
Se `python3` não existir: no Mac, rodar `python3` no Terminal oferece instalar as ferramentas; senão, python.org.

Conduza como conversa, em blocos curtos. Não despeje todas as perguntas de uma vez.

## 1. Quem é e para quem fala (uma mensagem)
- Nome como aparece no LinkedIn e o título curto (ex.: "Médica cardiologista · gestão hospitalar").
- Profissão. Se tem **conselho com regras de publicidade**: médico → `conselho: "CFM"` e monte a identificação
  (`MÉDICO · CRM-UF 000000 · Especialidade · RQE 0000`; sem RQE: "MÉDICO com pós-graduação em X · NÃO ESPECIALISTA").
  Pergunte se ela já está no título ou no Sobre do perfil (`identificacao_no_perfil`). Outro conselho (OAB, CRP, CVM…):
  grave o nome e avise que a skill só lembra, não confere (`$N/referencia/conselhos/geral.md`).
- É **conselheira** (de administração, consultivo, fiscal) ou **administradora** com acesso a informação estratégica
  de empresas? Se sim, `sigilo: true` e explique em uma frase: a skill vai alertar sobre deliberações, informação
  ainda não pública e casos que identifiquem a empresa (`$N/referencia/conselhos/sigilo.md`).
- Para quem ela escreve (público específico, não "todo mundo").
- Já publica no LinkedIn ou ainda não? (`situacao`: `ja_publica` | `nao_publica`)

## 2. Posicionamento
"Pelo que você quer ser lembrado(a)?": conhecimento (o que sabe), experiência (o que viveu e aprendeu), visão (como
interpreta o mundo) ou causa (o que defende). Ajude a chegar a **uma frase** de posicionamento. Posicionamento não é o
que ela diz sobre si: é o que as pessoas associam a ela (conhecimento → experiência → visão → relevância).

## 3. Linhas editoriais
Três linhas fixas ligadas ao posicionamento + uma linha `teste` para experimentar. Proponha a partir do que ela contou
e deixe ela ajustar. Ex.: "erro comum que eu vejo", "bastidores do trabalho", "leitura de notícia do setor", "teste".

## 4. Voz
- **Já publica:** peça 5 a 20 posts dela (colar aqui ou arquivo), separados por uma linha `---`. Salve em um arquivo
  e rode `$PY $N/tools/voz.py medir <arquivo>`. Depois leia os posts e escreva `~/.config/assistente-de-posicionamento/voz.md`:
  como ela abre, tamanho e ritmo das frases, vocabulário e expressões que usa, como fecha, o que ela **nunca** faz,
  2–3 trechos curtos que são a cara dela (só trechos neutros, nunca nada pessoal ou de terceiros). Use também as quatro perguntas sobre um post antigo: por que publiquei,
  o que queria provocar, o que aconteceu, o que faria diferente hoje.
- **Ainda não publica:** peça 2–3 textos que ela escreveu **para outras pessoas lerem** (e-mail de trabalho, post em
  outra rede, artigo, mensagem longa explicando algo). Avise antes: nada de diário ou conversa íntima; se vier algo assim,
  use só o que for texto para leitores, diga que não guarda cópia e que nada do conteúdo vai para os posts. Meça a voz
  do mesmo jeito; se não houver nada, escreva `voz.md` a partir de como ela fala nesta conversa e avise que a voz
  fica aproximada. Faça o **garimpo**: 5 a 10 situações que ela viveu, sabe, observa ou pensa, e grave como banco de
  ideias em `~/.config/assistente-de-posicionamento/notas.md` (seção "Banco de ideias").
- Com menos de 5 textos, diga claramente que a voz ficará aproximada.

## 5. Visual do carrossel
Cores: hex, ou uma imagem dela (logo, banner, print do perfil) → `$PY $N/tools/cores.py <imagem>` sugere `fundo`,
`texto`, `acento` e `suave`; **olhe a imagem** e ajuste a sugestão (cor pequena e marcante, como a de um destaque, às
vezes some na contagem). Sem resposta: paleta padrão.
Confira contraste texto/fundo. Fonte do título: `Inter` (padrão, limpa), `Playfair` (elegante, serifada) ou `Anton`
(condensada, caixa alta). Foto: caminho de uma foto de rosto (opcional; sem foto, usa as iniciais).
Pasta onde salvar os conteúdos (`pasta_saida`, padrão `~/Documents/LinkedIn`).

## 6. Gravar e mostrar
`$PY $N/tools/perfil.py definir '<json>'` com tudo acima (chaves em `$N/tools/comum.py`, `PERFIL_PADRAO`).
Depois `$PY $N/tools/carrossel.py --demo ./previa_carrossel.png` e **mostre a imagem**: "é assim que seus
carrosséis vão ficar; quer mudar cor, fonte ou foto?". Precisa de Chrome/Edge/Brave instalado.
Termine com `$PY $N/tools/perfil.py checar` e diga que, a partir de agora, é só pedir "post sobre…" ou
"carrossel sobre…".

## Regras da pessoa
Correções que ela der sobre o jeito de escrever ou de trabalhar vão em `~/.config/assistente-de-posicionamento/notas.md`, com
data e o porquê. As skills de post e carrossel leem esse arquivo antes de tudo.
