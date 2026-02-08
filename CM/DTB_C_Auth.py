def AuthHandler(_ch, _ms):
    if _ch.auth:
        _ch.send_message(
        "AlreadyAuthorized",
        "",
        None,
        -2
        )
    else:
        _ch.step = "Authorization"
        _ch.send_message(
                "AuthorizationProcess`",
                "",
                ["Button.CancelRegistration"]
            )

def AuthorizationProcessHandler(_ch, _ms):
    if)
