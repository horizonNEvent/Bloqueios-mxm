import sys
import json
import threading
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QMessageBox, QProgressBar, QDialog, QCompleter,
                             QListWidget, QListWidgetItem, QCheckBox, QDateTimeEdit,
                             QGroupBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QDateTime
from PyQt6.QtGui import QFont, QIcon
from .gerenciador_bases import GerenciadorBases
from .janela_gerenciar_bases import JanelaGerenciarBases
from .agendador import agendador_global, log_emitter
from .historico import historico_global
from .janela_historico import JanelaHistorico

class BloqueioThread(QThread):
    """Thread para executar o processo de bloqueio em background"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, usuario_para_bloquear, bases_selecionadas):
        super().__init__()
        self.usuario_para_bloquear = usuario_para_bloquear
        self.bases_selecionadas = bases_selecionadas
        
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
            
            sucesso_total = True
            mensagens_erro = []

            with sync_playwright() as p:
                for base_selecionada in self.bases_selecionadas:
                    self.log_signal.emit(f"--- Processando base: {base_selecionada['nome']} ---")
                    try:
                        browser = p.chromium.launch(headless=False)
                        page = browser.new_page()
                        
                        self.log_signal.emit(f"Acessando o sistema na base: {base_selecionada['nome']}")
                        page.goto(base_selecionada['url'])

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
                            raise Exception(f"Erro ao carregar tela principal: {str(e)}")

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
                            raise Exception(f"Erro ao navegar até o cadastro de usuário: {str(e)}")

                        # Acessar o iframe do cadastro de usuário
                        try:
                            self.log_signal.emit("Acessando formulário de cadastro...")
                            iframe_element = page.wait_for_selector('xpath=//*[@id="110001_IFrame"]', state="attached", timeout=20000)
                            iframe = iframe_element.content_frame()
                            if not iframe:
                                raise Exception("Não foi possível acessar o iframe de cadastro de usuário.")
                        except Exception as e:
                            raise Exception(f"Erro ao acessar o iframe: {str(e)}")

                        # Buscar usuário pelo código
                        try:
                            self.log_signal.emit(f"Buscando usuário: {self.usuario_para_bloquear}")
                            campo_codigo = iframe.wait_for_selector('input[name="hpfCodigo"]', state="visible", timeout=10000)
                            page.wait_for_timeout(2000)
                            campo_codigo.fill(self.usuario_para_bloquear)
                            page.wait_for_timeout(4000)
                            campo_codigo.press('Tab')
                            time.sleep(7)
                        except Exception as e:
                            raise Exception(f"Erro ao buscar usuário: {str(e)}")

                        # Verificar se encontrou o usuário
                        try:
                            campo_nome = iframe.wait_for_selector('input[name="txfNome"]', state="visible", timeout=5000)
                            nome_encontrado = campo_nome.input_value()
                            if not nome_encontrado:
                                raise Exception("Usuário não encontrado!")
                            self.log_signal.emit(f"Usuário encontrado: {nome_encontrado}")
                        except Exception:
                            raise Exception("Usuário não encontrado!")

                        # Desmarcar checkbox de acesso ao MXM
                        try:
                            checkbox_acessa_mxm = iframe.wait_for_selector('input[name="chkAcessaMXMManager"]', state="visible", timeout=5000)
                            if checkbox_acessa_mxm.is_checked():
                                checkbox_acessa_mxm.uncheck()
                                self.log_signal.emit("Acesso ao MXM desmarcado!")
                        except Exception as e:
                            self.log_signal.emit(f"Aviso: Erro ao desmarcar 'Acessa o MXM-WebManager': {str(e)}")

                        # Marcar o checkbox de bloqueio
                        try:
                            checkbox_bloqueio = iframe.wait_for_selector('input[name="chkUsuarioBloqueado"]', state="visible", timeout=5000)
                            if not checkbox_bloqueio.is_checked():
                                checkbox_bloqueio.check()
                                self.log_signal.emit("Checkbox de bloqueio marcado!")
                            else:
                                self.log_signal.emit("Usuário já está bloqueado.")
                        except Exception as e:
                            raise Exception(f"Erro ao marcar o checkbox de bloqueio: {str(e)}")

                        # Salvar alterações
                        try:
                            self.log_signal.emit("Salvando alterações...")
                            botao_gravar = iframe.wait_for_selector('button:has-text("Gravar")', state="visible", timeout=5000)
                            page.wait_for_timeout(2000)
                            botao_gravar.click()
                            self.log_signal.emit("Aguardando 10 segundos para a gravação...")
                            page.wait_for_timeout(10000) # Espera 10 segundos
                            self.log_signal.emit(f"Usuário '{self.usuario_para_bloquear}' bloqueado com sucesso na base '{base_selecionada['nome']}'!")
                        except Exception as e:
                            raise Exception(f"Erro ao gravar alterações: {str(e)}")

                    except Exception as e:
                        sucesso_total = False
                        erro_msg = f"Erro na base '{base_selecionada['nome']}': {str(e)}"
                        self.log_signal.emit(erro_msg)
                        mensagens_erro.append(erro_msg)
                    finally:
                        if 'browser' in locals() and browser.is_connected():
                            browser.close()

            if sucesso_total:
                self.finished_signal.emit(True, "Processo concluído! Todas as bases foram processadas com sucesso.")
            else:
                erros_formatados = "\n".join(mensagens_erro)
                self.finished_signal.emit(False, f"Processo concluído com erros:\n{erros_formatados}")
                
        except Exception as e:
            self.finished_signal.emit(False, f"Erro inesperado no processo: {str(e)}")


class InterfaceBloqueio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gerenciador_bases = GerenciadorBases()
        self.agendador = agendador_global
        self.ambiente_atual = "PROD"  # Ambiente padrão alterado para PROD
        self.initUI()
        self.setWindowTitle("Sistema de Bloqueio de Usuários")
        log_emitter.log_signal.connect(self.adicionar_log)
        
    def initUI(self):
        self.setGeometry(100, 100, 700, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        titulo = QLabel("Sistema de Bloqueio de Usuários")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(titulo)
        
        # Seletor de Ambiente
        layout_ambiente = QHBoxLayout()
        label_ambiente = QLabel("Ambiente:")
        self.switch_ambiente = QCheckBox("PROD")
        self.switch_ambiente.setToolTip("Alterne entre ambiente de Produção (ligado) e Homologação (desligado)")
        self.switch_ambiente.setChecked(True) # Inicia marcado como PROD
        self.switch_ambiente.stateChanged.connect(self.alternar_ambiente)
        layout_ambiente.addWidget(label_ambiente)
        layout_ambiente.addWidget(self.switch_ambiente)
        layout_ambiente.addStretch()
        layout.addLayout(layout_ambiente)
        
        # Layout horizontal para base e botão gerenciar
        layout_base_botoes = QHBoxLayout()
        label_base = QLabel("Selecione as bases:")
        label_base.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        self.botao_gerenciar_bases = QPushButton("Gerenciar Bases")
        self.botao_gerenciar_bases.setFont(QFont("Arial", 10))
        self.botao_gerenciar_bases.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white; padding: 8px 16px;
                border: none; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.botao_gerenciar_bases.clicked.connect(self.abrir_gerenciar_bases)
        
        self.botao_historico = QPushButton("Ver Histórico")
        self.botao_historico.clicked.connect(self.abrir_historico)
        
        layout_base_botoes.addWidget(label_base)
        layout_base_botoes.addStretch()
        layout_base_botoes.addWidget(self.botao_gerenciar_bases)
        layout_base_botoes.addWidget(self.botao_historico)
        layout.addLayout(layout_base_botoes)

        # Filtro de busca de bases
        self.filtro_base = QLineEdit()
        self.filtro_base.setPlaceholderText("Digite para filtrar as bases...")
        self.filtro_base.textChanged.connect(self.filtrar_bases)
        layout.addWidget(self.filtro_base)
        
        # Lista de bases com checkboxes
        self.lista_bases = QListWidget()
        self.lista_bases.setStyleSheet("QListWidget { border: 1px solid #bdc3c7; border-radius: 5px; }")
        layout.addWidget(self.lista_bases)

        # Botões para selecionar/desselecionar todas
        layout_selecao = QHBoxLayout()
        self.botao_selecionar_todas = QPushButton("Marcar Todas")
        self.botao_selecionar_todas.clicked.connect(lambda: self.selecionar_todas(True))
        layout_selecao.addWidget(self.botao_selecionar_todas)
        
        self.botao_desselecionar_todas = QPushButton("Desmarcar Todas")
        self.botao_desselecionar_todas.clicked.connect(lambda: self.selecionar_todas(False))
        layout_selecao.addWidget(self.botao_desselecionar_todas)
        layout.addLayout(layout_selecao)
        
        label_usuario = QLabel("Nome do usuário a ser bloqueado:")
        label_usuario.setFont(QFont("Arial", 10))
        layout.addWidget(label_usuario)
        
        self.campo_usuario = QLineEdit()
        self.campo_usuario.setPlaceholderText("Digite o nome do usuário...")
        layout.addWidget(self.campo_usuario)
        
        # Grupo de Agendamento
        self.grupo_agendamento = QGroupBox("Agendamento")
        self.grupo_agendamento.setCheckable(True)
        self.grupo_agendamento.setChecked(False)
        self.grupo_agendamento.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.grupo_agendamento.toggled.connect(self.toggle_agendamento)
        
        layout_agendamento = QHBoxLayout(self.grupo_agendamento)
        label_data_hora = QLabel("Data e Hora do Bloqueio:")
        self.campo_data_hora = QDateTimeEdit()
        self.campo_data_hora.setDateTime(QDateTime.currentDateTime().addSecs(60))
        self.campo_data_hora.setCalendarPopup(True)
        self.campo_data_hora.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        layout_agendamento.addWidget(label_data_hora)
        layout_agendamento.addWidget(self.campo_data_hora)
        
        self.botao_bloquear = QPushButton("Bloquear Usuário Agora")
        self.botao_bloquear.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.botao_bloquear.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white; padding: 12px;
                border: none; border-radius: 5px; font-size: 14px;
            }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:pressed { background-color: #a93226; }
            QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }
        """)
        self.botao_bloquear.clicked.connect(self.iniciar_bloqueio)
        layout.addWidget(self.grupo_agendamento)
        layout.addWidget(self.botao_bloquear)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        label_log = QLabel("Log de Execução:")
        label_log.setFont(QFont("Arial", 10))
        layout.addWidget(label_log)
        
        self.area_log = QTextEdit()
        self.area_log.setReadOnly(True)
        layout.addWidget(self.area_log)
        
        self.thread_bloqueio = None
        
        self.carregar_bases()
        self.toggle_agendamento(False)
        
    def alternar_ambiente(self, state):
        """Alterna o ambiente e recarrega a lista de bases."""
        if state == Qt.CheckState.Checked.value:
            self.ambiente_atual = "PROD"
        else:
            self.ambiente_atual = "HML"
        self.carregar_bases()
        
    def carregar_bases(self):
        """Carrega e filtra as bases na lista com checkboxes."""
        self.lista_bases.clear()
        bases = self.gerenciador_bases.obter_bases()
        
        bases_filtradas = [b for b in bases if b.get('ambiente', 'HML').upper() == self.ambiente_atual]
        bases_ordenadas = sorted(bases_filtradas, key=lambda b: b['nome'])
        
        for base in bases_ordenadas:
            item = QListWidgetItem(f"{base['nome']} - {base.get('descricao', '')}")
            item.setData(Qt.ItemDataRole.UserRole, base)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.lista_bases.addItem(item)
            
    def filtrar_bases(self, texto):
        """Filtra a lista de bases com base no texto digitado"""
        for i in range(self.lista_bases.count()):
            item = self.lista_bases.item(i)
            item.setHidden(texto.lower() not in item.text().lower())

    def selecionar_todas(self, selecionar):
        """Marcar ou desmarcar todas as bases visíveis"""
        check_state = Qt.CheckState.Checked if selecionar else Qt.CheckState.Unchecked
        for i in range(self.lista_bases.count()):
            item = self.lista_bases.item(i)
            if not item.isHidden():
                item.setCheckState(check_state)

    def abrir_gerenciar_bases(self):
        """Abre a janela de gerenciamento de bases"""
        janela = JanelaGerenciarBases(self.gerenciador_bases, self)
        janela.exec()
        self.carregar_bases()
        
    def toggle_agendamento(self, checked):
        """Alterna o texto do botão com base no agendamento."""
        if checked:
            self.botao_bloquear.setText("Agendar Bloqueio")
        else:
            self.botao_bloquear.setText("Bloquear Usuário Agora")
            
    def iniciar_bloqueio(self):
        self.usuario_atual = self.campo_usuario.text().strip()
        
        if not self.usuario_atual:
            QMessageBox.warning(self, "Aviso", "Por favor, digite o nome do usuário.")
            return
        
        self.bases_atuais = []
        for i in range(self.lista_bases.count()):
            item = self.lista_bases.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                self.bases_atuais.append(item.data(Qt.ItemDataRole.UserRole))
        
        if not self.bases_atuais:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos uma base.")
            return
            
        if self.grupo_agendamento.isChecked():
            data_hora = self.campo_data_hora.dateTime().toPyDateTime()
            
            if data_hora <= datetime.now():
                QMessageBox.warning(self, "Aviso", "A data e hora do agendamento devem ser no futuro.")
                return
                
            self.agendador.agendar_bloqueio(data_hora, self.usuario_atual, self.bases_atuais, self.ambiente_atual)
            QMessageBox.information(self, "Sucesso", f"Bloqueio para '{self.usuario_atual}' agendado com sucesso para {data_hora.strftime('%d/%m/%Y às %H:%M')} no ambiente {self.ambiente_atual}.")
            self.campo_usuario.clear()
            
        else:
            self.set_interface_enabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.area_log.clear()
            
            self.thread_bloqueio = BloqueioThread(self.usuario_atual, self.bases_atuais)
            self.thread_bloqueio.log_signal.connect(self.adicionar_log)
            self.thread_bloqueio.finished_signal.connect(self.processar_resultado)
            self.thread_bloqueio.start()
        
    def adicionar_log(self, mensagem):
        self.area_log.append(f"[{self.get_timestamp()}] {mensagem}")
        self.area_log.verticalScrollBar().setValue(self.area_log.verticalScrollBar().maximum())
        
    def processar_resultado(self, sucesso, mensagem):
        self.set_interface_enabled(True)
        self.progress_bar.setVisible(False)
        self.adicionar_log(mensagem)
        
        status_str = "Sucesso" if sucesso else "Falha"
        historico_global.adicionar_registro(self.usuario_atual, self.bases_atuais, self.ambiente_atual, status_str, mensagem)

        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
        else:
            QMessageBox.critical(self, "Erro", mensagem)
            
    def set_interface_enabled(self, enabled):
        """Habilita ou desabilita os controles da interface"""
        self.lista_bases.setEnabled(enabled)
        self.filtro_base.setEnabled(enabled)
        self.campo_usuario.setEnabled(enabled)
        self.botao_bloquear.setEnabled(enabled)
        self.botao_gerenciar_bases.setEnabled(enabled)
        self.botao_selecionar_todas.setEnabled(enabled)
        self.botao_desselecionar_todas.setEnabled(enabled)
        self.grupo_agendamento.setEnabled(enabled)

    def get_timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def closeEvent(self, event):
        """Garante que o agendador seja desligado corretamente."""
        try:
            log_emitter.log_signal.disconnect(self.adicionar_log)
        except TypeError:
            pass # Ignora o erro se o sinal não estiver conectado
        self.agendador.desligar()
        event.accept()

    def abrir_historico(self):
        """Abre a janela de histórico."""
        janela = JanelaHistorico(self)
        janela.exec()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = InterfaceBloqueio()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 