import CM.DTB_C_Reg
import DTB_Chat
import DTB_DB
import BOT.DTB_Bot
import DTB_Log
import DTB_User

def MenuDelChatYesHandler(_ch, _ms):
    _ch.clear_mess(-100, True)
    DTB_DB.DB.del_chat(_ch.gid)
    DTB_Chat.list_chat.pop(_ch.gid)
        
def MainAboutHandler(_ch, _ms):
    _ch.send_message(   
                        "MenuAbout",
                        _ch.user.id,
                        [["Button.MainMenu"], ["Button.GetNewToken"]]   
                    )

def MainDelChatHandler(_ch, _ms):
    _ch.send_message(   
                        "MenuDelChatQuestion",
                        "",
                        [["Button.Menu.DelChat.Yes"], ["Button.Menu.DelChat.No"]],
                    )
    
def MainDelUserHandler(_ch, _ms):
    _ch.send_message(   
                        "MenuDelUserQuestion",
                        "",
                        [["Button.Menu.DelUser.Yes"], ["Button.Menu.DelUser.No"]]
                    )    
def MainMenuHandler(_ch, _ms):
    _ch.send_message(   
                        "MainMenu",
                        "",
                        [
                            ["Button.Menu.Auth", "Button.Menu.About"],
                            ["Button.Menu.DeleteChat"],
                            ["Button.Menu.DeleteUser"],
                            ["Button.GetNewToken", "Button.Menu.Exit"]
                        ]
                       
                    )
    
def MenuAuthHandler(_ch, _ms):
    _ch.send_message(   
                        "ChangeAuthHeader",
                        ""
                    )
    _ch.send_message(   
                        "ChangeAuthHeaderWait",
                        "",
                        None,
                        1
                    )
    CM.DTB_C_Reg.RecoveryBotInput (_ch, _ms)

def MenuDelUserYesHandler(_ch, _ms):
   prev_ch = 0
   DTB_User.list_user.pop(_ch.user.id)
   lm = DTB_DB.DB.del_user(_ch.user.id)
   for ms in lm:
       nm = ms[0]
       id = ms[1]
       md = ms[2]
       gid = ms[3]
       if gid != prev_ch:
           prev_ch = gid
           if prev_ch in DTB_Chat.list_chat:
               DTB_Chat.list_chat.pop(prev_ch)
       try:
            bot = BOT.DTB_Bot.list_bot[nm]
            
            bot.delete_message(
                            id,   # ид чата  
                            md    # ид сообщения
                )
                
       except Exception as e:
           DTB_Log.log(e, "Ошибка on_clearmess_timer")
        