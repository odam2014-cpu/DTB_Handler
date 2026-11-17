import requests
import json
import time
import random
import vobject
import BOT.DTB_Bot
import DTB_Log
import DTB_Res
import DTB_Max_Cfg
import BOT.DTB_Btn_Max

class MaxApiError(Exception):
    """HTTP-ошибка MAX API с кодом ответа и рекомендуемой задержкой повтора."""

    def __init__(self, status_code, message="", retry_after=None):
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(f"MAX API HTTP {status_code}: {message}")


class c_BotApiMax:
    """Обёртка над Max API для отправки и управления сообщениями бота."""
    
    def __init__(self, _token):
        """Инициализация API-обёртки с токеном авторизации.
        
        Args:
            _token: Токен авторизации для Max API.
        """
        self.header = {'Authorization': _token}
        self.config = DTB_Max_Cfg.cfg.config
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


    def _wait_before_retry(self, delay):
        """Ожидание перед повторным запросом с небольшим случайным разбросом."""
        # Небольшой jitter не даёт нескольким ботам одновременно повторять запросы.
        delay = min(
            self.Bot.config["RetryMaxDelay"],
            max(0, random.uniform(delay * 0.8, delay * 1.2))
        )
        time.sleep(delay)

    def process_update(self, up):
        """Проверяет структуру и передаёт одно событие в общий шлюз обработки."""
        if not isinstance(up, dict):
            raise ValueError("Событие MAX имеет неверный формат")

        update_type = up.get("update_type")

        if update_type == "bot_started":
            user = up.get("user") or {}
            user_id = user.get("user_id")
            if user_id is None:
                raise ValueError("В событии bot_started отсутствует user.user_id")

            self.gate(self.name, user_id, None, "Start", "")
            return

        if update_type == "message_created":
            message = up.get("message") or {}
            sender = message.get("sender") or {}
            body = message.get("body") or {}
            user_id = sender.get("user_id")
            if user_id is None:
                raise ValueError("В событии message_created отсутствует sender.user_id")

            # Текст может отсутствовать, например, если пользователь отправил только вложение.
            message_text = body.get("text") or ""
            message_id = body.get("mid")
            message_type = "TEXT"
            phone = ""

            attachments = body.get("attachments") or []
            if not isinstance(attachments, list):
                raise ValueError("Поле message.body.attachments должно быть списком")

            # Не предполагаем, что первое вложение обязательно является контактом.
            for attachment in attachments:
                if not isinstance(attachment, dict) or attachment.get("type") != "contact":
                    continue

                message_type = "Contact"
                payload = attachment.get("payload") or {}
                vcf = payload.get("vcf_info")
                max_info = payload.get("max_info") or {}

                if vcf:
                    try:
                        vobj = vobject.readOne(stream=vcf, allowQP=True)
                        tel = getattr(vobj, "tel", None)
                        if tel is not None and getattr(tel, "value", None):
                            # Номер принимается только при совпадении ID отправителя
                            # с ID владельца профиля MAX, переданного вместе с контактом.
                            if user_id == max_info.get("user_id"):
                                phone = tel.value
                            elif max_info.get("user_id") is not None:
                                phone = "NOCORRECT"
                    except Exception as exc:
                        # Ошибка разбора карточки не должна блокировать само сообщение.
                        DTB_Log.log(exc, "MAX_CONTACT_PARSE", "_max")
                break

            self.gate(
                self.name,
                user_id,
                message_id,
                message_type,
                message_text,
                phone
            )
            return

        if update_type == "message_callback":
            callback = up.get("callback") or {}
            user = callback.get("user") or {}
            user_id = user.get("user_id")
            if user_id is None:
                raise ValueError("В событии message_callback отсутствует callback.user.user_id")

            self.gate(self.name, user_id, None, callback.get("payload") or "", "")
            return

        # Неизвестные типы не прерывают обработку остальных событий в пакете.
        DTB_Log.log(f"Неизвестный тип события MAX: {update_type}", "MAX_UPD_UNKNOWN", "_max")

    def start(self):
        """Запускает непрерывный Long Polling с восстановлением после ошибок."""
        retry_delay = self.Bot.config["RetryInitialDelay"]
        max_retry_delay = self.Bot.config["RetryMaxDelay"]

        while True:
            try:
                upd = self.Bot.GetUpdates()

                # Успешный ответ, в том числе пустой, сбрасывает накопленную задержку.
                retry_delay = self.Bot.config["RetryInitialDelay"]

                for up in upd["updates"]:
                    try:
                        self.process_update(up)
                    except Exception as exc:
                        # Ошибка одного события не должна останавливать обработку пакета.
                        DTB_Log.log(exc, "MAX_UPDATE_PROCESS", "_max")

            except MaxApiError as exc:
                status = exc.status_code
                DTB_Log.log(exc, "MAX_POLL_HTTP", "_max")

                if status == 429 and exc.retry_after is not None:
                    # Если MAX сообщил Retry-After, соблюдаем указанную паузу.
                    delay = max(0, exc.retry_after)
                    time.sleep(delay)
                else:
                    # 401/405 требуют исправления конфигурации или метода.
                    # Повторяем редко, чтобы поток не завершался и не создавал нагрузку.
                    if status in (401, 405) or 400 <= status < 500:
                        delay = max_retry_delay
                    else:
                        # Для серверных ошибок используем экспоненциальную задержку.
                        delay = retry_delay
                        retry_delay = min(retry_delay * 2, max_retry_delay)
                    self._wait_before_retry(delay)

            except (requests.Timeout, requests.ConnectionError) as exc:
                DTB_Log.log(exc, "MAX_POLL_NETWORK", "_max")
                self._wait_before_retry(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)

            except requests.RequestException as exc:
                DTB_Log.log(exc, "MAX_POLL_REQUEST", "_max")
                self._wait_before_retry(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)

            except (ValueError, json.JSONDecodeError) as exc:
                DTB_Log.log(exc, "MAX_POLL_RESPONSE", "_max")
                self._wait_before_retry(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)

            except Exception as exc:
                DTB_Log.log(exc, "MAX_POLL_RUN", "_max")
                self._wait_before_retry(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)

    def delete_message(self, _id, _ms):
        """Удаление отправленного сообщения бота.
        
        Args:
            _id: ID пользователя/чата.
            _ms: ID сообщения для удаления.
        """
        try:
            self.Bot.DeleteMessage(_id, _ms)
            # DTB_Log.log(_ms, "del", "_max")

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

        attachments = []

        # Загрузка изображения из DTB_Res
        if img != None:
            img_token = self.Bot.UploadImage(img)
            if img_token != None:
                attachments.append({
                    "type": "image",
                    "payload": {"token": img_token}
                })

        # Добавление клавиатуры
        if btn != None:
            attachments.extend(btn)

        _reply_markup = attachments if len(attachments) > 0 else None

        req = self.Bot.EditMessage(
                        _id,             # ид чата
                        _ms,             # ид сообщения
                        txt,             # текст сообщения
                        "html",          # признак, что формат HTML
                        _reply_markup    # клавиатура/вложения
                    )
        # DTB_Log.log(_ms, "edt", "_max")
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

        attachments = []

        # Загрузка изображения из DTB_Res
        if img != None:
            img_token = self.Bot.UploadImage(img)
            if img_token != None:
                attachments.append({
                    "type": "image",
                    "payload": {"token": img_token}
                })

        # Добавление клавиатуры
        if btn != None:
            attachments.extend(btn)

        _reply_markup = attachments if len(attachments) > 0 else None

        req = self.Bot.SendMessage(
                        _id,             # ид чата
                        txt,             # текст сообщения
                        "html",          # признак, что формат HTML
                        _reply_markup    # клавиатура/вложения
                    )
        try:
            mid = req["message"]["body"]["mid"]
            # DTB_Log.log(mid, "snd", "_max")
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
            # DTB_Log.log(mid, "snd", "_max")
        except Exception as e:          
            DTB_Log.log(e, "snd-err", "_max")
            mid = None
        return mid

       
