import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QTextEdit, QGroupBox, QWidget,
                             QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .gerenciador_bases import GerenciadorBases

class JanelaGerenciarBases(QDialog):
    """Janela para gerenciar as bases do sistema"""
    
    def __init__(self, gerenciador, parent=None):
        super().__init__(parent)
        self.gerenciador = gerenciador
        self.initUI()
        self.carregar_tabela()
        
    def initUI(self):
        self.setWindowTitle("Gerenciar Bases")
        self.setGeometry(200, 200, 800, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        titulo = QLabel("Gerenciar Bases do Sistema")
        titulo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(titulo)
        
        # Grupo para adicionar/editar base
        grupo_form = QGroupBox("Adicionar/Editar Base")
        grupo_form.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout_form = QVBoxLayout()
        
        # Campos do formulário
        form_layout = QHBoxLayout()
        
        # Coluna esquerda
        col_esq = QVBoxLayout()
        
        # Nome da base
        label_nome = QLabel("Nome da Base:")
        self.campo_nome = QLineEdit()
        self.campo_nome.setPlaceholderText("Ex: RIOENERGY")
        col_esq.addWidget(label_nome)
        col_esq.addWidget(self.campo_nome)
        
        # Ambiente
        label_ambiente = QLabel("Ambiente:")
        self.combo_ambiente = QComboBox()
        self.combo_ambiente.addItems(["HML", "PROD"])
        col_esq.addWidget(label_ambiente)
        col_esq.addWidget(self.combo_ambiente)
        
        # URL da base
        label_url = QLabel("URL da Base:")
        self.campo_url = QLineEdit()
        self.campo_url.setPlaceholderText("https://mxmhml-xxx.rsmbrasil.com.br/?grupo=XXXHOM")
        col_esq.addWidget(label_url)
        col_esq.addWidget(self.campo_url)
        
        form_layout.addLayout(col_esq)
        
        # Coluna direita
        col_dir = QVBoxLayout()
        
        # Descrição
        label_desc = QLabel("Descrição:")
        self.campo_descricao = QTextEdit()
        self.campo_descricao.setMaximumHeight(80)
        self.campo_descricao.setPlaceholderText("Descrição da base...")
        col_dir.addWidget(label_desc)
        col_dir.addWidget(self.campo_descricao)
        
        # Botões
        botoes_layout = QHBoxLayout()
        
        self.botao_adicionar = QPushButton("Adicionar Base")
        self.botao_adicionar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.botao_adicionar.clicked.connect(self.adicionar_base)
        
        self.botao_editar = QPushButton("Editar Base")
        self.botao_editar.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.botao_editar.clicked.connect(self.editar_base)
        self.botao_editar.setEnabled(False)
        
        self.botao_limpar = QPushButton("Limpar")
        self.botao_limpar.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.botao_limpar.clicked.connect(self.limpar_campos)
        
        botoes_layout.addWidget(self.botao_adicionar)
        botoes_layout.addWidget(self.botao_editar)
        botoes_layout.addWidget(self.botao_limpar)
        
        col_dir.addLayout(botoes_layout)
        form_layout.addLayout(col_dir)
        
        layout_form.addLayout(form_layout)
        grupo_form.setLayout(layout_form)
        layout.addWidget(grupo_form)
        
        # Tabela de bases
        label_tabela = QLabel("Bases Cadastradas:")
        label_tabela.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(label_tabela)
        
        self.tabela_bases = QTableWidget()
        self.tabela_bases.setColumnCount(5)
        self.tabela_bases.setHorizontalHeaderLabels(["Nome", "Ambiente", "URL", "Descrição", "Ações"])
        self.tabela_bases.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_bases.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_bases.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabela_bases.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_bases.setStyleSheet("""
            QTableWidget {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 8px;
                border: 1px solid #bdc3c7;
                font-weight: bold;
            }
        """)
        self.tabela_bases.itemSelectionChanged.connect(self.selecionar_base)
        layout.addWidget(self.tabela_bases)
        
        # Botão fechar
        botao_fechar = QPushButton("Fechar")
        botao_fechar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        botao_fechar.clicked.connect(self.accept)
        layout.addWidget(botao_fechar)
        
        # Variáveis de controle
        self.base_selecionada = None
        
    def carregar_tabela(self):
        """Carrega as bases na tabela"""
        bases = self.gerenciador.obter_bases()
        self.tabela_bases.setRowCount(len(bases))
        
        for i, base in enumerate(bases):
            # Nome
            self.tabela_bases.setItem(i, 0, QTableWidgetItem(base['nome']))
            
            # Ambiente
            self.tabela_bases.setItem(i, 1, QTableWidgetItem(base.get('ambiente', 'HML')))
            
            # URL
            self.tabela_bases.setItem(i, 2, QTableWidgetItem(base['url']))
            
            # Descrição
            self.tabela_bases.setItem(i, 3, QTableWidgetItem(base.get('descricao', '')))
            
            # Botões de ação
            widget_acoes = QWidget()
            layout_acoes = QHBoxLayout(widget_acoes)
            layout_acoes.setContentsMargins(5, 2, 5, 2)
            
            botao_editar = QPushButton("Editar")
            botao_editar.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 4px 8px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            """)
            botao_editar.clicked.connect(lambda checked, row=i: self.carregar_base_para_edicao(row))
            
            botao_remover = QPushButton("Remover")
            botao_remover.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 4px 8px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            botao_remover.clicked.connect(lambda checked, row=i: self.remover_base(row))
            
            layout_acoes.addWidget(botao_editar)
            layout_acoes.addWidget(botao_remover)
            layout_acoes.addStretch()
            
            self.tabela_bases.setCellWidget(i, 4, widget_acoes)
    
    def carregar_base_para_edicao(self, row):
        """Carrega os dados de uma base para edição"""
        nome = self.tabela_bases.item(row, 0).text()
        ambiente = self.tabela_bases.item(row, 1).text()
        url = self.tabela_bases.item(row, 2).text()
        descricao = self.tabela_bases.item(row, 3).text()
        
        self.campo_nome.setText(nome)
        self.combo_ambiente.setCurrentText(ambiente)
        self.campo_url.setText(url)
        self.campo_descricao.setPlainText(descricao)
        
        self.base_selecionada = {'nome': nome, 'ambiente': ambiente}
        self.botao_adicionar.setEnabled(False)
        self.botao_editar.setEnabled(True)
    
    def selecionar_base(self):
        """Quando uma base é selecionada na tabela"""
        current_row = self.tabela_bases.currentRow()
        if current_row >= 0:
            self.base_selecionada = {'nome': self.tabela_bases.item(current_row, 0).text(), 'ambiente': self.tabela_bases.item(current_row, 1).text()}
    
    def adicionar_base(self):
        """Adiciona uma nova base"""
        nome = self.campo_nome.text().strip()
        url = self.campo_url.text().strip()
        descricao = self.campo_descricao.toPlainText().strip()
        ambiente = self.combo_ambiente.currentText()
        
        if not nome or not url:
            QMessageBox.warning(self, "Aviso", "Nome e URL são obrigatórios!")
            return
        
        if self.gerenciador.adicionar_base(nome, url, descricao, ambiente):
            QMessageBox.information(self, "Sucesso", f"Base '{nome}' adicionada com sucesso!")
            self.carregar_tabela()
            self.limpar_campos()
        else:
            QMessageBox.warning(self, "Erro", f"Base '{nome}' já existe!")
    
    def editar_base(self):
        """Edita uma base existente"""
        if not self.base_selecionada:
            QMessageBox.warning(self, "Aviso", "Selecione uma base para editar!")
            return
        
        novo_nome = self.campo_nome.text().strip()
        nova_url = self.campo_url.text().strip()
        nova_descricao = self.campo_descricao.toPlainText().strip()
        novo_ambiente = self.combo_ambiente.currentText()
        
        if not novo_nome or not nova_url:
            QMessageBox.warning(self, "Aviso", "Nome e URL são obrigatórios!")
            return
        
        if self.gerenciador.editar_base(self.base_selecionada['nome'], self.base_selecionada['ambiente'], novo_nome, nova_url, nova_descricao, novo_ambiente):
            QMessageBox.information(self, "Sucesso", f"Base '{self.base_selecionada['nome']}' editada com sucesso!")
            self.carregar_tabela()
            self.limpar_campos()
        else:
            QMessageBox.warning(self, "Erro", "Erro ao editar a base!")
    
    def remover_base(self, row):
        """Remove uma base"""
        nome = self.tabela_bases.item(row, 0).text()
        ambiente = self.tabela_bases.item(row, 1).text()
        
        resposta = QMessageBox.question(
            self, 
            "Confirmar Remoção", 
            f"Deseja realmente remover a base '{nome}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if resposta == QMessageBox.StandardButton.Yes:
            if self.gerenciador.remover_base(nome, ambiente):
                QMessageBox.information(self, "Sucesso", f"Base '{nome}' removida com sucesso!")
                self.carregar_tabela()
                if self.base_selecionada == {'nome': nome, 'ambiente': ambiente}:
                    self.limpar_campos()
            else:
                QMessageBox.warning(self, "Erro", "Erro ao remover a base!")
    
    def limpar_campos(self):
        """Limpa os campos do formulário"""
        self.campo_nome.clear()
        self.campo_url.clear()
        self.campo_descricao.clear()
        self.combo_ambiente.setCurrentText("HML")
        self.base_selecionada = None
        self.botao_adicionar.setEnabled(True)
        self.botao_editar.setEnabled(False)
        self.tabela_bases.clearSelection() 