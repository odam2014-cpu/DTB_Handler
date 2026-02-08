import DTB_Res
import CM.DTB_C_Start
import DTB_User
import BOT.DTB_Bot
import CM.DTB_C_Pass
import DTB_Utils


def Start(_ch, _ms):
    _ch.step = "Contact"
    
    _ch.send_message(
                "RegistrationHeader"
                )

    _ch.send_message(
                "RegistrationPhone",
                "",
                ["CONTACT"],
                1
            )
def ContactHandler(_ch, _ms):
    if _ms["phone"] != "":
        _ch.phone = _ms["phone"]
        us = DTB_User.get_user(_ch.phone)
        if us != None:
            _ch.step = ""
            _ch.set_user(us)
            _ch.send_message(
                        "SetUserToChat.Final",
                        "",
                        [["Button.MainMenu"],["Button.GetNewToken"]]
                    )
            
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
                        -1
                    )
            
def RecoveryBotHandler(_ch, _ms):
    _ch.recovery = _ms["text"]
    _ch.token    = DTB_Utils.get_token()
    BOT.DTB_Bot.recovery_bot.send_message(
                        _ms["text"],
                        "RecoverySendToken",
                        _ch.phone
                    )
    BOT.DTB_Bot.recovery_bot.send_message(
                        _ms["text"],
                        "",
                        _ch.token 
                    )
    
    _ch.step = "Recovery.Token"

    _ch.send_message(   "RecoveryToken",
                        "",
                        [["Button.RecoveryBot"], ["Button.CancelCurrentOperation"]],
                        -1
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
            