-- ============================================================================
-- Schema COMPLETO (all-in-one) para montar o banco do ZERO em ambiente local.
-- Banco: app_pontointerno (MySQL 5.7+ / InnoDB / utf8mb4)
-- ----------------------------------------------------------------------------
-- Este arquivo já contém o estado FINAL do banco (todas as migrations 001-004
-- incorporadas) MAIS usuarios de teste. Use-o apenas para instalacoes locais
-- do zero. NAO rode junto com as migrations 001-004 (elas sao o historico
-- incremental do banco de producao ja existente).
--
-- Uso:
--   CREATE DATABASE app_pontointerno CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
--   mysql -u SEU_USUARIO -p app_pontointerno < migrations/000_schema_completo.sql
--
-- Usuarios de teste (login pela "chapa"):
--   chapa: admin  | senha: admin123  | nivel 1 (Administrador)
--   chapa: coord  | senha: coord123  | nivel 2 (Coordenador)
--   chapa: func   | senha: func123   | nivel 3 (Funcionario)
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- ---------------------------------------------------------------------------
-- Tabela de perfis (niveis de acesso)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS nivel (
    id             INT(11)      NOT NULL AUTO_INCREMENT,
    nivel          VARCHAR(255) NOT NULL,
    status         INT          NOT NULL DEFAULT 1 COMMENT '1 ativo, 0 inativo',
    criado_em      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    criado_por     INT(11)      NULL DEFAULT NULL,
    modificado_em  TIMESTAMP    NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    modificado_por INT(11)      NULL DEFAULT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO nivel (id, nivel) VALUES
    (1, 'Administrador'),
    (2, 'Coordenador'),
    (3, 'Funcionario');

-- ---------------------------------------------------------------------------
-- Tabela de usuarios
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INT(11)      NOT NULL AUTO_INCREMENT,
    chapa           VARCHAR(50)  NOT NULL,
    nome            VARCHAR(255) NOT NULL,
    sobrenome       VARCHAR(255) NOT NULL DEFAULT '',
    email           VARCHAR(255) NOT NULL,
    senha_hash      VARCHAR(255) NOT NULL,
    nivel           INT(11)      NOT NULL DEFAULT 3,
    status          INT          NOT NULL DEFAULT 1 COMMENT '1 ativo, 0 inativo',
    data_nascimento DATE         NULL DEFAULT NULL,
    presente1       VARCHAR(255) NOT NULL DEFAULT '',
    presente2       VARCHAR(255) NOT NULL DEFAULT '',
    img_url         VARCHAR(255) NOT NULL DEFAULT 'default.png',
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_chapa (chapa),
    UNIQUE KEY uq_users_email (email),
    KEY fk_users_nivel (nivel),
    CONSTRAINT fk_users_nivel FOREIGN KEY (nivel) REFERENCES nivel (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Usuarios de teste (um de cada nivel).
-- Hashes gerados com werkzeug.security.generate_password_hash (scrypt).
INSERT INTO users (id, chapa, nome, sobrenome, email, senha_hash, nivel, status, data_nascimento) VALUES
    (1, 'admin', 'Administrador', 'Teste', 'admin@teste.local',
     'scrypt:32768:8:1$cmiLnJyM3YzxLt30$045be906b1e4b1c19428dbd705a0daa79c99b156ab6ada806a0d3430b295b085bf124469cce1d3a8b3729cf8a35eac53ed772990ee72453fa4c7654d3328dd53',
     1, 1, '1990-07-10'),
    (2, 'coord', 'Coordenador', 'Teste', 'coord@teste.local',
     'scrypt:32768:8:1$CVX7NvmG7ZwPqsIm$fd67507fa7fa051f0e84a935abb96d70061f8e6e2ab66a37917b7274aeadea4b89dd9ea63308e16284e74d309c00ee17a81600dd50ddc0c59d2f9240101be213',
     2, 1, '1992-07-18'),
    (3, 'func', 'Funcionario', 'Teste', 'func@teste.local',
     'scrypt:32768:8:1$WAaZqsYTjSiO0SlL$543178f6e597c521de8bb6b14fc31bc5ad80616618d0d8ffc150196245f760e2b43a11914bd6cfcc8ce02a5c434067dea0eb77ddd9b14a83a160883edf18fe4b',
     3, 1, '1995-07-25');

-- ---------------------------------------------------------------------------
-- Tabela de ligacao coordenador x funcionario
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS coord_func (
    id             INT(11)   NOT NULL AUTO_INCREMENT,
    id_func        INT(11)   NOT NULL,
    id_coord       INT(11)   NOT NULL,
    status         INT       NOT NULL DEFAULT 1 COMMENT '1 ativo, 0 inativo',
    criado_em      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    criado_por     INT(11)   NULL DEFAULT NULL,
    modificado_em  TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    modificado_por INT(11)   NULL DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_coord_func (id_coord, id_func),
    KEY fk_coord_func_func (id_func),
    KEY fk_coord_func_coord (id_coord),
    CONSTRAINT fk_coord_func_func  FOREIGN KEY (id_func)  REFERENCES users (id),
    CONSTRAINT fk_coord_func_coord FOREIGN KEY (id_coord) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- O coordenador de teste (2) enxerga o funcionario de teste (3) no painel.
INSERT INTO coord_func (id_coord, id_func) VALUES
    (2, 3);

-- ---------------------------------------------------------------------------
-- Tabela de solicitacoes (nucleo do sistema)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS solicitacoes (
    id                INT(11)      NOT NULL AUTO_INCREMENT,
    pessoa_id         INT(11)      NOT NULL,
    tipo              VARCHAR(50)  NOT NULL,
    justificativa     TEXT         NULL,
    horas             VARCHAR(10)  NOT NULL DEFAULT '00:00' COMMENT 'formato HH:MM',
    dia_acontecimento DATE         NULL DEFAULT NULL,
    links_evidencias  TEXT         NULL,
    status            VARCHAR(20)  NOT NULL DEFAULT 'pendente',
    created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY fk_solic_pessoa (pessoa_id),
    CONSTRAINT fk_solic_pessoa FOREIGN KEY (pessoa_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Alguns lancamentos de exemplo para o funcionario de teste (id 3).
INSERT INTO solicitacoes (pessoa_id, tipo, justificativa, horas, dia_acontecimento, links_evidencias, status, created_at) VALUES
    (3, 'Horas Extra',      'Virada de sistema fora do horario', '02:00', '2026-07-20', '', 'Aprovado', '2026-07-20 19:30:00'),
    (3, 'Compensacao',      'Saida para consulta medica',        '01:00', '2026-07-22', '', 'Aprovado', '2026-07-22 09:00:00'),
    (3, 'Saida Antecipada', 'Compromisso pessoal',               '00:30', '2026-07-28', '', 'pendente', '2026-07-28 16:00:00');

-- ---------------------------------------------------------------------------
-- Tabela de notificacao (data da ultima notificacao aos lideres)
-- A pagina inicial exige ao menos UMA linha nesta tabela.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notificacao (
    id                 INT(11)  NOT NULL AUTO_INCREMENT,
    ultima_notificacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO notificacao (ultima_notificacao) VALUES
    (CURRENT_TIMESTAMP);

-- ---------------------------------------------------------------------------
-- Tabela da fila de massagem (rotativa + ferias)
-- Pode iniciar vazia: a aplicacao insere os usuarios automaticamente ao
-- acessar a pagina /massagem.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fila_massagem (
    id            INT(11)   NOT NULL AUTO_INCREMENT,
    id_func       INT(11)   NOT NULL,
    ordem         INT(11)   NOT NULL,
    vezes         INT(11)   NOT NULL DEFAULT 0,
    ultima_vez    TIMESTAMP NULL DEFAULT NULL,
    ferias        TINYINT(1) NOT NULL DEFAULT 0,
    criado_em     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modificado_em TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_fila_func (id_func),
    CONSTRAINT fk_fila_func FOREIGN KEY (id_func) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
