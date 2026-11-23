# Como instalar (sem precisar saber programação)

## O que você precisa
1. **App do Claude no computador**, com um plano que inclua o Claude Code (Pro ou Max). Baixe em
   [claude.com/download](https://claude.com/download) e entre com a sua conta.
2. **Google Chrome** instalado (é com ele que a skill gera o PDF do carrossel e as capas).
3. **Python 3** (no Mac, o próprio instalador avisa se faltar e diz como resolver).

Funciona no Mac. No Windows, use o caminho B (ainda não testado a fundo).

## Caminho A: pelo app do Claude (recomendado)
1. Abra o app do Claude e vá na aba **Code**.
2. Escolha qualquer pasta para trabalhar (por exemplo, Documentos).
3. Cole esta mensagem e envie:

   > Instale o Assistente de posicionamento rodando este comando no terminal:
   > `curl -fsSL https://raw.githubusercontent.com/Gomes287/assistente-de-posicionamento/main/instalar.sh | bash`

4. O Claude vai pedir permissão para rodar o comando. Aceite. No fim aparece uma lista com ✔ (o que está ok)
   e ✘ (o que falta, com a explicação de como resolver).
5. Comece uma conversa nova e diga: **"configurar meu assistente de posicionamento"**.

Para atualizar depois, repita o passo 3.

## Caminho com o zip (quando alguém te mandou o arquivo)
1. Abra o app do Claude e vá na aba **Code**. O Cowork e o chat do navegador não servem: lá a skill não guarda sua voz entre conversas.
2. Arraste o zip `assistente-de-posicionamento-<versão>.zip` para a conversa, ou deixe ele na pasta Downloads, e envie:

   > Instale o assistente de posicionamento deste zip: descompacte, leia o LEIA-ME.md e rode o instalador.

3. Aceite quando o Claude pedir permissão e siga a partir do passo 4 do caminho A.

Não precisa de internet nem de GitHub. Para atualizar, faça o mesmo com o zip novo: seus dados não são apagados.
(Para quem distribui: `bash empacotar.sh` gera o zip na Área de Trabalho a partir do último commit.)

## Caminho B: se você já usa o Claude Code no terminal
```
/plugin marketplace add Gomes287/assistente-de-posicionamento
/plugin install assistente-de-posicionamento@assistente-de-posicionamento
```

## Seus dados
Tudo fica no seu computador, na pasta `~/.config/assistente-de-posicionamento/` (perfil, voz, banco de ideias e
histórico). Nada é enviado para lugar nenhum pela skill, e ela nunca publica nada: quem publica é você.

## Desinstalar
Apague as pastas `~/.claude/assistente-de-posicionamento` e `~/.claude/skills/linkedin-*` (e, se quiser apagar seus
dados, `~/.config/assistente-de-posicionamento`).
