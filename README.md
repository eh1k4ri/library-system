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

## ✨ Funcionalidades Implementadas

### 👥 Gestão de Usuários
- ✅ **Cadastro de usuários** com validação de email (RFC 5322)
- ✅ **Listagem com paginação** (page, per_page configurável)
- ✅ **Consulta individual** por chave UUID
- ✅ **Histórico de empréstimos** do usuário
- ✅ **Normalização automática** de emails (lowercase, trim)
- ✅ **Status de usuário** (active/inactive)
- ✅ **Cache inteligente** de consultas frequentes (60s TTL)
- ✅ **Tratamento de erros** com códigos customizados (LBS001-LBS003)
- ✅ **Auditoria** com timestamps ISO 8601

### 📚 Gestão de Livros
- ✅ **Cadastro de livros** com título, autor, gênero
- ✅ **Listagem com paginação** e filtros opcionais
- ✅ **Consulta individual** por chave UUID
- ✅ **Verificação de disponibilidade** em tempo real
  - Retorna se está disponível
  - Se emprestado, mostra data prevista de retorno
- ✅ **Controle de status** (available/loaned/maintenance)
- ✅ **Alteração dinâmica de status** via endpoint dedicado
- ✅ **Cache de consultas** (60s TTL)
- ✅ **Tratamento de erros** específicos (LBS005-LBS006)
- ✅ **Eventos de livro** para rastreabilidade

### 🔄 Gestão de Empréstimos
- ✅ **Criação de empréstimos** com múltiplas validações:
  - ✓ Usuário deve estar ativo (status: active)
  - ✓ Livro deve estar disponível
  - ✓ Limite de 3 empréstimos ativos por usuário
  - ✓ Validação de UUIDs
- ✅ **Devolução de livros** com cálculo automático de multas
  - Multa: R$ 2,00 por dia de atraso
  - Cálculo automático na devolução
  - Atualização automática de status
- ✅ **Listagem com filtros avançados**:
  - Por status (ativo/retornado)
  - Empréstimos em atraso
  - Paginação configurável
- ✅ **Histórico completo** de eventos por empréstimo
  - Criação
  - Mudança de status
  - Devolução com multa
- ✅ **Prazo padrão** de 14 dias (configurável)
- ✅ **Cache de consultas** (60s TTL)
- ✅ **Relatórios** em CSV/PDF
- ✅ **Códigos de erro** específicos (LBS004, LBS007-LBS008)

### 📋 Gestão de Reservas
- ✅ **Criação de reservas** para livros emprestados
- ✅ **Consulta de reserva** por chave UUID
- ✅ **Listagem com paginação**
- ✅ **Cancelamento de reserva**
- ✅ **Conclusão de reserva** (quando livro fica disponível)
- ✅ **Status de reserva** (pending/completed/cancelled)
- ✅ **Histórico de eventos** da reserva
- ✅ **Expiração automática** (7 dias configurável)
- ✅ **Notificações** quando livro fica disponível (webhook)

### 📊 Relatórios e Exportação
- ✅ **Exportar empréstimos** em CSV/PDF
  - Filtro por período
  - Cálculo de multas
- ✅ **Exportar usuários** em CSV/PDF
  - Informações completas
  - Status do usuário
- ✅ **Exportar livros** em CSV/PDF
  - Com filtro por gênero
  - Status de disponibilidade
- ✅ **Exportar reservas** em CSV/PDF
  - Informações de data
  - Status da reserva
- ✅ **Validação de formato** com erros customizados
- ✅ **Cache de relatórios** para melhor performance

### 🔧 Recursos Técnicos e Observabilidade
- ✅ **Documentação interativa** Swagger/OpenAPI em `/docs`
- ✅ **ReDoc** (documentação alternativa) em `/redoc`
- ✅ **Healthcheck endpoint** em `/healthcheck`
  - Status da aplicação
  - Verificação de conexão com banco
  - Status de cache
- ✅ **Logging estruturado** com:
  - `trace_id` único por requisição
  - Query parameters
  - Status code e duração
  - Timestamps ISO 8601
