

# ✈️ Projeto CRUD – Companhia Aérea (Banco de Dados I)

## 📌 1. Visão Geral

Este projeto é uma aplicação web desenvolvida para a disciplina **Banco de Dados I**, com o objetivo de implementar um sistema **CRUD** (Create, Read, Update, Delete) voltado à gestão de uma companhia aérea.

A aplicação permite gerenciar **Voos**, **Trechos**, **Clientes**, **Operadoras de Cartão** e o ciclo completo de **Reservas e Vendas**.

### 🔧 Tecnologias Utilizadas

- **Backend:** Python + Flask  
- **Banco de Dados:** PostgreSQL  
- **Frontend:** HTML5 + Tailwind CSS  
- **Conexão com o Banco:** `psycopg2` (Python)

---

## 📁 2. Estrutura do Projeto

```plaintext
/
├── app.py                  # Arquivo principal com a lógica da aplicação
├── requirements.txt        # Dependências do projeto
├── script_final.sql        # Script SQL para criação e povoamento do banco
└── templates/              # Páginas HTML
    ├── layout.html         # Template base
    ├── index.html          # Tela principal (reservas)
    ├── voos.html           # Gestão de voos e trechos
    ├── clientes.html       # Cadastro de clientes
    ├── operadoras.html     # Cadastro de operadoras
    ├── venda_detalhes.html # Detalhes de venda
    ├── form_voo.html       
    ├── form_trecho.html    
    ├── form_cliente.html   
    ├── form_reserva.html   
    ├── form_operadora.html 
    └── form_venda.html
````

---

## ⚙️ 3. Funcionalidades CRUD

### ✈️ Voos e Trechos

1. Acesse **"Gerenciar Voos"**
2. Clique em **"Cadastrar Novo Voo"**
3. Informe **Origem** e **Destino** (ID é gerado automaticamente)
4. Adicione **Trechos** informando horários, classe e aeronave

### 👤 Clientes e Operadoras

* CRUD básico para cadastro de **Clientes** com CPF, nome, e-mail
* Cadastro padronizado de **Operadoras de Cartão** (ex: Visa, Mastercard)

### 🧾 Reservas e Vendas

1. **Criar Reserva:** Selecione cliente e trechos → status "Pendente"
2. **Visualizar Reservas:** Listagem com status codificado por cores
3. **Editar Status:**

   * "Cancelada" → apenas atualiza o banco
   * "Efetivada" → inicia processo de venda
4. **Efetivar Venda:** Preenche dados (valor, operadora, parcelas)

   * Operações são transacionais: rollback se houver erro
5. **Excluir Reserva:** Deleta reserva e venda associada (exclusão em cascata)

---

## 🚀 4. Instalação e Execução

### ✅ Pré-requisitos

* Python 3
* PostgreSQL
* Acesso ao terminal

### 🧱 Passo 1: Instalar PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql
```

No terminal do PostgreSQL:

```sql
ALTER USER postgres PASSWORD 'sua_senha_aqui';
\q
```

### 🛠️ Passo 2: Criar o Banco

```bash
sudo -u postgres createdb companhia_aerea
psql -U postgres -d companhia_aerea -f script_final.sql
```

### 📦 Passo 3: Configurar a Aplicação

1. Organize os arquivos numa pasta única
2. Acesse a pasta no terminal:

```bash
cd /caminho/para/seu/projeto
```

3. Instale as dependências:

```bash
pip install Flask psycopg2-binary
```

4. Edite o arquivo `app.py` e configure o acesso ao banco:

```python
DB_CONFIG = {
    "dbname": "companhia_aerea",
    "user": "postgres",
    "password": "sua_senha_aqui",  # <-- Altere aqui
    "host": "localhost",
    "port": "5432"
}
```

### ▶️ Passo 4: Executar a Aplicação

```bash
python3 -m flask run
```

Abra no navegador:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## ✅ Status

✔️ Projeto funcional
✔️ Banco de dados relacional estruturado
✔️ Transações com rollback automático
✔️ Separação clara de responsabilidades (HTML + Python + SQL)

---

## 🧑‍💻 Autor: Gabriel Victor Rosario, Jonathan Bufon, Rafael Merisio Neto

Desenvolvido como trabalho final da disciplina **Banco de Dados I** – CRUD Companhia Aérea

