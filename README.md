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
│   │   └── aniversariantes.py
│   │
│   ├── templates/           # HTMLs (Jinja2)
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
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
| `/aniversariantes`       | Aniversariantes do mês | Público         |
| `/movidesk`              | Gestão à Vista (Movidesk) | Público      |

---

## Tecnologias

- **Backend:** Flask 3, Flask-Login, Flask-Mail, PyMySQL
- **Frontend:** Bootstrap 5, Chart.js, AOS, GSAP
- **Banco:** MySQL com PyMySQL
- **Auth:** Werkzeug (hash de senhas), itsdangerous (tokens)
