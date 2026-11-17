import requests
import json
import time
import random
import vobject
import BOT.DTB_Bot
import DTB_Log
import DTB_Res
import BOT.DTB_Btn_Max
from BOT.DTB_Max_API import c_BotApiMax, MaxApiError

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

       
