import datetime
import random

import DTB_DB
import DTB_Token
import DTB_User
import DTB_Kbrd

import CM.DTB_C_Start
import CM.DTB_C_Reg
import CM.DTB_C_Pass
import CM.DTB_C_Auth
import CM.DTB_C_Token
import CM.DTB_C_MainMenu


list_chat = {}

class c_chat:
    def __init__(self, _bot, _nm, _ch, _op):
        self.name       = _nm
        self.bot        = _bot
        self.id         = _ch
        self.gid        = _nm + str(_ch)
        self.comm       = ""
        self.Opt_Auth   = _op["Authentication"]
        self.Opt_Unif   = _op["UnifiedAccount"]
        self.user       = DTB_User.get_user(DTB_DB.DB.get_chat(self.name, self.id))
        self.last_time  = datetime.datetime.now()
        self.list_mess  = {}
        self.level      = 0
        self.step       = ""
        self.auth       = False
        self.kbrd       = None
        self.inpt       = ""
        self.pasw       = ""
        self.phone      = ""
        self.recovery   = ""
        self.token      = ""
        self.restart    = True
        self.current_token = None

        # заполняем из БД
        for ms in DTB_DB.DB.get_mess(self.gid):
            self.list_mess[ms[0]] = ms[1]

    def create_token(self):
        if self.current_token != None:
            self.current_token.close()
        
        self.current_token = DTB_Token.c_token(self)
            
        self.user.set_token(self.current_token)
            
    def set_user(   self,
                    _us
                ):
        self.user = _us
        DTB_DB.DB.set_chat_user(self.gid, _us.id)

    def clear_button(   self  
                    ):

        # для вcех сообщений
        for ms in self.list_mess:
            self.bot.clear_button(self.id, ms)

    def add_mess(   self,
                    _id,
                    _lv = None
                ):
        
        if _lv == None:
            _lv = self.level
            
        if _id in self.list_mess:
            _id = _id
        else:
            self.list_mess[_id] = _lv

        # добавляем в БД
        DTB_DB.DB.add_mess( self.gid,
                            _id,
                            _lv
                    )

    def send_wait(  self
                ):
    # отправка сообщения в бот 
        return self.bot.send_wait(
                                self.id
                            )

    def delete_message( self,
                        _ms = None,
                    ):
        # удаление сообщения из ТГ
        self.bot.delete_message  (  self.id,    # ид чата  
                                    _ms         # ид сообщения
                            )
        
        # удаляем сообщение из спиcка
        if _ms in self.list_mess: 
            self.list_mess.pop(_ms)
        
            # удаляем сообщение из БД
            DTB_DB.DB.del_mess( self.gid,    # ид чата  
                                _ms
                            )
      
    def edit_message(   self,
                        _id,
                        _key,
                        _ins = "",
                        _btn = None,
                        _lvl = 0
    ): 
          self.bot.edit_message(
                            self.id,
                            _id,
                            _key,
                            _ins,
                            _btn
                         )
               
    def send_message(   self,
                        _key,
                        _ins = "",
                        _btn = None,
                        _lvl = 0
    ): 
        #wt = self.send_wait()

        # устанавливам уровень (согласно вх.данным), получая его пред.значение 
        pl = self.set_level(_lvl)

        self.clear_mess()

        # если есть кнопкт
        if _btn != None:
            # учижаем все inline кнопки пред.сообщений
            self.clear_button()

        ms = self.bot.send_message(
                            self.id,
                            _key,
                            _ins,
                            _btn
                         )
        
        self.add_mess(ms)
        
        #self.delete_message(wt)        
        
        #возвращаем пред.уровень 
        if _lvl == -2 or _lvl >= 100 :
            # уcтанавливаем уровень
            self.set_level(
                        pl  # уровень 
                    )
        return ms
    
# удаление сообщений
    def clear_mess( self,
                    _lv = None,     # уровень cообщений
                    _isrev = False  # реверсировать
            ):
        # вход.уровень не утановлен
        if _lv == None:
            # берем тек.уровень и устанавливаем реверс
            lv = self.level
            isrev = True
        else:
            # берем из входящих 
            lv = _lv
            isrev = _isrev
        
        del_mess = []
        # для всех сообщений (берем с конца    
        for ms in reversed(self.list_mess):
            
            # получаем уровень сообщения
            kl = self.list_mess[ms]
            # (уровень сообщения > указанного и есть реверс) или уровень сообщения = указанного
            if  (kl > lv and isrev) or kl == lv :
                # удаляем сообщение из бота ТГ
                del_mess.append(ms)
        
        for ms in del_mess:
            self.delete_message(
                                    ms      # ид сообщения
                                )
                
    # установка уровня сообщений
    def set_level(  self,
                _lv     # новый уровень  
                        #   -1 - текущий
                        #   -2 - увеличение уровня +1
                        #   иное - установить указанный уровень
            ):
        # получаем текущий уровень
        pl = self.level
        
        # расчитываем новый уровень
        match _lv:
            # + 1
            case -2:
                self.level = self.level + 1
            # текущий 
            case -1:
                self.level = self.level
            # что пришло, то и ставим
            case _:
                self.level = _lv
        # возвращаем уровень до изменения        
        return pl
    
    def set_password(self):
        us = DTB_User.set_user(self.phone, self.recovery, self.pasw)
        if self.user == None:
            self.set_user(us)
            
        self.auth = True    

