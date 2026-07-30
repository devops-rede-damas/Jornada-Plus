# Sistema de Aprovação - Ponto Interno

Sistema web para gerenciamento de solicitações de ponto (horas extras, compensações e saídas antecipadas) da equipe de TI.

---

## Pré-requisitos

| Ferramenta | Versão mínima |
|------------|---------------|
| Python     | 3.10+         |
| MySQL      | 5.7+          |
| pip        | incluído no Python |

---

## Instalação rápida

### 1. Clone ou copie o projeto para sua máquina

### 2. Configure o banco de dados

Crie o banco no MySQL:

```sql
CREATE DATABASE app_pontointerno CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Configure as credenciais

Copie o arquivo de exemplo e preencha com seus dados:

```bash
copy .env.exemplo .env
```

Edite o `.env` com as credenciais do banco, email SMTP e chave secreta.

### 4. Rode a aplicação

**Opção A — Automático (Windows):**

Dê um duplo-clique no `iniciar.bat`. Ele cria o ambiente virtual, instala dependências e inicia o servidor.

**Opção B — Manual (qualquer SO):**

```bash
# Cria o ambiente virtual
python -m venv venv

# Ativa (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Ativa (Windows CMD)
venv\Scripts\activate.bat

# Ativa (Linux/Mac)
source venv/bin/activate

# Instala dependências
pip install -r requirements.txt

# Inicia
python run.py
```

### 5. Acesse no navegador

```
http://localhost:5001
```

---

## Executando com Docker

O projeto inclui `Dockerfile` e `docker-compose.yml` para rodar em container
(Gunicorn na porta 5001). O banco de dados **não** sobe junto: o container
conecta ao MySQL definido no `.env` (ex.: um servidor MySQL existente).

```bash
# Sobe (ou reconstrói) o container em segundo plano
docker compose up -d --build

# Acompanha os logs
docker compose logs -f web

# Derruba o container
docker compose down
```

> **Importante:** o código é copiado durante o build. Após alterar arquivos
> Python ou templates, rode `docker compose up -d --build` novamente para que
> as mudanças tenham efeito. Apenas `app/static/arquivos` é montado como volume.

---

## Estrutura do projeto

```
├── .env                     # Credenciais (NÃO vai pro git)
├── .env.exemplo             # Template de configuração
├── .gitignore
├── requirements.txt
├── iniciar.bat              # Script de inicialização (Windows)
├── run.py                   # Ponto de entrada
│
├── app/
│   ├── __init__.py          # Application Factory (Flask)
│   ├── config.py            # Carrega configurações do .env
│   ├── banco.py             # Conexão centralizada com MySQL
│   ├── modelos.py           # Modelo de Usuário (Flask-Login)
│   ├── utilidades.py        # Funções auxiliares
│   │
│   ├── rotas/               # Blueprints organizados por domínio
│   │   ├── principal.py     # Página inicial + notificação
│   │   ├── autenticacao.py  # Login, logout, reset de senha
│   │   ├── solicitacoes.py  # CRUD de solicitações
│   │   ├── painel.py        # Dashboard do administrador
│   │   ├── perfil.py        # Perfil do usuário
│   │   ├── massagem.py      # Fila de massagem (rotativa + férias)
│   │   └── aniversariantes.py
│   │
│   ├── templates/           # HTMLs (Jinja2)
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
│
├── migrations/              # Scripts SQL de evolução do banco
│   ├── 001_coord_func.sql
│   ├── 002_users_nivel.sql
│   ├── 003_fila_massagem.sql       # Tabela da fila de massagem
│   └── 004_fila_massagem_ferias.sql # Coluna de férias na fila
│
├── Dockerfile               # Imagem da aplicação (Gunicorn)
├── docker-compose.yml       # Orquestração do container web
└── .dockerignore
```

---

## Páginas do sistema

| Rota                     | Página                 | Acesso          |
|--------------------------|------------------------|-----------------|
| `/`                      | Página inicial         | Público         |
| `/login`                 | Login                  | Público         |
| `/recuperar_senha`       | Recuperação de senha   | Público         |
| `/alterar_senha/<token>` | Nova senha via email   | Público (token) |
| `/solicitacoes`          | Minhas solicitações    | Logado          |
| `/nova_solicitacao`      | Criar/editar solicitação | Logado        |
| `/perfil`                | Perfil do usuário      | Logado          |
| `/painel`                | Dashboard admin        | Admin           |
| `/tabela_solicitacoes/<id>` | Solicitações de um colaborador | Admin |
| `/massagem`              | Fila de massagem       | Logado (exceto IDs 2 e 4) |
| `/aniversariantes`       | Aniversariantes do mês | Público         |
| `/movidesk`              | Gestão à Vista (Movidesk) | Público      |

---

## Fila de Massagem

Fila rotativa e persistente para organizar a ordem das massagens:

- O **próximo da vez** aparece em destaque no topo (verde). Ao concluir, a
  pessoa vai para o **fim da fila**.
- Usuários **inativos** não aparecem na fila.
- **Férias:** qualquer pessoa que vê a página pode marcar/desmarcar alguém de
  férias. A linha fica **amarela**, a pessoa é **pulada** na vez (a numeração
  não conta ela) mas **não perde a posição** — ao voltar, retoma exatamente o
  lugar em que estava.
- **Acesso:** os usuários de **IDs 2 e 4** não veem o link no menu e, caso
  tentem acessar a rota diretamente pela URL, são barrados e **devolvidos à
  última página** em que estavam.
- Um bloco de aviso no rodapé da página resume essas regras.

---

## Tecnologias

- **Backend:** Flask 3, Flask-Login, Flask-Mail, PyMySQL
- **Frontend:** Bootstrap 5, Chart.js, AOS, GSAP
- **Banco:** MySQL com PyMySQL
- **Auth:** Werkzeug (hash de senhas), itsdangerous (tokens)
- **Deploy:** Docker + Gunicorn
