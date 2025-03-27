# FLIPFLOPS - Ferramenta para Leitura Inteligente e Preparação para Processos Seletivos

![FLIPFLOPS Logo](https://via.placeholder.com/150?text=FLIPFLOPS)

FLIPFLOPS é uma ferramenta educacional baseada em IA desenvolvida para estudantes do ensino médio que estão se preparando para o exame FUVEST. A aplicação utiliza Inteligência Artificial para gerar questões de múltipla escolha, fornecer explicações detalhadas e facilitar a revisão de conteúdo, tudo em português.

## 📋 Índice

- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Comandos](#comandos)
- [Arquitetura do Código](#arquitetura-do-código)
  - [Padrão MCP](#padrão-mcp)
  - [Clean Architecture](#clean-architecture)
  - [Injeção de Dependências](#injeção-de-dependências)
- [Solução de Problemas](#solução-de-problemas)
- [Licença](#licença)

## 🔧 Requisitos

Para executar o FLIPFLOPS, você precisará de:

- Docker e Docker Compose (para execução em contêiner) **OU**
- Python 3.10+ (para execução local)
- Uma chave de API da Anthropic (Claude)
- Documentos em PDF para estudo (opcional, mas recomendado)

## 🚀 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/flipflops.git
   cd flipflops
   ```

2. Execute o script de inicialização:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

O script verificará automaticamente se você tem os requisitos necessários, criará os diretórios necessários e configurará o ambiente. Você terá a opção de executar a aplicação em um contêiner Docker ou localmente.

## ⚙️ Configuração

### Arquivo .env

Durante a primeira execução, o script `run.sh` criará um arquivo `.env` baseado no modelo `.env.example`. Você precisará editar este arquivo para adicionar sua chave de API da Anthropic:

```
CLAUDE_API_KEY=sua_chave_api_aqui
```

### Arquivo config.ini

Um arquivo `config.ini` será criado automaticamente com configurações padrão. Você pode personalizar estas configurações conforme necessário:

```ini
[API]
api_key = 
api_url = https://api.anthropic.com/v1/messages
api_model = claude-3-sonnet-20240229

[APP]
max_tokens = 4096
temperature = 0.7
language = pt-BR
log_level = INFO

[DATA]
context_file = data/FLIPFLOP.md
documents_dir = documents
embeddings_dir = data/embeddings
conversations_dir = data/conversations
topics_dir = data/topics
```

### Adicionando Documentos

Para aproveitar ao máximo o FLIPFLOPS, adicione seus materiais de estudo em formato PDF na pasta `documents/`. Estes documentos serão utilizados para:

1. Gerar perguntas personalizadas
2. Fornecer explicações baseadas no seu material
3. Extrair tópicos para exames simulados

## 💻 Uso

Após configurar o ambiente, você pode interagir com o FLIPFLOPS de duas maneiras:

### 1. Modo Docker

Após executar `./run.sh` e escolher a opção Docker:

```bash
# Conectar à aplicação em execução
docker-compose exec flipflops python main.py

# Visualizar logs
docker-compose logs -f

# Parar a aplicação
docker-compose down
```

### 2. Modo Local

Após executar `./run.sh` e escolher a opção local, a aplicação será iniciada automaticamente.

## 🔍 Comandos

O FLIPFLOPS suporta os seguintes comandos na interface CLI:

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `ajuda` | Mostra a lista de comandos disponíveis | `ajuda` |
| `pergunta` | Faz uma pergunta sobre um tópico | `pergunta O que é fotossíntese?` |
| `explicar` | Solicita uma explicação detalhada | `explicar Teorema de Pitágoras` |
| `exame` | Gera um exame sobre um tópico específico | `exame Literatura Brasileira` |
| `responder` | Responde a uma pergunta de exame | `responder 1 C` |
| `tópicos` | Lista todos os tópicos disponíveis | `tópicos` |
| `limpar` | Limpa o histórico da conversa atual | `limpar` |
| `sair` | Sai da aplicação | `sair` |

## 🏗️ Arquitetura do Código

O FLIPFLOPS segue princípios modernos de design de software, combinando Clean Architecture com o padrão Model-Context-Protocol (MCP).

### Estrutura de Diretórios

```
flipflops/
├── data/                    # Diretório para armazenamento de dados
├── documents/               # Documentos de estudo em PDF
├── src/                     # Código-fonte da aplicação
│   ├── container.py         # Container de injeção de dependências
│   ├── entities/            # Entidades do domínio
│   ├── http/                # Controladores HTTP
│   ├── infrastructure/      # Implementações concretas
│   ├── interfaces/          # Interfaces e contratos
│   ├── mcp/                 # Componentes MCP
│   │   ├── model.py         # Lógica de domínio
│   │   ├── context.py       # Gerenciamento de estado
│   │   ├── protocol.py      # Protocolos de interação
│   │   └── route.py         # Roteamento de solicitações
│   └── usecases/            # Casos de uso da aplicação
├── .env                     # Variáveis de ambiente
├── config.ini               # Configurações da aplicação
├── docker-compose.yml       # Configuração do Docker Compose
├── Dockerfile               # Configuração do Docker
├── main.py                  # Ponto de entrada da aplicação
├── README.md                # Este arquivo
└── run.sh                   # Script de execução
```

### Padrão MCP

O sistema implementa o padrão Model-Context-Protocol (MCP), que é uma evolução do MVC focada em manter o contexto das conversas e interações:

#### Model (src/mcp/model.py)

O componente Model encapsula toda a lógica de domínio relacionada a:
- Geração de perguntas e respostas
- Criação de exames
- Explicações de conceitos
- Processamento de documentos

O Model é responsável apenas pela lógica de negócios e não contém código relacionado a UI, persistência ou gerenciamento de estado.

#### Context (src/mcp/context.py)

O Context gerencia:
- O estado da conversação atual
- Histórico de interações
- Metadados do usuário
- Tópicos de interesse identificados
- Desempenho em exames anteriores

Este componente é crucial para fornecer uma experiência personalizada, mantendo o contexto entre diferentes interações.

#### Protocol (src/mcp/protocol.py)

Os Protocols definem como diferentes tipos de interações devem ser processados:
- Protocolos para perguntas e respostas
- Protocolos para explicações de conceitos
- Protocolos para geração e avaliação de exames
- Protocolos para gerenciamento de sessão

Cada protocolo define um fluxo específico de interação, garantindo consistência na experiência do usuário.

#### Route (src/mcp/route.py)

O componente Route:
- Recebe solicitações dos controladores
- Determina qual protocolo deve processar cada solicitação
- Coordena a interação entre Model e Context
- Retorna respostas formatadas para a camada de apresentação

### Clean Architecture

A aplicação segue os princípios da Clean Architecture:

1. **Independência de Frameworks**: O core da aplicação não depende de frameworks externos.
2. **Testabilidade**: Todos os componentes são projetados para serem facilmente testáveis.
3. **Independência de UI**: A lógica de negócios é separada da interface do usuário.
4. **Independência de Banco de Dados**: A persistência é uma preocupação externa à lógica central.
5. **Independência de Agentes Externos**: A aplicação pode funcionar sem depender de serviços externos.

### Injeção de Dependências

O arquivo `src/container.py` implementa um container de injeção de dependências que:
- Inicializa todos os componentes da aplicação
- Gerencia o ciclo de vida de objetos
- Conecta implementações concretas às interfaces
- Facilita a substituição de componentes para testes

## ❓ Solução de Problemas

### Problemas com a API Claude

Se você encontrar erros relacionados à API Claude:
- Verifique se sua chave API está correta no arquivo `.env`
- Confirme seu limite de uso da API
- Verifique se o modelo especificado (`claude-3-sonnet-20240229`) está disponível

### Problemas com Docker

Se o contêiner não iniciar:
```bash
# Verificar logs detalhados
docker-compose logs --tail=100 flipflops

# Verificar status do contêiner
docker-compose ps
```

### Problemas com Documentos

Se seus documentos não estão sendo processados corretamente:
1. Certifique-se de que estão em formato PDF sem proteção por senha
2. Verifique se o caminho está correto em `config.ini`
3. Execute o comando abaixo para reindexar os documentos:

```bash
# No modo Docker
docker-compose exec flipflops python main.py --reindex

# No modo local
python main.py --reindex
```

### Erros de Memória

Se a aplicação estiver consumindo muita memória:
1. Reduza o valor de `max_tokens` no arquivo `config.ini`
2. Processe menos documentos simultaneamente
3. Utilize o modo Docker que tem gerenciamento de recursos

## 📄 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
