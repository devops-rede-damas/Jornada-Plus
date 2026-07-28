-- ============================================================================
-- Migração 001: Tabelas `nivel` (perfis) e `coord_func` (coordenador x funcionário)
-- Banco: app_pontointerno (MySQL / InnoDB / utf8mb4)
-- ----------------------------------------------------------------------------
-- Substitui a regra hardcoded de painel_admin() por ligações persistidas.
-- Somente coordenadores 2 e 4 são migrados. Usuários inativos não entram.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- Tabela de perfis (níveis de acesso)
-- ---------------------------------------------------------------------------
CREATE TABLE nivel (
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
-- Tabela de ligação coordenador x funcionário
-- ---------------------------------------------------------------------------
CREATE TABLE coord_func (
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

-- ---------------------------------------------------------------------------
-- Seed das ligações (baseado na regra atual de painel_admin)
-- ---------------------------------------------------------------------------
-- Coordenador 4: todos os usuários ATIVOS, exceto 2, 10 e 37 (inclui o próprio 4).
INSERT INTO coord_func (id_coord, id_func)
SELECT 4, id
FROM users
WHERE status = 1
  AND id NOT IN (2, 10, 37);

-- Coordenador 2: ela mesma (2), 10 e 37 (apenas se estiverem ativos).
INSERT INTO coord_func (id_coord, id_func)
SELECT 2, id
FROM users
WHERE status = 1
  AND id IN (2, 10, 37);
