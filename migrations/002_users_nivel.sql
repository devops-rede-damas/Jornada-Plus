-- ============================================================================
-- Migração 002: Substitui users.perfil (VARCHAR) por users.nivel (INT FK nivel)
-- Banco: app_pontointerno (MySQL / InnoDB)
-- ----------------------------------------------------------------------------
-- Mapeamento:
--   perfil = 'admin' -> nivel = 2 (Coordenador)
--   demais (user)    -> nivel = 3 (Funcionario)
--   id 34            -> nivel = 1 (Administrador)
-- ============================================================================

-- 1) Cria a nova coluna já com padrão Funcionario (3)
ALTER TABLE users
    ADD COLUMN nivel INT(11) NOT NULL DEFAULT 3 AFTER perfil;

-- 2) Aplica o mapeamento
UPDATE users SET nivel = 2 WHERE perfil = 'admin';
UPDATE users SET nivel = 1 WHERE id = 34;

-- 3) Remove a coluna antiga
ALTER TABLE users DROP COLUMN perfil;

-- 4) Cria a FK para a tabela nivel
ALTER TABLE users
    ADD CONSTRAINT fk_users_nivel FOREIGN KEY (nivel) REFERENCES nivel (id);
