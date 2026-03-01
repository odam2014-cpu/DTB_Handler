# реализуемся клавиатуру для сообщений
import DTB_Res 
import random
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# создание клавиатуры        
def create( _bt     # список ключей конпок
           ):
    # добавление строку кнопок
    def add(    _lb     # клчей кнопок
            ):
           
        # для всех ключей из списка получаем ключ конпки        
        for bt in _lb:
            # добавляем inline кнопку в список кнопок 
            markup.add_callback_button(DTB_Res.get_text(bt, ""), color=VkKeyboardColor.PRIMARY, payload={"data": DTB_Res.get_comm(bt)})
        
        markup.add_line()
    
    markup = None
    
    # список кнопок есть
    if _bt != None:
        # создаем inline клавиатуру
        markup  = VkKeyboard(inline=True)

        for b1 in _bt:
            # если элемент списка - список ключей
            if type(b1) is list:
                # добавляем строку клавиатуры, получаем флаг кнопки токена
                add(b1)    
            else:
                # если элемент не список, получаем флаг кнопки токена
                add([b1])    

        return markup