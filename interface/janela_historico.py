from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from .historico import historico_global
import json

class JanelaHistorico(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.carregar_historico()

    def initUI(self):
        self.setWindowTitle("Histórico de Bloqueios")
        self.setGeometry(150, 150, 1000, 700)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        titulo = QLabel("Histórico de Bloqueios")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(titulo)

        # Filtro
        filtro_layout = QHBoxLayout()
        filtro_label = QLabel("Buscar no histórico:")
        self.filtro_campo = QLineEdit()
        self.filtro_campo.setPlaceholderText("Digite para filtrar por usuário, base, status...")
        self.filtro_campo.textChanged.connect(self.filtrar_historico)
        filtro_layout.addWidget(filtro_label)
        filtro_layout.addWidget(self.filtro_campo)
        layout.addLayout(filtro_layout)

        self.tabela_historico = QTableWidget()
        self.tabela_historico.setColumnCount(6)
        self.tabela_historico.setHorizontalHeaderLabels(["Data/Hora", "Usuário", "Ambiente", "Bases", "Status", "Detalhes"])
        self.tabela_historico.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_historico.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_historico.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_historico.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_historico.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabela_historico.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.tabela_historico.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela_historico.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela_historico.setWordWrap(True)
        layout.addWidget(self.tabela_historico)

        botoes_layout = QHBoxLayout()
        botao_limpar = QPushButton("Limpar Histórico")
        botao_limpar.clicked.connect(self.limpar_historico)
        botoes_layout.addStretch()
        botoes_layout.addWidget(botao_limpar)
        layout.addLayout(botoes_layout)
        
    def carregar_historico(self):
        registros = historico_global.obter_registros()
        self.tabela_historico.setRowCount(len(registros))
        self.tabela_historico.setSortingEnabled(False)

        for row, registro in enumerate(registros):
            timestamp, usuario, bases_json, ambiente, status, detalhes = registro
            
            try:
                bases_list = json.loads(bases_json)
                bases_str = ", ".join(bases_list)
            except (json.JSONDecodeError, TypeError):
                bases_str = str(bases_json)

            self.tabela_historico.setItem(row, 0, QTableWidgetItem(timestamp))
            self.tabela_historico.setItem(row, 1, QTableWidgetItem(usuario))
            
            ambiente_item = QTableWidgetItem(ambiente)
            if ambiente == "PROD":
                ambiente_item.setForeground(QColor("#C0392B")) # Vermelho
                ambiente_item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            else:
                ambiente_item.setForeground(QColor("#2980B9")) # Azul
            self.tabela_historico.setItem(row, 2, ambiente_item)

            self.tabela_historico.setItem(row, 3, QTableWidgetItem(bases_str))
            
            status_item = QTableWidgetItem(status)
            if "Falha" in status or "Erro" in status:
                status_item.setForeground(QColor("red"))
            else:
                status_item.setForeground(QColor("#006400")) # DarkGreen
            self.tabela_historico.setItem(row, 4, status_item)

            self.tabela_historico.setItem(row, 5, QTableWidgetItem(detalhes))

        self.tabela_historico.resizeRowsToContents()
        self.tabela_historico.setSortingEnabled(True)

    def filtrar_historico(self, texto):
        """Filtra a tabela de histórico."""
        texto_lower = texto.lower()
        for i in range(self.tabela_historico.rowCount()):
            visivel = False
            if texto_lower == "":
                visivel = True
            else:
                for j in range(self.tabela_historico.columnCount()):
                    item = self.tabela_historico.item(i, j)
                    if item and texto_lower in item.text().lower():
                        visivel = True
                        break
            self.tabela_historico.setRowHidden(i, not visivel)

    def limpar_historico(self):
        resposta = QMessageBox.question(self, "Confirmar", "Tem certeza que deseja apagar todo o histórico de bloqueios?\nEsta ação não pode ser desfeita.",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if resposta == QMessageBox.StandardButton.Yes:
            if historico_global.limpar_historico():
                QMessageBox.information(self, "Sucesso", "Histórico limpo com sucesso.")
                self.carregar_historico()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível limpar o histórico.") 