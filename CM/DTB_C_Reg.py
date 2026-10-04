import DTB_Res
import CM.DTB_C_Start
import DTB_User
import BOT.DTB_Bot
import CM.DTB_C_Pass
import CM.DTB_C_Auth
import DTB_Utils
import time


def Start(_ch, _ms):
    _ch.step = "Contact"
    
    _ch.send_message(
                "RegistrationHeader"
                )

    _ch.send_message(
                "RegistrationPhone",
                "",
                ["CONTACT"],
                5
            )
    
def ContactHandler(_ch, _ms):
    
    if _ms["phone"] != "":
        _ch.phone = _ms["phone"]
        if _ch.phone == "NONE":
            _ch.send_message(
                    "CreateSimpleUser",
                    "",
                    [
                        ["Button.CreateSimpleUserYes"],
                        ["Button.CreateSimpleUserNo"]
                    ],
                    5
                )
        else:
            us = DTB_User.get_user(_ch.phone)
            _ch.step = ""
            if us != None:
                _ch.set_user(us)
                CM.DTB_C_Auth.AuthHandler(_ch, _ms)
            else:
                RecoveryBotInput(_ch, _ms)            
    else:
        if _ms["text"] == DTB_Res.get_text("Button.CancelRegistration"):
            CM.DTB_C_Start.Start(_ch, _ms)
        else:
            _ch.send_message(
                    "None.Text",
                    _ms["text"],         
                    _lvl = 1000
                )

def RecoveryBotInput(_ch, _ms):
            _ch.step = "Recovery.Bot"
            _ch.send_message(
                        "Recovery.Bot",
                        "",
                        ["Button.CancelCurrentOperation"],
                        5
                    )

def RecoveryStartHandler(_ch, _ms):
    _ms["text"] = _ch.user.recovery
    
    _ch.send_message(
                "RecoveryHeader"
                )

#    _ch.send_message(
#                "RecoveryHeaderSendToken",
#                "",
#                None,
#                1
#            )
 
    RecoveryBotHandler(_ch, _ms)

def RecoveryBotHandler(_ch, _ms):
    _ch.recovery = _ms["text"]
    _ch.token    = DTB_Utils.get_token()
    BOT.DTB_Bot.recovery_bot.send_message(
                        _ch.recovery,
                        "RecoverySendToken",
                        _ch.phone
                    )
    BOT.DTB_Bot.recovery_bot.send_message(
                        _ch.recovery,
                        "",
                        _ch.token 
                    )
    
    _ch.step = "Recovery.Token"

    _ch.send_message(   "RecoveryToken",
                        "",
                        [
                            ["Button.CancelCurrentOperation"]
                        ],
                        5
                )
                      
    
def RecoveryBotTokenHandler(_ch, _ms):
    if _ch.token == _ms["text"]:
        CM.DTB_C_Pass.PasswordFirstInput(_ch, _ms)
    else:
        _ch.send_message("RecoveryTokenError",
                    "",
                    None,
                    -2
            )
            
def CreateSimpleUserHandler(_ch, _ms):
        _ms["phone"] = str(int(time.time())) 
        ContactHandler(_ch, _ms)
            
            
        