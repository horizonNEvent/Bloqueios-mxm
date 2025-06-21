#!/usr/bin/env python3
"""
Sistema de Bloqueio de Usuários - Interface Gráfica
Executa a interface gráfica para o sistema de bloqueio
"""

import sys
import os

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos da interface
from interface.interface_bloqueio import main

if __name__ == "__main__":
    main() 