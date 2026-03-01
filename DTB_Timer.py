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
        gid = ms1[2]
        try:
            bot = BOT.DTB_Bot.list_bot[nm]
            ms= bot.send_message(
                    id,                   # ид чата
                    "Start.Main",         # ключ сообщения
                    "",                   # вставки в сообщение
                    ["Button.Start"]      # кнопки
                )
            DTB_DB.DB.add_mess(gid, ms, 0)
        except Exception as e:
            DTB_Log.log(e, f"Ошибка on_clearmess_timer/ Start.Main : {gid}") 
            DTB_DB.DB.del_chat(gid)
            
    for ms2 in list_ms:
        nm = ms2[0]
        id = ms2[1]
        md = ms2[2]
        try:
            bot = BOT.DTB_Bot.list_bot[nm]
            
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
            # все очищаем
            sw = ch.send_wait()
            ch.clear_mess(-100, True)
            # отправляем сообщение, что соединение разорвано
            if ch.user == None:   
                    ch.send_message(    "Message.Timeout",
                                        "",
                                        ["Button.Registration"]
                                    )
            else:        
                    ch.send_message(    "Message.Timeout",
                                        "",
                                        ["Button.Authorization"]
                                    )
            ch.delete_message(sw)
            lc.append(id)
            
    for id in lc:
        # удаляем чат из списков        
        try:
            DTB_Chat.list_chat.pop(id)
        except:
            r=0    

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