#########################################################################################################################################    
                
    def gate(self, _mess):

        comm = _mess["comm"]
        text = _mess["text"]

        self.last_time = datetime.datetime.now()

        if self.restart :
            sw = self.send_wait()

            if _mess["mess"] != None:
                self.delete_message(_mess["mess"])

            CM.DTB_C_Start.Start(self, _mess)
            self.restart = False
            
            if sw != None:
                self.delete_message(sw)
            
            return

        if len(comm) > 5:
            cm = comm[0:5]
        else: 
            cm = ""
        
        if cm != "KBRD.":
            sw = self.send_wait()

            if _mess["mess"] != None:
                self.delete_message(_mess["mess"])
                       
        else:
            if DTB_Kbrd.KeyboardHandler(self, _mess):
                return

            comm = "TEXT"
            text = self.inpt
                        
            _mess["comm"] = comm  
            _mess["text"] = text 
            sw = self.send_wait()
            self.delete_message(self.kbrd)
                          
        match comm:
            case "MenuDeleteUser":
                CM.DTB_C_MainMenu.MainDelUserHandler(self, _mess)
            case "MenuDeleteChat":
                CM.DTB_C_MainMenu.MainDelChatHandler(self, _mess)
            case "MenuDelUserYes":
                CM.DTB_C_MainMenu.MenuDelUserYesHandler(self, _mess)
            case "MenuDelChatYes":
                CM.DTB_C_MainMenu.MenuDelChatYesHandler(self, _mess)
            case "Start" | "CancelRegistration" | "MenuDelChatNo" | "CreateSimpleUserNo" | "MenuDelUserNo" | "MenuExit":
                CM.DTB_C_Start.Start(self, _mess)
            case "CreateSimpleUserYes":
                CM.DTB_C_Reg.CreateSimpleUserHandler(self, _mess)
            case "MenuAbout":
                CM.DTB_C_MainMenu.MainAboutHandler(self, _mess)
            case "MenuAuth":
                CM.DTB_C_MainMenu.MenuAuthHandler(self, _mess)
            case "MainMenu":
                CM.DTB_C_MainMenu.MainMenuHandler(self, _mess)
            case "RecoveryAuthorization":
                CM.DTB_C_Reg.RecoveryStartHandler(self, _mess)
            case "GetNewToken":
                CM.DTB_C_Token.NewTokenHandler(self, _mess)
            case "Authorization":
                CM.DTB_C_Auth.AuthHandler(self, _mess)       
            case "Contact":
                CM.DTB_C_Reg.ContactHandler(self, _mess)
            case "Registration":
                CM.DTB_C_Reg.Start(self, _mess)
            case "CancelCurrentOperation":
                CM.DTB_C_Start.Cancel(self, _mess)
            case "RecoveryBot":
                CM.DTB_C_Reg.RecoveryBotInput(self, _mess)            
            
            case "TEXT":
                if text == "/start":
                    CM.DTB_C_Start.Start(self, _mess)
                else:
                    match self.step:

                        case "Authorization":
                            CM.DTB_C_Auth.AuthorizationProcessHandler(self, _mess)
                        case "Password.First":
                            CM.DTB_C_Pass.PasswordFirstHandler(self, _mess)
                        case "Password.Second":
                            CM.DTB_C_Pass .PasswordSecondHandler(self, _mess)
                        case "Recovery.Bot":
                            CM.DTB_C_Reg.RecoveryBotHandler(self, _mess)
                        case "Recovery.Token":
                            CM.DTB_C_Reg.RecoveryBotTokenHandler(self, _mess)
                        case "Contact":
                            CM.DTB_C_Reg.ContactHandler(self, _mess)
                        case _:
                            self.send_message(
                                "None.Text",
                                text,         
                                _lvl = 1000
                            )

            case _:
                self.send_message(
                    "None.Type",
                    _lvl = 1000
                )       

        if sw != None:  
            self.delete_message(sw)        

