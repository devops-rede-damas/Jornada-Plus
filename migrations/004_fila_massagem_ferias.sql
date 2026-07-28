-- ============================================================================
-- Migração 004: Adiciona coluna `ferias` na tabela `fila_massagem`
-- Banco: app_pontointerno (MySQL / InnoDB)
-- ----------------------------------------------------------------------------
-- Quando `ferias = 1`, o usuário é pulado na escolha do "próximo da vez",
-- mas NÃO perde a posição (a coluna `ordem` permanece inalterada).
-- Ao voltar (ferias = 0), retoma exatamente a posição em que estava.
-- ============================================================================

ALTER TABLE fila_massagem
    ADD COLUMN ferias TINYINT(1) NOT NULL DEFAULT 0 AFTER ultima_vez;
