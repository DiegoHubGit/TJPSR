from flask import Flask, request, render_template, redirect, url_for, session
import csv
from datetime import datetime, timedelta
import os
import reportlab

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aleatoria'

usuarios = {'leandro': 'TJLeandro@', 'wemerson': 'TJWemerson@', 'diego': 'TJDiego@', 'ailton': '82667063600'}
registros = []

def calcular_horas(hora_entrada, hora_saida):
    formato = "%H:%M"
    entrada = datetime.strptime(hora_entrada, formato)
    saida = datetime.strptime(hora_saida, formato)
    if saida <= entrada:
        saida += timedelta(days=1)
    total_horas = (saida - entrada).total_seconds() / 3600
    return total_horas

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('preencher_horario'))
    mensagem = ''
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        if usuarios.get(username) == password:
            session['username'] = username
            return redirect(url_for('preencher_horario'))
        else:
            mensagem = 'Login falhou. Por favor, tente novamente.'
    return render_template('login.html', mensagem=mensagem)

@app.route('/preencher_horario', methods=['GET', 'POST'])
def preencher_horario():
    if 'username' not in session:
        return redirect(url_for('login'))
    mensagem = 'Digite os nomes separados por vírgula (,). Exemplo: João, Maria, José'
    if request.method == 'POST':
        nomes = [nome.strip() for nome in request.form['nomes'].split(',')]
        data = request.form['data']
        hora_entrada = request.form['hora_entrada']
        hora_saida = request.form['hora_saida']
        local_trabalho = request.form['local_trabalho']
        turno = request.form['turno']
        for nome in nomes:
            registros.append({
                'nome': nome,
                'data': data,
                'hora_entrada': hora_entrada,
                'hora_saida': hora_saida,
                'local_trabalho': local_trabalho,
                'turno': turno,
                'horas_trabalhadas': calcular_horas(hora_entrada, hora_saida) - (1 if turno == 'manha' else 0)
            })
        mensagem = 'Registro(s) adicionado(s) com sucesso!'
    return render_template('preencher_horario.html', mensagem=mensagem)

@app.route('/gerar_relatorio', methods=['GET'])
def gerar_relatorio():
    if 'username' not in session:
        return redirect(url_for('login'))
    nome_arquivo = f"Relatorio_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    # Define o diretório onde os relatórios serão salvos, ajuste conforme necessário
    relatorio_diretorio = os.path.join(os.getcwd(), 'relatorios')
    os.makedirs(relatorio_diretorio, exist_ok=True)
    caminho_completo = os.path.join(relatorio_diretorio, nome_arquivo)
    with open(caminho_completo, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=registros[0].keys())
        writer.writeheader()
        for registro in registros:
            writer.writerow(registro)
    mensagem = "Relatório gerado com sucesso."
    return render_template('relatorio.html', mensagem=mensagem, relatorio=nome_arquivo)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
