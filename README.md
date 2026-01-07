# Library System API - Sistema de Gerenciamento de Biblioteca Digital

---

## Instalação e Execução

### Setup Rápido

```bash
# 1. Clone e entre no diretório
git clone https://github.com/eh1k4ri/library-system.git
cd library_system

# 2. Crie ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows ou source venv/bin/activate (Linux/Mac)

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure .env (copiar do .env.example)
cp .env.example .env

# 5. Inicie banco com Docker
docker-compose up -d

# 6. Execute migrações
alembic upgrade head

# 7. Inicie a API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 8. (Opcional) Inicie o Prometheus para monitorar métricas
cd ops/monitoring
copy prometheus.example.yml prometheus.yml
docker run --rm -p 9090:9090 -v "$(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml" prom/prometheus --config.file=/etc/prometheus/prometheus.yml
```

Acesse:
- **API (Swagger)**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090

### Verificação

```bash
# Testes
pytest

# Healthcheck
curl http://localhost:8000/

# Métricas
curl http://localhost:8000/metrics
```

## Lista de Funcionalidades Implementadas

### Entidades Obrigatórias (100%)
-  **Usuário** → [`app/models/user.py`](app/models/user.py)
- **Livro** → [`app/models/book.py`](app/models/book.py)
- **Empréstimo** → [`app/models/loan.py`](app/models/loan.py)

### Features Necessárias (100%)

#### a) Gestão de Usuários
- Listar todos os usuários → `GET /users/`
- Cadastrar novo usuário → `POST /users/`
- Buscar usuário por ID → `GET /users/{user_key}` (UUID utilizado visando segurança)
- Listar todos os empréstimos associados a um usuário → `GET /users/{user_key}/loans`

#### b) Catálogo de Livros
- Listar livros → `GET /books/`
- Cadastrar novo livro vinculado a um autor → `POST /books/`
- Verificar disponibilidade para empréstimo → `GET /books/{book_key}/availability`

#### c) Sistema de Empréstimos
- Realizar empréstimo de livro→ `POST /loans/`
- Processar devolução com cálculo de multa → `POST /loans/return`
- Listar empréstimos ativos/atrasados → `GET /loans/?status=active&overdue=true`
- Consultar histórico de empréstimos por usuário → `GET /users/{user_key}/loans`

**Regras de Negócio:**
- Prazo padrão: 14 dias
- Multa: R$ 2,00 por dia de atraso
- Usuário pode ter no máximo 3 empréstimos ativos

### Funcionalidades Extras (Diferenciais)

#### Básico (100%)
- Implementar paginação em todas as listagens
- Documentação automática com Swagger/OpenAPI
- Validação robusta com Pydantic
- Logging estruturado de operações

#### Intermediário (100%)
- Sistema de reservas de livros
- Cache em memória (thread-safe)
- Rate limiting nos endpoints
- Testes automatizados (80+ testes)
- Middleware de autenticação básica