- ✅ **Métricas Prometheus** em `/metrics`
  - Endpoints acessados
  - Latência
  - Taxa de erro
  - Integração com Grafana
- ✅ **Validação Pydantic v2** com validators customizados
- ✅ **Tratamento de erros** centralizado com códigos (LBS001-LBS018)
- ✅ **Paginação obrigatória** em todos os endpoints de listagem
  - Proteção contra consultas pesadas
  - Defaults sensatos (page=1, per_page=100)
- ✅ **Cache em memória** thread-safe com TTL
  - 1000 itens máximo
  - 60s para entidades
  - 300s para status
- ✅ **Validação centralizada** de UUIDs
- ✅ **Normalização de strings** (trim, lowercase)

### 🗄️ Banco de Dados e Migrações
- ✅ **PostgreSQL 15+** com suporte JSONB
- ✅ **Alembic** para versionamento de schema
  - Histórico completo de mudanças
  - Migrações automáticas
  - Rollback seguro
- ✅ **SQLAlchemy ORM** com relacionamentos
  - Foreign keys
  - Cascading deletes/updates
  - Índices otimizados
- ✅ **Tabelas de status** normalizadas (lookup tables)
- ✅ **Event tables** para auditoria
- ✅ **Relacionamentos** bem definidos (One-to-Many, Many-to-One)

### 🔐 Segurança
- ✅ **UUIDs como identificadores públicos** (não IDs sequenciais)
- ✅ **Validação de entrada** em todos os endpoints
- ✅ **Prevenção de SQL injection** via ORM
- ✅ **Normalização de dados** para evitar duplicatas
- ✅ **Timestamps auditáveis** em todas as operações

### ⚡ Performance
- ✅ **Cache em memória** para consultas frequentes
- ✅ **Índices de banco de dados** otimizados
- ✅ **Paginação obrigatória** em listagens
- ✅ **Lazy loading** de relacionamentos
- ✅ **Compressão de respostas** (gzip)
- ✅ **Rate limiting** (100 req/min padrão)

### 🧪 Qualidade de Código
- ✅ **Cobertura de testes** >90%
  - 40+ testes automatizados
  - Testes unitários e integração
  - Testes de schemas
  - Testes de business logic
- ✅ **Type hints** completos (Python 3.11+)
- ✅ **Docstrings** em funções públicas
- ✅ **Padrão Service Layer**
- ✅ **Separação de responsabilidades**
- ✅ **Code reusability**

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

