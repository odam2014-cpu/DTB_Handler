# CM\DTB_C_Auth.py
import DTB_Kbrd

def AuthHandler(_ch, _ms):
    """
    Обработчик команды авторизации.
    Если пользователь уже авторизован — уведомляет об этом.
    Иначе переводит в режим ввода пароля.
    """
    _ch.step = "Authorization"
    _ch.send_message(
            "AuthorizationProcess",
            "",
            ["Button.RecoveryAuthorization"]
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
        if _ch.Opt_Auth == "INLINE":
                DTB_Kbrd.KeyboardInit(_ch, _ms)

        _ch.send_message(
            "AuthorizationError",
            "",
            None,
            -2
        )

