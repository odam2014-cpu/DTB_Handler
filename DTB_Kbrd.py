Keyboard = [
                ["Button.KBRD.7", "Button.KBRD.8", "Button.KBRD.9"],
                ["Button.KBRD.4", "Button.KBRD.5", "Button.KBRD.6"],
                ["Button.KBRD.3", "Button.KBRD.2", "Button.KBRD.1"],
                ["Button.KBRD.0", "Button.KBRD.Cancel"],
                ["Button.RecoveryAuthorization"],
                ["Button.CancelCurrentOperation"]

            ]

def KeyboardInit(_ch, _ms):
        _ch.inpt = ""
        _ch.kbrd = _ch.send_message(
                    "KeyboardInline",
                    " _ _ _ _",
                    Keyboard,
                    10    
                )
        
def KeyboardHandler(_ch, _ms):
    btn = _ms["comm"].split(".")[1]
    match btn:
        case "Cancel":
            _ch.inpt = ""
        case _:
            _ch.inpt = _ch.inpt + btn
    
    tx = " *" * len(_ch.inpt) + " _" * (4 - len(_ch.inpt))
    _ch.edit_message(
                _ch.kbrd,
                "KeyboardInline",
                tx,
                Keyboard    
            )

    return len(_ch.inpt) != 4