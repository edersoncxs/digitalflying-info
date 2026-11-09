# DigitalFlyingInfo

Informações da Digital Flying lidas por **todos os apps** (contatos, PIX de contribuição, chamada comercial).

- Publicar este arquivo num repositório **público** do GitHub: `edersoncxs/digitalflying-info`, branch `main`.
- Os apps buscam, nesta ordem:
  1. `https://digitalflying.com.br/app/info/digitalflying.json` (quando o domínio estiver no ar)
  2. `https://raw.githubusercontent.com/edersoncxs/digitalflying-info/main/digitalflying.json`
  3. última versão salva no computador
  4. versão embutida no app (cópia em `Delivery/src-tauri/recursos/digitalflying.json`)
- Para mudar um contato ou a chave PIX: editar o JSON no GitHub (e no domínio, se houver). Cada instalação atualiza sozinha ao abrir.
- `{app}` nos textos é trocado pelo nome do app.
- Manter o campo `versao` em 1 enquanto o formato não mudar.

## Mensagens dos apps para a Digital Flying

- Desde 2026-11-07 **sem serviços de terceiros**: o botão "Mensagem" dos apps envia direto para o Telegram da Digital (bot com token/chat definidos na compilação do app). WhatsApp e e-mail ficam só como links (`wa.me` e `mailto:`) com a mensagem pronta, além de copiar número/endereço.
- O campo `envio` (Web3Forms) foi removido do JSON; apps antigos que ainda o lêem simplesmente o ignoram.

## Conteúdo de exemplo (`exemplos/`)

- `exemplos/delivery/<chave>.jpg`: fotos do cardápio de exemplo do DF Delivery (botão "Instalar conteúdo de exemplo" no app). Licença livre (CC0/domínio público) — créditos em `exemplos/delivery/CREDITOS.md`.
- Cópia de referência: as fotos vão **embutidas no app** (`Delivery/src-tauri/recursos/exemplo/`); para trocar, substitua lá e aqui mantendo o nome (a chave).

## Obsoleto

- `servidor/contato.php`: endpoint de e-mail próprio, pensado para substituir o Web3Forms. Não é mais usado (as mensagens vão pelo Telegram). Pode ser apagado.

## Atualizações dos apps (`atualizacoes`)

- `atualizacoes.delivery`: `{ versao, data, notas[], linux, windows, pagina, importante }`. Os apps consultam este arquivo ao abrir e a cada 6 h; se `versao` for maior que a instalada, avisam no Início e em Sobre com as notas e o "como atualizar".
- **Downloads com nome fixo** nas Releases deste repositório: `df-delivery_amd64.deb` (Ubuntu/Debian), `df-delivery.x86_64.rpm` (Fedora/openSUSE, em teste) e `df-delivery_x64-setup.exe` (Windows).
- **Site oficial do DF Delivery:** https://dfdelivery.netlify.app/ (Netlify, projeto `dfdelivery`). O link `.../releases/latest/download/<arquivo>` sempre aponta para a versão mais nova.
- **Publicar uma versão nova:** (1) criar a Release `vX.Y.Z` com os três arquivos (mesmos nomes); (2) só depois mudar `versao`, `data` e `notas` aqui.
- **Testar o aviso sem publicar:** abrir o app com `DF_INFO_FONTE=<url de um JSON de teste>`.
