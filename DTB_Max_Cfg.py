# Загрузка настроек MAX, отделённых от общей конфигурации DTB_Handler.

import json


class c_max_config:
    def __init__(self):
        # Файл содержит только параметры MAX API и Long Polling.
        with open("DTB_Max_Cfg.json", "r", encoding="UTF-8") as file:
            self.config = json.load(file)


# Общий объект настроек; каждый MAX-бот использует его значения,
# но создаёт собственную HTTP-сессию и собственное состояние опроса.
cfg = c_max_config()
