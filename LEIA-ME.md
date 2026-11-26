# Assistente de posicionamento: como instalar pelo zip

## Para você
1. Abra o app do Claude no computador e vá na aba **Code**. O Cowork e o chat do navegador não servem: lá a skill não guarda sua voz entre conversas.
2. Arraste este zip para a conversa, ou deixe ele na pasta Downloads, e envie:

   > Instale o assistente de posicionamento deste zip: descompacte, leia o LEIA-ME.md e rode o instalador.

3. Aceite quando o Claude pedir permissão. No fim aparece uma lista com ✔ (ok) e ✘ (o que falta, com a explicação).
4. Comece uma conversa nova e diga: **"configurar meu assistente de posicionamento"**.

## Antes de configurar, separe
A configuração é uma conversa de uns 20 a 30 minutos, feita uma vez só. Ela fica melhor se você tiver à mão:
- **Textos seus.** Se já publica no LinkedIn, de 5 a 20 posts antigos. Se não publica, 2 ou 3 textos que você
  escreveu para outras pessoas lerem (e-mail de trabalho, post em outra rede, artigo). Nada de diário ou conversa
  íntima. É deles que sai a sua voz.
- **Logo ou print do banner** do seu LinkedIn, para as cores. Sem identidade visual, você escolhe entre três paletas.
- **Uma foto de rosto**, para a capa dos carrosséis (opcional).
- **Se for médico:** CRM, UF e RQE.

## Painel
O instalador deixa na Área de Trabalho o atalho **Painel do LinkedIn** (Mac). Dois cliques abrem no navegador o
que está pendente (colar o link do post, enviar a planilha do LinkedIn), o que você já publicou com os números,
ideias para o próximo post e a sua voz. O painel roda só no seu computador. Para escrever, os botões copiam o pedido
para você colar na conversa com o Claude. Também dá para pedir ao Claude: "abre meu painel".

## Usar
Depois disso, é só pedir numa conversa nova: "quero um post sobre…", "não sei o que postar essa semana" ou
"carrossel sobre…". O Claude reconhece o pedido e usa a skill sozinho; se não usar, digite `/` na caixa de
mensagem e escolha `linkedin-post` (ou `linkedin-carrossel`, `linkedin-config`). De 2 a 7 dias depois de publicar, exporte a planilha em Análises de publicação → Exportar e
entregue à skill para ver o resultado.

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
