/********************************************************************************
*
* TRABALHO DE BANCO DE DADOS I - COMPANHIA AÉREA (VERSÃO FINAL)
* ESCOLA POLITÉCNICA - UNOCHAPECÓ
*
* Alunos: Gabriel Victor Rosario, Jonathan Bufon, Rafael Merisio Neto
*
* Este script cria a estrutura correta do banco, com a tabela `operadora_cartao`
* e nomes de tabelas padronizados para minúsculas.
*
********************************************************************************/

-- Passo 1: Apaga o esquema público para limpar tudo e recomeçar (CUIDADO: APAGA TUDO)
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- Recriando os tipos ENUM
CREATE TYPE classe_voo_enum AS ENUM ('Econômica', 'Executiva', 'Primeira Classe');
CREATE TYPE status_reserva_enum AS ENUM ('Pendente', 'Efetivada', 'Cancelada');

-- Tabela de clientes
CREATE TABLE IF NOT EXISTS cliente (
    cpf VARCHAR(11) PRIMARY KEY,
    rg VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    data_nascimento DATE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    cidade_residencia VARCHAR(100),
    unidade_federal CHAR(2)
);

-- Tabela de aeronaves
CREATE TABLE IF NOT EXISTS aeronave (
    id SERIAL PRIMARY KEY,
    modelo VARCHAR(50) NOT NULL,
    capacidade INT NOT NULL
);

-- Tabela de voos
CREATE TABLE IF NOT EXISTS voo (
    id VARCHAR(10) PRIMARY KEY,
    origem VARCHAR(100) NOT NULL,
    destino VARCHAR(100) NOT NULL
);

-- Tabela de trechos
CREATE TABLE IF NOT EXISTS trecho (
    id SERIAL PRIMARY KEY,
    data_hora_partida TIMESTAMP NOT NULL,
    data_hora_chegada TIMESTAMP NOT NULL,
    classe classe_voo_enum NOT NULL,
    id_voo VARCHAR(10) NOT NULL,
    id_aeronave INT NOT NULL,
    FOREIGN KEY (id_voo) REFERENCES voo(id),
    FOREIGN KEY (id_aeronave) REFERENCES aeronave(id)
);

-- Tabela de reservas
CREATE TABLE IF NOT EXISTS reserva (
    id SERIAL PRIMARY KEY,
    cpf_cliente VARCHAR(11) NOT NULL,
    data_reserva TIMESTAMP NOT NULL,
    status status_reserva_enum NOT NULL,
    FOREIGN KEY (cpf_cliente) REFERENCES cliente(cpf)
);

-- Tabela Associativa reserva_trecho
CREATE TABLE IF NOT EXISTS reserva_trecho (
    id_reserva INT NOT NULL,
    id_trecho INT NOT NULL,
    PRIMARY KEY (id_reserva, id_trecho),
    FOREIGN KEY (id_reserva) REFERENCES reserva(id) ON DELETE CASCADE,
    FOREIGN KEY (id_trecho) REFERENCES trecho(id)
);

-- Tabela de Operadoras de Cartão (NOVA)
CREATE TABLE IF NOT EXISTS operadora_cartao (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) UNIQUE NOT NULL
);

-- Tabela de vendas (MODIFICADA)
CREATE TABLE IF NOT EXISTS venda (
    id SERIAL PRIMARY KEY,
    id_reserva INT UNIQUE NOT NULL,
    data_venda TIMESTAMP NOT NULL,
    valor_total DECIMAL(10, 2) NOT NULL,
    id_operadora_cartao INT NOT NULL,
    numero_parcelas INT NOT NULL,
    FOREIGN KEY (id_reserva) REFERENCES reserva(id) ON DELETE CASCADE, -- Cascata para deletar a venda junto com a reserva
    FOREIGN KEY (id_operadora_cartao) REFERENCES operadora_cartao(id)
);

-- Tabela Auxiliar para reservas_canceladas
CREATE TABLE IF NOT EXISTS reservas_canceladas (
    id INT PRIMARY KEY,
    cpf_cliente VARCHAR(11) NOT NULL,
    data_reserva TIMESTAMP NOT NULL,
    data_cancelamento DATE NOT NULL
);

SELECT 'Estrutura do banco de dados recriada com sucesso.' AS status;

/* =============================================================================
 * SCRIPT PARA INSERÇÃO DOS DADOS (POPULAÇÃO DO BANCO)
 * =============================================================================
 */
