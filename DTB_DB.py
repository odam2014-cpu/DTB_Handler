import threading
import sqlite3
import DTB_Log
import DTB_Cfg
import time

# класс, описывающий работу с SQLite
# используем параметрические запросы 
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
                _sql_text,   # текст sql запроса
                _params=None # параметры для параметрического запроса
            ):
        # накладываем блокировку 
        with threading.Lock():
            try:
                # получаем курсор    
                cur = self.conn.cursor()
                # выполняем запрос
                if _params:
                    cur.execute(_sql_text, _params)
                else:
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
        rs = self.exec("SELECT ID, USER_ID FROM CHAT WHERE ID = ? AND NAME = ?", (_ch, _nm))
        if len(rs) == 0:
            self.exec("INSERT INTO CHAT (ID, NAME) VALUES (?, ?)", (_ch, _nm))
            return ""
        else:
            return rs[0][1]

    def get_mess(self, _ch):
        return self.exec("SELECT MESS_ID, LEVEL FROM MESSAGE WHERE CHAT_ID = ?", (_ch,))
        
    def add_mess(self, _ch, _ms, _lv):
            self.exec("INSERT INTO MESSAGE (CHAT_ID, MESS_ID, LEVEL) VALUES (?, ?, ?)", (_ch, _ms, _lv))
        
    def del_mess(self, _ch, _ms):
            self.exec("DELETE FROM MESSAGE WHERE CHAT_ID = ? AND MESS_ID = ?", (_ch, _ms))
        
    def delete_old_mess(self):
            tm = time.time()
            lifetime = DTB_Cfg.cfg.gs("ClearLifeTime")
            lm = self.exec(
                "SELECT CH.NAME, CH.ID, MS.MESS_ID, CH.GID FROM MESSAGE AS MS "
                "INNER JOIN CHAT AS CH ON CH.GID = MS.CHAT_ID "
                "WHERE ? - LASTTIME > ?",
                (tm, lifetime)
            )
            self.exec(
                "DELETE FROM MESSAGE WHERE ? - LASTTIME > ?",
                (tm, lifetime)
            )
            return lm
        
    def get_chat_ping(self):
            lm = self.exec(
                "SELECT CH.ID, CH.NAME, CH.GID FROM CHAT AS CH "
                "WHERE NOT EXISTS(SELECT MS.MESS_ID FROM MESSAGE AS MS WHERE MS.CHAT_ID = CH.GID)"
            )
            return lm  

    def set_chat_user(self, _ch, _uid):
            self.exec("UPDATE CHAT SET USER_ID = ? WHERE GID = ?", (_uid, _ch))

    def del_chat(self, _ch):
            self.exec("DELETE FROM CHAT WHERE GID = ?", (_ch,))

    def get_user(self, _id):
            lm = self.exec(
                "SELECT ID, PASSWORD, RECOVERY, BLOCK_DT, BLOCK_CN, BLOCK_AT FROM USER WHERE ID = ?",
                (_id,)
            )
            return lm

    def unblock_user(self, _id):
        self.exec("UPDATE USER SET BLOCK_DT = 0, BLOCK_CN = 0, BLOCK_AT = 0 WHERE ID = ?", (_id,))

    def block_at_user(self, _id):
        self.exec("UPDATE USER SET BLOCK_AT = BLOCK_AT + 1 WHERE ID = ?", (_id,))

    def block_user(self, _id, _dt):
        self.exec(
            "UPDATE USER SET BLOCK_DT = ?, BLOCK_CN = BLOCK_CN + 1, BLOCK_AT = 0 WHERE ID = ?",
            (_dt, _id)
        )

    def upd_user(self, _id, _rec, _pass):
        self.exec(
            "UPDATE USER SET PASSWORD = ?, RECOVERY = ?, BLOCK_DT = 0, BLOCK_CN = 0, BLOCK_AT = 0 WHERE ID = ?",
            (_pass, _rec, _id)
        )
        
    def add_user(self, _id):
        self.exec("INSERT INTO USER (ID) VALUES (?)", (_id,))

    def del_user(self, _id):
            lm = self.exec(
                "SELECT CH.NAME, CH.ID, MS.MESS_ID, CH.GID FROM CHAT AS CH "
                "INNER JOIN MESSAGE AS MS ON MS.CHAT_ID = CH.GID "
                "WHERE CH.USER_ID = ? ORDER BY MS.CHAT_ID",
                (_id,)
            )
            self.exec("DELETE FROM MESSAGE WHERE CHAT_ID IN (SELECT GID FROM CHAT WHERE USER_ID = ?)", (_id,))
            self.exec("DELETE FROM CHAT WHERE USER_ID = ?", (_id,))
            self.exec("DELETE FROM USER WHERE ID = ?", (_id,))
            return lm
    

DB = c_DB(DTB_Cfg.cfg.gs("DataBaseName"))