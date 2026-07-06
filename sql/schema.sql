-- Criação do banco (rodar uma vez, fora de uma transação/dentro do psql):
-- CREATE DATABASE sistema_ponto;

CREATE TABLE IF NOT EXISTS funcionarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    matricula VARCHAR(30) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS marcacoes (
    id SERIAL PRIMARY KEY,
    funcionario_id INTEGER NOT NULL REFERENCES funcionarios(id) ON DELETE CASCADE,
    horario TIMESTAMP NOT NULL DEFAULT NOW(),
    is_feriado BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_marcacoes_funcionario ON marcacoes(funcionario_id);
