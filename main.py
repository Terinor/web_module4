from flask import Flask, render_template, request, send_from_directory
import threading
import socket
import json
import os
from datetime import datetime

# Вказуємо Flask, що HTML файли знаходяться в кореневій папці
app = Flask(__name__, template_folder='.')

# Функція для обробки статичних файлів
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Головна сторінка
@app.route('/')
def index():
    return render_template('index.html')

# Сторінка для відправки повідомлень
@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        data = request.form
        send_message_to_socket(data)
        return render_template('message.html', message_sent=True)
    return render_template('message.html', message_sent=False)

# Обробка помилки 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

def send_message_to_socket(data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(json.dumps(data).encode(), ('localhost', 5000))

# Функція для запуску Socket сервера
def run_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind(('localhost', 5000))
        while True:
            data, addr = server_socket.recvfrom(1024)
            data = json.loads(data.decode())
            save_message(data)

# Функція для збереження повідомлення у файлі
def save_message(data):
    filename = 'storage/data.json'
    if not os.path.exists('storage'):
        os.makedirs('storage')
    if os.path.exists(filename):
        with open(filename, 'r+') as file:
            file_data = json.load(file)
            file_data[str(datetime.now())] = data
            file.seek(0)
            json.dump(file_data, file, indent=4)
    else:
        with open(filename, 'w') as file:
            json.dump({str(datetime.now()): data}, file, indent=4)

if __name__ == '__main__':
    threading.Thread(target=run_socket_server).start()
    app.run(port=3000)
