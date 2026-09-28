# АПИ для проверки токенов внешним потребителем

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import DTB_User
import DTB_Log
import json

# определяем класс обработчика HTTP запросов 
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    # проверка запроса
    def check ( self, 
                url     # url запроса
            ):
        # парсим параметры из запроса 
        query_components = parse_qs(url.query)
        # пользователь
        user = query_components.get("user", ["0000"])[0]
        # токен
        token = query_components.get("token", ["0000"])[0]
        # респондент
        resp = query_components.get("respondent", ["Неизвестно"])[0]
        
        # проверяем токен пользователя
        if DTB_User.token_check(user, token, resp):
            res = 200
        else:
            res = 201    
        # формируем ответ на запрос
        return res             
            
    # реализация метода GET HTTP запроса
    def do_GET(self):
        # парсим путь запроса
        url = urlparse(self.path)
        # устанавливаем код ответа
        resp = 200
        # получаем имя сервиса  
        match url.path:
            # сервис проверки токена : <base url>:9000/check?user=<логин/ид чата>&token=<токен>&respondent=<кто запрашивает>
            case "/check_token":
                # вызов проверки
                resp = self.check(url)
            # неизвестный сервис
            case _:
                #код ответа - все плохо
                resp = 404
                txt = "[{{'result': 'none'}}]"    
                
        # устанавливаем код ответа        
        self.send_response(resp)  
        # устанавливаем заголовок - данные приложения      
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        # отправляем ответ на запрос
        self.wfile.write("OK".encode())

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
