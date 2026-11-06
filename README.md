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

- `envio.email`: serviço que recebe o formulário de contato dos apps e entrega no e-mail da Digital Flying. O app não guarda senha de e-mail.
- Atual: **Web3Forms** (`https://api.web3forms.com/submit`, gratuito). `envio.chave` = "Access Key" criada em https://web3forms.com com o e-mail ederson.cxs@gmail.com (a chave é pública por natureza: feita para ficar em sites/apps).
- O FormSubmit foi descartado em 2026-11-06: não respondia a partir da rede do desenvolvedor.
- Para trocar de serviço (ou usar um endpoint próprio em digitalflying.com.br), basta mudar estes campos.