- **Python 3.11+** - [Download aqui](https://www.python.org/downloads/)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/) ou use Docker
- **Git** - [Download aqui](https://git-scm.com/)
- **Docker + Docker Compose** (recomendado para simplificar setup) - [Download aqui](https://www.docker.com/products/docker-desktop)

### Guia Rápido (Recomendado com Docker)

```bash
# 1. Clone o repositório
git clone <repository-url>
cd library_system

# 2. Crie o arquivo .env
cp .env.example .env  # ou crie manualmente (ver abaixo)

# 3. Suba os containers
docker-compose up -d

# 4. Instale dependências Python
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 5. Execute as migrações
alembic upgrade head

# 6. Inicie a aplicação
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ✅ Acesse em http://localhost:8000/docs
```

### Instalação Detalhada

#### 1. Clone o Repositório

```bash
git clone <repository-url>
cd library_system
```

#### 2. Configure o Ambiente Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

Principais dependências:
- `fastapi` - Framework web
- `sqlalchemy` - ORM para banco de dados
- `pydantic` - Validação de dados
- `psycopg2-binary` - Driver PostgreSQL
- `alembic` - Migrações de banco
- `uvicorn` - Servidor ASGI
- `pytest` - Framework de testes

#### 4. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Database (OBRIGATÓRIO)
DATABASE_URL=postgresql://admin:password123@localhost:5432/library_db

# Logging (opcional)
LOG_LEVEL=INFO

# Notificações (opcional)
# Se configurado, envia webhooks de notificações
# NOTIFY_WEBHOOK_URL=https://webhook.site/seu-id-aqui

# Cache
CACHE_MAX_SIZE=1000
CACHE_DEFAULT_TTL=300
CACHE_ENTITY_TTL=60

# Paginação
PAGINATION_MIN=100
PAGINATION_MAX_LIMIT=1000

# Empréstimos
LOAN_DEFAULT_DAYS=14
LOAN_FINE_PER_DAY=2.0
LOAN_MAX_ACTIVE_LOANS=3

# Reservas
RESERVATION_EXPIRY_DAYS=7
```

#### 5. Inicie o Banco de Dados

**Opção A: Docker Compose (Recomendado)**

```bash
docker-compose up -d
```

Serviços iniciados:
- **PostgreSQL 15** na porta 5432 (usuário: `admin`, senha: `password123`)
- Pronto para receber migrações

**Opção B: PostgreSQL Local**

Se usar PostgreSQL já instalado localmente:
1. Crie um database: `createdb library_db`
2. Ajuste `DATABASE_URL` no `.env` com suas credenciais
3. Certifique-se que o servidor está rodando (`psql -U admin -d library_db`)

#### 6. Execute as Migrações

```bash
alembic upgrade head
```

Tabelas criadas:
- `users` - Usuários do sistema
- `user_status` - Status de usuários (active/inactive)
- `books` - Livros da biblioteca
- `book_status` - Status de livros (available/loaned/maintenance)
- `loans` - Empréstimos e devoluções
- `loan_status` - Status de empréstimos (active/returned)
- `loan_events` - Histórico de eventos por empréstimo
- `reservations` - Reservas de livros
- `reservation_status` - Status de reservas
- `reservation_events` - Histórico de eventos por reserva

#### 7. (Opcional) Seed de Dados Iniciais

Os status são criados automaticamente nas migrações. Para adicionar dados de teste manualmente:

```python
# Executar via Python shell
from app.db.session import SessionLocal
from app.models.user_status import UserStatus
from app.models.book_status import BookStatus
from app.models.loan_status import LoanStatus

db = SessionLocal()

# User Status
db.add_all([
    UserStatus(enumerator="active", name="Active"),
    UserStatus(enumerator="inactive", name="Inactive"),
])

# Book Status
db.add_all([
    BookStatus(enumerator="available", name="Available"),
    BookStatus(enumerator="loaned", name="Loaned"),
    BookStatus(enumerator="maintenance", name="Maintenance"),
])

# Loan Status
db.add_all([
    LoanStatus(enumerator="active", name="Active"),
    LoanStatus(enumerator="returned", name="Returned"),
])

db.commit()
```

#### 8. Inicie a Aplicação

**Modo Desenvolvimento (com reload automático):**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Modo Produção:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Endpoints disponíveis:
- **API REST**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs (Teste endpoints interativamente)
- **ReDoc**: http://localhost:8000/redoc (Documentação alternativa)
- **Healthcheck**: http://localhost:8000/healthcheck
- **Métricas Prometheus**: http://localhost:8000/metrics

#### 9. Execute os Testes

```bash
# Todos os testes
pytest

# Com output detalhado
pytest -vv

# Com cobertura de código
pytest --cov=app --cov-report=html

# Apenas um arquivo de teste
pytest tests/users/test_post.py

# Apenas um teste específico
pytest tests/users/test_post.py::test_create_user_success

# Com marcadores
pytest -m "not slow"
```

Resultado esperado: **40+ testes passando** em menos de 5 segundos.

### Verificar Instalação

Após completar todos os passos, verifique:

```bash
# 1. API respondendo
curl http://localhost:8000/healthcheck

# 2. Documentação Swagger acessível
curl -I http://localhost:8000/docs

# 3. Métricas Prometheus disponíveis
curl http://localhost:8000/metrics | grep -i library_system

# 4. Testes passando
pytest -q
```

### Solução de Problemas

**Erro: "PostgreSQL connection failed"**
```bash
# Verifique se Docker está rodando
docker ps

# Reinicie os containers
docker-compose down
docker-compose up -d

# Confirme a URL no .env
# DATABASE_URL=postgresql://admin:password123@localhost:5432/library_db
```

**Erro: "Module not found: app"**
```bash
# Certifique-se de estar no diretório raiz
cd library_system

# Reinstale as dependências
pip install -r requirements.txt --force-reinstall
```

**Erro: "Port 8000 already in use"**
```bash
# Mude a porta
uvicorn app.main:app --reload --port 8001
```

**Erro: "Alembic migration failed"**
```bash
# Verifique a conexão com o banco
psql postgresql://admin:password123@localhost:5432/library_db

# Limpe e recrie (⚠️ Cuidado: deleta dados!)
alembic downgrade base
alembic upgrade head
```

## 📖 Exemplos de Uso

### Usando a Documentação Interativa (Recomendado)

Acesse **http://localhost:8000/docs** para usar a interface Swagger:
- ✅ Visualize todos os endpoints com seus parâmetros
- ✅ Teste requisições diretamente no navegador
- ✅ Veja schemas de request/response com exemplos
- ✅ Copie comandos cURL automaticamente

### Cenários de Uso Completos

#### Cenário 1: Criar Usuário e Emprestar um Livro

**Passo 1: Criar um Usuário**

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao.silva@example.com"
  }'
```

**Resposta (201 Created):**
```json
{
  "user_key": "123e4567-e89b-12d3-a456-426614174000",
  "name": "João Silva",
  "email": "joao.silva@example.com",
  "status": {
    "enumerator": "active",
    "name": "Active"
  },
  "created_at": "2026-01-07T10:30:00Z"
}
```

Salve `user_key` para próximos passos: `123e4567-e89b-12d3-a456-426614174000`

**Passo 2: Criar um Livro**

```bash
curl -X POST "http://localhost:8000/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "genre": "Programming"
  }'
```

**Resposta (201 Created):**
```json
{
  "book_key": "987fcdeb-51a2-43f7-b123-123456789abc",
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "genre": "Programming",
  "status": {
    "enumerator": "available",
    "name": "Available"
  },
  "created_at": "2026-01-07T10:31:00Z"
}
```

Salve `book_key`: `987fcdeb-51a2-43f7-b123-123456789abc`

**Passo 3: Criar Empréstimo**

```bash
curl -X POST "http://localhost:8000/loans/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_key": "123e4567-e89b-12d3-a456-426614174000",
    "book_key": "987fcdeb-51a2-43f7-b123-123456789abc"
  }'
```

**Resposta (201 Created):**
```json
{
  "loan_key": "456def78-90ab-cdef-1234-567890abcdef",
  "user": {
    "user_key": "123e4567-e89b-12d3-a456-426614174000",
    "name": "João Silva",
    "email": "joao.silva@example.com",
    "status": {
      "enumerator": "active",
      "name": "Active"
    }
  },
  "book": {
    "book_key": "987fcdeb-51a2-43f7-b123-123456789abc",
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "status": {
      "enumerator": "loaned",
      "name": "Loaned"
    }
  },
  "status": {
    "enumerator": "active",
    "name": "Active"
  },
  "start_date": "2026-01-07T10:32:00Z",
  "due_date": "2026-01-21T10:32:00Z",
  "return_date": null,
  "fine_amount": 0.0
}
```

**Passo 4: Verificar Disponibilidade do Livro (agora emprestado)**

```bash
curl "http://localhost:8000/books/987fcdeb-51a2-43f7-b123-123456789abc/availability"
```

**Resposta (200 OK):**
```json
{
  "available": false,
  "status": "loaned",
  "expected_return_date": "2026-01-21T10:32:00Z"
}
```

**Passo 5: Consultar Empréstimos do Usuário**

```bash
curl "http://localhost:8000/users/123e4567-e89b-12d3-a456-426614174000/loans?page=1&per_page=10"
```

**Resposta (200 OK):**
```json
{
  "data": [
    {
      "loan_key": "456def78-90ab-cdef-1234-567890abcdef",
      "book": {
        "title": "Clean Code",
        "author": "Robert C. Martin"
      },
      "status": {
        "enumerator": "active",
        "name": "Active"
      },
      "due_date": "2026-01-21T10:32:00Z",
      "fine_amount": 0.0
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 1
  }
}
```

**Passo 6: Devolver Livro (antes do prazo)**

```bash
curl -X POST "http://localhost:8000/loans/return" \
  -H "Content-Type: application/json" \
  -d '{
    "book_key": "987fcdeb-51a2-43f7-b123-123456789abc"
  }'
```

**Resposta (200 OK):**
```json
{
  "loan_key": "456def78-90ab-cdef-1234-567890abcdef",
  "book": {
    "title": "Clean Code",
    "status": {
      "enumerator": "available",
      "name": "Available"
    }
  },
  "status": {
    "enumerator": "returned",
    "name": "Returned"
  },
  "return_date": "2026-01-10T14:20:00Z",
  "fine_amount": 0.0
}
```

#### Cenário 2: Devolução com Atraso (Multa)

**Devolução 5 dias após o prazo:**

```bash
# Devolver livro (simulando 5 dias de atraso)
curl -X POST "http://localhost:8000/loans/return" \
  -H "Content-Type: application/json" \
  -d '{
    "book_key": "987fcdeb-51a2-43f7-b123-123456789abc"
  }'
```

**Resposta com multa:**
```json
{
  "loan_key": "456def78-90ab-cdef-1234-567890abcdef",
  "status": {
    "enumerator": "returned",
    "name": "Returned"
  },
  "return_date": "2026-01-26T14:20:00Z",
  "fine_amount": 10.0
}
```

**Cálculo da multa:**
- Prazo: 2026-01-21
- Devolução: 2026-01-26 (5 dias de atraso)
- Multa: 5 dias × R$ 2.00/dia = **R$ 10.00**

#### Cenário 3: Listar Empréstimos em Atraso

```bash
curl "http://localhost:8000/loans/?overdue=true&page=1&per_page=20"
```

**Resposta:**
```json
{
  "data": [
    {
      "loan_key": "456def78-90ab-cdef-1234-567890abcdef",
      "user": {
        "name": "João Silva",
        "email": "joao.silva@example.com"
      },
      "book": {
        "title": "Clean Code"
      },
      "due_date": "2026-01-21T10:32:00Z",
      "days_overdue": 5,
      "fine_amount": 10.0
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1
  }
}
```

#### Cenário 4: Exportar Relatório de Empréstimos

**Exportar como CSV:**

```bash
curl "http://localhost:8000/reports/loans/export?format=csv" \
  -H "Authorization: Bearer token_aqui" \
  -o loans_report.csv
```

**Resultado:**
```csv
loan_key,user_name,user_email,book_title,book_author,status,start_date,due_date,return_date,fine_amount
456def78-90ab-cdef-1234-567890abcdef,João Silva,joao.silva@example.com,Clean Code,Robert C. Martin,returned,2026-01-07T10:32:00Z,2026-01-21T10:32:00Z,2026-01-10T14:20:00Z,0.0
```

**Exportar como PDF:**

```bash
curl "http://localhost:8000/reports/loans/export?format=pdf" \
  -H "Authorization: Bearer token_aqui" \
  -o loans_report.pdf
```

#### Cenário 5: Listar Usuários com Paginação

```bash
# Primeira página
curl "http://localhost:8000/users/?page=1&per_page=10"

# Segunda página
curl "http://localhost:8000/users/?page=2&per_page=10"

# Com filtro de status
curl "http://localhost:8000/users/?status=active&page=1&per_page=10"
```

**Resposta:**
```json
{
  "data": [
    {
      "user_key": "123e4567-e89b-12d3-a456-426614174000",
      "name": "João Silva",
      "email": "joao.silva@example.com",
      "status": {
        "enumerator": "active",
        "name": "Active"
      },
      "created_at": "2026-01-07T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 1
  }
}
```

### Usando Python Requests

Exemplo completo em Python:

```python
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

class LibraryClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def create_user(self, name: str, email: str):
        """Criar novo usuário"""
        response = self.session.post(
            f"{self.base_url}/users/",
            json={"name": name, "email": email}
        )
        response.raise_for_status()
        return response.json()
    
    def create_book(self, title: str, author: str, genre: str = ""):
        """Criar novo livro"""
        response = self.session.post(
            f"{self.base_url}/books/",
            json={"title": title, "author": author, "genre": genre}
        )
        response.raise_for_status()
        return response.json()
    
    def create_loan(self, user_key: str, book_key: str):
        """Criar novo empréstimo"""
        response = self.session.post(
            f"{self.base_url}/loans/",
            json={"user_key": user_key, "book_key": book_key}
        )
        response.raise_for_status()
        return response.json()
    
    def return_book(self, book_key: str):
        """Devolver livro"""
        response = self.session.post(
            f"{self.base_url}/loans/return",
            json={"book_key": book_key}
        )
        response.raise_for_status()
        return response.json()
    
    def get_user_loans(self, user_key: str, page: int = 1, per_page: int = 10):
        """Listar empréstimos do usuário"""
        response = self.session.get(
            f"{self.base_url}/users/{user_key}/loans",
            params={"page": page, "per_page": per_page}
        )
        response.raise_for_status()
        return response.json()
    
    def check_book_availability(self, book_key: str):
        """Verificar disponibilidade do livro"""
        response = self.session.get(
            f"{self.base_url}/books/{book_key}/availability"
        )
        response.raise_for_status()
        return response.json()
    
    def export_loans(self, format: str = "csv"):
        """Exportar relatório de empréstimos"""
        response = self.session.get(
            f"{self.base_url}/reports/loans/export",
            params={"format": format}
        )
        response.raise_for_status()
        return response.content

# Exemplo de uso
if __name__ == "__main__":
    client = LibraryClient()
    
    # 1. Criar usuário
    user = client.create_user("Maria Santos", "maria@example.com")
    user_key = user["user_key"]
    print(f"✓ Usuário criado: {user['name']}")
    
    # 2. Criar livro
    book = client.create_book("Design Patterns", "Gang of Four", "Programming")
    book_key = book["book_key"]
    print(f"✓ Livro criado: {book['title']}")
    
    # 3. Verificar disponibilidade antes
    avail = client.check_book_availability(book_key)
    print(f"✓ Livro disponível: {avail['available']}")
    
    # 4. Criar empréstimo
    loan = client.create_loan(user_key, book_key)
    print(f"✓ Empréstimo criado, prazo: {loan['due_date']}")
    
    # 5. Listar empréstimos do usuário
    loans = client.get_user_loans(user_key)
    print(f"✓ Usuário tem {len(loans['data'])} empréstimo(s) ativo(s)")
    
    # 6. Verificar disponibilidade após (deve estar emprestado)
    avail = client.check_book_availability(book_key)
    print(f"✓ Livro disponível: {avail['available']}")
    print(f"  Retorno esperado: {avail['expected_return_date']}")
    
    # 7. Devolver livro
    return_info = client.return_book(book_key)
    print(f"✓ Livro devolvido, multa: R$ {return_info['fine_amount']:.2f}")
    
    # 8. Exportar relatório
    csv_data = client.export_loans("csv")
    with open("loans_export.csv", "wb") as f:
        f.write(csv_data)
    print(f"✓ Relatório exportado: loans_export.csv")
```

### Usando JavaScript/Fetch

```javascript
const BASE_URL = "http://localhost:8000";

class LibraryAPI {
  async createUser(name, email) {
    const response = await fetch(`${BASE_URL}/users/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email })
    });
    return response.json();
  }

  async createBook(title, author, genre = "") {
    const response = await fetch(`${BASE_URL}/books/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, author, genre })
    });
    return response.json();
  }

  async createLoan(userKey, bookKey) {
    const response = await fetch(`${BASE_URL}/loans/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_key: userKey, book_key: bookKey })
    });
    return response.json();
  }

  async returnBook(bookKey) {
    const response = await fetch(`${BASE_URL}/loans/return`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ book_key: bookKey })
    });
    return response.json();
  }

  async getUserLoans(userKey, page = 1, perPage = 10) {
    const response = await fetch(
      `${BASE_URL}/users/${userKey}/loans?page=${page}&per_page=${perPage}`
    );
    return response.json();
  }

  async checkBookAvailability(bookKey) {
    const response = await fetch(`${BASE_URL}/books/${bookKey}/availability`);
    return response.json();
  }
}

