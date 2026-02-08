import json

# определяем словарь строк сообщений/кнопок
dict_mess_text = {}
# определяем словарь команд
dict_command = {}

# перезагрузка ресурсов
def reload():
    # очищаем ресурсы
    dict_command.clear()
    dict_mess_text.clear()
    # загружаем ресурсы
    load()

# загружаем ресурсы
def load():
    # грузим ресурсы из файла
    with open('DTB_Res.json', 'r', encoding="UTF-8") as file:
        mess_list = json.load(file)

    # перебираем загруженные из файла ресурсы
    for mess in mess_list:

        # наличие параметра Command        
        if 'Command' in mess:
            # сохраняем команду в словарь команд под ключем из Text
            dict_command[mess['Text']] = mess['Command']
        # сохраняем спиок в словарь строк под ключем из Name
        dict_mess_text[mess["Name"]] =  [
                                            mess['Text'],           # текст
                                            mess.get('Image'),      # имя файла картинки
                                            mess.get('Command')     # команда для кнопки
                                        ] 
# получения текста строки по ключу
def get_text    (
                    _key,                                       # ключ строки
                    _txt = "Текст для <b>%%%</b> не найден"     # дополнительный текст
                ):
    try:
        # получение текста сроки по ключу 
        txt = dict_mess_text[_key][0]
    # если нет такой строки
    except Exception as e:
        # если доп.текст не пустой
        if _txt != "":
            # вставляем ключ в строку
            txt = _txt.replace("%%%", _key, 1)
        else:
            # просто ключ
            txt = _key
    return txt

# получение команды по ключу
def get_comm(_key):
    try:
        #получаем команду по ключу 
        txt = dict_mess_text[_key][2]
        # не получили
        if txt == None:
            #получаем команду-текс по ключу 
            txt = dict_mess_text[_key][0]
            # не получили
            if txt == None:
                # в качетве команды возвращаем ключ
                txt = _key
    # еcли ошибка
    except Exception as e:
        # в качетве команды возвращаем ключ
        txt = _key 
    return txt

# получение фото по ключу
def get_image(_key):
    try:
        # получение фото из спика
        _img = dict_mess_text[_key][1]
    except Exception as e:
        # если ошибка, значит фото нет
        _img = None
    return _img

# грузим ресурсы при загрузки 
load()