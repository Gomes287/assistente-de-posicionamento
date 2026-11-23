# Assistente de posicionamento: como instalar pelo zip

## Para você
1. Abra o app do Claude no computador e vá na aba **Code** (ou use o Cowork).
2. Arraste este zip para a conversa, ou deixe ele na pasta Downloads, e envie:

   > Instale o assistente de posicionamento deste zip: descompacte, leia o LEIA-ME.md e rode o instalador.

3. Aceite quando o Claude pedir permissão. No fim aparece uma lista com ✔ (ok) e ✘ (o que falta, com a explicação).
4. Comece uma conversa nova e diga: **"configurar meu assistente de posicionamento"**.

Para atualizar, faça o mesmo com o zip novo. Seu perfil, sua voz e seu histórico não são apagados: ficam no seu
computador, em `~/.config/assistente-de-posicionamento/`, e a skill nunca publica nada nem envia seus dados.

## Para o Claude
Descompacte o zip numa pasta temporária e rode, a partir da pasta descompactada que contém este arquivo:

```
bash instalar.sh
```

O instalador copia a skill para `~/.claude/assistente-de-posicionamento`, cria os atalhos das três skills em
`~/.claude/skills/` (linkedin-config, linkedin-post, linkedin-carrossel) e confere Python 3.9+ e Chrome. Não precisa
de internet e não mexe em `~/.config/assistente-de-posicionamento/`. Mostre à pessoa o resultado da conferência e, se
houver ✘, explique em português simples como resolver. Depois diga a ela para abrir uma conversa nova (as skills só
aparecem numa sessão nova) e pedir "configurar meu assistente de posicionamento". Se o plugin
`assistente-de-posicionamento` também estiver instalado pelo menu de plugins, avise que as skills vão aparecer em
dobro e que basta manter um dos dois.
