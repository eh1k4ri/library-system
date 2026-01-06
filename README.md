# Library System API

Sistema de gerenciamento de biblioteca desenvolvido com FastAPI, PostgreSQL e SQLAlchemy. Permite gerenciar usuários, livros e empréstimos com recursos de cache, validação robusta e tratamento de erros customizados.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Arquitetura e Decisões Técnicas](#-arquitetura-e-decisões-técnicas)
- [Instalação e Execução](#-instalação-e-execução)
- [Exemplos de Uso](#-exemplos-de-uso)
- [Documentação da API](#-documentação-da-api)
- [Testes](#-testes)
- [Estrutura do Projeto](#-estrutura-do-projeto)

## ✨ Funcionalidades

### Gestão de Usuários
- ✅ Cadastro de usuários com validação de email
- ✅ Listagem de usuários com paginação
- ✅ Consulta de usuário por chave UUID
- ✅ Listagem de empréstimos por usuário
- ✅ Normalização automática de emails
- ✅ Cache de consultas frequentes

### Gestão de Livros
- ✅ Cadastro de livros
- ✅ Listagem de livros com paginação
- ✅ Consulta de livro por chave UUID
- ✅ Verificação de disponibilidade com data prevista de retorno
- ✅ Controle de status (disponível/emprestado/manutenção)
- ✅ Cache de consultas frequentes

### Gestão de Empréstimos
- ✅ Criação de empréstimos com validações:
  - Usuário deve estar ativo
  - Livro deve estar disponível
  - Limite de 3 empréstimos ativos por usuário
- ✅ Devolução de livros com cálculo automático de multas (R$ 2,00/dia de atraso)
- ✅ Listagem de empréstimos com filtros:
  - Por status (ativo/retornado)
  - Empréstimos em atraso
- ✅ Histórico completo de eventos por empréstimo
- ✅ Prazo padrão de 14 dias
- ✅ Cache de consultas frequentes

### Recursos Técnicos
- ✅ Documentação interativa Swagger/OpenAPI em `/docs`
- ✅ Healthcheck endpoint
- ✅ Logging estruturado com trace_id e query parameters
- ✅ Validação Pydantic v2 com validators customizados
- ✅ Tratamento de erros com códigos customizados
- ✅ Paginação configurável em todos os endpoints de listagem
- ✅ Cache em memória thread-safe com TTL
- ✅ Validação centralizada de UUIDs
- ✅ Normalização e limpeza de strings

## 🏗️ Arquitetura e Decisões Técnicas

### Padrão Arquitetural

**Service Layer Pattern** com separação clara de responsabilidades:

```
app/
├── api/            # Camada de apresentação (routers)
├── services/       # Camada de lógica de negócio
├── models/         # Camada de dados (SQLAlchemy ORM)
├── schemas/        # Validação e serialização (Pydantic)
├── core/           # Infraestrutura (erros, logging, middlewares)
└── utils/          # Utilitários compartilhados
```

**Justificativa:**
- **Separação de responsabilidades**: routers lidam apenas com HTTP, services com regras de negócio
- **Testabilidade**: services podem ser testados isoladamente
- **Manutenibilidade**: mudanças em lógica de negócio não afetam a camada HTTP
- **Reusabilidade**: services podem ser chamados de diferentes contextos

### Decisões de Design

#### 1. **Cache em Memória (In-Memory) ao invés de Redis**

**Implementação:** `app/utils/cache.py`
- Cache thread-safe com `RLock`
- TTL configurável por entrada (padrão: 60s para entidades, 300s para status)
- Limite de 1000 itens com limpeza automática

**Justificativa:**
- ✅ **Simplicidade**: sem dependências externas para deploy
- ✅ **Performance**: acesso direto à memória é mais rápido que rede
- ✅ **Adequado ao contexto**: status de livros/usuários mudam pouco, cache local suficiente
- ✅ **Escalabilidade futura**: interface permite trocar por Redis sem refatoração

**Trade-offs:**
- ❌ Cache não compartilhado entre instâncias (aceitável para MVP)
- ❌ Perdido em restart (aceitável, dados não críticos)

#### 2. **UUIDs como Identificadores Públicos**

**Implementação:** Chaves UUID (`user_key`, `book_key`, `loan_key`) separadas de IDs internos

**Justificativa:**
- ✅ **Segurança**: IDs sequenciais vazam informações de volume
- ✅ **Distribuição**: UUIDs permitem geração descentralizada
- ✅ **Integrações**: padrão amplamente adotado em APIs

#### 3. **Tratamento de Erros Customizado**

**Implementação:** `app/core/errors.py` - hierarquia de erros com códigos únicos (LBS001-LBS012)

```python
class EmailAlreadyRegistered(CustomError):
    code = "LBS001"  # Library System Business Error 001
    title = "Email Already Registered"
```

**Justificativa:**
- ✅ **Rastreabilidade**: códigos únicos facilitam suporte e logs
- ✅ **Internacionalização**: mensagens estruturadas (title/description/translation)
- ✅ **Consistência**: formato padronizado de resposta de erro
- ✅ **Cliente-amigável**: clientes podem programar contra códigos estáveis

#### 4. **Validação Centralizada com Pydantic**

**Implementação:** 
- `app/utils/text.py`: normalização de strings e emails
- `app/utils/uuid.py`: validação de UUIDs
- Validators Pydantic v2 em schemas

**Justificativa:**
- ✅ **DRY**: lógica de validação em um só lugar
- ✅ **Consistência**: mesma regra aplicada em todo o sistema
- ✅ **Manutenibilidade**: mudanças em uma função refletem globalmente
- ✅ **Tipagem**: validators aproveitam type hints do Python

#### 5. **Logging Estruturado com Middleware**

**Implementação:** `app/core/middlewares/logging.py`

Registra para cada requisição:
- `trace_id` único (UUID)
- Path, método, query parameters
- Status code e duração
- Timestamp ISO 8601

**Justificativa:**
- ✅ **Observabilidade**: trace_id permite rastrear requisição completa
- ✅ **Debugging**: query params e duração ajudam a identificar problemas
- ✅ **Auditoria**: registro completo de todas as operações
- ✅ **Performance**: identificar endpoints lentos

#### 6. **Paginação Obrigatória**

**Implementação:** `app/api/deps.py` - `PaginationParams` com defaults (page=1, per_page=100)

**Justificativa:**
- ✅ **Performance**: evita carregar milhares de registros
- ✅ **Escalabilidade**: permite crescimento do dataset
- ✅ **UX**: carregamento progressivo em frontends

#### 7. **Alembic para Migrações**

**Implementação:** `alembic/` - histórico versionado de schema

**Justificativa:**
- ✅ **Rastreabilidade**: cada mudança de schema é documentada
- ✅ **Reversibilidade**: rollback em caso de problemas
- ✅ **CI/CD**: migrações automatizadas em pipelines
- ✅ **Colaboração**: equipe sincronizada com mesma versão

#### 8. **Event Sourcing Parcial para Empréstimos**

**Implementação:** `LoanEvent` registra mudanças de status

**Justificativa:**
- ✅ **Auditoria**: histórico completo de cada empréstimo
- ✅ **Debugging**: rastrear quando/como status mudou
- ✅ **Analytics**: analisar padrões de uso
- ✅ **Compliance**: registros imutáveis para auditoria

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.11+
- PostgreSQL 15+ (ou Docker)
- Git

### 1. Clone o Repositório

```bash
git clone <repository-url>
cd library_system
```

### 2. Configure o Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Database
DATABASE_URL=postgresql://admin:password123@localhost:5432/library_db

# Application
LOG_LEVEL=INFO
```

### 5. Inicie o Banco de Dados

#### Opção A: Docker Compose (Recomendado)

```bash
docker-compose up -d
```

Isso iniciará:
- PostgreSQL na porta 5432
- Redis na porta 6379 (opcional)
- RabbitMQ na porta 5672 (opcional)

#### Opção B: PostgreSQL Local

Configure sua instância local e ajuste `DATABASE_URL` no `.env`.

### 6. Execute as Migrações

```bash
alembic upgrade head
```

Isso criará todas as tabelas necessárias:
- `users` e `user_status`
- `books` e `book_status`
- `loans`, `loan_status` e `loan_events`

### 7. Inicie a Aplicação

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Healthcheck**: http://localhost:8000/healthcheck

### 8. Execute os Testes

```bash
# Todos os testes
pytest

# Com detalhes
pytest -vv

# Com coverage
pytest --cov=app --cov-report=html
```

## 📖 Exemplos de Uso

### Usando a Documentação Interativa (Recomendado)

Acesse http://localhost:8000/docs para usar a interface Swagger:
- Visualize todos os endpoints
- Teste requisições diretamente no navegador
- Veja schemas de request/response

### Usando cURL

#### 1. Criar Usuário

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao.silva@example.com"
  }'
```

**Resposta:**
```json
{
  "user_key": "123e4567-e89b-12d3-a456-426614174000",
  "name": "João Silva",
  "email": "joao.silva@example.com",
  "status": {
    "enumerator": "active",
    "name": "Active"
  },
  "created_at": "2026-01-06T10:30:00Z"
}
```

#### 2. Criar Livro

```bash
curl -X POST "http://localhost:8000/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin"
  }'
```

**Resposta:**
```json
{
  "book_key": "987fcdeb-51a2-43f7-b123-123456789abc",
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "status": {
    "enumerator": "available",
    "name": "Available"
  },
  "created_at": "2026-01-06T10:31:00Z"
}
```

#### 3. Criar Empréstimo

```bash
curl -X POST "http://localhost:8000/loans/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_key": "123e4567-e89b-12d3-a456-426614174000",
    "book_key": "987fcdeb-51a2-43f7-b123-123456789abc"
  }'
```

**Resposta:**
```json
{
  "loan_key": "456def78-90ab-cdef-1234-567890abcdef",
  "user": {
    "user_key": "123e4567-e89b-12d3-a456-426614174000",
    "name": "João Silva",
    "email": "joao.silva@example.com"
  },
  "book": {
    "book_key": "987fcdeb-51a2-43f7-b123-123456789abc",
    "title": "Clean Code",
    "author": "Robert C. Martin"
  },
  "status": {
    "enumerator": "active",
    "name": "Active"
  },
  "start_date": "2026-01-06T10:32:00Z",
  "due_date": "2026-01-20T10:32:00Z",
  "return_date": null,
  "fine_amount": 0.0
}
```

#### 4. Verificar Disponibilidade do Livro

```bash
curl "http://localhost:8000/books/987fcdeb-51a2-43f7-b123-123456789abc/availability"
```

**Resposta (emprestado):**
```json
{
  "available": false,
  "status": "loaned",
  "expected_return_date": "2026-01-20T10:32:00Z"
}
```

#### 5. Devolver Livro

```bash
curl -X POST "http://localhost:8000/loans/return" \
  -H "Content-Type: application/json" \
  -d '{
    "book_key": "987fcdeb-51a2-43f7-b123-123456789abc"
  }'
```

**Resposta (com multa por atraso):**
```json
{
  "loan_key": "456def78-90ab-cdef-1234-567890abcdef",
  "status": {
    "enumerator": "returned",
    "name": "Returned"
  },
  "return_date": "2026-01-23T14:20:00Z",
  "fine_amount": 6.0
}
```

#### 6. Listar Empréstimos em Atraso

```bash
curl "http://localhost:8000/loans/?overdue=true&page=1&per_page=10"
```

#### 7. Listar Empréstimos do Usuário

```bash
curl "http://localhost:8000/users/123e4567-e89b-12d3-a456-426614174000/loans?page=1&per_page=10"
```

#### 8. Consultar Usuário (com cache)

```bash
curl "http://localhost:8000/users/123e4567-e89b-12d3-a456-426614174000"
```

**Nota:** A segunda chamada será servida do cache (60s TTL) com latência <1ms.

### Usando Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Criar usuário
user_response = requests.post(
    f"{BASE_URL}/users/",
    json={"name": "Maria Santos", "email": "maria@example.com"}
)
user_key = user_response.json()["user_key"]

# Criar livro
book_response = requests.post(
    f"{BASE_URL}/books/",
    json={"title": "Design Patterns", "author": "Gang of Four"}
)
book_key = book_response.json()["book_key"]

# Criar empréstimo
loan_response = requests.post(
    f"{BASE_URL}/loans/",
    json={"user_key": user_key, "book_key": book_key}
)
print(loan_response.json())

# Verificar disponibilidade
availability = requests.get(f"{BASE_URL}/books/{book_key}/availability")
print(availability.json())
```

## 📚 Documentação da API

### Endpoints Principais

#### Users

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/users/` | Criar novo usuário |
| GET | `/users/` | Listar usuários (paginado) |
| GET | `/users/{user_key}` | Consultar usuário específico |
| GET | `/users/{user_key}/loans` | Listar empréstimos do usuário |

#### Books

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/books/` | Criar novo livro |
| GET | `/books/` | Listar livros (paginado) |
| GET | `/books/{book_key}` | Consultar livro específico |
| GET | `/books/{book_key}/availability` | Verificar disponibilidade |

#### Loans

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/loans/` | Criar novo empréstimo |
| POST | `/loans/return` | Devolver livro |
| GET | `/loans/` | Listar empréstimos com filtros |
| GET | `/loans/{loan_key}` | Consultar empréstimo específico |

#### System

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/healthcheck` | Status do sistema |
| GET | `/docs` | Documentação Swagger |

### Códigos de Erro

| Código | HTTP | Descrição |
|--------|------|-----------|
| LBS001 | 400 | Email já cadastrado |
| LBS002 | 404 | Usuário não encontrado |
| LBS003 | 403 | Usuário inativo |
| LBS004 | 400 | Limite de empréstimos atingido (3) |
| LBS005 | 404 | Livro não encontrado |
| LBS006 | 400 | Livro indisponível |
| LBS007 | 404 | Empréstimo não encontrado |
| LBS008 | 404 | Empréstimo ativo não encontrado |

### Parâmetros de Paginação

Todos os endpoints de listagem aceitam:
- `page` (default: 1) - número da página
- `per_page` (default: 100, max: 1000) - itens por página

Exemplo: `/users/?page=2&per_page=50`

## 🧪 Testes

### Estrutura de Testes

```
tests/
├── conftest.py          # Fixtures compartilhadas (client, db)
├── users/
│   ├── test_get.py      # Testes de leitura de usuários
│   ├── test_post.py     # Testes de criação de usuários
│   └── test_get_user_loans.py
├── books/
│   ├── test_get.py
│   └── test_post.py
└── loans/
    ├── test_get.py
    └── test_post.py
```

### Executar Testes

```bash
# Todos os testes
pytest

# Apenas um módulo
pytest tests/users/

# Apenas um arquivo
pytest tests/users/test_post.py

# Apenas um teste específico
pytest tests/users/test_post.py::test_create_user_success

# Com cobertura
pytest --cov=app --cov-report=term-missing

# Com relatório HTML
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Cobertura Atual

- **Users**: 100% - todos os cenários cobertos
- **Books**: 100% - incluindo validações e disponibilidade
- **Loans**: 100% - incluindo regras de negócio e multas

## 📁 Estrutura do Projeto

```
library_system/
├── alembic/                    # Migrações de banco de dados
│   ├── versions/
│   └── env.py
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point da aplicação
│   ├── api/
│   │   ├── deps.py            # Dependências (paginação, etc)
│   │   └── routers/           # Endpoints HTTP
│   │       ├── users.py
│   │       ├── books.py
│   │       ├── loans.py
│   │       └── healthcheck.py
│   ├── core/
│   │   ├── errors.py          # Erros customizados
│   │   ├── logger.py          # Configuração de logs
│   │   └── middlewares/
│   │       └── logging.py     # Middleware de requisições
│   ├── db/
│   │   └── session.py         # Configuração SQLAlchemy
│   ├── models/                # Modelos ORM
│   │   ├── user.py
│   │   ├── user_status.py
│   │   ├── book.py
│   │   ├── book_status.py
│   │   ├── loan.py
│   │   ├── loan_status.py
│   │   └── loan_event.py
│   ├── schemas/               # Schemas Pydantic
│   │   ├── user.py
│   │   ├── book.py
│   │   └── loan.py
│   ├── services/              # Lógica de negócio
│   │   ├── user_service.py
│   │   ├── book_service.py
│   │   └── loan_service.py
│   └── utils/                 # Utilitários
│       ├── cache.py           # Cache em memória
│       ├── text.py            # Normalização de strings
│       └── uuid.py            # Validação de UUIDs
├── tests/                      # Testes automatizados
├── .env                        # Variáveis de ambiente (criar)
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```env
# Database (obrigatório)
DATABASE_URL=postgresql://user:password@host:port/database

# Logging
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR

# Cache
CACHE_TTL_SECONDS=300
MAX_CACHE_SIZE=1000

# Application
PAGINATION_MAX_PER_PAGE=1000
LOAN_DURATION_DAYS=14
FINE_AMOUNT_PER_DAY=2.0
MAX_ACTIVE_LOANS_PER_USER=3
```

### Seed do Banco de Dados

Execute após `alembic upgrade head` para criar status padrões:

```sql
-- User Status
INSERT INTO user_status (enumerator, name) VALUES ('active', 'Active');
INSERT INTO user_status (enumerator, name) VALUES ('inactive', 'Inactive');

-- Book Status
INSERT INTO book_status (enumerator, name) VALUES ('available', 'Available');
INSERT INTO book_status (enumerator, name) VALUES ('loaned', 'Loaned');
INSERT INTO book_status (enumerator, name) VALUES ('maintenance', 'Maintenance');

-- Loan Status
INSERT INTO loan_status (enumerator, name) VALUES ('active', 'Active');
INSERT INTO loan_status (enumerator, name) VALUES ('returned', 'Returned');
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Guidelines

- Mantenha cobertura de testes acima de 90%
- Siga PEP 8 para estilo de código
- Adicione docstrings para funções públicas
- Atualize o README se necessário

## 📝 Licença

Este projeto está sob a licença MIT.

## 👥 Autores

- BTG Pactual Case Técnico - 2026

## 🙏 Agradecimentos

- FastAPI por um framework moderno e rápido
- SQLAlchemy por um ORM robusto
- Pydantic por validação de dados tipo-safe
- PostgreSQL por um banco de dados confiável
