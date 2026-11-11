"""Testes públicos sobre o instalador real. Não importa nem requer o código do app.

WebKitWebDriver no Linux; Microsoft Edge WebDriver no Windows.
Somente ambientes descartáveis de CI e dados fictícios. Sem testes de FTP.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request


LOJA = 'Loja Teste CI'
PRODUTO = 'Produto Teste CI'
EDITADO = 'Produto Teste CI editado'


class Interface:
    def __init__(self, app, driver, pasta, sistema):
        self.app = Path(app).resolve()
        self.driver = driver
        self.pasta = Path(pasta)
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.sistema = sistema
        self.url = 'http://127.0.0.1:4444'
        self.sessao = None
        self.processo = None
        self.resultados = []
        self.erros_driver = (self.pasta / 'webdriver.log').open('w', encoding='utf-8')

    def wd(self, metodo, caminho, dados=None):
        corpo = json.dumps(dados).encode() if dados is not None else None
        req = urllib.request.Request(self.url + caminho, data=corpo, method=metodo,
                                     headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                j = json.load(resp)
        except urllib.error.HTTPError as e:
            texto = e.read().decode(errors='replace')
            raise RuntimeError(f'WebDriver HTTP {e.code}: {texto[:1500]}') from None
        valor = j.get('value')
        if isinstance(valor, dict) and valor.get('error'):
            raise RuntimeError(valor.get('message', valor['error']))
        return valor

    def abrir(self):
        if self.processo is None:
            comando = [self.driver, '--port=4444']
            self.processo = subprocess.Popen(comando, stdout=self.erros_driver, stderr=subprocess.STDOUT)
            fim = time.monotonic() + 30
            while time.monotonic() < fim:
                if self.processo.poll() is not None:
                    raise RuntimeError('Driver encerrou; consultar webdriver.log')
                try:
                    self.wd('GET', '/status')
                    break
                except (OSError, RuntimeError):
                    time.sleep(.3)
            else:
                raise TimeoutError('Driver não respondeu')
        if os.name == 'nt':
            caps = {'browserName': 'webview2', 'ms:edgeChromium': True,
                    'ms:edgeOptions': {'binary': str(self.app)}}
        else:
            caps = {'webkitgtk:browserOptions': {'binary': str(self.app)}}
        s = self.wd('POST', '/session', {'capabilities': {'alwaysMatch': caps}})
        self.sessao = s['sessionId']
        self.wd('POST', f'/session/{self.sessao}/timeouts',
                {'script': 30000, 'pageLoad': 60000, 'implicit': 0})
        self.esperar("!!document.body && !!window.__TAURI_INTERNALS__", 'interface nativa do app')

    def js(self, script, *args):
        return self.wd('POST', f'/session/{self.sessao}/execute/sync', {'script': script, 'args': list(args)})

    def esperar(self, expressao, descricao, segundos=30):
        fim = time.monotonic() + segundos
        ultimo = None
        while time.monotonic() < fim:
            try:
                if self.js('return !!(' + expressao + ')'):
                    return
            except (OSError, RuntimeError) as e:
                ultimo = str(e)
            time.sleep(.2)
        raise TimeoutError(f'Não ocorreu: {descricao}' + (f' ({ultimo})' if ultimo else ''))

    def clicar(self, texto):
        busca = "[...document.querySelectorAll('button,a')].find(e=>e.getClientRects().length&&!e.disabled&&e.textContent.trim().startsWith(%s))" % json.dumps(texto)
        self.esperar(busca, 'botão ' + texto)
        self.js('const e=' + busca + ";e.scrollIntoView({block:'center'});e.click();")
        time.sleep(.2)

    def menu(self, rotulo):
        self.js("const e=[...document.querySelectorAll('aside button[aria-label]')].find(e=>e.getAttribute('aria-label').startsWith(arguments[0]));if(!e)throw Error('Menu ausente');e.click();", rotulo)
        time.sleep(.3)

    def preencher_id(self, campo, valor):
        self.preencher('[id=' + json.dumps(campo) + ']', valor)

    def preencher(self, seletor, valor):
        self.esperar('!!document.querySelector(' + json.dumps(seletor) + ')', 'campo ' + seletor)
        self.js("const e=document.querySelector(arguments[0]);e.focus();e.value=arguments[1];e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));", seletor, valor)
        time.sleep(.1)

    def campo_rotulo(self, rotulo, valor):
        self.js("const l=[...document.querySelectorAll('label')].find(e=>e.getClientRects().length&&e.textContent.trim().startsWith(arguments[0]));const e=l?.querySelector('input,textarea');if(!e)throw Error('Campo ausente: '+arguments[0]);e.focus();e.value=arguments[1];e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));", rotulo, valor)
        time.sleep(.1)

    def invalidos(self, *campos):
        for campo in campos:
            expr = f"document.getElementById({json.dumps(campo)})?.getAttribute('aria-invalid')==='true'"
            self.esperar(expr, 'campo recusado ' + campo)

    def foto(self, nome):
        codigo = self.js("const e=document.querySelector('.codigo-rec');if(!e)return null;const t=e.textContent;e.textContent='Código de teste ocultado';return t;")
        try:
            data = self.wd('GET', f'/session/{self.sessao}/screenshot')
            (self.pasta / f'{self.sistema}-{nome}.png').write_bytes(base64.b64decode(data))
        finally:
            if codigo is not None:
                self.js("const e=document.querySelector('.codigo-rec');if(e)e.textContent=arguments[0];", codigo)

    def ok(self, nome):
        self.resultados.append({'teste': nome, 'resultado': 'aprovado'})
        self.relatorio()
        print('OK:', nome, flush=True)

    def relatorio(self):
        (self.pasta / 'resultados.json').write_text(json.dumps({
            'sistema': self.sistema, 'release': os.environ.get('DF_RELEASE_TAG'),
            'testes': self.resultados, 'ftp': 'fora desta suíte: servidor de teste pendente'
        }, ensure_ascii=False, indent=2), encoding='utf-8')

    def encerrar_app(self):
        if self.sessao:
            try:
                self.wd('DELETE', f'/session/{self.sessao}')
            except Exception:
                pass
            self.sessao = None
        # O app pode continuar na bandeja; encerrar somente o executável de teste.
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/IM', self.app.name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            for item in Path('/proc').iterdir():
                if not item.name.isdigit():
                    continue
                try:
                    if (item / 'exe').resolve() == self.app:
                        os.kill(int(item.name), signal.SIGTERM)
                except (OSError, ProcessLookupError):
                    pass
        time.sleep(1)

    def fechar(self):
        self.encerrar_app()
        if self.processo:
            self.processo.terminate()
            try:
                self.processo.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.processo.kill()
        self.erros_driver.close()


def executar(ui):
    ui.abrir()
    ui.esperar("document.body.innerText.includes('Bem-vindo ao DF Delivery')", 'primeira execução limpa')
    ui.foto('01-instalacao-inicial')
    ui.ok('Instalador abriu o configurador inicial')
    ui.clicar('Continuar')
    ui.clicar('Continuar')
    ui.invalidos('assistente-loja.nome')
    ui.foto('02-loja-vazia')
    ui.preencher_id('assistente-loja.nome', '   ')
    ui.clicar('Continuar')
    ui.invalidos('assistente-loja.nome')
    ui.ok('Nome obrigatório vazio ou só com espaços impede o avanço')
    ui.preencher_id('assistente-loja.nome', LOJA)
    ui.preencher_id('assistente-loja.whatsapp', '123')
    ui.clicar('Continuar')
    ui.invalidos('assistente-loja.whatsapp')
    ui.ok('WhatsApp inválido impede o avanço')
    ui.preencher_id('assistente-loja.whatsapp', '(54) 99999-0000')
    ui.clicar('Continuar')
    ui.clicar('Continuar')
    ui.invalidos('assistente-dono.nome', 'assistente-dono.login', 'assistente-dono.senha')
    ui.foto('03-acesso-vazio')
    ui.ok('Dados obrigatórios do dono vazios impedem o avanço')
    ui.preencher_id('assistente-dono.nome', 'Operador CI')
    ui.preencher_id('assistente-dono.login', 'login com espaço')
    ui.preencher_id('assistente-dono.senha', 'TesteCI1234')
    ui.preencher_id('assistente-dono.confirmar', 'outra-senha')
    ui.clicar('Continuar')
    ui.invalidos('assistente-dono.login', 'assistente-dono.confirmar')
    ui.ok('Login inválido e senha divergente impedem o avanço')
    ui.preencher_id('assistente-dono.login', 'operador.ci')
    ui.preencher_id('assistente-dono.confirmar', 'TesteCI1234')
    ui.clicar('Continuar')
    # Preferência de teste: não iniciar com sistema nem permanecer na bandeja.
    ui.js("for(const l of document.querySelectorAll('label')){if(l.textContent.includes('Continuar na bandeja')||l.textContent.includes('Iniciar junto')){const e=l.querySelector('input[type=checkbox]');if(e?.checked)e.click();}}")
    ui.clicar('Continuar')
    ui.preencher_id('assistente-integ.telegram', 'incompleto')
    ui.clicar('Continuar')
    ui.invalidos('assistente-integ.telegram')
    ui.ok('Token Telegram incompleto impede o avanço')
    ui.preencher_id('assistente-integ.telegram', '')
    ui.clicar('Continuar')
    ui.esperar("document.body.innerText.includes('Tudo certo, ')", 'última etapa com integrações vazias')
    ui.ok('Integrações opcionais vazias permitem prosseguir')
    ui.clicar('Começar a usar')
    ui.esperar("document.body.innerText.includes('Guarde o seu código de recuperação')", 'dono criado e código de recuperação', 60)
    # Não fotografar o código de recuperação, mesmo sendo de conta fictícia.
    ui.clicar('Já anotei')
    ui.esperar("!!document.querySelector('aside.df-sidebar') && document.querySelector('main')?.innerText.includes('Loja Teste CI')", 'tela Início após cadastro', 45)
    ui.foto('04-inicio-apos-configuracao')
    ui.ok('Cadastro válido completa e abre a tela Início')
    # Evitar que instalações fictícias contaminem estatísticas de uso.
    ui.menu('Sistema')
    ui.clicar('Sobre o app')
    ui.esperar("document.body.innerText.includes('Enviar estatísticas de uso')", 'preferência de estatísticas')
    ui.js("const l=[...document.querySelectorAll('label')].find(e=>e.textContent.includes('Enviar estatísticas de uso'));const e=l?.querySelector('input[type=checkbox]');if(e?.checked)e.click();")
    ui.menu('Início')
    ui.js("const e=[...document.querySelectorAll('button')].find(e=>e.textContent.trim()==='Fechar e não mostrar mais');if(e)e.click();")
    ui.menu('Cardápio')
    ui.clicar('1. Categorias')
    ui.preencher('input[placeholder^="Nova categoria"]', 'Categoria CI')
    ui.clicar('Criar')
    ui.esperar("[...document.querySelectorAll('button')].some(e=>e.textContent.includes('Categoria CI'))", 'categoria criada')
    ui.clicar('3. Produtos')
    ui.clicar('Novo produto')
    ui.clicar('Criar produto')
    ui.esperar("document.body.innerText.includes('Informe o nome do produto.') && document.body.innerText.includes('Informe o preço.')", 'produto vazio recusado')
    ui.foto('05-produto-vazio')
    ui.ok('Produto sem nome/preço não é criado')
    ui.campo_rotulo('Nome', PRODUTO)
    ui.preencher('input[aria-label="Preço"]', '25,90')
    ui.clicar('Criar produto')
    ui.esperar("document.body.innerText.includes('Produto salvo.')", 'produto salvo')
    ui.foto('06-produto-criado')
    ui.ok('Produto válido é criado pela interface')
    ui.campo_rotulo('Nome', EDITADO)
    ui.preencher('input[aria-label="Preço"]', '29,90')
    ui.clicar('Salvar')
    ui.esperar("document.querySelector('button[disabled]')?.textContent.trim()==='Salvar' || [...document.querySelectorAll('button')].some(e=>e.textContent.trim()==='Salvar'&&e.disabled)", 'edição salva')
    ui.clicar('Produtos')
    ui.esperar("document.querySelector('main')?.innerText.includes('Produto Teste CI editado')", 'produto editado na lista')
    ui.foto('07-lista-produtos')
    ui.ok('Nome e preço editados são salvos')
    ui.encerrar_app()
    ui.abrir()
    ui.esperar("!!document.querySelector('aside.df-sidebar')", 'app reaberto com cadastro preservado', 45)
    ui.menu('Cardápio')
    ui.clicar('3. Produtos')
    ui.clicar(EDITADO)
    ui.esperar("document.querySelector('input[aria-label=\"Preço\"]')?.value==='29,90'", 'preço persistido após reiniciar')
    ui.foto('08-produto-apos-reabrir')
    ui.ok('Produto e preço permanecem após encerrar e reabrir o app')


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true' and os.environ.get('DF_UI_TEST_ISOLATED') != 'true':
        raise SystemExit('Executar somente em CI ou ambiente descartável explicitamente isolado.')
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', required=True)
    parser.add_argument('--driver', required=True)
    parser.add_argument('--out', default='prints')
    parser.add_argument('--sistema', required=True)
    args = parser.parse_args()
    if not Path(args.app).is_file():
        raise SystemExit('Executável instalado não encontrado')
    os.environ['TAURI_WEBVIEW_AUTOMATION'] = 'true'
    ui = Interface(args.app, args.driver, args.out, args.sistema)
    try:
        executar(ui)
    except Exception as e:
        ui.resultados.append({'teste': 'Execução interrompida', 'resultado': 'falhou', 'erro': str(e)})
        ui.relatorio()
        if ui.sessao:
            try:
                ui.foto('FALHA')
                texto = ui.js("const e=document.querySelector('.codigo-rec');const t=document.body.innerText;return e?t.replace(e.textContent,'[código de teste ocultado]'):t;")
                (ui.pasta / 'tela-falha.txt').write_text(texto, encoding='utf-8')
            except Exception:
                pass
        raise
    finally:
        ui.fechar()


if __name__ == '__main__':
    main()
