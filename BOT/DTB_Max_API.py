# Работа с HTTP API платформы MAX.

import requests
import json
import DTB_Log

class MaxApiError(Exception):
    """HTTP-ошибка MAX API с кодом ответа и рекомендуемой задержкой повтора."""

    def __init__(self, status_code, message="", retry_after=None):
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(f"MAX API HTTP {status_code}: {message}")


class c_BotApiMax:
    """Обёртка над Max API для отправки и управления сообщениями бота."""
    
    # Инициализация API-обёртки с токеном авторизации
    def __init__(   self, 
                    _token  #Токен авторизации для Max API
                ):
  
        # Файл содержит только параметры MAX API и Long Polling.
        with open("BOT/DTB_Max_Cfg.json", "r", encoding="UTF-8") as file:
            self.config = json.load(file)


        self.header = {'Authorization': _token}
        self.base_url = self.config["ApiBaseUrl"]

        # Отдельная HTTP-сессия создаётся для каждого бота, поэтому сбои одного
        # экземпляра MAX не влияют на соединения остальных ботов.
        self.session = requests.Session()
        self.connect_timeout = self.config["HttpConnectTimeout"]
        self.read_timeout = self.config["HttpReadTimeout"]

        # Параметры длительного опроса MAX. Marker пока работает по прежней схеме;
        # его надёжное сохранение и подтверждение относятся ко второму этапу.
        self.GET_url = self.base_url + "updates"
        self.GET_params = {
            "timeout": self.config["LongPollingTimeout"],
            "limit": self.config["UpdatesLimit"],
            "types": "bot_started,message_created,message_callback"
        }

        # URL для операций с сообщениями
        self.MES_url = self.base_url + "messages"
        
        
    def GetUpdates(self):
        """Получение списка обновлений через long polling.
        
        Returns:
            dict: Ответ API с массивом обновлений и маркером для следующей итерации.
        """
        # Тайм-аут чтения больше тайм-аута Long Polling на стороне MAX:
        # это позволяет серверу штатно завершить длительный запрос.
        req = self.session.get(
            url=self.GET_url,
            params=self.GET_params,
            headers=self.header,
            timeout=(self.connect_timeout, self.read_timeout)
        )

        if req.status_code != 200:
            retry_after = req.headers.get("Retry-After")
            try:
                retry_after = float(retry_after) if retry_after is not None else None
            except (TypeError, ValueError):
                retry_after = None
            raise MaxApiError(req.status_code, req.text, retry_after)

        try:
            upd = req.json()
        except ValueError as exc:
            raise ValueError("MAX вернул ответ, который не является корректным JSON") from exc

        # Проверяем форму ответа до обращения к его полям.
        if not isinstance(upd, dict) or not isinstance(upd.get("updates"), list):
            raise ValueError("Некорректная структура ответа MAX: отсутствует список updates")

        # Сохраняем marker по прежней логике. Перенос его подтверждения на этап
        # успешной обработки событий будет выполнен отдельно, на втором этапе.
        if "marker" in upd:
            self.GET_params["marker"] = upd["marker"]

        return upd
        
    def DeleteMessage(self, _id, _ms):
        """Удаление сообщения бота.
        
        Args:
            _id: ID пользователя/чата.
            _ms: ID сообщения для удаления.
            
        Returns:
            dict: Ответ API после удаления.
        """
        params = {
            "message_id": _ms
        }
        req = self.session.delete(url=self.MES_url, params=params, headers=self.header, timeout=(self.connect_timeout, self.read_timeout))
        return json.loads(req.text)
        
        
    def SendBody(self, _id, _body):
        """Отправка сырого тела сообщения (без парсинга ответа).
        
        Args:
            _id: ID пользователя/чата.
            _body: Словарь с телом сообщения (text, attachments и т.д.).
            
        Returns:
            requests.Response: Объект ответа HTTP.
        """
        params = {
                    "user_id"               : _id,
                    "disable_link_preview"  : "False"
                }
        req = self.session.post(url=self.MES_url, params=params, headers=self.header, json=_body, timeout=(self.connect_timeout, self.read_timeout))
        return req
    
    def SendMessage(self, _id, _txt, _parse_mode="html", _reply_markup=None):        
        """Отправка текстового сообщения пользователю.
        
        Args:
            _id: ID пользователя/чата.
            _txt: Текст сообщения.
            _parse_mode: Формат парсинга текста (html по умолчанию).
            _reply_markup: Клавиатура/вложения (опционально).
            
        Returns:
            dict: Ответ API с данными отправленного сообщения.
        """        
        params = {
                    "user_id"               : _id,
                    "disable_link_preview"  : "False"
                    }

        body = {
                "text"      : _txt,
                "format"    : _parse_mode
        }
        if _reply_markup != None:
             body["attachments"] = _reply_markup

        req = self.SendBody(_id, body)

        return json.loads(req.text)
        
    def EditMessage(self, _ms, _id=None, _txt=None, _parse_mode="html", _reply_markup=None):
        """Редактирование существующего сообщения бота.
        
        Args:
            _ms: ID редактируемого сообщения.
            _id: ID пользователя/чата (опционально).
            _txt: Новый текст сообщения.
            _parse_mode: Формат парсинга текста (html по умолчанию).
            _reply_markup: Новая клавиатура/вложения (опционально).
        """
                
        params = {
            "message_id": _ms
        }

        body = {}
        
        if _txt != None:
           body = {
                  "text"      : _txt,
                   "format"    : _parse_mode
               }
          
        if _reply_markup != None:
             body["attachments"] = _reply_markup

        self.session.put(url=self.MES_url, params=params, headers=self.header, json=body, timeout=(self.connect_timeout, self.read_timeout))

    def UploadImage(self, _file_path):
        """Загрузка изображения на сервер Max API через POST /uploads.

        Этап 1: POST /uploads?type=image — получение URL загрузки.
        Этап 2: POST по URL — загрузка файла.
        Возвращает токен из ответа для использования в attachments.

        Args:
            _file_path: Путь к файлу изображения на диске.

        Returns:
            str: Токен загруженного изображения для attachments.payload.token,
                  либо None при ошибке.
        """
        UPLOAD_URL = self.base_url + "uploads?type=image"

        try:
            # Этап 1: получаем URL загрузки
            req = self.session.post(url=UPLOAD_URL, headers=self.header, timeout=(self.connect_timeout, self.read_timeout))
            resp = json.loads(req.text)

            if "url" not in resp:
                DTB_Log.log(resp, "IMG_UPLOAD_NO_URL")
                return None

            upload_url = resp["url"]

            # Этап 2: загружаем файл по полученному URL
            with open(_file_path, "rb") as img_file:
                files = {"data": img_file}
                req = self.session.post(url=upload_url, headers=self.header, files=files, timeout=(self.connect_timeout, self.read_timeout))

            if req.status_code != 200:
                DTB_Log.log(req.text, "IMG_UPLOAD_FAIL")
                return None

            # Токен возвращается в ответе после загрузки файла
            upload_resp = json.loads(req.text)
            if "photos" in upload_resp and len(upload_resp["photos"]) > 0:
                return upload_resp["photos"]["0"]["token"]

            DTB_Log.log(upload_resp, "IMG_UPLOAD_NO_TOKEN")
            return None

        except Exception as e:
            DTB_Log.log(e, "IMG_UPLOAD")
            return None
