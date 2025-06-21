# Interface Gráfica - Sistema de Bloqueio de Usuários

## Descrição
Interface gráfica desenvolvida com PyQt6 para o sistema de bloqueio de usuários do MXM-WebManager, com suporte a múltiplas bases.

## Funcionalidades
- **Interface gráfica intuitiva e moderna**
- **Seleção de base** - Escolha em qual base o usuário será bloqueado
- **Gerenciamento de bases** - Adicione, edite e remova bases do sistema
- Campo para inserir o nome do usuário a ser bloqueado
- Botão para iniciar o processo de bloqueio
- Área de log em tempo real mostrando o progresso
- Barra de progresso durante a execução
- Execução em thread separada para não travar a interface
- Mensagens de sucesso e erro

## Como Executar

### Pré-requisitos
1. Ter o ambiente virtual ativado
2. Ter as dependências instaladas (PyQt6, playwright)
3. Ter o arquivo `credentials.json` configurado na raiz do projeto

### Execução
```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Executar a interface
python interface/main_interface.py
```

## Estrutura dos Arquivos
- `interface_bloqueio.py` - Interface gráfica principal
- `gerenciador_bases.py` - Classe para gerenciar as bases
- `janela_gerenciar_bases.py` - Janela para gerenciar bases
- `main_interface.py` - Arquivo de execução
- `__init__.py` - Arquivo do pacote
- `README.md` - Esta documentação

## Gerenciamento de Bases

### Bases Padrão
O sistema vem com duas bases pré-configuradas:
- **RIOENERGY** - `https://mxmhml-rioenergy.rsmbrasil.com.br/?grupo=RIOENERGYHOM`
- **ACAL003** - `https://mxmhml-acal003.rsmbrasil.com.br/?grupo=ACAL003HOM`

### Adicionar Nova Base
1. Clique no botão "Gerenciar Bases"
2. Preencha os campos:
   - **Nome da Base**: Nome identificador (ex: MINHAEMPRESA)
   - **URL da Base**: URL completa do sistema
   - **Descrição**: Descrição opcional da base
3. Clique em "Adicionar Base"

### Editar Base Existente
1. Clique no botão "Gerenciar Bases"
2. Selecione a base na tabela
3. Clique em "Editar" na linha da base
4. Modifique os campos desejados
5. Clique em "Editar Base"

### Remover Base
1. Clique no botão "Gerenciar Bases"
2. Clique em "Remover" na linha da base desejada
3. Confirme a remoção

## Características da Interface
- **Design Moderno**: Interface com cores e estilos modernos
- **Responsiva**: A interface não trava durante a execução
- **Log em Tempo Real**: Mostra cada etapa do processo
- **Validação**: Verifica se o usuário e base foram informados
- **Feedback Visual**: Barra de progresso e mensagens de status
- **Gerenciamento de Bases**: Interface completa para administrar bases

## Fluxo de Uso
1. Selecione a base onde o usuário será bloqueado
2. Digite o nome do usuário no campo de entrada
3. Clique no botão "Bloquear Usuário"
4. Acompanhe o progresso na área de log
5. Aguarde a conclusão do processo
6. Receba confirmação de sucesso ou erro

## Tratamento de Erros
- Validação de entrada do usuário
- Validação de seleção de base
- Tratamento de erros de conexão
- Tratamento de erros de navegação
- Mensagens informativas para o usuário
- Validação de bases duplicadas

## Arquivo de Configuração
As bases são armazenadas no arquivo `bases.json` na raiz do projeto:

```json
{
  "bases": [
    {
      "nome": "RIOENERGY",
      "url": "https://mxmhml-rioenergy.rsmbrasil.com.br/?grupo=RIOENERGYHOM",
      "descricao": "Base Rio Energy"
    }
  ]
}
``` 