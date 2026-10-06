# класс и функции работы с конфикурацией

import json
from dotenv import load_dotenv

# класс, описывающий конфигурации бота 
class c_config: 

    def __init__(self):
        # конфигурация
        self.config = {}
        
        # грузим конфигурации из файла
        with open('DTB_Cfg.json', 'r', encoding="UTF-8") as file:
            self.config = json.load(file)

        # Загружаем переменные из .env в самом начале
        load_dotenv()

    # получение параметра конфигурации как строку  
    def gs  (   self, 
                _key    # ключ параметра
            ):              
        return str(                          # пребразование к строке                    
                    self.config[_key]        # получаем из словаря конфигурации параметр по ключу
        )
    # получение параметра конфигурации как целое число  
    def gi  (   self, 
                _key    # ключ параметра
            ):
        # запрашиваем парамет и преобразуем к целому
        return int(self.gs(_key))
        
# создаем объект конфигурации
cfg = c_config()