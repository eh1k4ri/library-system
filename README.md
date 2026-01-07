# Library System API

Sistema de gerenciamento de biblioteca com FastAPI, PostgreSQL e SQLAlchemy.

## Instalação e Execução

### Setup Rápido

```bash
# 1. Clone e entre no diretório
git clone <repository-url>
cd library_system

# 2. Crie ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows ou source venv/bin/activate (Linux/Mac)

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure .env
# DATABASE_URL=postgresql://admin:password123@localhost:5432/library_db

# 5. Inicie banco com Docker
docker-compose up -d

# 6. Execute migrações
alembic upgrade head

# 7. Inicie a API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: **http://localhost:8000/docs** (Swagger)

### Verificação

```bash
# Testes
pytest

# Healthcheck
curl http://localhost:8000/

# Métricas
curl http://localhost:8000/metrics
```

## Funcionalidades Implementadas

### Gestão de Usuários
- Cadastro de usuário
- Listagem com paginação
- Consulta por UUID (escolha feita visando segurança)
- Histórico de empréstimos
- Cache de consultas

### Gestão de Livros
- Cadastro com título/autor/gênero
- Listagem com paginação
- Verificação de disponibilidade em tempo real
- Controle de status (available/loaned/maintenance)
- Cache de consultas

### Gestão de Empréstimos
- Criação com validações:
  - Usuário ativo
  - Livro disponível
  - Máx. 3 empréstimos por usuário
- Devolução com multa automática (R$ 2.00/dia)
- Listagem com filtros (status, atraso)
- Histórico de eventos

### Gestão de Reservas
- Criar/cancelar/concluir reservas
- Expiração automática (7 dias)
- Notificações via webhook

### Relatórios
- Exportar em CSV/PDF
- Empréstimos, usuários, livros, reservas

### Observabilidade
- Swagger/OpenAPI em `/docs`
- Healthcheck em `/healthcheck`
- Métricas Prometheus em `/metrics`
- Logging estruturado (trace_id, duração)

## Arquitetura e Decisões Técnicas

### Padrão Service Layer
```
api (routers) → services (lógica) → models (ORM) → database
```

### Cache em Memória
- Thread-safe com `RLock`
- 1000 itens máximo
- TTL: 60s (entidades), 300s (status)
- **Justificativa**: Simplicidade, sem dependências externas

### UUIDs como Identificadores Públicos
- Chaves UUID (`user_key`, `book_key`, `loan_key`) separadas de IDs internos
- **Justificativa**: Segurança (não vaza volume)

### Tratamento de Erros Customizado
- Códigos únicos (LBS001-LBS018)
- Respostas padronizadas com title/description
- Suporte a internacionalização (pt-BR)
- **Justificativa**: Rastreabilidade, suporte facilitado, consistência

### Validação com Pydantic v2
- Normalização centralizada (trim, lowercase)
- Validators em schemas
- Type hints completos
- **Justificativa**: DRY, consistência global, tipagem segura

### Logging Estruturado
- Trace ID único por requisição
- Query parameters capturados
- Duração e status code
- Timestamps ISO 8601
- **Justificativa**: Observabilidade, debugging facilitado, auditoria

### Paginação Obrigatória
- Todos endpoints de listagem com page/per_page
- Defaults: page=1, per_page=100
- **Justificativa**: Performance, escalabilidade, UX

### Alembic para Migrações
- Versionamento de schema
- Histórico completo
- Rollback seguro
- **Justificativa**: Rastreabilidade, reversibilidade, CI/CD automation

### Event Sourcing Parcial
- Tabelas de eventos (LoanEvent, ReservationEvent)
- Histórico imutável de mudanças
- **Justificativa**: Auditoria, debugging, compliance

## 📖 Exemplos de Uso

### Criar Usuário

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "João Silva", "email": "joao@example.com"}'
```

**Resposta:**
```json
{
  "user_key": "123e4567-e89b-12d3-a456-426614174000",
  "name": "João Silva",
  "email": "joao@example.com",
  "status": {"enumerator": "active", "name": "Active"},
  "created_at": "2026-01-07T10:30:00Z"
}
```

### Criar Livro

```bash
curl -X POST "http://localhost:8000/books/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Clean Code", "author": "Robert C. Martin", "genre": "Programming"}'
```

**Resposta:**
```json
{
  "book_key": "987fcdeb-51a2-43f7-b123-123456789abc",
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "status": {"enumerator": "available", "name": "Available"}
}
```