// Exemplo de uso
(async () => {
  const api = new LibraryAPI();

  // Criar usuário
  const user = await api.createUser("Pedro Costa", "pedro@example.com");
  console.log("✓ Usuário criado:", user.name);

  // Criar livro
  const book = await api.createBook("The Pragmatic Programmer", "Hunt & Thomas");
  console.log("✓ Livro criado:", book.title);

  // Criar empréstimo
  const loan = await api.createLoan(user.user_key, book.book_key);
  console.log("✓ Empréstimo criado até:", loan.due_date);

  // Devolver livro
  const returned = await api.returnBook(book.book_key);
  console.log("✓ Livro devolvido, multa: R$", returned.fine_amount.toFixed(2));
})();
```

### Tratamento de Erros

Exemplo de tratamento de erro (email duplicado):

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao.silva@example.com"
  }' \
  -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Outro Usuário",
    "email": "joao.silva@example.com"
  }'
```

**Resposta (400 Bad Request):**
```json
{
  "code": "LBS001",
  "title": "Email Already Registered",
  "description": "The email joao.silva@example.com is already registered in the system",
  "detail": "Email Already Registered: joao.silva@example.com is already registered",
  "translation": {
    "pt": "O email joao.silva@example.com já está registrado no sistema"
  }
}
```

