import CM.DTB_C_Auth

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

def Start(_ch, _ms):
    _ch.step = ""
    if _ch.user == None:
        _ch.send_message(
            "RequiredRegistration",
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
