# Library System API - Sistema de Gerenciamento de Biblioteca Digital

> **Case Técnico - BTG Pactual**  
> API REST para gerenciar biblioteca digital com controle de livros, usuários e empréstimos.

---

## 📋 Cumprimento dos Requisitos do Case

### ✅ Entidades Obrigatórias (100%)
- ✅ **Usuário** → [`app/models/user.py`](app/models/user.py)
- ✅ **Livro** → [`app/models/book.py`](app/models/book.py)
- ✅ **Empréstimo** → [`app/models/loan.py`](app/models/loan.py)

### ✅ Features Necessárias (100%)

#### a) Gestão de Usuários
- ✅ Listar todos os usuários → `GET /users/`
- ✅ Cadastrar novo usuário → `POST /users/`
- ✅ Buscar usuário por ID → `GET /users/{user_key}`
- ✅ Listar empréstimos do usuário → `GET /users/{user_key}/loans`

#### b) Catálogo de Livros
- ✅ Listar livros → `GET /books/`
- ✅ Cadastrar livro com autor → `POST /books/`
- ✅ Verificar disponibilidade → `GET /books/{book_key}/availability`

#### c) Sistema de Empréstimos
- ✅ Realizar empréstimo → `POST /loans/`
- ✅ Processar devolução com multa → `POST /loans/return`
- ✅ Listar empréstimos ativos/atrasados → `GET /loans/?status=active&overdue=true`
- ✅ Histórico por usuário → `GET /users/{user_key}/loans`

**Regras de Negócio:**
- ✅ Prazo padrão: 14 dias
- ✅ Multa: R$ 2,00 por dia de atraso
- ✅ Máximo 3 empréstimos ativos por usuário

### ✅ Diferenciais Implementados

#### Básico (4/4 - 100%)
- ✅ Paginação em todas as listagens
- ✅ Documentação Swagger/OpenAPI
- ✅ Validação robusta com Pydantic
- ✅ Logging estruturado

#### Intermediário (5/5 - 100%)
- ✅ Sistema de reservas de livros
- ✅ Cache em memória (thread-safe)
- ✅ Rate limiting nos endpoints
- ✅ Testes automatizados (80+ testes)
- ✅ Middleware de autenticação básica

#### Avançado (4/5 - 80%)
- ✅ Notificações via webhook
- ✅ Sistema de renovação de empréstimos
- ✅ Exportação de relatórios (CSV/PDF)
- ✅ Observabilidade (métricas + health check)
- ❌ Frontend (não implementado)

### 📦 Entregáveis
- ✅ Código no GitHub
- ✅ README detalhado (este arquivo)
- ✅ Instruções de instalação e execução
- ✅ Documentação de decisões arquiteturais
- ✅ Lista de funcionalidades implementadas
- ✅ Exemplos de uso da API
- ✅ Collection do Postman ([`Library_System_API.postman_collection.json`](Library_System_API.postman_collection.json))
- ✅ Docker Compose para infraestrutura

---

## 🚀 Instalação e Execução

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

---

## 🎯 Padrões de Projeto Aplicados

1. **Repository Pattern** → Service Layer acessa dados via ORM
2. **Dependency Injection** → Services injetados nos routers
3. **Factory Pattern** → Criação de objetos complexos (relatórios)
4. **Strategy Pattern** → Diferentes formatos de exportação (CSV/PDF)
5. **Observer Pattern** → Sistema de notificações (webhooks)
6. **Singleton Pattern** → Cache compartilhado entre requisições

---

## 📊 Qualidade de Código

