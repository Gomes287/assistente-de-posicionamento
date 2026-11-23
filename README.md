# assistente-linkedin

Assistente de publicação no LinkedIn para o [Claude Code](https://claude.com/claude-code), em português. Ele não
fabrica posts: ajuda você a sair da **experiência** para a **ideia**, escolher a **intenção**, escrever com a **sua
voz**, sem cara de IA, e aprender com os números do que você publicou.

## O que ele faz
- **Entrevista antes de escrever.** Começa pelo que você viveu, sabe, observa e pensa, e só escreve quando existe uma
  ideia em uma frase ("o que eu quero que alguém leve daqui?"). Assunto não é ideia.
- **Intenção antes de formato.** Ampliar alcance, compartilhar conhecimento, gerar conversa ou reforçar posicionamento.
  A intenção escolhe o formato e a métrica que vai dizer se funcionou.
- **Sua voz, medida.** Lê seus posts antigos e mede tamanho de frase, ritmo, emojis e primeira pessoa. O texto novo
  não pode ficar "mais sofisticado do que você fala".
- **Sem cara de IA.** Um conferidor aponta os cacoetes que leitores reconhecem: "não é X, é Y" em série, clichês,
  transições mecânicas, tríades, emojis como marcadores, travessões, fecho "e você, o que acha?".
- **Regras de autoria.** Nenhuma opinião que você não deu, nenhuma experiência inventada, e um aviso quando o texto
  não tem nada seu. A skill não escreve comentários e não publica nada.
- **Carrossel em PDF** (1080×1350) com suas cores, fonte, foto e identificação, pronto para subir como documento.
- **Memória editorial.** Registra o que foi publicado, com que intenção, os números (lidos da planilha que o próprio
  LinkedIn exporta, sem digitar nada) e o que você aprendeu. O resultado
  é lido contra a intenção, porque métrica sem objetivo é só número.
- **Módulo CFM para médicos.** Confere a identificação, promessa de resultado, autopromoção, sensacionalismo e oferta
  de consulta (Res. CFM 2.336/2023 e 2.454/2026).

## As três skills
| skill | quando |
|---|---|
| `linkedin-config` | uma vez: quem você é, posicionamento, público, linhas editoriais, voz, cores e fonte |
| `linkedin-post` | "post sobre…", "não sei o que postar", "trouxe os números do post" |
| `linkedin-carrossel` | "carrossel sobre…", "transforma esse artigo em carrossel" |

## Requisitos
Claude Code, Python 3.9+ e Google Chrome (ou Edge, Brave, Chromium) para gerar o PDF do carrossel.

## Instalar
```
/plugin marketplace add Gomes287/assistente-linkedin
/plugin install assistente-linkedin@assistente-linkedin
```
Depois diga *"configurar meu assistente de LinkedIn"*. Seus dados ficam só no seu computador, em
`~/.config/assistente-linkedin/`.

## Exemplo
`exemplo/` tem o resultado de um teste: `ideia.json` (a entrevista), `post.md` e `carrossel.json`.

## Créditos e limites
- Este projeto não tem ligação com o LinkedIn.
- As regras do CFM são uma checagem de apoio, não parecer jurídico. Outras profissões com regras próprias (OAB, CRP,
  CVM…) ainda não têm módulo.
- Código: MIT, © 2026 Pedro Gomes. Fontes em `nucleo/fontes/`: SIL Open Font License 1.1.
