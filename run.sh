#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner function
print_banner() {
    echo -e "${GREEN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                      FLIPFLOPS LAUNCHER                       ║"
    echo "║           Ferramenta para Leitura Inteligente e               ║"
    echo "║          Preparação para Processos Seletivos (FUVEST)         ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Arquivo de ambiente (.env) não encontrado.${NC}"
        echo "Criando um novo arquivo .env..."
        
        if [ -f .env.example ]; then
            cp .env.example .env
            echo -e "${GREEN}Arquivo .env criado a partir do exemplo.${NC}"
            echo -e "${YELLOW}Por favor, edite o arquivo .env para definir sua chave API da Anthropic.${NC}"
            echo "Pressione qualquer tecla para abrir o arquivo para edição..."
            read -n 1
            ${EDITOR:-vi} .env
        else
            echo "CLAUDE_API_KEY=" > .env
            echo -e "${GREEN}Arquivo .env vazio criado.${NC}"
            echo -e "${YELLOW}Por favor, adicione sua chave API da Anthropic ao arquivo .env:${NC}"
            echo "CLAUDE_API_KEY=sua_chave_api_aqui"
        fi
        
        return 1
    fi
    
    # Check if CLAUDE_API_KEY is set
    if ! grep -q "CLAUDE_API_KEY=" .env || grep -q "CLAUDE_API_KEY=$" .env; then
        echo -e "${RED}CLAUDE_API_KEY não está definida no arquivo .env.${NC}"
        echo -e "${YELLOW}Por favor, adicione sua chave API da Anthropic ao arquivo .env.${NC}"
        echo "Pressione qualquer tecla para abrir o arquivo para edição..."
        read -n 1
        ${EDITOR:-vi} .env
        return 1
    fi
    
    return 0
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker não está instalado neste sistema.${NC}"
        echo -e "${YELLOW}Por favor, instale o Docker antes de executar este script.${NC}"
        echo "Instruções de instalação: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}O serviço Docker não está em execução ou você não tem permissões suficientes.${NC}"
        echo -e "${YELLOW}Por favor, inicie o serviço Docker e certifique-se de que você tenha as permissões adequadas.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Docker está instalado e em execução.${NC}"
}

# Check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}Docker Compose não está instalado neste sistema.${NC}"
        echo -e "${YELLOW}Por favor, instale o Docker Compose antes de executar este script.${NC}"
        echo "Instruções de instalação: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    echo -e "${GREEN}Docker Compose está instalado.${NC}"
}

# Check if required Python packages are installed (for local mode)
check_python_packages() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 não está instalado neste sistema.${NC}"
        echo -e "${YELLOW}Por favor, instale o Python 3 antes de executar este script em modo local.${NC}"
        exit 1
    fi
    
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}Pip3 não está instalado neste sistema.${NC}"
        echo -e "${YELLOW}Por favor, instale o pip3 antes de executar este script em modo local.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Python 3 e pip3 estão instalados.${NC}"
    
    # Check for virtual environment
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Ambiente virtual não encontrado. Criando...${NC}"
        python3 -m venv venv
        echo -e "${GREEN}Ambiente virtual criado.${NC}"
    fi
    
    # Activate virtual environment
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
    
    # Install dependencies
    echo "Instalando dependências..."
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Dependências instaladas com sucesso.${NC}"
    else
        echo -e "${RED}Falha ao instalar dependências.${NC}"
        exit 1
    fi
}

# Check if folders exist
check_folders() {
    # Ensure the data directory exists
    if [ ! -d "data" ]; then
        echo "Criando diretório de dados..."
        mkdir -p data/documents data/embeddings data/conversations data/topics
        echo -e "${GREEN}Diretórios de dados criados.${NC}"
    fi
    
    # Create documents folder if it doesn't exist
    if [ ! -d "documents" ]; then
        echo "Criando diretório de documentos..."
        mkdir -p documents
        echo -e "${GREEN}Diretório de documentos criado.${NC}"
        echo -e "${YELLOW}Por favor, adicione seus documentos PDF à pasta 'documents'.${NC}"
    fi
    
    # Create config if it doesn't exist
    if [ ! -f "config.ini" ]; then
        echo "Criando arquivo de configuração padrão..."
        cat > config.ini << EOF
[API]
api_key = 
api_url = https://api.anthropic.com/v1/messages
api_model = claude-3-sonnet-20240229

[APP]
max_tokens = 4096
temperature = 0.7

[DATA]
context_file = data/FLIPFLOP.md
documents_dir = documents
EOF
        echo -e "${GREEN}Arquivo de configuração criado.${NC}"
    fi
}

# Pull the latest Python image
pull_python_image() {
    echo "Baixando a imagem mais recente do Python..."
    docker pull python:3.11-slim
    echo -e "${GREEN}Imagem Python baixada com sucesso.${NC}"
}