#### Avançado (100%)
- Notificações de vencimento (email/webhook)
- Sistema de renovação de empréstimos
- Exportação de relatórios (CSV/PDF)
- Observabilidade (métricas + health check)
- Frontend em repositório separado: [library-system-frontend](https://github.com/eh1k4ri/library-front)

## 📖 Funcionalidades Implementadas

### Requisitos Obrigatórios

#### **Gestão de Usuários**
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/users/` | GET | Lista todos os usuários com paginação |
| `/users/` | POST | Cadastra novo usuário |
| `/users/{user_key}` | GET | Busca usuário por UUID |
| `/users/{user_key}` | PATCH | Atualiza dados do usuário |
| `/users/{user_key}/status` | PATCH | Altera status (active/inactive/blocked) |
| `/users/{user_key}/loans` | GET | Lista empréstimos do usuário |

**Validações:** E-mail único, normalização automática de dados, cache de consultas

#### **Catálogo de Livros**
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/books/` | GET | Lista livros com paginação e filtros |
| `/books/` | POST | Cadastra livro com autor e gênero |
| `/books/{book_key}` | GET | Busca livro por UUID |
| `/books/{book_key}` | PATCH | Atualiza dados do livro |
| `/books/{book_key}/status` | PATCH | Altera status (available/loaned/maintenance) |
| `/books/{book_key}/availability` | GET | Verifica disponibilidade em tempo real |
| `/books/genres` | GET | Lista gêneros cadastrados |

**Features:** Controle de disponibilidade, múltiplos status, cache de consultas

#### **Sistema de Empréstimos**
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/loans/` | GET | Lista empréstimos com filtros (status, overdue) |
| `/loans/` | POST | Cria novo empréstimo |
| `/loans/{loan_key}` | GET | Busca empréstimo por UUID |
| `/loans/{loan_key}/renew` | POST | Renova empréstimo (+7 dias) |
| `/loans/return` | POST | Processa devolução com cálculo de multa |

**Regras de Negócio Implementadas:**
- ✅ Prazo padrão: 14 dias (`LOAN_DEFAULT_DAYS`)
- ✅ Multa: R$ 2,00 por dia de atraso (`LOAN_FINE_PER_DAY`)
- ✅ Máximo 3 empréstimos ativos por usuário (`LOAN_MAX_ACTIVE_LOANS`)
- ✅ Renovação: +7 dias (apenas se não estiver em atraso)

**Validações Automáticas:**
- Usuário deve estar ativo
- Livro deve estar disponível
- Limite de empréstimos por usuário
- Histórico completo com eventos imutáveis

### Funcionalidades Extras

#### **Sistema de Reservas** (Intermediário)
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/reservations/` | GET | Lista reservas com filtros |
| `/reservations/` | POST | Cria reserva para livro emprestado |
| `/reservations/{key}` | GET | Busca reserva por UUID |
| `/reservations/{key}/cancel` | POST | Cancela reserva |
| `/reservations/{key}/complete` | POST | Marca reserva como concluída |

**Features:** Expiração automática (7 dias), notificações via webhook, validações

#### **Relatórios e Exportação** (Avançado)
| Endpoint | Formato | Descrição |
|----------|---------|-----------|
| `/reports/loans/export?format=csv` | CSV | Exporta empréstimos |
| `/reports/loans/export?format=pdf` | PDF | Exporta empréstimos |
| `/reports/users/export` | CSV/PDF | Exporta usuários |
| `/reports/books/export` | CSV/PDF | Exporta livros |
| `/reports/reservations/export` | CSV/PDF | Exporta reservas |

#### **Observabilidade** (Avançado)
| Endpoint | Descrição |
|----------|-----------|
| `/docs` | Documentação Swagger/OpenAPI interativa |
| `/healthcheck` | Status do sistema e banco de dados |
| `/metrics` | Métricas no formato Prometheus |

**Métricas Coletadas:**
- Total de requisições HTTP por método/endpoint/status
- Duração de requisições (histograma)
- Trace ID único por requisição
- Logging estruturado com contexto completo

---

## 🏗️ Decisões Arquiteturais

### 1. Arquitetura em Camadas (Service Layer Pattern)

```
┌─────────────────────────────────────┐
│   API Layer (Routers)               │  ← Recebe requisições HTTP
│   app/api/routers/                  │
├─────────────────────────────────────┤
│   Service Layer (Lógica de Negócio)│  ← Regras de negócio
│   app/services/                     │
├─────────────────────────────────────┤
│   Model Layer (ORM)                 │  ← Acesso a dados
│   app/models/                       │
├─────────────────────────────────────┤
│   Database (PostgreSQL)             │  ← Persistência
└─────────────────────────────────────┘
```

**Justificativa:** 
- Separação clara de responsabilidades
- Facilita testes unitários e de integração
- Permite reutilização de lógica de negócio
- Manutenção e evolução simplificadas

### 2. UUIDs como Identificadores Públicos

**Implementação:** Chaves UUID (`user_key`, `book_key`, `loan_key`) separadas de IDs internos

**Justificativa:**
- **Segurança:** Não expõe volume de dados (ex: total de usuários)
- **Distribuição:** Permite merge de bancos sem conflitos
- **Previsibilidade:** IDs incrementais são vulneráveis

### 3. Cache em Memória Thread-Safe

**Implementação:** 
- Classe `Cache` com `RLock` para sincronização
- TTL configurável: 60s (entidades), 300s (status)
- LRU com limite de 1000 itens

**Justificativa:**
- **Simplicidade:** Sem dependências externas (Redis opcional)
- **Performance:** Reduz carga no banco para consultas frequentes
- **Portabilidade:** Funciona em qualquer ambiente

### 4. Tratamento de Erros Customizado

**Implementação:**
- Códigos únicos (LBS001-LBS018)
- Estrutura padronizada: `{"code": "...", "title": "...", "description": "..."}`
- Suporte a i18n (pt-BR)

**Justificativa:**
- **Rastreabilidade:** Fácil identificar origem do erro
- **Suporte:** Usuários podem reportar código específico
- **Consistência:** Respostas uniformes em toda API

### 5. Event Sourcing Parcial

**Implementação:** Tabelas de eventos (`LoanEvent`, `ReservationEvent`, `UserEvent`, `BookEvent`)

**Justificativa:**
- **Auditoria:** Histórico imutável de todas as operações
- **Debugging:** Reprodução de estados passados
- **Compliance:** Rastreabilidade para regulamentações

### 6. Paginação Obrigatória

**Implementação:** Todos os endpoints de listagem exigem `page` e `per_page`

**Justificativa:**
- **Performance:** Evita carregamento de milhares de registros
- **Escalabilidade:** Sistema preparado para crescimento
- **UX:** Respostas rápidas mesmo com grande volume

### 7. Validação com Pydantic v2

**Implementação:**
- Schemas em `app/schemas/`
- Validators customizados
- Normalização automática (trim, lowercase)

**Justificativa:**
- **DRY:** Validações centralizadas
- **Tipagem:** Type hints completos
- **Documentação:** Schemas geram OpenAPI automaticamente

### 8. Middlewares para Cross-Cutting Concerns

**Implementação:**
- `basic_auth`: Autenticação básica
- `metrics_middleware`: Coleta de métricas
- `rate_limit`: Limite de requisições por IP
- `log_requests`: Logging estruturado

**Justificativa:**
- **Modularidade:** Concerns separados da lógica de negócio
- **Reutilização:** Aplicado a todos os endpoints
- **Manutenção:** Fácil adicionar/remover funcionalidades

### 9. Migrações com Alembic

**Implementação:** Versionamento de schema em `alembic/versions/`

**Justificativa:**
- **Rastreabilidade:** Histórico completo de mudanças no schema
- **Reversibilidade:** Rollback seguro em caso de problemas
- **CI/CD:** Automação de deploys de banco

### 10. Testes Abrangentes

**Implementação:** 80+ testes em `tests/` (unitários + integração)

**Justificativa:**
- **Confiabilidade:** Garante funcionamento correto
- **Refatoração:** Segurança para mudanças
- **Documentação:** Testes servem como exemplos de uso


## 📖 Exemplos de Uso

> **Nota**: Para documentação completa e teste interativo, acesse **http://localhost:8000/docs** (Swagger)

### cURL

```bash
# Criar usuário
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "João Silva", "email": "joao@example.com"}'

# Criar livro
curl -X POST "http://localhost:8000/books/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Clean Code", "author": "Robert C. Martin"}'

# Criar empréstimo
curl -X POST "http://localhost:8000/loans/" \
  -H "Content-Type: application/json" \
  -d '{"user_key": "user-uuid", "book_key": "book-uuid"}'

# Devolver livro
curl -X POST "http://localhost:8000/loans/return" \
  -H "Content-Type: application/json" \
  -d '{"book_key": "book-uuid"}'

# Listar empréstimos em atraso
curl "http://localhost:8000/loans/?overdue=true"

# Exportar relatório
curl "http://localhost:8000/reports/loans/export?format=csv" -o loans.csv
```

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Criar usuário
user = requests.post(f"{BASE_URL}/users/", 
    json={"name": "Maria Santos", "email": "maria@example.com"}).json()

# Criar livro
book = requests.post(f"{BASE_URL}/books/",
    json={"title": "Design Patterns", "author": "Gang of Four"}).json()

# Criar empréstimo
loan = requests.post(f"{BASE_URL}/loans/",
    json={"user_key": user["user_key"], "book_key": book["book_key"]}).json()

# Devolver
returned = requests.post(f"{BASE_URL}/loans/return",
    json={"book_key": book["book_key"]}).json()
print(f"Multa: R$ {returned['fine_amount']:.2f}")
```

---

## 📞 Links Úteis

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Healthcheck**: http://localhost:8000/
- **Métricas Prometheus**: http://localhost:8000/metrics
- **Prometheus Dashboard**: http://localhost:9090
- **Collection Postman**: [`Library_System_API.postman_collection.json`](Library_System_API.postman_collection.json)