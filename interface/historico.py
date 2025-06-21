import sqlite3
import json
from datetime import datetime
import os

class GerenciadorHistorico:
    """Gerencia o banco de dados do histórico de bloqueios."""
    def __init__(self, db_path='historico.sqlite'):
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.criar_tabela()

    def criar_tabela(self):
        """Cria a tabela de histórico se ela não existir."""
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS historico (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        usuario TEXT NOT NULL,
                        bases TEXT NOT NULL,
                        ambiente TEXT NOT NULL,
                        status TEXT NOT NULL,
                        detalhes TEXT
                    )
                """)
                # Adicionar a coluna 'ambiente' se não existir (para compatibilidade)
                cursor = self.conn.execute("PRAGMA table_info(historico)")
                columns = [col[1] for col in cursor.fetchall()]
                if 'ambiente' not in columns:
                    self.conn.execute("ALTER TABLE historico ADD COLUMN ambiente TEXT NOT NULL DEFAULT 'HML'")
        except sqlite3.Error as e:
            print(f"Erro ao criar/atualizar tabela de histórico: {e}")

    def adicionar_registro(self, usuario: str, bases: list, ambiente: str, status: str, detalhes: str):
        """Adiciona um novo registro ao histórico."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        bases_json = json.dumps([base.get('nome', 'N/A') for base in bases])

        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO historico (timestamp, usuario, bases, ambiente, status, detalhes) VALUES (?, ?, ?, ?, ?, ?)",
                    (timestamp, usuario, bases_json, ambiente, status, detalhes)
                )
            return True
        except sqlite3.Error as e:
            print(f"Erro ao adicionar registro ao histórico: {e}")
            return False

    def obter_registros(self):
        """Obtém todos os registros do histórico, do mais recente para o mais antigo."""
        try:
            with self.conn:
                cursor = self.conn.execute("SELECT timestamp, usuario, bases, ambiente, status, detalhes FROM historico ORDER BY id DESC")
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao obter registros do histórico: {e}")
            return []

    def limpar_historico(self):
        """Apaga todos os registros do histórico."""
        try:
            with self.conn:
                self.conn.execute("DELETE FROM historico")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao limpar histórico: {e}")
            return False

    def __del__(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()

historico_global = GerenciadorHistorico() 