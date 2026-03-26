import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import BOT.DTB_Bot
import BOT.DTB_Btn_Vk
import DTB_Log
import DTB_Res
import random
from bs4 import BeautifulSoup
class c_BotVk(BOT.DTB_Bot.c_Bot):
    def build_message(self, _key, _ins=""):
        txt = super().build_message(_key, _ins)
        
        soup = BeautifulSoup(txt, "html.parser")
        return soup.get_text()
    
    def __init__(self, _param):
        super().__init__(_param)  
          
        # регистрим бота
        self.vk_bot = vk_api.VkApi(api_version="5.199", token=self.token)
        self.vk = self.vk_bot.get_api()
        
        DTB_Log.log(f"Бот {self.name} подключен")
    
    def clear_button(   self,
                        _id,
                        _ms    
                   ):
        try:  
            t=0
        except Exception as e:  
            DTB_Log.log(e, "DEL_MES_BTN") 

    def start(self):
        
        res = self.vk.groups.getById()
        gr = res['groups'][0]['id']

        longpoll = VkBotLongPoll(self.vk_bot,
                                 group_id=gr)
        while True:
            try:
                for event in longpoll.listen():
                    match event.type:
                        case VkBotEventType.MESSAGE_NEW:
                            txt = event.message["text"] 
                            if txt == "Нвчать":
                                txt = "/Start"
                            self.gate(self.name, event.message["from_id"], None, "TEXT", txt)
                        case VkBotEventType.MESSAGE_EVENT:       
                            comm = event.object["payload"]["data"]
                            if comm == "SendContact":
                                usr = self.vk.users.get(fields = "about,contacts", user_ids = event.object["user_id"])           

                                self.gate(self.name, event.object["user_id"], None, "Contact", "", "NONE")
                                
                            else: 
                                self.gate(self.name, event.object["user_id"], None, comm, "")
                            
        #                case _:       
        #                    self.gate(self.name, event.object["user_id"], None, "OTHER", "")  
            except Exception as e:      
                DTB_Log.log(e, "LNGP", "_VK")
                                       
    def delete_message(  self,
                        _id,   # ид чата  
                        _ms    # ид сообщения
                    ):
        try:
            self.vk.messages.delete(delete_for_all=1, message_ids=_ms)
        except Exception as e:  
            DTB_Log.log(e, "VK_DEL_MES")

    def send_message(   self,
                        _id,                    # ид чата
                        _key,                   # ключ сообщения
                        _ins,                   # вставки в сообщение
                        _btn   = None           # кнопки
    ):
        txt = self.build_message(_key, _ins)
        btn = BOT.DTB_Btn_Vk.create(_btn)
        if btn == None:
            kb = None
        else:
            kb = btn.get_keyboard()
        #img = DTB_Res.get_image(_key)
        
        md = self.vk.messages.send( user_id=_id, message=txt, keyboard=kb, random_id=random.randint(0, 2048))
           
        return md

    def edit_message(   self,
                        _id,                    # ид чата
                        _ms,
                        _key,                   # ключ сообщения
                        _ins,                   # вставки в сообщение
                        _btn   = None           # кнопки
    ):
        txt = self.build_message(_key, _ins)
        btn = BOT.DTB_Btn_Vk.create(_btn)
        if btn == None:
            kb = None
        else:
            kb = btn.get_keyboard()
        #img = DTB_Res.get_image(_key)
        
        md = self.vk.messages.edit(message_id=_ms, peer_id=_id, message=txt, keyboard=kb, random_id=random.randint(0, 2048))
           
        return md


    def send_wait(self, _id):
        return self.send_message(
                                _id,
                                "",
                                "💤"   # эмоджи
                            )





