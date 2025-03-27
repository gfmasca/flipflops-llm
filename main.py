#!/usr/bin/env python3
"""
FLIPFLOPS - Ferramenta para Leitura Inteligente e Preparação 
para Processos Seletivos

Ponto de entrada principal da aplicação FLIPFLOPS, responsável por inicializar
componentes, configurar o sistema e iniciar a interface de usuário.
"""
import os
import sys
import signal
import argparse
import logging
from logging.handlers import RotatingFileHandler
import traceback

from src.container import Container


# Configuração inicial de logging
def setup_logging(log_level: str, log_file: str = None) -> None:
    """
    Configura o sistema de logging com o nível especificado.
    
    Args:
        log_level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho opcional para arquivo de log
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Nível de log inválido: {log_level}")
    
    # Formato do log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configuração básica
    handlers = []
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    handlers.append(console_handler)
    
    # Handler para arquivo, se especificado
    if log_file:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    
    # Configurar o logging
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=handlers
    )
    
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Silenciar logs muito verbosos
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


# Handler para sinais de interrupção
def setup_signal_handlers(container) -> None:
    """
    Configura os handlers para sinais do sistema.
    
    Args:
        container: Contêiner de dependências
    """
    def signal_handler(sig, frame):
        logging.info("Sinal de interrupção recebido. Encerrando aplicação...")
        sys.exit(0)
    
    # Registra handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


# Validação de ambiente
def check_environment() -> None:
    """
    Verifica se as variáveis de ambiente necessárias estão configuradas.
    
    Raises:
        EnvironmentError: Se uma variável de ambiente obrigatória estiver faltando
    """
    required_vars = ['CLAUDE_API_KEY']
    
    for var in required_vars:
        if not os.getenv(var):
            logging.error(
                f"Variável de ambiente obrigatória não configurada: {var}"
            )
            raise EnvironmentError(
                f"A variável de ambiente {var} é obrigatória. "
                f"Por favor, adicione-a ao arquivo .env ou ao ambiente."
            )


# Função principal
def main():
    """Função principal para iniciar a aplicação FLIPFLOPS."""
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description='FLIPFLOPS - Ferramenta para Leitura Inteligente e '
                    'Preparação para Processos Seletivos'
    )
    
    parser.add_argument(
        '--config', 
        type=str, 
        default='config.ini',
        help='Caminho para o arquivo de configuração'
    )
    
    parser.add_argument(
        '--data-dir', 
        type=str, 
        default='data',
        help='Diretório para armazenamento de dados'
    )
    
    parser.add_argument(
        '--log-level', 
        type=str, 
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Nível de logging'
    )
    
    parser.add_argument(
        '--log-file', 
        type=str, 
        help='Arquivo para salvar logs'
    )
    
    # Parse dos argumentos
    args = parser.parse_args()
    
    try:
        # Configurar logging
        setup_logging(args.log_level, args.log_file)
        logging.info("Iniciando FLIPFLOPS...")
        
        # Verificar ambiente
        try:
            check_environment()
        except EnvironmentError as e:
            logging.error(f"Erro de ambiente: {e}")
            print(f"\nERRO: {e}\n")
            sys.exit(1)
        
        # Criar e inicializar container
        container = Container(
            config_path=args.config,
            data_dir=args.data_dir
        )
        
        # Configurar handlers de sinais
        setup_signal_handlers(container)
        
        # Obter interface CLI
        cli = container.get_cli()
        
        # Exibir mensagem de boas-vindas
        logging.info("Aplicação iniciada com sucesso.")
        
        # Iniciar a CLI
        cli.start()
        
    except KeyboardInterrupt:
        logging.info("Aplicação encerrada pelo usuário.")
    except Exception as e:
        logging.error(f"Erro fatal: {str(e)}")
        logging.error(traceback.format_exc())
        print(f"\nERRO FATAL: {str(e)}")
        print("Verifique os logs para mais detalhes.")
        sys.exit(1)
    finally:
        logging.info("Aplicação encerrada.")


if __name__ == "__main__":
    main() 
