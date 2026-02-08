import BOT.DTB_Bot_Tlg
import BOT.DTB_Recovery

class c_BotTelegramRecovery(BOT.DTB_Bot_Tlg.c_BotTelegram):
    def __init__(self, _name, _token):
        super().__init__(_name, _token)  

    def gate(self, _nm, _cID, _mID, _comm, _text):
        _ms= {  "name"  : _nm,
                "bot"   : self,
                "chat"  : _cID,
                "mess"  : _mID,
                "comm"  : _comm,
                "text"  : _text            
            }
        BOT.DTB_Recovery.gate(_ms)
