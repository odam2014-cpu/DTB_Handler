# CM\DTB_C_Auth.py

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


def AuthorizationProcessHandler(_ch, _ms):
    """
    Обработчик ввода пароля пользователем.
    Проверяет соответствие пароля и выполняет переход в главное меню или выводит ошибку.
    """
    input_password = _ms.get("text", "")
        
    # Защита от пустого ввода
    if not input_password:
        _ch.send_message("AuthorizationError", "", None, -2)
        return

    # Проверка пароля через функцию (лучше инкапсулировать логику проверки)
    if  _ch.user.check_password(input_password):
        _ch.step = ""
        _ch.send_message(
            "MainMenu",
            "",
            [["Button.MainMenu"], ["Button.GetNewToken"]]
        )
    else:
        _ch.send_message(
            "AuthorizationError",
            "",
            None,
            -2
        )

