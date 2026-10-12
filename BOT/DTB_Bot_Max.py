import requests
import json
import vobject
import BOT.DTB_Bot
import DTB_Log
import DTB_Res
import DTB_Cfg
import BOT.DTB_Btn_Max

class c_BotApiMax:
    """Обёртка над Max API для отправки и управления сообщениями бота."""
    
    def __init__(self, _token):
        """Инициализация API-обёртки с токеном авторизации.
        
        Args:
            _token: Токен авторизации для Max API.
        """
        self.header      = {'Authorization': _token}
        self.base_url    = DTB_Cfg.cfg.gs("MaxApiBaseUrl") 
        
        # URL и параметры для получения обновлений (long polling)
        self.GET_url = self.base_url + "updates"
        self.GET_params = {
                            "timeout"   : "10", 
                            "types"     : "bot_started,message_created,message_callback"
                        }
        # URL для операций с сообщениями
        self.MES_url = self.base_url + "messages"
        
        
    def GetUpdates(self):
        """Получение списка обновлений через long polling.
        
        Returns:
            dict: Ответ API с массивом обновлений и маркером для следующей итерации.
        """
        req = requests.get(url = self.GET_url, params=self.GET_params, headers=self.header)
        upd = json.loads(req.text)  
        # Сохраняем маркер для продолжения чтения с того же места
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
        req = requests.delete(url = self.MES_url, params=params, headers=self.header)
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
        req = requests.post(url = self.MES_url, params=params, headers=self.header, json=_body)
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

        requests.put(url = self.MES_url, params=params, headers=self.header, json=body)        