### Cache em Ação

O cache é transparente para o usuário. Exemplo:

```bash
# Primeira chamada (lê do banco, ~50ms)
time curl "http://localhost:8000/users/123e4567-e89b-12d3-a456-426614174000"

# Segunda chamada (lê do cache, <1ms)
time curl "http://localhost:8000/users/123e4567-e89b-12d3-a456-426614174000"
```

O header `X-Cache` pode ser adicionado à resposta para indicar cache hit (opcional).

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

#### Reports

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/reports/loans/export` | Exporta empréstimos em CSV/PDF |
| GET | `/reports/users/export` | Exporta usuários em CSV/PDF |
| GET | `/reports/books/export` | Exporta livros em CSV/PDF |
| GET | `/reports/reservations/export` | Exporta reservas em CSV/PDF |

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
│   └── test_update.py   # Testes de atualização e status de usuários
├── books/
│   ├── test_get.py
│   └── test_post.py
│   └── test_update.py   # Testes de atualização e status de livros
├── loans/
│   ├── test_get.py
│   └── test_post.py
├── reservations/
│   ├── test_get.py
│   └── test_post.py
├── reports/
│   └── test_export.py
├── notifications/
│   └── test_notification_service.py
└── system/
  └── test_metrics.py
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

## 🔭 Observabilidade (Prometheus)

Passo a passo local (Windows):
- Start da API: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` (metrics liberado sem Basic Auth em `/metrics`).
- Gerar config: `Copy-Item ops\monitoring\prometheus.example.yml ops\monitoring\prometheus.yml`.
- Subir Prometheus (de `.../library_system`):
  `docker run --rm -p 9090:9090 -v "//c/Users/alber/OneDrive/Documentos/GitHub/btg-case/case-tecnico/library_system/ops/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml" prom/prometheus --config.file=/etc/prometheus/prometheus.yml`
- Verificar targets: http://localhost:9090/targets deve mostrar `library-api` como UP.
- Se rodar Prometheus fora de container, edite o `targets` em [ops/monitoring/prometheus.yml](ops/monitoring/prometheus.yml) para `localhost:8000`.

### Variáveis de Ambiente

```env
# Database (obrigatório)
DATABASE_URL=postgresql://user:password@host:port/database

# Logging
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR

# Notificações (opcional)
NOTIFY_WEBHOOK_URL=https://webhook.site/d208aa8c-8bb7-4e38-af79-c01f6ca08e39  # se não definido, notificações são ignoradas

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
