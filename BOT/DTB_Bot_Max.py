import requests
import json
import vobject
import BOT.DTB_Bot
import DTB_Log
import DTB_Res
import BOT.DTB_Btn_Max

class c_BotApiMax(BOT.DTB_Bot.c_Bot):
    def __init__(self, _token):
        self.header      = {'Authorization': _token}
        self.base_url    = "https://platform-api.max.ru/"
        
        self.GET_url = self.base_url + "updates"
        self.GET_params = {
                            "timeout"   : "10", 
                            "types"     : "bot_started,message_created,message_callback"
                        }
        self.MES_url = self.base_url + "messages"
        
        
    def GetUpdates(self):
        req = requests.get(url = self.GET_url, params=self.GET_params, headers=self.header)
        upd = json.loads(req.text)  
        self.GET_params["marker"] = upd["marker"]
        return upd
        
    def DeleteMessage(self, _id, _ms):
        params = {
            "message_id": _ms
        }
        req = requests.delete(url = self.MES_url, params=params, headers=self.header)
        return json.loads(req.text)
        
        
    def SendBody(self, _id, _body):
        params = {
                    "user_id"               : _id,
                    "disable_link_preview"  : "False"
                }
        req = requests.post(url = self.MES_url, params=params, headers=self.header, json=_body)
        return req
    
    def SendMessage(self, _id, _txt, _parse_mode="html", _reply_markup=None):        
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
    def __init__(self, _param):
        super().__init__(_param)  
        
        self.Bot  = c_BotApiMax(self.token)    # регистрим бота
        DTB_Log.log(f"Бот {self.name} подключен")
    
    def clear_button(   self,
                        _id,
                        _ms    
                   ):
        try:  
            self.Bot.EditMessage (_ms=_ms, _reply_markup=[])   
        except Exception as e:  
            DTB_Log.log(e, "DEL_MES_BTN") 


    def start(self):
        while True:
            upd = None
            try:
                upd = self.Bot.GetUpdates()
            except Exception as e:  
                t=0
            if upd != None:
                try:
                    for up in upd["updates"]:
                        match up["update_type"]:
                            case "bot_started":
                                self.gate(  self.name, 
                                            up["user"]["user_id"], 
                                            None, 
                                            "Start", 
                                            "")

                            case "message_created":
                                typ = "TEXT"
                                pho = ""
                                if "attachments" in up["message"]["body"]:
                                    if up["message"]["body"]["attachments"][0]["type"] == "contact":
                                        typ = "Contact"
                                        vcf = up["message"]["body"]["attachments"][0]["payload"]["vcf_info"]
                                        vobj = vobject.readOne(stream=vcf, allowQP=True)
                                        pho = vobj.tel.value
                                DTB_Log.log(up, "txt", "_max")
                                self.gate(  self.name, 
                                            up["message"]["sender"]["user_id"], 
                                            up["message"]["body"]["mid"], 
                                            typ,
                                            up["message"]["body"]["text"], 
                                            pho)

                            case "message_callback":
                                DTB_Log.log(up, "clb", "_max")
                                self.gate(  self.name, 
                                            up["callback"]["user"]["user_id"], 
                                            None, 
                                            up["callback"]["payload"], 
                                            "")
                except:
                    t=0     

    def delete_message(  self,
                        _id,   # ид чата  
                        _ms    # ид сообщения
                    ):
        try:
            self.Bot.DeleteMessage(_id, _ms)
            DTB_Log.log(_ms, "del", "_max")

        except Exception as e:  
            DTB_Log.log(e, "MAX_DEL_MES")

    def edit_message(   self,
                        _ms,
                        _id,                    # ид чата
                        _key,                   # ключ сообщения
                        _ins,                   # вставки в сообщение
                        _btn   = None           # кнопки
    ):
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

    def send_message(   self,
                        _id,                    # ид чата
                        _key,                   # ключ сообщения
                        _ins,                   # вставки в сообщение
                        _btn   = None           # кнопки
    ):
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

       
#🔥⚡️🎉
