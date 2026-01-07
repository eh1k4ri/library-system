# Library System API - Sistema de Gerenciamento de Biblioteca Digital

---

## Instalação e Execução

### Setup Rápido

```bash
# 1. Clone e entre no diretório
git clone https://github.com/eh1k4ri/library-system.git
cd ./library-system

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
- **Prometheus**: http://localhost:9090/targets

### Verificação

```bash
# Testes
pytest

# Healthcheck
curl http://localhost:8000/

# Métricas
curl http://localhost:8000/metrics
```
---

## Funcionalidades Implementadas

### Requisitos Obrigatórios

#### Entidades Obrigatórias
| Entidade | Caminho do Arquivo |
| :--- | :--- |
| **Usuário** | `app/models/user.py` |
| **Livro** | `app/models/book.py` |
| **Empréstimo** | `app/models/loan.py` |

#### Status das Entidades
**User Status:**
- `active` - Usuário ativo (pode fazer empréstimos)
- `suspended` - Usuário suspenso (não pode fazer empréstimos)
- `deactivated` - Usuário desativado (não pode fazer empréstimos)

**Book Status:**
- `available` - Livro disponível para empréstimo
- `loaned` - Livro emprestado

**Loan Status:**
- `active` - Empréstimo em andamento
- `returned` - Empréstimo devolvido

**Reservation Status:**
- `active` - Reserva ativa
- `cancelled` - Reserva cancelada
- `completed` - Reserva concluída (usuário pegou o livro)

#### **Gestão de Usuários**
| Requerimento | Método | Endpoint |
| :--- | :---: | :--- |
| Listar todos os usuários | `GET` | `/users/` |
| Cadastrar novo usuário | `POST` | `/users/` |
| Buscar usuário por UUID (usando uuid visando segurança) | `GET` | `/users/{user_key}` |
| Listar todos os empréstimos ativos associados a um usuário | `GET` | `/users/{user_key}/loans?status=active` |


#### **Catálogo de Livros**
| Requerimento | Método | Endpoint |
| :--- | :---: | :--- |
| Listar todos os livros | `GET` | `/books/` |
| Cadastrar novo livro vinculado a um autor | `POST` | `/books/` |
| Verificar disponibilidade para empréstimo | `GET` | `/books/{book_key}/availability` |

#### **Sistema de Empréstimos**
| Requerimento | Método | Endpoint |
| :--- | :---: | :--- |
| Realizar empréstimo de livro | `POST` | `/loans/` |
| Processar devolução com cálculo de multa | `POST` | `/loans/return` |
| Listar empréstimos ativos/atrasados | `GET` | `/loans/` |
| Consultar histórico de empréstimos por usuário | `GET` | `/users/{user_key}/loans` |

**Regras de Negócio Implementadas:**
- Prazo padrão: 14 dias (`LOAN_DEFAULT_DAYS`)
- Multa: R$ 2,00 por dia de atraso (`LOAN_FINE_PER_DAY`)
- Máximo 3 empréstimos ativos por usuário (`LOAN_MAX_ACTIVE_LOANS`)

**Validações Automáticas:**
- Usuário deve estar ativo
- Livro deve estar disponível
- Limite de empréstimos por usuário
- Histórico completo com eventos imutáveis

### Funcionalidades Extras
#### Básico
| Requerimento | Método | Endpoint/Path |
| :--- | :---: | :--- |
| Implementar paginação em todas as listagens | `GET` | Todos os endpoints de listagem |
| Documentação automática com Swagger/OpenAPI | `GET` | `/docs` |
| Validação robusta com Pydantic | N/A | `/app/schemas` |
| Logging estruturado de operações | N/A | `/app/core/logging` |

#### Intermediário
| Requerimento | Método | Endpoint/Path |
| :--- | :---: | :--- |
| Sistema de reservas de livros | `POST`/`GET` | [Ver Tabela de Sistema de Reservas](#sistema-de-reservas)|
| Cache para consultas frequentes | N/A | `/app/utils/cache.py` |
| Rate limiting nos endpoints | N/A | `app/core/middlewares/rate_limit.py` |
| Testes automatizados (unitários + integração) | N/A | `/tests/` |
| Middleware de autenticação básica | N/A | `app/core/middlewares/auth.py` |

#### Avançado
| Requerimento | Método | Endpoint/Path |
| :--- | :---: | :--- |
| Notificações de vencimento (email/webhook) | N/A | `app/services/notification_service.py` |
| Sistema de renovação de empréstimos | `POST` | `/loans/{loan_key}/renew` |
| Exportação de relatórios (CSV/PDF) | `GET` | [Ver Tabela de Relatórios e Exportação](#relatórios-e-exportação) |
| Observabilidade (métricas + health check) | N/A | [Ver Tabela de Observabilidade](#observabilidade) |
| Frontend em repositório separado | N/A | [library-system-frontend](https://github.com/eh1k4ri/library-front) |

#### **Sistema de Reservas**
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/reservations/` | GET | Lista reservas com filtros |
| `/reservations/` | POST | Cria reserva para livro emprestado |
| `/reservations/{key}` | GET | Busca reserva por UUID |
| `/reservations/{key}/cancel` | POST | Cancela reserva |
| `/reservations/{key}/complete` | POST | Marca reserva como concluída |

#### **Relatórios e Exportação** 
| Endpoint | Formato | Descrição |
|----------|---------|-----------|
| `/reports/loans/export?format=csv` | CSV | Exporta empréstimos |
| `/reports/loans/export?format=pdf` | PDF | Exporta empréstimos |
| `/reports/users/export` | CSV/PDF | Exporta usuários |
| `/reports/books/export` | CSV/PDF | Exporta livros |
| `/reports/reservations/export` | CSV/PDF | Exporta reservas |

#### **Observabilidade**
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

## Decisões Arquiteturais

### 1. Arquitetura em Camadas (Service Layer Pattern)

```
┌─────────────────────────────────────┐
│   API Layer (Routers)               │  ← Recebe requisições HTTP
│   app/api/routers/                  │
├─────────────────────────────────────┤
│   Service Layer                     │  ← Regras de negócio
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
- Manutenção e escalabilidade simplificadas

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
- **Performance:** Reduz carga no banco para consultas frequentes

### 4. Tratamento de Erros Customizado

**Implementação:**
- Códigos únicos (LBS001-LBS018)
- Estrutura padronizada: `{"code": "...", "title": "...", "description": "..."}`

**Justificativa:**
- **Rastreabilidade:** Fácil identificar origem do erro
- **Suporte:** Usuários podem reportar código específico
- **Consistência:** Respostas uniformes em toda API


## Exemplos de Uso

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

## Links Úteis

- **Swagger UI**: http://localhost:8000/docs
- **Healthcheck**: http://localhost:8000/
- **Métricas**: http://localhost:8000/metrics
- **Prometheus Dashboard**: http://localhost:9090/targets