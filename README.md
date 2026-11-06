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

## Envio de mensagens (`envio`)

- `envio.email`: endereço que recebe o formulário de contato dos apps e entrega no e-mail da Digital Flying. Hoje: FormSubmit (gratuito, sem senha no app).
  - Na **primeira** mensagem, o FormSubmit manda um e-mail de ativação para `ederson.cxs@gmail.com`: clicar em "Activate Form". Depois disso as mensagens chegam direto.
  - Depois de ativar, o FormSubmit mostra um endereço "aleatório" (ex.: `https://formsubmit.co/ajax/abc123...`): pode trocar aqui para não expor o e-mail no link.
  - Para usar outro serviço (ou um endpoint próprio em digitalflying.com.br), é só trocar a URL aqui.
