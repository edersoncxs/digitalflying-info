# Testes dos instaladores

A suíte usa somente os instaladores publicados e a interface do aplicativo, em máquinas descartáveis do GitHub Actions. Não depende do código-fonte do produto.

## Cenários

- Abertura da primeira execução, com print.
- Nome da loja vazio e somente com espaços; WhatsApp inválido.
- Nome, login e senha do dono vazios; login inválido e confirmação divergente.
- Integração inválida e integrações opcionais vazias.
- Conclusão com dados fictícios e print da tela Início.
- Criação de categoria; produto sem nome/preço; criação e edição válidas.
- Encerrar e reabrir o aplicativo, conferindo persistência do produto e preço.
- Prints das validações, produtos e eventuais falhas; relatório JSON por ambiente.

Campos opcionais permanecem opcionais. Estes testes não definem novos requisitos de preenchimento.

## Execução

Actions → Testes dos instaladores → Run workflow. Informe uma tag publicada (ex.: v1.0.2), ou deixe vazia para resolver a mais recente uma única vez. Todos os ambientes usam a mesma Release. Uma nova Release publicada também dispara a rotina.

Windows usa o Microsoft Edge WebDriver correspondente ao WebView2 instalado. Linux usa WebKitWebDriver e Xvfb; no Fedora o executável do controlador é distribuído em webkitgtk6.0. O app continua usando suas bibliotecas originais.

Os sete ambientes são Windows, Ubuntu 22.04 e 24.04, Mint 21.3 e 22, Debian 12 e Fedora 41. Há também um job de seleção de versão.

Os artefatos `prints-*` contêm imagens, relatório e log do controlador. Nenhuma credencial de hospedagem é utilizada. Códigos de recuperação são ocultados das capturas de falha. A suíte recusa execução fora de CI, salvo indicação explícita de ambiente descartável isolado.

FTP e sincronização externa ficam pendentes de servidor de teste dedicado. Os testes atuais não cobrem atualização sobre uma instalação existente, todos os recursos do cardápio, pedidos ou impressão.