class c_BotMax(BOT.DTB_Bot.c_Bot):
    """Основной класс бота для работы с платформой Max."""
    
    def __init__(self, _param):
        """Инициализация бота Max.
        
        Args:
            _param: Параметры инициализации бота (название, токен и т.д.).
        """
        super().__init__(_param)  
        
        self.Bot  = c_BotApiMax(self.token)    # регистрим бота
        DTB_Log.log(f"Бот {self.name} подключен")
    
    def clear_button(self, _id, _ms):
        """Очистка клавиатуры из сообщения (удаление attachments).
        
        Args:
            _id: ID пользователя/чата.
            _ms: ID сообщения для очистки клавиатуры.
        """
        try:  
            self.Bot.EditMessage (_ms=_ms, _reply_markup=[])   
        except Exception as e:  
            DTB_Log.log(e, "DEL_MES_BTN") 


    def start(self):
        """Запуск цикла обработки обновлений (long polling).
        
        Метод постоянно опрашивает API Max на наличие новых событий и передаёт их
        в шлюз обработки (gate) для дальнейшей маршрутизации.
        """
        while True:
            try:
                upd = None
                try:
                    upd = self.Bot.GetUpdates()
                except Exception as e:
                    DTB_Log.log(e, "MAX_UPD_GET")
                if upd != None:
                    for up in upd["updates"]:
                        match up["update_type"]:
                            case "bot_started":
                                # Пользователь запустил бота
                                self.gate(  self.name, 
                                            up["user"]["user_id"], 
                                            None, 
                                            "Start", 
                                            "")

                            case "message_created":
                                # Новое сообщение от пользователя
                                typ = "TEXT"
                                pho = ""
                                if "attachments" in up["message"]["body"]:
                                    if up["message"]["body"]["attachments"][0]["type"] == "contact":
                                        typ = "Contact"
                                        vcf = up["message"]["body"]["attachments"][0]["payload"]["vcf_info"]
                                        vobj = vobject.readOne(stream=vcf, allowQP=True)
                                        # проверяем на совпадение id пользователя бота с id из контакта 
                                        if up["message"]["sender"]["user_id"] == up["message"]["body"]["attachments"][0]["payload"]["max_info"]["user_id"]:
                                            pho = vobj.tel.value
                                        # не совпало - отправляем вместо телефона NOCORRECT
                                        else:
                                            pho = "NOCORRECT"
                                DTB_Log.log(up, "txt", "_max")
                                self.gate(  self.name, 
                                            up["message"]["sender"]["user_id"], 
                                            up["message"]["body"]["mid"], 
                                            typ,
                                            up["message"]["body"]["text"], 
                                            pho)

                            case "message_callback":
                                # Нажатие на callback-кнопку
                                DTB_Log.log(up, "clb", "_max")
                                self.gate(  self.name, 
                                            up["callback"]["user"]["user_id"], 
                                            None, 
                                            up["callback"]["payload"], 
                                            "")
            except Exception as e:
                DTB_Log.log(e, "MAX_UPD_RUN")

    def delete_message(self, _id, _ms):
        """Удаление отправленного сообщения бота.
        
        Args:
            _id: ID пользователя/чата.
            _ms: ID сообщения для удаления.
        """
        try:
            self.Bot.DeleteMessage(_id, _ms)
            DTB_Log.log(_ms, "del", "_max")

        except Exception as e:  
            DTB_Log.log(e, "MAX_DEL_MES")

    def edit_message(self, _ms, _id, _key, _ins, _btn=None):
        """Редактирование отправленного сообщения бота.
        
        Args:
            _ms: ID редактируемого сообщения.
            _id: ID пользователя/чата.
            _key: Ключ сообщения для шаблона текста.
            _ins: Вставки/переменные для подстановки в текст.
            _btn: Опциональные кнопки для клавиатуры.
            
        Returns:
            str: ID отредактированного сообщения.
        """
        txt = self.build_message(_key, _ins)
        btn = BOT.DTB_Btn_Max.create(_btn)
        img = DTB_Res.get_image(_key)
            
        req = self.Bot.EditMessage(
                        _id,             # ид чата
                        _ms,             # ид сообщения
                        txt,             # текст сообщения
                        "html",          # признак, что формат HTML
                        btn              # клавиатура
                    )
        DTB_Log.log(_ms, "edt", "_max")
        return _ms

    def send_message(self, _id, _key, _ins, _btn=None):
        """Отправка нового сообщения пользователю.
        
        Args:
            _id: ID пользователя/чата.
            _key: Ключ сообщения для шаблона текста.
            _ins: Вставки/переменные для подстановки в текст.
            _btn: Опциональные кнопки для клавиатуры.
            
        Returns:
            str: ID отправленного сообщения или None при ошибке.
        """
        txt = self.build_message(_key, _ins)
        btn = BOT.DTB_Btn_Max.create(_btn)
        img = DTB_Res.get_image(_key)
        
        req = self.Bot.SendMessage(
                        _id,             # ид чата
                        txt,             # текст сообщения
                        "html",          # признак, что формат HTML
                        btn              # клавиатура
                    )
        try:
            mid = req["message"]["body"]["mid"]
            DTB_Log.log(mid, "snd", "_max")
        except Exception as e:
            mid = None       
            DTB_Log.log(e, "snd-err", "_max")
        return mid
        
        
    def send_wait(self, _id):
        """Отправка анимации ожидания (стикер) пользователю.
        
        Используется для визуального обозначения процесса обработки запроса.
        
        Args:
            _id: ID пользователя/чата.
            
        Returns:
            str: ID отправленного сообщения или None при ошибке.
        """
        params = {
                    "user_id"               : _id,
                    "disable_link_preview"  : "False"
                    }

        body = {
                "text"          : "",
                "attachments"   :   [
                                        {
                                            "type"  : "sticker",
                                            "payload" : {
                                                "code" : "10d2970bb"
                                            }
                                        }
                                    ]
        }

        req = self.Bot.SendBody(_id, body)
        try:
            mid = json.loads(req.text)["message"]["body"]["mid"]
            DTB_Log.log(mid, "snd", "_max")
        except Exception as e:          
            DTB_Log.log(e, "snd-err", "_max")
            mid = None
        return mid

       
