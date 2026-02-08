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
            if _ch.comm == "Start":
                _ch.comm = "Authorization"
                _ms["comm"] = "Authorization"
            # сюда вызов гейта авторизации 
            else:     
                _ch.send_message(
                    "RequiredAuthorization",
                    "",
                    ["Button.Authorization"]
                )
