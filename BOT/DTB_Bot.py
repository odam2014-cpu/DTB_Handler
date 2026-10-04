# получение ссылки на бот
import DTB_Res
import DTB_Chat

recovery_bot = None
list_bot = {}

class c_Bot: 
    def __init__(self, _param):
        self.name   = _param["Name"]
        self.token  = _param["Token"]
        self.options= _param["Options"]
                
    def gate(self, _nm, _cID, _mID, _comm, _text, _ph=""):

        txt = ""
        if _text != None:
            txt = _text.strip()
        _ms= {  "name"  : _nm,
                "chat"  : _cID,
                "mess"  : _mID,
                "comm"  : _comm,
                "text"  : txt,
                "phone" : _ph           
            }

        DTB_Chat.chat_gate(self, _ms)

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
