-- ============================================================================
-- Migração 003: Tabela `fila_massagem` (fila de massagens)
-- Banco: app_pontointerno (MySQL / InnoDB / utf8mb4)
-- ----------------------------------------------------------------------------
-- Fila persistente e rotativa. A ordem inicial é explícita (coluna `ordem`).
-- Ao concluir uma massagem, o usuário recebe ordem = MAX(ordem)+1 (vai pro fim).
-- Usuários inativos e os IDs 2 e 4 não entram na fila (filtrado na aplicação).
-- ============================================================================

CREATE TABLE fila_massagem (
    id            INT(11)   NOT NULL AUTO_INCREMENT,
    id_func       INT(11)   NOT NULL,
    ordem         INT(11)   NOT NULL,
    vezes         INT(11)   NOT NULL DEFAULT 0,
    ultima_vez    TIMESTAMP NULL DEFAULT NULL,
    criado_em     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modificado_em TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_fila_func (id_func),
    CONSTRAINT fk_fila_func FOREIGN KEY (id_func) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- Ordem inicial da fila (user.id na sequência fornecida)
-- ---------------------------------------------------------------------------
INSERT INTO fila_massagem (id_func, ordem) VALUES
    (10, 1),
    (1,  2),
    (32, 3),
    (16, 4),
    (34, 5),
    (5,  6),
    (36, 7),
    (33, 8),
    (7,  9),
    (37, 10);
