import DTB_DB

list_user = {}
class c_User:
    def __init__(self, _id):
        lm = DTB_DB.DB.get_user(_id)
        self.id         = _id
        if len(lm) > 0:
            self.password   = lm[0][1]
            self.recovery   = lm[0][2] 
        else:    
            DTB_DB.DB.add_user(_id)
            self.password   = ""
            self.recovery   = "" 
        
    def set_user(self, _recovery, _password):
        if _recovery != "":
            self.recovery = _recovery
        self.password = _password
        DTB_DB.DB.upd_user(self.id, self.recovery, self.password)    
        
def get_user(_id):
    us = None
    try:
        us = list_user[_id]
    except:
        lm = DTB_DB.DB.get_user(_id)
        if len(lm) > 0:
            us = c_User(id)
            list_user[id] = us
    return us

def set_user(_id, _recovery, _password):
    us = get_user(_id)
    if us == None:
        us = c_User(_id)
    us.set_user(_recovery, _password)
    return us