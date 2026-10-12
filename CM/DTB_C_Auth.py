# CM\DTB_C_Auth.py
import DTB_Kbrd
import CM.DTB_C_Start
import datetime

# отправляем сообщение о блокировке
def BlockHandler(_ch, _ms):
    _ch.send_message(
            "AuthorizationUserBlock",
            datetime.datetime.fromtimestamp(_ch.user.block_dt).strftime("%d.%m.%Y %H:%M"),
            ["Button.Authorization","Button.RecoveryAuthorization"]
        )

def AuthHandler(_ch, _ms):
    """
    Обработчик ко
    манды авторизации.
    Если пользователь уже авторизован — уведомляет об этом.
    Иначе переводит в режим ввода пароля.
    """
    if _ch.user.check_block():
        BlockHandler(_ch, _ms)
    else:
        _ch.step = "Authorization"
        _ch.send_message(
                "AuthorizationProcess",
                "",
                ["Button.RecoveryAuthorization"]
            )
        _ch.send_message(
                        "AuthorizationAttemtion",
                        str(_ch.user.get_block_at()),
                        None,
                        5
                    )
        if _ch.Opt_Auth == "INLINE":
            DTB_Kbrd.KeyboardInit(_ch, _ms)


def AuthorizationProcessHandler(_ch, _ms):
    """
    Обработчик ввода пароля пользователем.
    Проверяет соответствие пароля и выполняет переход в главное меню или выводит ошибку.
    """
    input_password = _ms.get("text", "")
        
    # Проверка пароля через функцию (лучше инкапсулировать логику проверки)
    if  _ch.user.check_password(input_password):
        _ch.step = ""
        _ch.auth = True
        _ch.send_message(
            "MainMenu",
            "",
            [["Button.MainMenu"], ["Button.GetNewToken"]]
        )
    else: 
        _at = _ch.user.block_at_user() 
        # проверяем остаток попыток ввода пароля
        if _at > 0:   
            _ch.send_message(
                            "AuthorizationAttemtion",
                            str(_at),
                            None,
                            5
                        )
            
            if _ch.Opt_Auth == "INLINE":
                    DTB_Kbrd.KeyboardInit(_ch, _ms)

            _ch.send_message(
                "AuthorizationError",
                "",
                None,
                -2
            )
        # остаток попыток = 0 
        else:
            _ch.user.block_user()
            _ms["comm"] = "Start"
            CM.DTB_C_Start.Start(_ch, _ms)