from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime
import os
import uuid
import json
from PyQt6.QtCore import QObject, pyqtSignal
from .historico import historico_global

class AgendadorLogger(QObject):
    log_signal = pyqtSignal(str)

log_emitter = AgendadorLogger()

class Agendador:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Agendador, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path='agendamentos.sqlite'):
        if not hasattr(self, 'scheduler'):
            # Garante que o diretório para o DB exista, se necessário
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            
            jobstores = {
                'default': SQLAlchemyJobStore(url=f'sqlite:///{db_path}')
            }
            executors = {
                'default': ThreadPoolExecutor(20)
            }
            job_defaults = {
                'coalesce': False,
                'max_instances': 3
            }
            
            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults
            )
            
            self.scheduler.start()
            print("Agendador iniciado.")

    def agendar_bloqueio(self, data_hora: datetime, usuario: str, bases: list, ambiente: str):
        """Agenda uma nova tarefa de bloqueio."""
        job_id = str(uuid.uuid4())
        
        log_emitter.log_signal.emit(f"Agendando bloqueio para {usuario} em {data_hora.strftime('%d/%m/%Y %H:%M')} no ambiente {ambiente}")
        
        self.scheduler.add_job(
            self.executar_bloqueio_agendado,
            'date',
            run_date=data_hora,
            args=[job_id, usuario, bases, ambiente],
            id=job_id,
            name=f"Bloqueio de {usuario} ({ambiente})"
        )
        return job_id

    @staticmethod
    def executar_bloqueio_agendado(job_id: str, usuario: str, bases: list, ambiente: str):
        """Função que será executada pela tarefa agendada."""
        from interface.interface_bloqueio import BloqueioThread

        log_emitter.log_signal.emit(f"--- [AGENDADO] INICIANDO BLOQUEIO PARA '{usuario}' (Job: {job_id}) no ambiente {ambiente} ---")

        def on_log(msg):
            log_emitter.log_signal.emit(f"[AGENDADO] {msg}")

        def on_finish(sucesso, msg_final):
            status_str = "Sucesso" if sucesso else "Falha"
            log_emitter.log_signal.emit(f"--- [AGENDADO] FINALIZADO (Job: {job_id}) ---")
            on_log(f"Resultado: {status_str}")
            on_log(msg_final)
            historico_global.adicionar_registro(usuario, bases, ambiente, status_str, msg_final)
            
        try:
            # Criamos uma thread para não bloquear o agendador
            thread_bloqueio = BloqueioThread(usuario, bases)
            
            # Conectamos os sinais da thread aos callbacks
            thread_bloqueio.log_signal.connect(on_log)
            thread_bloqueio.finished_signal.connect(on_finish)
            
            # Iniciamos a thread e esperamos ela terminar
            thread_bloqueio.start()
            thread_bloqueio.wait()

        except Exception as e:
            on_finish(False, f"Falha crítica na execução da tarefa agendada: {e}")

    def obter_tarefas(self):
        """Retorna todas as tarefas agendadas."""
        return self.scheduler.get_jobs()

    def cancelar_tarefa(self, job_id: str):
        """Cancela uma tarefa agendada."""
        try:
            self.scheduler.remove_job(job_id)
            return True
        except Exception as e:
            print(f"Erro ao cancelar tarefa {job_id}: {e}")
            return False

    def desligar(self):
        """Desliga o agendador de forma segura."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("Agendador desligado.")

# Singleton para garantir uma única instância do agendador
agendador_global = Agendador() 