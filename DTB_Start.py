import threading
import DTB_Cfg
import BOT.DTB_Bot
import BOT.DTB_Bot_Tlg_Chat
import BOT.DTB_Bot_Tlg_Recovery

# стартуем
def start(_bt):
    match _bt["Type"]:
        case "Telegram":
            bot = BOT.DTB_Bot_Tlg_Chat.c_BotTelegramChat(_bt["Name"], _bt["Token"])
            BOT.DTB_Bot.list_bot[_bt["Name"]] = bot
            bot.start()
        case "Recovery":
            bot = BOT.DTB_Bot_Tlg_Recovery.c_BotTelegramRecovery(_bt["Name"], _bt["Token"])
            BOT.DTB_Bot.recovery_bot = bot
            bot.start()
                
for bt in DTB_Cfg.cfg.config["BotList"]:
    # создаем поток""
    thread_server = threading.Thread(
                target=start,   # функция, которая будет выполнться в потоке
                args=(bt,))      # args передаются как кортеж
    # стартуем
    thread_server.start()
   


