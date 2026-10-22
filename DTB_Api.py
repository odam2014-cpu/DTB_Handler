# АПИ для проверки токенов внешним потребителем

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import DTB_User
import DTB_Log
import json

# определяем класс обработчика HTTP запросов 
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    # реализация метода POST HTTP запроса
    def do_POST(self):
        # парсим путь запроса
        url = urlparse(self.path)
        # устанавливаем код ответа
        resp = 200
        result = "none"
        # получаем имя сервиса  
        match url.path:
            # сервис проверки токена : <base url>:9000/check_token (POST)
            case "/check_token":
                # читаем тело запроса
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
                # парсим параметры из тела запроса (JSON или form-encoded)
                user = ""
                token = ""
                resp_param = "Неизвестно"
                try:
                    if post_data:
                        data = json.loads(post_data)
                        user = data.get("user", "0000")
                        token = data.get("token", "0000")
                        resp_param = data.get("respondent", "Неизвестно")
                except json.JSONDecodeError:
                    # пробуем распарсить как form-encoded
                    query_params = parse_qs(post_data)
                    user = query_params.get("user", ["0000"])[0]
                    token = query_params.get("token", ["0000"])[0]
                    resp_param = query_params.get("respondent", ["Неизвестно"])[0]
                # вызов проверки
                if DTB_User.token_check(user, token, resp_param):
                    resp = 200
                    result = "ok"
                else:
                    resp = 400
                    result = "fail"
            # неизвестный сервис
            case _:
                #код ответа - все плохо
                resp = 404
                result = "none"
                
        # формируем тело ответа
        response_body = json.dumps({"result": result}, ensure_ascii=False).encode('utf-8')
        
        # устанавливаем код ответа        
        self.send_response(resp)  
        # устанавливаем заголовок - данные приложения      
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', len(response_body))
        self.end_headers()
        # отправляем ответ на запрос
        self.wfile.write(response_body)

# запускаем параллельный поток
def run():
    # создаем поток
    thread_server = threading.Thread(
        target=start,   # функция, которая будет выполняться в потоке
            args=())    # args передаются как кортеж
    # стартуем
    thread_server.start()          
    
# стартуем http сервер
def start(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
 
    # грузим имя текущей конфигурации из файла 
    with open('DTB_Api.cfg', 'r', encoding="UTF-8") as file:
        cfg = json.load(file)
    
    # устанавливаем адрес/порт http сервера
    server_address = (cfg["ADDRESS"], int(cfg["PORT"]))
    # создаем сервер
    httpd = server_class(server_address, handler_class)
    DTB_Log.log(f"Http-сервер {server_address[0]}:{server_address[1]} создан")

    # запускаем сервер
    httpd.serve_forever()
