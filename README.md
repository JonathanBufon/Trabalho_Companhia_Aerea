# **Projeto CRUD \- Companhia Aérea (Banco de Dados I)**

## **1\. Visão Geral**

Este projeto consiste numa aplicação web completa desenvolvida para a disciplina de Banco de Dados I. A aplicação implementa um sistema CRUD (Create, Read, Update, Delete) para gerir as operações de uma companhia aérea, seguindo o estudo de caso proposto.

O sistema permite a gestão de Voos, Trechos, Clientes, Operadoras de Cartão e, principalmente, o ciclo de vida de uma Reserva, desde a sua criação até à efetivação numa Venda.

### **Tecnologias Utilizadas**

* **Backend:** Python com o micro-framework Flask.  
* **Banco de Dados:** PostgreSQL.  
* **Frontend:** HTML5 com o framework CSS Tailwind CSS para estilização.  
* **Comunicação com o Banco:** Biblioteca psycopg2 do Python.

## **2\. Estrutura do Projeto**

A aplicação está organizada na seguinte estrutura de ficheiros e pastas:

/  
|-- app.py                  \# Ficheiro principal do backend, com toda a lógica da aplicação.  
|-- requirements.txt        \# Lista de dependências Python para o projeto.  
|-- script\_final.sql        \# Script SQL para criar e popular o banco de dados.  
|  
└───/templates/             \# Pasta que contém todos os ficheiros HTML (as telas do sistema).  
    |-- layout.html         \# Template base, com o menu de navegação e estrutura padrão.  
    |-- index.html          \# Tela principal, para listagem e gestão de Reservas.  
    |-- voos.html           \# Tela para listagem e gestão de Voos e seus Trechos.  
    |-- clientes.html       \# Tela para listagem de Clientes.  
    |-- operadoras.html     \# Tela para listagem e gestão de Operadoras de Cartão.  
    |-- venda\_detalhes.html \# Tela para exibir os detalhes de uma Venda já realizada.   
    |-- form\_voo.html  
    |-- form\_trecho.html  
    |-- form\_cliente.html  
    |-- form\_reserva.html  
    |-- form\_operadora.html  
    └── form\_venda.html

## **3\. Como Funciona o CRUD**

A aplicação é dividida em módulos lógicos, cada um responsável por uma entidade do banco de dados.

### **3.1. Gestão de Voos e Trechos**

Este é o ponto de partida para a criação de viagens.

* **Fluxo de Cadastro:**  
  1. O utilizador acede ao ecrã **"Gerenciar Voos"**.  
  2. Clica em **"Cadastrar Novo Voo"**.  
  3. Um formulário simples solicita a **Origem** e o **Destino**. O **ID do Voo** é gerado aleatoriamente pelo sistema (ex: AZ1234).  
  4. Após cadastrar o voo, o utilizador pode clicar em **"+ Adicionar Trecho"** para aquele voo específico.  
  5. O formulário de trecho solicita **Data/Hora de Partida e Chegada**, a **Classe** e a **Aeronave** (selecionada de uma lista).

### **3.2. Gestão de Clientes e Operadoras**

Estas são entidades de suporte, geridas de forma simples.

* **Clientes:** Um CRUD básico permite cadastrar novos clientes com todos os dados solicitados (CPF, nome, e-mail, etc.).  
* **Operadoras de Cartão:** Um CRUD permite cadastrar e gerir as operadoras de cartão de crédito (ex: Visa, Mastercard). Isso garante que os dados sejam consistentes, pois, ao registar uma venda, o utilizador selecionará uma operadora de uma lista, em vez de digitar o nome livremente.

### **3.3. Gestão de Reservas e Vendas (Fluxo Principal)**

Este é o coração da aplicação, implementando a principal regra de negócio do trabalho.

1. **Criação da Reserva (Create):**  
   * No ecrã **"Gerenciar Reservas"**, o utilizador clica em **"+ Nova Reserva"**.  
   * Um formulário permite selecionar um **Cliente** e um ou mais **Trechos** de voos já cadastrados.  
   * A reserva é criada com o status inicial de **"Pendente"**.  
2. **Visualização das Reservas (Read):**  
   * O ecrã principal lista todas as reservas, exibindo o status de cada uma com um código de cores para fácil identificação.  