# Build the application
build_app() {
    echo "Construindo a aplicação Flipflops..."
    docker-compose build
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Aplicação Flipflops construída com sucesso.${NC}"
    else
        echo -e "${RED}Falha ao construir a aplicação.${NC}"
        echo "Por favor, verifique as mensagens de erro acima."
        exit 1
    fi
}

# Start the application in Docker
start_app_docker() {
    echo "Iniciando a aplicação Flipflops no Docker..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}A aplicação Flipflops está em execução!${NC}"
    else
        echo -e "${RED}Falha ao iniciar a aplicação.${NC}"
        echo "Por favor, verifique as mensagens de erro acima."
        exit 1
    fi
}

# Start the application locally
start_app_local() {
    echo "Iniciando a aplicação Flipflops localmente..."
    echo -e "${YELLOW}Pressione Ctrl+C para sair da aplicação.${NC}"
    
    # Activate virtual environment if not already activated
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
    
    # Run the application
    python main.py --config config.ini --data-dir data --log-level INFO
}

# Show application logs
show_logs() {
    echo -e "${YELLOW}Exibindo logs da aplicação. Pressione Ctrl+C para sair dos logs (a aplicação continuará em execução).${NC}"
    docker-compose logs -f
}

# Print usage instructions for Docker mode
print_docker_instructions() {
    echo -e "${GREEN}==== INSTRUÇÕES DE USO DO FLIPFLOPS (DOCKER) ====${NC}"
    echo -e "A aplicação está em execução em segundo plano."
    echo -e "Para interagir com ela:"
    echo -e "  ${YELLOW}* Adicione seus documentos PDF à pasta 'documents'${NC}"
    echo -e "  ${YELLOW}* Conecte-se à aplicação:${NC}"
    echo -e "    docker-compose exec flipflops python main.py"
    echo
    echo -e "Para parar a aplicação:"
    echo -e "  docker-compose down"
    echo
    echo -e "Para visualizar logs:"
    echo -e "  docker-compose logs -f"
    echo
    echo -e "${GREEN}Bons estudos com o Flipflops!${NC}"
}

# Print usage instructions for local mode
print_local_instructions() {
    echo -e "${GREEN}==== INSTRUÇÕES DE USO DO FLIPFLOPS (LOCAL) ====${NC}"
    echo -e "A aplicação está em execução."
    echo -e "Comandos disponíveis:"
    echo -e "  ${YELLOW}* ajuda${NC} - Exibe a lista de comandos disponíveis"
    echo -e "  ${YELLOW}* pergunta <sua pergunta>${NC} - Faz uma pergunta"
    echo -e "  ${YELLOW}* explicar <conceito>${NC} - Solicita explicação de um conceito"
    echo -e "  ${YELLOW}* exame <tópico>${NC} - Gera um exame sobre um tópico"
    echo -e "  ${YELLOW}* tópicos${NC} - Lista todos os tópicos disponíveis"
    echo -e "  ${YELLOW}* limpar${NC} - Limpa o histórico da conversa"
    echo -e "  ${YELLOW}* sair${NC} - Sai da aplicação"
    echo
    echo -e "${GREEN}Bons estudos com o Flipflops!${NC}"
}

# Main execution
main() {
    print_banner
    
    # Check environment and dependencies
    check_env_file
    check_folders
    
    # Ask if user wants to run in Docker or locally
    echo -e "${YELLOW}Como você deseja executar o FLIPFLOPS?${NC}"
    echo "1) Docker (recomendado para uso normal)"
    echo "2) Local (recomendado para desenvolvimento)"
    read -p "Escolha (1/2): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            # Docker mode
            check_docker
            check_docker_compose
            
            # Confirm API key is set
            if [ $? -ne 0 ]; then
                echo -e "${YELLOW}Por favor, reinicie o script após definir sua chave API.${NC}"
                exit 1
            fi
            
            # Ask user if they want to proceed
            echo -e "${YELLOW}Este script construirá e iniciará a aplicação Flipflops no Docker.${NC}"
            read -p "Deseja continuar? (s/n): " -n 1 -r
            echo
            
            if [[ ! $REPLY =~ ^[Ss]$ ]]; then
                echo -e "${YELLOW}Operação cancelada.${NC}"
                exit 0
            fi
            
            # Build and start the application
            pull_python_image
            build_app
            start_app_docker
            
            # Print instructions
            print_docker_instructions
            
            # Ask if user wants to see logs
            read -p "Deseja ver os logs da aplicação? (s/n): " -n 1 -r
            echo
            
            if [[ $REPLY =~ ^[Ss]$ ]]; then
                show_logs
            fi
            ;;
        2)
            # Local mode
            check_python_packages
            
            # Confirm API key is set
            if [ $? -ne 0 ]; then
                echo -e "${YELLOW}Por favor, reinicie o script após definir sua chave API.${NC}"
                exit 1
            fi
            
            # Print instructions
            print_local_instructions
            
            # Start the application
            start_app_local
            ;;
        *)
            echo -e "${RED}Opção inválida. Por favor, execute o script novamente.${NC}"
            exit 1
            ;;
    esac
}

# Run the main function
main
