import threading
import DTB_Cfg
import datetime
import DTB_DB
import BOT.DTB_Bot
import DTB_Log
import DTB_Chat

def on_clearmess_timer():
    list_ms = DTB_DB.DB.delete_old_mess() 
    
    for ms1 in DTB_DB.DB.get_chat_ping():
        id = ms1[0]
        nm = ms1[1]
        try:
            bot = BOT.DTB_Bot.list_bot[nm]
            ms= bot.send_message(
                    id,                   # ид чата
                    "Start.Main",         # ключ сообщения
                    "",                   # вставки в сообщение
                    ["Button.Start"]      # кнопки
                )
            BOT.DTB_DB.DB.add_mess(id, nm, ms, 0)
        except Exception as e:
            DTB_Log.log(e, f"Ошибка on_clearmess_timer/ Start.Main : {id}") 
            DTB_DB.DB.del_chat(id)
            
    for ms2 in list_ms:
        nm = ms2[0]
        id = ms2[1]
        md = ms2[2]
        try:
            bot = DTB_Bot.list_bot[nm]
            
            bot.delete_message(
                            id,   # ид чата  
                            md    # ид сообщения
                )
                
        except Exception as e:
            DTB_Log.log(e, "Ошибка on_clearmess_timer")
        
    # cоздаем и запускаем таймер
    clear_timer = threading.Timer(DTB_Cfg.cfg.gi("ClearLifeTimeInterval"), on_clearmess_timer)
    clear_timer.start()        


# обработчик проверки бездействия чатов        
def on_clear_timer():
    
    lc = []
    # перебираем все чаты
    for id in DTB_Chat.list_chat:
        ch = DTB_Chat.list_chat[id]
        # рассчитываем разницу между текужим временем и временем последней активности
        dt = datetime.datetime.now() - ch.last_time
        
        # проверям, что интервал привышает установленный в конфигурации
        if dt.total_seconds() > DTB_Cfg.cfg.gi("ChatLifeTime"):
            # устанавливаем уровень сообщения 0
            ch.level = 0
        
            # отправляем сообщение, что соединение разорвано
            if ch.user == 0:   
                    ch.send_message(    "Message.Timeout",
                                        "",
                                        ["Button.Registration"],
                                        -100
                                    )
            else:        
                    ch.send_message(    "Message.Timeout",
                                    "",
                                    ["Button.Authorization"],
                                    -100
                                )
            lc.append(id)
            
    for id in lc:
        # удаляем чат из списков
        DTB_Chat.list_chat.pop(id)      
        lc.append(id)
        
    for id in lc:
        # удаляем чат из списков        
        DTB_Chat.list_chat.pop(id)    

    # создаем и запускаем таймер
    clear_timer = threading.Timer(DTB_Cfg.cfg.gi("ChatLifeTimeInterval"), on_clear_timer)
    clear_timer.start()        


# создаем таймер по очистки сообщений    
clearmess_timer = threading.Timer( DTB_Cfg.cfg.gi("ClearLifeTimeInterval"),  # интервал берем из конфигурации
                                    on_clearmess_timer                         # функция обработки таймера
                                )
# стартуем таймер
clearmess_timer.start()   


# создаем таймер по отлеживанию простоя чатов    
clear_timer = threading.Timer( DTB_Cfg.cfg.gi("ChatLifeTimeInterval"),  # интервал берем из конфигурации
                                    on_clear_timer                         # функция обработки таймера
                                )
# стартуем таймер
clear_timer.start()   
