import BOT.DTB_Bot
import BOT.DTB_Btn_Tlg
import DTB_Log
import DTB_Res
from telebot import apihelper, TeleBot

class c_BotTelegram(BOT.DTB_Bot.c_Bot):
    def __init__(self, _param):
        super().__init__(_param)  
        
        
        
        apihelper.proxy = {'https':'socks5h://bumz9h:dokHSW@161.115.226.216:9423'}
        #apihelper.proxy = {'https':'socks5h://sJ6wMR:Fs8Evk@45.153.20.235:11307'}
        
        self.Bot  = TeleBot(self.token)    # регистрим бота
        DTB_Log.log(f"Бот {self.name} подключен")

# переопределение обработчика сообщений всех типов
        @self.Bot.message_handler(content_types=["text", "audio", "document", "photo", "sticker", "video", "video_note", "voice", "location", "contact",
                            "new_chat_members", "left_chat_member", "new_chat_title", "new_chat_photo", "delete_chat_photo",
                            "group_chat_created", "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
                            "migrate_from_chat_id", "pinned_message"])  
        def handler_message(_ms):  
            # контекст - текст
            match _ms.content_type:
                case "text":
                    self.gate(self.name, _ms.chat.id, _ms.id, "TEXT", _ms.text)
                case "contact":
                    self.gate(self.name, _ms.chat.id, _ms.id, "Contact", _ms.text, _ms.contact.phone_number)   
            # контекст - что-то другое
                case _: 
                    self.gate(self.name, _ms.chat.id, _ms.id, "OTHER", _ms.text)

            # переопределение обработчика callback

        @self.Bot.callback_query_handler()
        def handler_call(_cb):
            # вызов шлюза
            self.gate(self.name, _cb.message.chat.id, None, _cb.data, "")
    
    def clear_button(   self,
                        _id,
                        _ms    
                   ):
        try:  
                self.Bot.edit_message_reply_markup(     _id,                     # ид чата 
                                                        message_id = _ms,        # ид сообщения
                                                        reply_markup = None      # кнопок нет
                                            )   
        except Exception as e:  
            DTB_Log.log(e, "DEL_MES_BTN") 

    def start(self):
        self.Bot.infinity_polling() 

    def delete_message(  self,
                        _id,   # ид чата  
                        _ms    # ид сообщения
                    ):
        try:
            self.Bot.delete_message(    _id,   # ид чата  
                                        _ms    # ид сообщения
                                )
        except Exception as e:  
            DTB_Log.log(e, "TLG_DEL_MES")

    def send_message(   self,
                        _id,                    # ид чата
                        _key,                   # ключ сообщения
                        _ins,                   # вставки в сообщение
                        _btn   = None           # кнопки
    ):
        txt = self.build_message(_key, _ins)
        btn = BOT.DTB_Btn_Tlg.create(_btn)
        img = DTB_Res.get_image(_key)
        
        if img == None:
            mID = self.Bot.send_message(
                            _id,                            # ид чата
                            txt,                            # текст сообщения
                            parse_mode="HTML",              # признак, что формат HTML
                            reply_markup = btn              # клавиатура
                        )
        else:
            # если есть картинка
            # загружаем из файла
            with open(img, "rb") as photo:
                # сохраняем ИД отправленного сообщения 
                mID = self.Bot.send_photo(
                                _id,                    # ид чата
                                photo,                  # загруженное фото
                                txt,                    # текст сообщения
                                parse_mode='HTML',      # признак, что формат HTML
                                reply_markup = btn      # клавиатура
                            )
           
        return mID.id
    
    def send_wait(self, _id):
            
        return self.send_message(
                                _id,
                                "",
                                "💤"   # эмоджи
                            )

    def edit_message(   self,
                        _id,                    # ид чата
                        _ms,                    # id сообщения
                        _key,                   # ключ сообщения
                        _ins,                   # вставки в сообщение
                        _btn   = None           # кнопки
    ):
        txt = self.build_message(_key, _ins)
        btn = BOT.DTB_Btn_Tlg.create(_btn)
            
        self.Bot.edit_message_text(     text = txt,             # новый текс
                                        chat_id = _id,          # ид чата 
                                        message_id = _ms,       # ид сообщения
                                        parse_mode='HTML',      # признак, что формат HTML
                                        reply_markup = btn      # кнопок нет
                                    )   
        DTB_Log.log(_ms, "edt", "_max")

        return _ms
