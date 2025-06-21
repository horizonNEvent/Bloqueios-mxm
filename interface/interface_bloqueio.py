import sys
import json
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QMessageBox, QProgressBar, QComboBox, QDialog, QCompleter)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon
from .gerenciador_bases import GerenciadorBases
from .janela_gerenciar_bases import JanelaGerenciarBases

class BloqueioThread(QThread):
    """Thread para executar o processo de bloqueio em background"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, usuario_para_bloquear, base_selecionada):
        super().__init__()
        self.usuario_para_bloquear = usuario_para_bloquear
        self.base_selecionada = base_selecionada
        
    def run(self):
        try:
            from playwright.sync_api import sync_playwright
            import time
            
            # Carregar credenciais do arquivo externo
            try:
                with open("credentials.json", "r") as f:
                    creds = json.load(f)
                    username = creds["username"]
                    password = creds["password"]
            except Exception as e:
                self.finished_signal.emit(False, f"Erro ao carregar credenciais: {str(e)}")
                return
                
            self.log_signal.emit("Iniciando processo de bloqueio...")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                
                self.log_signal.emit(f"Acessando o sistema na base: {self.base_selecionada['nome']}")
                page.goto(self.base_selecionada['url'])

                # Login
                self.log_signal.emit("Realizando login...")
                page.wait_for_selector("div.login#div1", state="visible", timeout=30000)
                page.fill('input[name="txfUsuario"]', username)
                page.fill('input[name="txfSenha"]', password)
                page.click('button:has-text("Conectar")')

                # Esperar campo de busca da tela principal
                try:
                    page.wait_for_selector('input[name="tgfBusca"]', state="visible", timeout=30000)
                    self.log_signal.emit("Login realizado com sucesso!")
                except Exception as e:
                    self.finished_signal.emit(False, f"Erro ao carregar tela principal: {str(e)}")
                    browser.close()
                    return

                # Navegar até o menu de cadastro de usuário
                try:
                    self.log_signal.emit("Navegando para o cadastro de usuário...")
                    page.wait_for_selector("button#ext-gen20.mainMenuIconSystemMXADMINISTRA", state="visible", timeout=30000).click()
                    page.wait_for_timeout(2000)
                    page.wait_for_selector('div#MXADMINISTRA[title="Administrador"]', state="visible", timeout=30000).click()
                    page.wait_for_timeout(2000)
                    page.wait_for_selector("button#ext-gen923.mainMenuIconCadastro", state="visible", timeout=30000).click()
                    page.wait_for_timeout(2000)
                    page.wait_for_selector("span#ext-gen965.x-menu-item-text", state="visible", timeout=30000).click()
                    page.wait_for_timeout(2000)
                    self.log_signal.emit("Menu de cadastro acessado!")
                except Exception as e:
                    self.finished_signal.emit(False, f"Erro ao navegar até o cadastro de usuário: {str(e)}")
                    browser.close()
                    return

                # Acessar o iframe do cadastro de usuário
                try:
                    self.log_signal.emit("Acessando formulário de cadastro...")
                    iframe_element = page.wait_for_selector('xpath=//*[@id="110001_IFrame"]', state="attached", timeout=20000)
                    iframe = iframe_element.content_frame()
                    if not iframe:
                        self.finished_signal.emit(False, "Não foi possível acessar o iframe de cadastro de usuário.")
                        browser.close()
                        return
                except Exception as e:
                    self.finished_signal.emit(False, f"Erro ao acessar o iframe: {str(e)}")
                    browser.close()
                    return

                # Buscar usuário pelo código
                try:
                    self.log_signal.emit(f"Buscando usuário: {self.usuario_para_bloquear}")
                    campo_codigo = iframe.wait_for_selector('input[name="hpfCodigo"]', state="visible", timeout=10000)
                    page.wait_for_timeout(2000)
                    campo_codigo.fill(self.usuario_para_bloquear)
                    page.wait_for_timeout(4000)
                    campo_codigo.press('Tab')
                    time.sleep(7)  # Espera o carregamento dos dados do usuário
                except Exception as e:
                    self.finished_signal.emit(False, f"Erro ao buscar usuário: {str(e)}")
                    browser.close()
                    return

                # Verificar se encontrou o usuário
                try:
                    campo_nome = iframe.wait_for_selector('input[name="txfNome"]', state="visible", timeout=5000)
                    nome_encontrado = campo_nome.input_value()
                    if not nome_encontrado:
                        self.finished_signal.emit(False, "Usuário não encontrado!")
                        browser.close()
                        return
                    self.log_signal.emit(f"Usuário encontrado: {nome_encontrado}")
                except Exception:
                    self.finished_signal.emit(False, "Usuário não encontrado!")
                    browser.close()
                    return

                # Desmarcar checkbox de acesso ao MXM
                try:
                    self.log_signal.emit("Desmarcando acesso ao MXM...")
                    checkbox_acessa_mxm = iframe.wait_for_selector('input[name="chkAcessaMXMManager"]', state="visible", timeout=5000)
                    if checkbox_acessa_mxm.is_checked():
                        checkbox_acessa_mxm.uncheck()
                        self.log_signal.emit("Acesso ao MXM desmarcado!")
                except Exception as e:
                    self.log_signal.emit(f"Aviso: Erro ao desmarcar a checkbox 'Acessa o MXM-WebManager': {str(e)}")

                # Marcar o checkbox de bloqueio
                try:
                    self.log_signal.emit("Marcando bloqueio do usuário...")
                    checkbox_bloqueio = iframe.wait_for_selector('input[name="chkUsuarioBloqueado"]', state="visible", timeout=5000)
                    if not checkbox_bloqueio.is_checked():
                        checkbox_bloqueio.check()
                        self.log_signal.emit("Checkbox de bloqueio marcado!")
                    else:
                        self.log_signal.emit("Usuário já está bloqueado.")
                except Exception as e:
                    self.finished_signal.emit(False, f"Erro ao marcar o checkbox de bloqueio: {str(e)}")
                    browser.close()
                    return

                # Salvar alterações
                try:
                    self.log_signal.emit("Salvando alterações...")
                    botao_gravar = iframe.wait_for_selector('button:has-text("Gravar")', state="visible", timeout=5000)
                    page.wait_for_timeout(2000)
                    botao_gravar.click()
                    self.log_signal.emit(f"Usuário '{self.usuario_para_bloquear}' bloqueado com sucesso!")
                except Exception as e:
                    self.finished_signal.emit(False, f"Erro ao gravar alterações: {str(e)}")
                    browser.close()
                    return

                page.wait_for_timeout(5000)
                browser.close()
                self.finished_signal.emit(True, f"Processo concluído! Usuário '{self.usuario_para_bloquear}' foi bloqueado com sucesso na base '{self.base_selecionada['nome']}'.")
                
        except Exception as e:
            self.finished_signal.emit(False, f"Erro inesperado: {str(e)}")


class InterfaceBloqueio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gerenciador_bases = GerenciadorBases()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Sistema de Bloqueio de Usuários")
        self.setGeometry(100, 100, 700, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        titulo = QLabel("Sistema de Bloqueio de Usuários")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(titulo)
        
        # Seleção de base
        label_base = QLabel("Selecione a base:")
        label_base.setFont(QFont("Arial", 10))
        layout.addWidget(label_base)
        
        # Layout horizontal para base e botão gerenciar
        layout_base = QHBoxLayout()
        
        self.combo_base = QComboBox()
        self.combo_base.setEditable(True)
        self.combo_base.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo_base.setFont(QFont("Arial", 10))
        self.combo_base.setMaxVisibleItems(15) # Limita a altura e força o scroll
        self.combo_base.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.combo_base.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
                min-width: 200px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #7f8c8d;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #bdc3c7;
                background-color: white;
                selection-background-color: #3498db;
                outline: 0px; /* Remove a borda de foco */
            }
        """)
        layout_base.addWidget(self.combo_base)
        
        self.botao_gerenciar_bases = QPushButton("Gerenciar Bases")
        self.botao_gerenciar_bases.setFont(QFont("Arial", 10))
        self.botao_gerenciar_bases.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.botao_gerenciar_bases.clicked.connect(self.abrir_gerenciar_bases)
        layout_base.addWidget(self.botao_gerenciar_bases)
        
        layout.addLayout(layout_base)
        
        # Campo de entrada do usuário
        label_usuario = QLabel("Nome do usuário a ser bloqueado:")
        label_usuario.setFont(QFont("Arial", 10))
        layout.addWidget(label_usuario)
        
        self.campo_usuario = QLineEdit()
        self.campo_usuario.setPlaceholderText("Digite o nome do usuário...")
        self.campo_usuario.setFont(QFont("Arial", 10))
        self.campo_usuario.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.campo_usuario)
        
        # Botão de bloqueio
        self.botao_bloquear = QPushButton("Bloquear Usuário")
        self.botao_bloquear.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.botao_bloquear.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.botao_bloquear.clicked.connect(self.iniciar_bloqueio)
        layout.addWidget(self.botao_bloquear)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Área de log
        label_log = QLabel("Log de Execução:")
        label_log.setFont(QFont("Arial", 10))
        layout.addWidget(label_log)
        
        self.area_log = QTextEdit()
        self.area_log.setReadOnly(True)
        self.area_log.setFont(QFont("Consolas", 9))
        self.area_log.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
                padding: 10px;
            }
        """)
        layout.addWidget(self.area_log)
        
        # Thread de bloqueio
        self.thread_bloqueio = None
        
        # Carregar bases no combo
        self.carregar_bases()
        
    def carregar_bases(self):
        """Carrega as bases no combo box"""
        current_data = self.combo_base.currentData()

        self.combo_base.clear()
        bases = self.gerenciador_bases.obter_bases()
        
        # Ordenar as bases em ordem alfabética pelo nome
        bases_ordenadas = sorted(bases, key=lambda b: b['nome'])
        
        display_texts = []
        for base in bases_ordenadas:
            text = f"{base['nome']} - {base.get('descricao', '')}"
            self.combo_base.addItem(text, base)
            display_texts.append(text)

        # Setup completer for search functionality
        self.completer = QCompleter(display_texts, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.combo_base.setCompleter(self.completer)

        # Restore selection
        if current_data:
            index = self.combo_base.findData(current_data)
            if index != -1:
                self.combo_base.setCurrentIndex(index)
        elif bases:
            self.combo_base.setCurrentIndex(0)
        
    def abrir_gerenciar_bases(self):
        """Abre a janela de gerenciamento de bases"""
        janela = JanelaGerenciarBases(self.gerenciador_bases, self)
        janela.exec()
        # Recarregar bases sempre que a janela for fechada
        self.carregar_bases()
        
    def iniciar_bloqueio(self):
        usuario = self.campo_usuario.text().strip()
        
        if not usuario:
            QMessageBox.warning(self, "Aviso", "Por favor, digite o nome do usuário a ser bloqueado.")
            return
        
        # Verificar se uma base foi selecionada
        if self.combo_base.count() == 0:
            QMessageBox.warning(self, "Aviso", "Nenhuma base cadastrada. Por favor, cadastre uma base primeiro.")
            return

        # Validar que a base digitada/selecionada é válida
        if self.combo_base.findText(self.combo_base.currentText()) == -1:
            QMessageBox.warning(self, "Aviso", "A base digitada não é válida. Por favor, selecione uma da lista.")
            return
            
        base_selecionada = self.combo_base.currentData()
        if not base_selecionada:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione uma base.")
            return
            
        # Desabilitar interface durante execução
        self.botao_bloquear.setEnabled(False)
        self.campo_usuario.setEnabled(False)
        self.combo_base.setEnabled(False)
        self.botao_gerenciar_bases.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Progresso indeterminado
        
        # Limpar área de log
        self.area_log.clear()
        
        # Criar e iniciar thread
        self.thread_bloqueio = BloqueioThread(usuario, base_selecionada)
        self.thread_bloqueio.log_signal.connect(self.adicionar_log)
        self.thread_bloqueio.finished_signal.connect(self.processar_resultado)
        self.thread_bloqueio.start()
        
    def adicionar_log(self, mensagem):
        self.area_log.append(f"[{self.get_timestamp()}] {mensagem}")
        # Rolar para o final
        scrollbar = self.area_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def processar_resultado(self, sucesso, mensagem):
        # Reabilitar interface
        self.botao_bloquear.setEnabled(True)
        self.campo_usuario.setEnabled(True)
        self.combo_base.setEnabled(True)
        self.botao_gerenciar_bases.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Adicionar mensagem final
        self.adicionar_log(mensagem)
        
        # Mostrar mensagem de resultado
        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.campo_usuario.clear()
        else:
            QMessageBox.critical(self, "Erro", mensagem)
            
    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")


def main():
    app = QApplication(sys.argv)
    
    # Configurar estilo da aplicação
    app.setStyle('Fusion')
    
    # Criar e mostrar a janela
    window = InterfaceBloqueio()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 