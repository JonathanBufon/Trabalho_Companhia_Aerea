import psycopg2
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, flash
import random
import string

app = Flask(__name__)
app.secret_key = 'sua-chave-secreta-aqui'

DB_CONFIG = {
    "dbname": "companhia_aerea",
    "user": "postgres",
    "password": "sua_senha_aqui",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

@app.route('/')
def home():
    return redirect(url_for('index_reservas'))

# --- ROTAS CRUD DE VOOS E TRECHOS (NOVA SEÇÃO) ---

@app.route('/voos')
def index_voos():
    """Página para listar todos os voos e seus trechos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Usamos um dicionário para agrupar os trechos por voo
    voos_com_trechos = {}
    
    # Busca todos os voos
    cursor.execute("SELECT id, origem, destino FROM voo ORDER BY id;")
    voos = cursor.fetchall()
    
    # Para cada voo, busca seus trechos
    for voo in voos:
        voo_id = voo[0]
        cursor.execute("""
            SELECT t.id, t.data_hora_partida, t.data_hora_chegada, t.classe, a.modelo
            FROM trecho t
            JOIN aeronave a ON t.id_aeronave = a.id
            WHERE t.id_voo = %s
            ORDER BY t.data_hora_partida;
        """, (voo_id,))
        trechos = cursor.fetchall()
        voos_com_trechos[voo] = trechos

    cursor.close()
    conn.close()
    return render_template('voos.html', voos_com_trechos=voos_com_trechos)

@app.route('/voo/new', methods=('GET', 'POST'))
def new_voo():
    """Página para cadastrar um novo voo."""
    if request.method == 'POST':
        origem = request.form['origem']
        destino = request.form['destino']

        if not origem or not destino:
            flash('Origem e Destino são obrigatórios.', 'danger')
            return render_template('form_voo.html', form=request.form)

        # Gera um ID de voo aleatório (ex: AZ1234)
        id_voo = ''.join(random.choices(string.ascii_uppercase, k=2)) + ''.join(random.choices(string.digits, k=4))

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO voo (id, origem, destino) VALUES (%s, %s, %s);", (id_voo, origem, destino))
            conn.commit()
            flash(f'Voo {id_voo} cadastrado com sucesso! Agora adicione os trechos.', 'success')
            return redirect(url_for('index_voos'))
        except psycopg2.Error as e:
            if conn: conn.rollback()
            flash(f'Erro ao cadastrar o voo: {e}', 'danger')
        finally:
            if conn: conn.close()
            
    return render_template('form_voo.html', form={})

@app.route('/trecho/new/<id_voo>', methods=('GET', 'POST'))
def new_trecho(id_voo):
    """Página para adicionar um trecho a um voo existente."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        data_hora_partida = request.form['data_hora_partida']
        data_hora_chegada = request.form['data_hora_chegada']
        classe = request.form['classe']
        id_aeronave = request.form['id_aeronave']

        if not all([data_hora_partida, data_hora_chegada, classe, id_aeronave]):
            flash('Todos os campos são obrigatórios.', 'danger')
        else:
            try:
                cursor.execute("""
                    INSERT INTO trecho (data_hora_partida, data_hora_chegada, classe, id_voo, id_aeronave)
                    VALUES (%s, %s, %s, %s, %s);
                """, (data_hora_partida, data_hora_chegada, classe, id_voo, id_aeronave))
                conn.commit()
                flash('Trecho adicionado com sucesso!', 'success')
                return redirect(url_for('index_voos'))
            except psycopg2.Error as e:
                conn.rollback()
                flash(f'Erro ao adicionar trecho: {e}', 'danger')
    
    # GET: Busca aeronaves para popular o dropdown
    cursor.execute("SELECT id, modelo FROM aeronave ORDER BY modelo;")
    aeronaves = cursor.fetchall()
    
    # Busca dados do voo para exibir no título
    cursor.execute("SELECT origem, destino FROM voo WHERE id = %s;", (id_voo,))
    voo = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('form_trecho.html', id_voo=id_voo, aeronaves=aeronaves, voo=voo, form={})


# --- DEMAIS ROTAS (sem alterações) ---
# ... (Cole aqui o restante do seu código app.py para as rotas de reservas, clientes, operadoras, etc.) ...
@app.route('/reservas')
def index_reservas():
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT r.id, c.nome, r.data_reserva, r.status, STRING_AGG(v.origem || ' -> ' || v.destino, ', ') AS trechos, (SELECT id FROM venda WHERE id_reserva = r.id) as venda_id FROM reserva r JOIN cliente c ON r.cpf_cliente = c.cpf LEFT JOIN reserva_trecho rt ON r.id = rt.id_reserva LEFT JOIN trecho t ON rt.id_trecho = t.id LEFT JOIN voo v ON t.id_voo = v.id GROUP BY r.id, c.nome ORDER BY r.id DESC;")
    reservas = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('index.html', reservas=reservas)
@app.route('/reserva/edit/<int:id>', methods=('GET', 'POST'))
def edit_reserva(id):
    conn = get_db_connection(); cursor = conn.cursor()
    if request.method == 'POST':
        status = request.form['status']
        if status == 'Efetivada':
            cursor.execute("SELECT id FROM venda WHERE id_reserva = %s", (id,))
            venda_existente = cursor.fetchone()
            cursor.close(); conn.close()
            if venda_existente:
                flash('Esta reserva já possui uma venda registrada.', 'warning')
                return redirect(url_for('index_reservas'))
            else:
                return redirect(url_for('new_venda', id_reserva=id))
        try:
            cursor.execute("UPDATE reserva SET status = %s WHERE id = %s;", (status, id))
            conn.commit()
            flash('Status da reserva atualizado com sucesso!', 'success')
        except psycopg2.Error as e:
            conn.rollback(); flash(f'Erro ao atualizar o status da reserva: {e}', 'danger')
        finally:
            cursor.close(); conn.close()
        return redirect(url_for('index_reservas'))
    cursor.execute("SELECT * FROM reserva WHERE id = %s;", (id,))
    reserva_data = cursor.fetchone()
    if not reserva_data:
        flash('Reserva não encontrada!', 'danger'); return redirect(url_for('index_reservas'))
    cursor.execute("SELECT cpf, nome FROM cliente ORDER BY nome;"); clientes = cursor.fetchall()
    cursor.execute("SELECT t.id, v.origem, v.destino, t.data_hora_partida FROM trecho t JOIN voo v ON t.id_voo = v.id ORDER BY t.data_hora_partida;"); trechos = cursor.fetchall()
    cursor.execute("SELECT id_trecho FROM reserva_trecho WHERE id_reserva = %s;", (id,)); trechos_selecionados_raw = cursor.fetchall()
    trechos_selecionados = [item[0] for item in trechos_selecionados_raw]
    cursor.close(); conn.close()
    return render_template('form_reserva.html', reserva=reserva_data, clientes=clientes, trechos=trechos, trechos_selecionados=trechos_selecionados, edit_mode=True)
@app.route('/venda/new/<int:id_reserva>', methods=('GET', 'POST'))
def new_venda(id_reserva):
    conn = get_db_connection(); cursor = conn.cursor()
    if request.method == 'POST':
        try:
            valor_total = Decimal(request.form['valor_total']); id_operadora_cartao = int(request.form['id_operadora_cartao']); numero_parcelas = int(request.form['numero_parcelas'])
        except (ValueError, TypeError):
            flash('Valores inválidos. Verifique os dados.', 'danger'); return redirect(url_for('new_venda', id_reserva=id_reserva))
        try:
            cursor.execute("UPDATE reserva SET status = 'Efetivada' WHERE id = %s;", (id_reserva,))
            cursor.execute("INSERT INTO venda (id_reserva, data_venda, valor_total, id_operadora_cartao, numero_parcelas) VALUES (%s, NOW(), %s, %s, %s);", (id_reserva, valor_total, id_operadora_cartao, numero_parcelas))
            conn.commit(); flash('Venda registrada com sucesso!', 'success'); return redirect(url_for('index_reservas'))
        except psycopg2.Error as e:
            conn.rollback(); flash(f'Erro ao registrar a venda: {e}', 'danger')
        finally:
            cursor.close(); conn.close()
        return redirect(url_for('new_venda', id_reserva=id_reserva))
    cursor.execute("SELECT id, nome FROM operadora_cartao ORDER BY nome;"); operadoras = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('form_venda.html', id_reserva=id_reserva, operadoras=operadoras, form={})
@app.route('/venda/<int:id_venda>')
def view_venda(id_venda):
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT v.id, v.data_venda, v.valor_total, op.nome, v.numero_parcelas, c.nome FROM venda v JOIN reserva r ON v.id_reserva = r.id JOIN cliente c ON r.cpf_cliente = c.cpf JOIN operadora_cartao op ON v.id_operadora_cartao = op.id WHERE v.id = %s;", (id_venda,))
    venda = cursor.fetchone()
    cursor.close(); conn.close()
    if not venda:
        flash('Venda não encontrada.', 'danger'); return redirect(url_for('index_reservas'))
    return render_template('venda_detalhes.html', venda=venda)
@app.route('/operadoras')
def index_operadoras():
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM operadora_cartao ORDER BY nome;"); operadoras = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('operadoras.html', operadoras=operadoras)
@app.route('/operadora/new', methods=('GET', 'POST'))
def new_operadora():
    if request.method == 'POST':
        nome = request.form['nome']
        if not nome: flash('O nome da operadora é obrigatório.', 'danger')
        else:
            conn = get_db_connection(); cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO operadora_cartao (nome) VALUES (%s);", (nome,))
                conn.commit(); flash('Operadora cadastrada com sucesso!', 'success')
            except psycopg2.IntegrityError:
                conn.rollback(); flash('Esta operadora já existe.', 'danger')
            except psycopg2.Error as e:
                conn.rollback(); flash(f'Erro: {e}', 'danger')
            finally:
                cursor.close(); conn.close()
        return redirect(url_for('index_operadoras'))
    return render_template('form_operadora.html', operadora=None, edit_mode=False)
@app.route('/operadora/edit/<int:id>', methods=('GET', 'POST'))
def edit_operadora(id):
    conn = get_db_connection(); cursor = conn.cursor()
    if request.method == 'POST':
        nome = request.form['nome']
        if not nome: flash('O nome da operadora é obrigatório.', 'danger')
        else:
            try:
                cursor.execute("UPDATE operadora_cartao SET nome = %s WHERE id = %s;", (nome, id))
                conn.commit(); flash('Operadora atualizada com sucesso!', 'success')
            except psycopg2.Error as e:
                conn.rollback(); flash(f'Erro: {e}', 'danger')
            finally:
                cursor.close(); conn.close()
        return redirect(url_for('index_operadoras'))
    cursor.execute("SELECT id, nome FROM operadora_cartao WHERE id = %s;", (id,)); operadora = cursor.fetchone()
    cursor.close(); conn.close()
    return render_template('form_operadora.html', operadora=operadora, edit_mode=True)
@app.route('/operadora/delete/<int:id>', methods=('POST',))
def delete_operadora(id):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM operadora_cartao WHERE id = %s;", (id,))
        conn.commit(); flash('Operadora deletada com sucesso!', 'success')
    except psycopg2.Error:
        conn.rollback(); flash('Erro: Não é possível deletar uma operadora que já está em uso em uma venda.', 'danger')
    finally:
        cursor.close(); conn.close()
    return redirect(url_for('index_operadoras'))
@app.route('/clientes')
def index_clientes():
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT cpf, nome, email, cidade_residencia FROM cliente ORDER BY nome;"); clientes = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('clientes.html', clientes=clientes)
@app.route('/cliente/new', methods=('GET', 'POST'))
def new_cliente():
    if request.method == 'POST':
        cpf = request.form['cpf']; rg = request.form['rg']; nome = request.form['nome']; data_nascimento = request.form['data_nascimento']; email = request.form['email']; cidade = request.form['cidade_residencia']; uf = request.form['unidade_federal']
        if not all([cpf, rg, nome, data_nascimento, email]):
            flash('CPF, RG, Nome, Data de Nascimento e E-mail são obrigatórios!', 'danger'); return render_template('form_cliente.html', form=request.form)
        conn = None
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("INSERT INTO cliente (cpf, rg, nome, data_nascimento, email, cidade_residencia, unidade_federal) VALUES (%s, %s, %s, %s, %s, %s, %s);", (cpf, rg, nome, data_nascimento, email, cidade, uf))
            conn.commit(); flash('Cliente cadastrado com sucesso!', 'success'); return redirect(url_for('index_clientes'))
        except psycopg2.IntegrityError:
            if conn: conn.rollback(); flash('Erro: CPF ou E-mail já cadastrado no sistema.', 'danger'); return render_template('form_cliente.html', form=request.form)
        except psycopg2.Error as e:
            if conn: conn.rollback(); flash(f'Ocorreu um erro inesperado: {e}', 'danger'); return render_template('form_cliente.html', form=request.form)
        finally:
            if conn: conn.close()
    return render_template('form_cliente.html', form={})
@app.route('/reserva/new', methods=('GET', 'POST'))
def new_reserva():
    if request.method == 'POST':
        cpf_cliente = request.form['cpf_cliente']; status = request.form['status']; trechos_ids = request.form.getlist('trechos_ids')
        if not cpf_cliente or not status or not trechos_ids: flash('Todos os campos são obrigatórios!', 'danger')
        else:
            conn = None
            try:
                conn = get_db_connection(); cursor = conn.cursor()
                cursor.execute("INSERT INTO reserva (cpf_cliente, data_reserva, status) VALUES (%s, NOW(), %s) RETURNING id;", (cpf_cliente, status)); id_reserva = cursor.fetchone()[0]
                for id_trecho in trechos_ids: cursor.execute("INSERT INTO reserva_trecho (id_reserva, id_trecho) VALUES (%s, %s);", (id_reserva, id_trecho))
                conn.commit(); flash('Reserva criada com sucesso!', 'success'); return redirect(url_for('index_reservas'))
            except psycopg2.Error as e:
                if conn: conn.rollback(); flash(f'Erro ao criar a reserva: {e}', 'danger')
            finally:
                if conn: conn.close()
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT cpf, nome FROM cliente ORDER BY nome;"); clientes = cursor.fetchall()
    cursor.execute("SELECT t.id, v.origem, v.destino, t.data_hora_partida FROM trecho t JOIN voo v ON t.id_voo = v.id ORDER BY t.data_hora_partida;"); trechos = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('form_reserva.html', clientes=clientes, trechos=trechos, reserva=None, trechos_selecionados=[], edit_mode=False)
@app.route('/reserva/delete/<int:id>', methods=('POST',))
def delete_reserva(id):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM reserva WHERE id = %s;", (id,)); conn.commit(); flash('Reserva e a venda associada foram deletadas com sucesso!', 'success')
    except psycopg2.Error as e:
        conn.rollback(); flash(f'Erro ao deletar a reserva: {e}', 'danger')
    finally:
        cursor.close(); conn.close()
    return redirect(url_for('index_reservas'))

if __name__ == '__main__':
    app.run(debug=True)