3. **Atualização de Status (Update):**  
   * O utilizador pode clicar em **"Editar Status"** em qualquer reserva.  
   * **Cenário 1 (Cancelar):** Se o status for alterado para **"Cancelada"**, a aplicação simplesmente atualiza o registo no banco.  
   * **Cenário 2 (Efetivar Venda):** Se o status for alterado para **"Efetivada"**, a aplicação inicia o fluxo de venda.  
4. **Fluxo de Venda:**  
   * Ao tentar efetivar uma reserva, o sistema redireciona o utilizador para o formulário **"Registrar Venda"**.  
   * Neste formulário, o utilizador informa o **Valor Total**, seleciona a **Operadora do Cartão** de uma lista e o **Número de Parcelas**.  
   * Ao confirmar, a aplicação executa uma transação no banco de dados:  
     a. Atualiza o status da reserva para "Efetivada".  
     b. Insere um novo registo na tabela venda, ligando-o à reserva.  
   * Se qualquer um desses passos falhar, a transação é desfeita (rollback), garantindo a consistência dos dados.  
5. **Exclusão da Reserva (Delete):**  
   * O utilizador pode deletar uma reserva a qualquer momento.  
   * A aplicação possui uma lógica de **exclusão em cascata no backend**: ao receber o pedido para deletar uma reserva, ela primeiro deleta a venda associada (se houver) e depois deleta a reserva em si. Isso evita erros de violação de chave estrangeira no banco de dados.

## **4\. Guia de Instalação e Execução**

Siga os passos abaixo para configurar e rodar o projeto num ambiente Linux (como Pop\!\_OS ou Ubuntu).

### **Pré-requisitos**

* Python 3 instalado.  
* Acesso ao terminal.

### **Passo 1: Instalar e Configurar o PostgreSQL**

Se ainda não tiver o PostgreSQL instalado, siga estes comandos no terminal:

\# Atualiza os pacotes do sistema  
sudo apt update

\# Instala o PostgreSQL  
sudo apt install postgresql postgresql-contrib

\# Acede ao psql como superutilizador para configurar a senha  
sudo \-u postgres psql

Dentro do psql, execute o comando abaixo, trocando pela sua senha:

ALTER USER postgres PASSWORD 'sua\_senha\_aqui';

Depois, saia do psql com \\q.

### **Passo 2: Configurar o Banco de Dados**

1. **Crie o banco:**  
   \# Cria o banco de dados que será usado pela aplicação  
   sudo \-u postgres createdb companhia\_aerea

2. **Execute o Script SQL:**  
   * Salve o script SQL final do projeto (ex: script\_final.sql).  
   * Execute o script para criar todas as tabelas e popular os dados de exemplo.

\# Este comando pedirá a senha que definiu no Passo 1  
psql \-U postgres \-d companhia\_aerea \-f script\_final.sql

### **Passo 3: Configurar a Aplicação Python**

1. **Crie a Pasta do Projeto:** Organize todos os ficheiros (app.py, templates/, etc.) dentro de uma única pasta.  
2. **Navegue até à Pasta:** Abra o terminal e use o comando cd para entrar na pasta do seu projeto.  
3. **Instale as Dependências:**  
   \# Instala o Flask e o conector do PostgreSQL  
   pip install Flask psycopg2-binary

4. **Configure a Senha no Código:**  
   * Abra o ficheiro app.py.  
   * Encontre a secção DB\_CONFIG e **altere a senha** para a mesma que configurou no Passo 1\.

DB\_CONFIG \= {  
    "dbname": "companhia\_aerea",  
    "user": "postgres",  
    "password": "sua\_senha\_aqui", \# \<-- MUDE AQUI  
    "host": "localhost",  
    "port": "5432"  
}

### **Passo 4: Executar a Aplicação**

1. **Inicie o Servidor:** No terminal, dentro da pasta do projeto, execute:  
   python3 \-m flask run

2. **Aceda no Navegador:** O terminal mostrará uma mensagem indicando que o servidor está a rodar. Abra o seu navegador e aceda ao endereço:  
   * [**http://127.0.0.1:5000**](http://127.0.0.1:5000)

Pronto\! A sua aplicação CRUD estará totalmente funcional.
