import CM.DTB_C_Auth
import datetime

def Cancel(_ch, _ms):
    _ch.step = ""
    if _ch.auth:
        _ch.send_message(
                "OperationCancel",
                "",
                [["Button.MainMenu"],["Button.GetNewToken"]]                        
            )
    else:
        Start(_ch, _ms)

def Start(_ch, _ms, _keyReg = "RequiredRegistration"):
    _ch.step = ""

    if _ch.user == None:
        _ch.send_message(
            _keyReg,
            "",
            ["Button.Registration"]
        )
    else:
        if _ch.auth:
            _ch.send_message(
                    "MainMessage",
                    "",
                    [["Button.MainMenu"],["Button.GetNewToken"]]                        
                )
        else:
            #проверям если не блокировка истекла
            if _ch.user.check_block(): 
                CM.DTB_C_Auth.BlockHandler(_ch, _ms)
            else:
                if _ms["comm"] == "Start" or _ms["comm"] == "Authorization":
                    _ms["comm"] = "Authorization"
                    CM.DTB_C_Auth.AuthHandler(_ch, _ms)
                # сюда вызов гейта авторизации 
                else:    
                    _ch.send_message(
                        "RequiredAuthorization",
                        "",
                        ["Button.Authorization"]
                    )