### Criar Empréstimo

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
  "user": {"name": "João Silva", "email": "joao@example.com"},
  "book": {"title": "Clean Code"},
  "status": {"enumerator": "active", "name": "Active"},
  "start_date": "2026-01-07T10:32:00Z",
  "due_date": "2026-01-21T10:32:00Z",
  "fine_amount": 0.0
}
```

### Verificar Disponibilidade

```bash
curl "http://localhost:8000/books/987fcdeb-51a2-43f7-b123-123456789abc/availability"
```

**Resposta:**
```json
{
  "available": false,
  "status": "loaned",
  "expected_return_date": "2026-01-21T10:32:00Z"
}
```

### Devolver Livro

```bash
curl -X POST "http://localhost:8000/loans/return" \
  -H "Content-Type: application/json" \
  -d '{"book_key": "987fcdeb-51a2-43f7-b123-123456789abc"}'
```

**Resposta:**
```json
{
  "loan_key": "456def78-90ab-cdef-1234-567890abcdef",
  "status": {"enumerator": "returned", "name": "Returned"},
  "return_date": "2026-01-10T14:20:00Z",
  "fine_amount": 0.0
}
```

### Devolução com Atraso (Multa)

```bash
# Devolver 5 dias após o prazo
curl -X POST "http://localhost:8000/loans/return" \
  -H "Content-Type: application/json" \
  -d '{"book_key": "987fcdeb-51a2-43f7-b123-123456789abc"}'
```

**Resposta com multa:**
```json
{
  "loan_key": "456def78-90ab-cdef-1234-567890abcdef",
  "status": {"enumerator": "returned", "name": "Returned"},
  "return_date": "2026-01-26T14:20:00Z",
  "fine_amount": 10.0
}
```

Cálculo: 5 dias × R$ 2.00/dia = **R$ 10.00**

### Listar Empréstimos em Atraso

```bash
curl "http://localhost:8000/loans/?overdue=true&page=1&per_page=20"
```

### Listar Empréstimos do Usuário

```bash
curl "http://localhost:8000/users/123e4567-e89b-12d3-a456-426614174000/loans?page=1&per_page=10"
```

### Exportar Relatório

```bash
# CSV
curl "http://localhost:8000/reports/loans/export?format=csv" -o loans.csv

# PDF
curl "http://localhost:8000/reports/loans/export?format=pdf" -o loans.pdf
```

### Com Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Criar usuário
user = requests.post(f"{BASE_URL}/users/", 
    json={"name": "Maria Santos", "email": "maria@example.com"}).json()
user_key = user["user_key"]

# Criar livro
book = requests.post(f"{BASE_URL}/books/",
    json={"title": "Design Patterns", "author": "Gang of Four"}).json()
book_key = book["book_key"]

# Criar empréstimo
loan = requests.post(f"{BASE_URL}/loans/",
    json={"user_key": user_key, "book_key": book_key}).json()
print(f"Empréstimo criado: {loan['loan_key']}")

# Devolver
returned = requests.post(f"{BASE_URL}/loans/return",
    json={"book_key": book_key}).json()
print(f"Multa: R$ {returned['fine_amount']:.2f}")
```

## 📊 Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/users/` | Criar usuário |
| GET | `/users/` | Listar usuários |
| GET | `/users/{user_key}` | Consultar usuário |
| GET | `/users/{user_key}/loans` | Empréstimos do usuário |
| POST | `/books/` | Criar livro |
| GET | `/books/` | Listar livros |
| GET | `/books/{book_key}` | Consultar livro |
| GET | `/books/{book_key}/availability` | Disponibilidade |
| POST | `/loans/` | Criar empréstimo |
| POST | `/loans/return` | Devolver livro |
| GET | `/loans/` | Listar empréstimos |
| POST | `/reservations/` | Criar reserva |
| GET | `/reports/loans/export` | Exportar empréstimos |
| GET | `/docs` | Swagger |
| GET | `/healthcheck` | Status |
| GET | `/metrics` | Prometheus |

## 🧪 Testes

```bash
# Todos
pytest

# Cobertura
pytest --cov=app --cov-report=html

# Específico
pytest tests/users/test_post.py::test_create_user_success
```

Cobertura: **>90%** com 40+ testes automatizados

## 📝 Variáveis de Ambiente

```env
DATABASE_URL=postgresql://admin:password123@localhost:5432/library_db
LOG_LEVEL=INFO
NOTIFY_WEBHOOK_URL=https://webhook.site/seu-id  # Opcional
```

## 📁 Estrutura do Projeto

```
app/
├── api/routers/           # Endpoints HTTP
├── services/              # Lógica de negócio
├── models/                # ORM SQLAlchemy
├── schemas/               # Validação Pydantic
├── core/                  # Infraestrutura (erros, logging, cache)
└── utils/                 # Utilitários
tests/                      # Testes automatizados
alembic/                    # Migrações de banco
```

## 🔗 Links Úteis

- **Documentação Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Healthcheck**: http://localhost:8000/healthcheck
- **Métricas**: http://localhost:8000/metrics

