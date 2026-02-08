def PasswordFirstInput(_ch, _ms):
    _ch.step = "Password.First"
    _ch.send_message(   "PasswordFirst",
                        "",
                        ["Button.CancelCurrentOperation"],
                        -1
                )

def PasswordFirstHandler(_ch, _ms):
    ps = _ms["text"]
    if len(ps) < 4:
        _ch.send_message(   "PasswordFirstError",
                            "",
                            None,
                            -2
                    )
    else:
        _ch.pasw = ps
        _ch.step = "Password.Second"
        _ch.send_message(   "PasswordSecond",
                            "",
                            ["Button.CancelCurrentOperation"],
                            -1
                    )
    
def PasswordSecondHandler(_ch, _ms):
    ps = _ms["text"]
    if _ch.pasw != ps:
        _ch.send_message(   "PasswordSecondtError",
                            "",
                            None,
                            -2
                    )
    else:
        _ch.set_password()
        _ch.step = ""
        _ch.send_message(   "MainMenu",
                            "",
                            [["Button.MainMenu"],["Button.GetNewToken"]],
                    )
        