- ✅ **Type hints** completos em todo o código
- ✅ **Docstrings** em funções complexas
- ✅ **Separação de concerns** clara
- ✅ **DRY** (Don't Repeat Yourself)
- ✅ **SOLID** principles
- ✅ **Nomenclatura** consistente e descritiva
- ✅ **Tratamento de exceções** robusto
- ✅ **Logging** estruturado para debugging

---

## Funcionalidades Implementadas

### Gestão de Usuários
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

---

## 🎯 Padrões de Projeto Aplicados

1. **Repository Pattern** → Service Layer acessa dados via ORM
2. **Dependency Injection** → Services injetados nos routers
3. **Factory Pattern** → Criação de objetos complexos (relatórios)
4. **Strategy Pattern** → Diferentes formatos de exportação (CSV/PDF)
5. **Observer Pattern** → Sistema de notificações (webhooks)
6. **Singleton Pattern** → Cache compartilhado entre requisições

---

## 📊 Qualidade de Código

- ✅ **Type hints** completos em todo o código
- ✅ **Docstrings** em funções complexas
- ✅ **Separação de concerns** clara
- ✅ **DRY** (Don't Repeat Yourself)
- ✅ **SOLID** principles
- ✅ **Nomenclatura** consistente e descritiva
- ✅ **Tratamento de exceções** robusto
- ✅ **Logging** estruturado para debugging

---

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

## 🧪 Testes

### Executar Todos os Testes
```bash
pytest
```

### Cobertura de Testes
```bash
pytest --cov=app --cov-report=html
```

### Testes por Módulo
```bash
pytest tests/users/        # Testes de usuários
pytest tests/books/        # Testes de livros
pytest tests/loans/        # Testes de empréstimos
pytest tests/reservations/ # Testes de reservas
pytest tests/reports/      # Testes de relatórios
```

### Áreas Cobertas (80+ testes)
- ✅ CRUD completo de usuários
- ✅ CRUD completo de livros
- ✅ Ciclo de vida de empréstimos
- ✅ Sistema de reservas
- ✅ Cálculo de multas
- ✅ Validações de regras de negócio
- ✅ Exportação de relatórios
- ✅ Notificações (mocks)
- ✅ Healthcheck e métricas

---

## 📁 Estrutura do Projeto

```
library_system/
├── app/
│   ├── api/
│   │   ├── routers/          # Endpoints da API
│   │   └── deps.py           # Dependências compartilhadas
│   ├── core/
│   │   ├── middlewares/      # Auth, logging, rate limit, metrics
│   │   ├── constants.py      # Constantes (multas, prazos, etc)
│   │   ├── errors.py         # Erros customizados
│   │   └── logger.py         # Configuração de logs
│   ├── db/
│   │   └── session.py        # Conexão com banco
│   ├── models/               # SQLAlchemy models (ORM)
│   ├── schemas/              # Pydantic schemas (validação)
│   ├── services/             # Lógica de negócio
│   ├── utils/                # Cache, UUID, text utils
│   └── main.py               # Aplicação FastAPI
├── alembic/
│   └── versions/             # Migrações do banco
├── tests/                    # Testes automatizados
├── ops/
│   └── monitoring/           # Config do Prometheus
├── docker-compose.yml        # PostgreSQL, Redis, RabbitMQ
├── requirements.txt          # Dependências Python
├── alembic.ini              # Config Alembic
└── README.md                # Este arquivo
```

---

## 🔧 Tecnologias Utilizadas

### Core
- **Python 3.10+** - Linguagem principal
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy 2.0** - ORM para acesso a dados
- **Pydantic v2** - Validação e serialização
- **Alembic** - Migrações de banco de dados
- **PostgreSQL** - Banco de dados relacional

### Observabilidade
- **Prometheus Client** - Métricas
- **Python Logging** - Logs estruturados

### Testes
- **Pytest** - Framework de testes
- **Pytest-Cov** - Cobertura de código

### Extras
- **ReportLab** - Geração de PDFs
- **HTTPX** - Cliente HTTP para notificações
- **Docker** - Containerização
- **Redis** (opcional) - Cache distribuído
- **RabbitMQ** (opcional) - Message broker

---

## 🌟 Diferenciais Implementados

### ✅ Implementados (13/14)

1. **Paginação obrigatória** - Todas as listagens
2. **Documentação Swagger** - `/docs` interativo
3. **Validação Pydantic** - Robusta e automática
4. **Logging estruturado** - Trace ID e contexto
5. **Sistema de reservas** - Completo com notificações
6. **Cache em memória** - Thread-safe, configurável
7. **Rate limiting** - Por IP e endpoint
8. **Testes automatizados** - 80+ testes
9. **Autenticação básica** - Middleware
10. **Notificações webhook** - Eventos importantes
11. **Renovação de empréstimos** - +7 dias
12. **Exportação de relatórios** - CSV e PDF
13. **Observabilidade completa** - Métricas + health check

### ❌ Não Implementado (1/14)

14. **Frontend** - Focado na API REST

---

## 🚀 Melhorias Futuras

- [ ] Frontend React/Vue para interface gráfica
- [ ] Autenticação JWT com refresh tokens
- [ ] Upload de capas de livros (S3/MinIO)
- [ ] Sistema de avaliações e comentários
- [ ] Recomendações baseadas em histórico
- [ ] Integração com APIs externas (Google Books)
- [ ] Notificações por e-mail (SendGrid/SES)
- [ ] Deploy automatizado (CI/CD)
- [ ] Cache distribuído com Redis
- [ ] Mensageria com RabbitMQ

---

## 📞 Links Úteis

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Healthcheck**: http://localhost:8000/healthcheck
- **Métricas Prometheus**: http://localhost:8000/metrics
- **Prometheus Dashboard**: http://localhost:9090 (se iniciado)
- **Collection Postman**: [`Library_System_API.postman_collection.json`](Library_System_API.postman_collection.json)

---

## 👨‍💻 Autor

**Desenvolvido para o Case Técnico - BTG Pactual**

Demonstrando conhecimentos em:
- ✅ Arquitetura em camadas (Service Layer Pattern)
- ✅ Padrões de projeto (Repository, Factory, Strategy, Observer)
- ✅ Qualidade de código (SOLID, DRY, type hints)
- ✅ Tratamento de erros e validações robustas
- ✅ Conhecimentos extras (observabilidade, testes, cache, rate limiting)

---

## 📝 Licença

Este projeto foi desenvolvido como parte de um case técnico.

---

**⭐ Obrigado por avaliar este projeto!**
