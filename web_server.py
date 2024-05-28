import socket
import os
import threading
import datetime

SUPPORTED_EXTENSIONS = ['.html', '.css', '.js']
LOG_FILE = 'server.log'
WORKING_DIR = 'www'
response_codes = {
    405: 'Method Not Allowed',
    200: 'OK',
    403: 'Forbidden',
    404: 'Not Found'
}


def log(client_ip, requested_file, status_code):
    with open(LOG_FILE, 'a') as log:
        log.write(f"{datetime.datetime.now()} - {client_ip} - {requested_file} - {status_code}\n")


def response(conn, status_code, content, content_type):
    response = f"HTTP/1.1 {status_code}\r\n"
    response += f"Date: {datetime.datetime.utcnow().strftime('%d %H:%M:%S GMT')}\r\n"
    response += "Server: Server 1.0\r\n"
    response += f"Content-Length: {len(content)}\r\n"
    response += f"Content-Type: {content_type}\r\n"
    response += "Connection: close\r\n"
    response += "\r\n"
    response = response.encode() + content
    conn.sendall(response)
    conn.close()


def handle_request(conn, addr):
    try:
        data = conn.recv(8192)
        if not data:
            return

        request = data.decode().split('\r\n')[0]
        method, path, _ = request.split()

        resp_content = None
        status_code = 200

        if method != 'GET':
            status_code = 405

        filepath = os.path.join(WORKING_DIR, path.lstrip('/'))
        file_ext = os.path.splitext(filepath)[1]

        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, 'rb') as file:
                resp_content = file.read()
        else:
            status_code = 404

        if file_ext not in SUPPORTED_EXTENSIONS:
            status_code = 403

        log(addr[0], path, status_code)
        if status_code != 200:
            response(conn, status_code, response_codes[status_code].encode(), content_type='text/plain')
        else:
            response(conn, status_code, resp_content, content_type=f"text/{file_ext[1:]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":

    if not os.path.exists(WORKING_DIR):
        os.mkdir(WORKING_DIR)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        HOST = '' or input('HOST:')
        PORT = input('PORT (default 8000)')
        PORT = int(PORT) if PORT else 8000
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Сервер запущен на данном адресе {HOST}:{PORT} ...")

        while True:
            conn, addr = server_socket.accept()
            print(f"Новое подключение  {addr}")
            threading.Thread(target=handle_request, args=(conn, addr)).start()
