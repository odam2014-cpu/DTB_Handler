# реализуемся клавиатуру для сообщений
import DTB_Res 

# создание клавиатуры        
def create( _bt     # список ключей конпок
           ):
    # добавление строку кнопок
    def add(    _lb     # клчей кнопок
            ):
        
        button_array = []
        
        # для всех ключей из списка получаем ключ конпки        
        for bt in _lb:
            # добавляем inline кнопку в список кнопок 
            
            button_array.append({
                                    "type"      : "callback",
                                    "text"      : DTB_Res.get_text(bt),
                                    "payload"   : DTB_Res.get_comm(bt)
                                    })
        # добавляем строку кнопок в клавиатуру
        markup[0]["payload"]["buttons"].append(button_array)
    
    markup = None
    
    # список кнопок есть
    if _bt != None:
        if _bt == ["CONTACT"]:
            markup = [
                        {
                            "type": "inline_keyboard",
                            "payload": {
                                "buttons": [
                                                [
                                                    {
                                                    "type"      : "request_contact",
                                                    "text"      : DTB_Res.get_text("Button.SendContact")
                                                    }
                                                ],
                                                [
                                                    {
                                                    "type"      : "callback",
                                                    "text"      : DTB_Res.get_text("Button.CancelRegistration"),
                                                    "payload"   : DTB_Res.get_comm("Button.CancelRegistration")
                                                    }
                                                ]
                                                
                                            ]
                            }
                        }
                    ]
        else:
            markup = [
                        {
                            "type": "inline_keyboard",
                            "payload": {
                                "buttons": []
                                
                            }
                        }
                    ]
            
            # создаем inline клавиатуру
            for b1 in _bt:
                # если элемент списка - список ключей
                if type(b1) is list:
                    add(b1)    
                else:
                    add([b1])    
                
        return markup