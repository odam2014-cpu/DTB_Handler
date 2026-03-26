import datetime
import os

# Создаём путь к папке логов заранее
LOG_DIR = 'log'
os.makedirs(LOG_DIR, exist_ok=True)  # Упрощаем создание папки: exist_ok избавляет от проверки

def log(e, m="", f=""):
    """
    Записывает сообщение об ошибке/событии в лог-файл с датой и временем.
    :param e: Основное сообщение (например, ошибка)
    :param m: Дополнительное сообщение (опционально)
    """
    # Формируем имя файла лога по дате
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"{date_str}{f}.log")
    
    # Формируем временную метку
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Записываем в файл (режим 'a' подходит всегда — создаётся автоматически при открытии)
    with open(log_file, 'a', encoding='utf-8') as file:
        file.write(f"{timestamp}\n")
        file.write(f"{e}\n")
        if m:
            file.write(f"{m}\n")
        file.write("\n")  # Пустая строка для разделения записей

    # Выводим в консоль
    print(timestamp)
    print(e)
    if m:
        print(m)