INSERT INTO cliente (cpf, rg, nome, data_nascimento, email, cidade_residencia, unidade_federal) VALUES
('11122233344', '1234567', 'João da Silva', '1985-06-28', 'joao.silva@email.com', 'Chapecó', 'SC'),
('55566677788', '7654321', 'Maria Oliveira', '1992-03-15', 'maria.o@email.com', 'São Paulo', 'SP'),
('99988877766', '9876543', 'Pedro Souza', '2001-11-01', 'pedro.souza@email.com', 'Florianópolis', 'SC'),
('12345678900', '1122334', 'Ana Pereira', '1979-01-10', 'ana.p@email.com', 'Porto Alegre', 'RS'),
('22233344455', '2233445', 'Carlos Lima', '1995-09-20', 'carlos.lima@email.com', 'Chapecó', 'SC');

INSERT INTO aeronave (modelo, capacidade) VALUES ('Airbus A320', 180), ('Boeing 737', 160);

DROP TABLE IF EXISTS voo CASCADE;

INSERT INTO voo (id, origem, destino) VALUES
('G31303', 'Chapecó', 'Florianópolis'),
('AD4042', 'São Paulo', 'Porto Alegre'),
('LA3020', 'Florianópolis', 'São Paulo'),
('AZ5501', 'Chapecó', 'Florianópolis');

INSERT INTO trecho (data_hora_partida, data_hora_chegada, classe, id_voo, id_aeronave) VALUES
('2025-07-10 08:00:00', '2025-07-10 09:00:00', 'Econômica', 'G31303', 1),
('2025-07-15 10:00:00', '2025-07-15 11:30:00', 'Econômica', 'AD4042', 2),
('2024-05-20 14:00:00', '2024-05-20 15:15:00', 'Econômica', 'LA3020', 1);

INSERT INTO operadora_cartao (nome) VALUES ('Visa'), ('Mastercard'), ('Elo');

INSERT INTO reserva (cpf_cliente, data_reserva, status) VALUES
('11122233344', '2025-06-20 10:00:00', 'Efetivada'),
('55566677788', '2025-07-01 11:00:00', 'Efetivada'),
('99988877766', '2025-06-23 09:15:00', 'Pendente'),
('12345678900', '2024-05-10 16:00:00', 'Efetivada');

INSERT INTO reserva_trecho (id_reserva, id_trecho) VALUES (1, 1), (2, 2), (3, 1), (4, 3);

INSERT INTO venda (id_reserva, data_venda, valor_total, id_operadora_cartao, numero_parcelas) VALUES
(1, '2025-06-21 10:05:00', 450.50, 1, 3),
(2, '2025-07-02 12:00:00', 780.00, 2, 6),
(4, '2024-05-11 17:00:00', 399.90, 1, 2);


SELECT 'Dados de exemplo inseridos com sucesso.' AS status;



/* =============================================================================
 * ETAPA II - PROCEDIMENTOS, FUNÇÕES E CONSULTAS (com nomes corrigidos)
 * =============================================================================
 */

CREATE OR REPLACE PROCEDURE moverreservasnaoefetivadas()
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO reservas_canceladas (id, cpf_cliente, data_reserva, data_cancelamento)
    SELECT id, cpf_cliente, data_reserva, CURRENT_DATE FROM reserva WHERE status != 'Efetivada';
    DELETE FROM reserva WHERE status != 'Efetivada';
END;
$$;

CREATE OR REPLACE FUNCTION calcularidade(p_cpf VARCHAR(11))
RETURNS INT LANGUAGE plpgsql AS $$
DECLARE v_data_nascimento DATE;
BEGIN
    SELECT data_nascimento INTO v_data_nascimento FROM cliente WHERE cpf = p_cpf;
    IF v_data_nascimento IS NULL THEN RETURN NULL; END IF;
    RETURN EXTRACT(YEAR FROM age(CURRENT_DATE, v_data_nascimento));
END;
$$;

CREATE OR REPLACE FUNCTION contarreservascliente(p_cpf VARCHAR(11), p_data_inicio DATE, p_data_fim DATE)
RETURNS INT LANGUAGE plpgsql AS $$
DECLARE v_total_reservas INT;
BEGIN
    SELECT COUNT(*) INTO v_total_reservas FROM reserva WHERE cpf_cliente = p_cpf AND data_reserva::DATE BETWEEN p_data_inicio AND p_data_fim;
    RETURN v_total_reservas;
END;
$$;

SELECT 'Funções e Procedimentos criados com sucesso.' AS status;
