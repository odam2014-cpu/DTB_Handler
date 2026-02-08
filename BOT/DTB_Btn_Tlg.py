# реализуемся клавиатуру для сообщений
import telebot
from telebot import types
import DTB_Res 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton  

# создание клавиатуры        
def create( _bt     # список ключей конпок
           ):
    # добавление строку кнопок
    def add(    _lb     # клчей кнопок
            ):
        
        button_array = []
        
        # для всех ключейиз списка получаем ключ конпки        
        for bt in _lb:
            # добавляем inline кнопку в список кнопок 
            button_array.append(InlineKeyboardButton(   text=DTB_Res.get_text(bt, ""),       # получаем текст кнопки из ресурса
                                                        callback_data=DTB_Res.get_comm(bt)   # получаем команду кнопки из ресурса
                                                    ))
        # добавляем строку кнопок в клавиатуру
        markup.keyboard.append(button_array)
    
    markup = None
    
    # список кнопок есть
    if _bt != None:
        if _bt == ["CONTACT"]:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            # добавляем reply кнопку(словарь) в список кнопок 
            markup.keyboard.append([{  'text': DTB_Res.get_text("Button.SendContact"),   # получаем текст кнопки из ресурса 
                                       'request_contact': True                           # устнавливаем признак, что кнопка отправляет контакт
                                    }])
            markup.keyboard.append([
                                    {  'text': DTB_Res.get_text("Button.CancelRegistration")   # получаем текст кнопки из ресурса 
                                    }])
            
        else:
            # создаем inline клавиатуру
            markup = types.InlineKeyboardMarkup()

            for b1 in _bt:
                # если элемент списка - список ключей
                if type(b1) is list:
                    # добавляем строку клавиатуры, получаем флаг кнопки токена
                    add(b1)    
                else:
                    # если элемент не список, получаем флаг кнопки токена
                    add([b1])    
                
        return markup