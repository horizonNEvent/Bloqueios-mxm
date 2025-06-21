from playwright.sync_api import sync_playwright
import json
import time

# Carregar credenciais do arquivo externo
with open("credentials.json", "r") as f:
    creds = json.load(f)
    username = creds["username"]
    password = creds["password"]

# Receber o nome do usuário a ser bloqueado
usuario_para_bloquear = input("Digite o nome do usuário a ser bloqueado: ")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://mxmhml-rioenergy.rsmbrasil.com.br/?grupo=RIOENERGYHOM")

    # Login
    page.wait_for_selector("div.login#div1", state="visible", timeout=30000)
    page.fill('input[name="txfUsuario"]', username)
    page.fill('input[name="txfSenha"]', password)
    page.click('button:has-text("Conectar")')

    # Esperar campo de busca da tela principal
    try:
        page.wait_for_selector('input[name="tgfBusca"]', state="visible", timeout=30000)
    except Exception as e:
        print(f"Erro ao carregar tela principal: {str(e)}")
        browser.close()
        exit(1)

    # Navegar até o menu de cadastro de usuário
    try:
        page.wait_for_selector("button#ext-gen20.mainMenuIconSystemMXADMINISTRA", state="visible", timeout=30000).click()
        page.wait_for_timeout(2000)
        page.wait_for_selector('div#MXADMINISTRA[title="Administrador"]', state="visible", timeout=30000).click()
        page.wait_for_timeout(2000)
        page.wait_for_selector("button#ext-gen923.mainMenuIconCadastro", state="visible", timeout=30000).click()
        page.wait_for_timeout(2000)
        page.wait_for_selector("span#ext-gen965.x-menu-item-text", state="visible", timeout=30000).click()
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Erro ao navegar até o cadastro de usuário: {str(e)}")
        browser.close()
        exit(1)

    # Acessar o iframe do cadastro de usuário
    try:
        iframe_element = page.wait_for_selector('xpath=//*[@id="110001_IFrame"]', state="attached", timeout=20000)
        iframe = iframe_element.content_frame()
        if not iframe:
            print("Não foi possível acessar o iframe de cadastro de usuário.")
            browser.close()
            exit(1)
    except Exception as e:
        print(f"Erro ao acessar o iframe: {str(e)}")
        browser.close()
        exit(1)

    # Buscar usuário pelo código
    try:
        campo_codigo = iframe.wait_for_selector('input[name="hpfCodigo"]', state="visible", timeout=10000)
        page.wait_for_timeout(2000)
        campo_codigo.fill(usuario_para_bloquear)
        page.wait_for_timeout(4000)
        campo_codigo.press('Tab')
        time.sleep(7)  # Espera o carregamento dos dados do usuário
    except Exception as e:
        print(f"Erro ao buscar usuário: {str(e)}")
        browser.close()
        exit(1)

    # Verificar se encontrou o usuário
    try:
        campo_nome = iframe.wait_for_selector('input[name="txfNome"]', state="visible", timeout=5000)
        nome_encontrado = campo_nome.input_value()
        if not nome_encontrado:
            print("Usuário não encontrado!")
            browser.close()
            exit(1)
    except Exception:
        print("Usuário não encontrado!")
        browser.close()
        exit(1)

    # Dentro do bloco do iframe, antes de marcar o bloqueio:
    try:
        checkbox_acessa_mxm = iframe.wait_for_selector('input[name="chkAcessaMXMManager"]', state="visible", timeout=5000)
        if checkbox_acessa_mxm.is_checked():
            checkbox_acessa_mxm.uncheck()
    except Exception as e:
        print(f"Erro ao desmarcar a checkbox 'Acessa o MXM-WebManager': {str(e)}")

    # Marcar o checkbox de bloqueio
    try:
        checkbox_bloqueio = iframe.wait_for_selector('input[name="chkUsuarioBloqueado"]', state="visible", timeout=5000)
        if not checkbox_bloqueio.is_checked():
            checkbox_bloqueio.check()
        else:
            print("Usuário já está bloqueado.")
    except Exception as e:
        print(f"Erro ao marcar o checkbox de bloqueio: {str(e)}")
        browser.close()
        exit(1)

    # Salvar alterações
    try:
        botao_gravar = iframe.wait_for_selector('button:has-text("Gravar")', state="visible", timeout=5000)
        page.wait_for_timeout(2000)
        botao_gravar.click()
        print(f"Usuário '{usuario_para_bloquear}' bloqueado com sucesso!")
    except Exception as e:
        print(f"Erro ao gravar alterações: {str(e)}")

    page.wait_for_timeout(5000)
    browser.close()
