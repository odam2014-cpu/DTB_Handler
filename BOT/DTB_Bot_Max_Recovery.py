import BOT.DTB_Bot_Max
import BOT.DTB_Recovery

class c_BotMaxRecovery(BOT.DTB_Bot_Max.c_BotMax):
    def __init__(self, _param):
        super().__init__(_param)  

    def gate(self, _nm, _cID, _mID, _comm, _text):
        _ms= {  "name"  : _nm,
                "bot"   : self,
                "chat"  : _cID,
                "mess"  : _mID,
                "comm"  : _comm,
                "text"  : _text            
            }
        BOT.DTB_Recovery.gate(_ms)
