import threading
import sqlite3
import DTB_Log
import DTB_Cfg
import time

# класс, описывающий работу с SQLite 
class c_DB:
    def __init__(   self, 
                    _db_name    # имя базы
                ):
        # накладываем блокировку 
        with threading.Lock():
            # создаем коннект           
            self.conn = sqlite3.connect(    _db_name,                   # имя БД
                                            check_same_thread = False   # - можно в разных потоков
                                        )            
    # выполнение sql запроса    
    def exec(   self, 
                _sql_text   # текст sql запроса
            ):
        # накладываем блокировку 
        with threading.Lock():
            try:
                # получаем курсор    
                cur = self.conn.cursor()
                # выполняем запрос
                cur.execute(_sql_text)
                # получаем список данных
                lst = cur.fetchall()
                # закрываем курсор
                self.conn.commit()
            except Exception as e:   
                lst = []    
                DTB_Log.log(e, "EXEC " + _sql_text)          
                
        return lst    

    def get_chat(self, _nm, _ch):
        rs = self.exec(f"SELECT ID, USER_ID FROM CHAT WHERE ID = {_ch}")
        if len(rs) == 0:
            self.exec(f"INSERT INTO CHAT (ID, NAME) VALUES ({_ch}, '{_nm}')")
            return ""
        else:
            return rs[0][1]

    def get_mess(self, _ch):
        return self.exec(f"SELECT MESS_ID, LEVEL FROM MESSAGE WHERE CHAT_ID = {_ch}")
        
    def add_mess(self, _ch, _nm, _ms, _lv):
            self.exec(f"INSERT INTO MESSAGE (CHAT_ID, BOT_NM, MESS_ID, LEVEL) VALUES ({_ch}, '{_nm}', {_ms}, {_lv})")
        
    def del_mess(self, _ch, _ms):
            self.exec(f"DELETE FROM MESSAGE WHERE CHAT_ID = {_ch} AND MESS_ID = {_ms}")
        
    def delete_old_mess(self):
            tm = time.time()
            lm = self.exec(f"SELECT BOT_NM, CHAT_ID, MESS_ID, LEVEL FROM MESSAGE WHERE {tm} - LASTTIME > { DTB_Cfg.cfg.gs("ClearLifeTime")}")
            self.exec(f"DELETE FROM MESSAGE WHERE {tm} - LASTTIME > {DTB_Cfg.cfg.gs("ClearLifeTime")}")
            return lm
        
    def get_chat_ping(self):
            lm = self.exec(f"SELECT CH.ID, CH.NAME FROM CHAT AS CH WHERE NOT EXISTS(SELECT MS.MESS_ID FROM MESSAGE AS MS WHERE MS.CHAT_ID = CH.ID)")
            return lm  
    
    def set_chat_user(self, _ch, _uid):
            self.exec(f"UPDATE CHAT SET USER_ID = '{_uid}' WHERE ID = {_ch}")

    def del_chat(self, _ch):
            self.exec(f"DELETE FROM CHAT WHERE ID = {_ch}")

    def get_user(self, _id):
            lm = self.exec(f"SELECT ID, PASSWORD, RECOVERY FROM USER WHERE ID = '{_id}'")
            return lm

    def upd_user(self, _id, _rec, _pass):
        self.exec(f"UPDATE USER SET PASSWORD = '{_pass}', RECOVERY = '{_rec}' WHERE ID = '{_id}'")
        
    def add_user(self, _id):
        self.exec(f"INSERT INTO USER (ID) VALUES ('{_id}')")

DB = c_DB(DTB_Cfg.cfg.gs("DataBaseName"))