import DTB_Cfg
import DTB_Utils
import threading

class c_token:
    def __init__(self, _ch):

        self.ch = _ch
        self.token = DTB_Utils.get_token()
        self.enable = True
                
        # выдаем сообщение
        self.ch.send_message("Token.Get", "", None, -100)
        # выдаем новый токен
        self.ch.send_message("",  f"<tg-spoiler><b>{self.token}</b></tg-spoiler>", [["Button.MainMenu"],["Button.GetNewToken"]], -99)
        
        self.lock = threading.Lock()    # создаем блокировку
        self.timer = threading.Timer(   # оздаем таймер жизни токена
                                        DTB_Cfg.cfg.gi("TokenLifeTime"),  # указываем время жизни из конфига
                                        self.on_timer                       # указываем функцию обработки выполнеения таймера
                                    )
        self.timer.start()              # запускаем таймер
        
    def close(self):
        self.lock.acquire()
        if self.enable:
            self.timer.cancel()
            self.enable = False
            self.ch.send_message(   "Token.IsDeactive",          # ключ сообщения
                                    self.token,                  # доп.текст - бывший токен
                                    [["Button.MainMenu"],["Button.GetNewToken"]],
                                    -100
                            )

        self.lock.release()
        
    def check(self, _tk = None):
        ret = False
        self.lock.acquire()                         # блокируем доступ к токену
        if self.enable:
            if _tk != None:
                if self.token == _tk:
                    self.enable = False
                    self.timer.cancel()             # останавливаем таймер
                    ret = True
            else:
                ret = True
                self.enable = False
                    
        self.lock.release()                         # разблокируем токен
        return ret
     
    def on_timer(self):
        # деактивируем токен
        if self.check():
            self.ch.send_message(   "Token.IsDisabled",          # ключ сообщения
                                    self.token,                  # доп.текст - бывший токен
                                    [["Button.MainMenu"],["Button.GetNewToken"]],
                                    -100
                            )

