import threading
import DTB_Cfg
import BOT.DTB_Bot
import BOT.DTB_Bot_Tlg_Chat
import BOT.DTB_Bot_Tlg_Recovery
import BOT.DTB_Bot_Vk
import BOT.DTB_Bot_Max_Chat
import BOT.DTB_Bot_Max_Recovery
import DTB_Api

# стартуем
def start(_bt):
    match _bt["Type"]:
        case "TLG":
            bot = BOT.DTB_Bot_Tlg_Chat.c_BotTelegramChat(_bt)
            BOT.DTB_Bot.list_bot[_bt["Name"]] = bot
            bot.start()
        case "MAX":
            bot = BOT.DTB_Bot_Max_Chat.c_BotMaxChat(_bt)
            BOT.DTB_Bot.list_bot[_bt["Name"]] = bot
            bot.start()
        case "VK":
            bot = BOT.DTB_Bot_Vk.c_BotVk(_bt)
            BOT.DTB_Bot.list_bot[_bt["Name"]] = bot
            bot.start()
        case "TLG_Recovery":
            bot = BOT.DTB_Bot_Tlg_Recovery.c_BotTelegramRecovery(_bt)
            BOT.DTB_Bot.recovery_bot = bot
            bot.start()
        case "MAX_Recovery":
            bot = BOT.DTB_Bot_Max_Recovery.c_BotMaxRecovery(_bt)
            BOT.DTB_Bot.recovery_bot = bot
            bot.start()
        
for bt in DTB_Cfg.cfg.config["BotList"]:
    # создаем поток""
    thread_server = threading.Thread(
                target=start,   # функция, которая будет выполнться в потоке
                args=(bt,))      # args передаются как кортеж
    # стартуем
    thread_server.start()

DTB_Api.run()   


