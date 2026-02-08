# получение ссылки на бот
import DTB_Res
import DTB_Chat

recovery_bot = None
list_bot = {}

class c_Bot: 
    def gate(self, _nm, _cID, _mID, _comm, _text, _ph=""):
        _ms= {  "name"  : _nm,
                "bot"   : self,
                "chat"  : _cID,
                "mess"  : _mID,
                "comm"  : _comm,
                "text"  : _text,
                "phone" : _ph           
            }
        DTB_Chat.gate(_ms)
        
    def build_message(  self,
                        _key,                   # ключ сообщения
                        _ins    = "",           # вставки в сообщение
                      
    ):
        # ключ не пустой
        if _key != "":
        # полчаем текст сообщения по ключу 
            txt = DTB_Res.get_text(_key) 
            # ищем вхождение подстроки
            # не нашел
            if txt.find("%%%") == -1: 
                # добавляем в конец
                txt = txt + "%%%" 
        else:
            # устанавливаем текст
            txt = "%%%"
        
        # еcли доп.текст это список    
        if type(_ins) is list:
            # делаем замену для каждого элемента доп.списка
            for tx in _ins:
                txt = txt.replace("%%%", tx, 1)   
        else:
            # делаем замену для доп.списка
            txt = txt.replace("%%%", _ins)
        return txt
