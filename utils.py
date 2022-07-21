import shelve
from mssqlworker import mssqlworker
from config import SHELVE_NAME, CONNECTION_STRING
from telebot import types

def groups(db):
    """
    Данный метод считает проекты в базе данных и сохраняет в хранилище.
    """
    all_groups = db.select_all_groups()
    with shelve.open(SHELVE_NAME) as storage:
        storage['all_groups'] = all_groups

def grouprows(db):
    """
    Данный метод считает детализацию (пункты меню) для проектов в базе данных и сохраняет в хранилище.
    """
    all_grouprows = db.select_all_grouprows()
    with shelve.open(SHELVE_NAME) as storage:
        storage['all_grouprows'] = all_grouprows

def users(db):
    """
    Данный метод считает пользователей в базе данных и сохраняет в хранилище.
    """
    all_users = db.select_all_users()
    with shelve.open(SHELVE_NAME) as storage:
        storage['all_users'] = all_users

def init_data_from_db():
    """
    Данный метод запускает все процедуры считывания данных из базы.
    """
    _db = mssqlworker(CONNECTION_STRING)
    groups(_db)
    grouprows(_db)
    users(_db)
    _db.close()

def get_groups():
    """
    Получает из хранилища группы
    """
    with shelve.open(SHELVE_NAME) as storage:
        all_groups = storage['all_groups']
    return all_groups

def get_group_bycodename(codename):
    """
    Получает из хранилища группу по заданному кодовому имени(вызов)
    """
    result = None
    with shelve.open(SHELVE_NAME) as storage:
        all_groups = storage['all_groups']
        for group in all_groups:
            if group[3] == codename:
                result = group
    return result

def get_grouprows(group_id):
    """
    Получает из хранилища подпункты для проекта
    :param chat_id: id чата юзера
    """
    with shelve.open(SHELVE_NAME) as storage:
        all_grouprows = storage['all_grouprows']
        grouprows = list()
        for grouprow in all_grouprows:
            if grouprow[1] == group_id:
                grouprows.append(grouprow)
    return grouprows

def get_grouprow_bycodename(codename):
    """
    Получает из хранилища группу по заданному кодовому имени(вызов)
    """
    result = None
    with shelve.open(SHELVE_NAME) as storage:
        splitted_codename = codename.split("_")
        group = get_group_bycodename(splitted_codename[0])
        all_grouprows = get_grouprows(group[0])
        for grouprow in all_grouprows:
            if grouprow[3] == splitted_codename[1]:
                result = grouprow
    return result

def get_users():
    """
    Получает из хранилища пользователей
    """
    with shelve.open(SHELVE_NAME) as storage:
        all_users = storage['all_users']
    return all_users

def set_user_status(chat_id, user_status):
    """
    Записываем юзера в список и запоминаем его текущий статус.
    :param chat_id: id чата юзера
    :param user_status: статус юзера
    """
    with shelve.open(SHELVE_NAME) as storage:
        storage[str(chat_id)+"_user_status"] = user_status

def set_user_role(chat_id, user_role):
    """
    Записываем юзера в список и запоминаем его роль.
    :param chat_id: id чата юзера
    :param user_role: роль юзера
    """
    with shelve.open(SHELVE_NAME) as storage:
        storage[str(chat_id)+"_user_role"] = user_role

def set_user_id(chat_id, user_id):
    """
    Записываем юзера в список и запоминаем id из базы данных.
    :param chat_id: id чата юзера
    :param user_id: id юзера из базы
    """
    with shelve.open(SHELVE_NAME) as storage:
        storage[str(chat_id)+"_user_id"] = str(user_id)

def clear_user_data(chat_id):
    """
    Чистим данные юзера в хранилище.
    :param chat_id: id чата юзера
    """
    with shelve.open(SHELVE_NAME) as storage:
        del storage[str(chat_id)+"_user_id"]
        del storage[str(chat_id)+"_user_status"]
        del storage[str(chat_id)+"_user_role"]

def auth_user(chat_id, tel_num):
    """
    авторизация пользователя
    В случае, если человека не нашли в базе, возвращаем None
    """
    users = get_users();
    result = False
    for user in users:
        if user[2] == tel_num or "+"+str(user[2]) == tel_num:
            result = True
            set_user_status(chat_id, "Authorized")
            set_user_id(chat_id, user[0])
            set_user_role(chat_id, user[3])
    return result;

def get_user_status(chat_id):
    """
    Получаем статус текущего юзера.
    В случае, если человек не авторизован, возвращаем None
    :param chat_id: id юзера
    :return: (str) Текущий статус
    """
    with shelve.open(SHELVE_NAME) as storage:
        try:
            result = storage[str(chat_id)+"_user_status"]
            return result
        # Если человек не авторизован, ничего не возвращаем
        except KeyError:
            return None

def get_user_role(chat_id):
    """
    Получаем роль текущего юзера (для определения доступов).
    В случае, если человек не авторизован, возвращаем None
    :param chat_id: id юзера
    :return: (str) Роль пользователя (уровень доступа)
    """
    with shelve.open(SHELVE_NAME) as storage:
        try:
            result = storage[str(chat_id)+"_user_role"]
            return result
        # Если человек не авторизован, ничего не возвращаем
        except KeyError:
            return None

def get_user_name(chat_id):
    """
    Получаем имя текущего юзера.
    В случае, если человек не авторизован, возвращаем None
    :param chat_id: id юзера
    :return: (str) Имя из базы
    """
    result = None
    with shelve.open(SHELVE_NAME) as storage:
        users = get_users();
        id_ = storage[str(chat_id)+"_user_id"]
        for user in users:
            if user[0] == int(id_):
                result = user[1]
    return result

def generate_markup_groups():
    """
    Создаем кастомную клавиатуру для категорий вопросов
    :return: Объект кастомной клавиатуры
    """
    markup = types.InlineKeyboardMarkup(); #клавиатура

    groups = get_groups()
    for group in groups:
        item = types.InlineKeyboardButton(text=str(group[1]), callback_data=str(group[3]))
        markup.add(item)
    return markup

def generate_markup_grouprows(group):
    """
    Создаем кастомную клавиатуру для меню подгруппы
    :param group_id: Идентификатор группы
    :return: Объект кастомной клавиатуры
    """
    markup = types.InlineKeyboardMarkup(); #клавиатура

    grouprows = get_grouprows(group[0])
    for grouprow in grouprows:
        item = types.InlineKeyboardButton(text=str(grouprow[2]), callback_data=str(group[3]+"_"+grouprow[3]))
        markup.add(item)
    item = types.InlineKeyboardButton(text="<-Назад", callback_data="<-back")
    markup.add(item)
    return markup

def generate_markup_tel(tel, geo):
    """
    Создаем кастомную клавиатуру для отправки данных с телефона
    :param tel: Параметр определяет, нужно ли включать кнопку отправки телефона
    :param geo: Параметр определяет, нужно ли включать кнопку отправки геолокации
    :return: Объект кастомной клавиатуры
    """
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)

    if tel:
        button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
        markup.add(button_phone);
    if geo:
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        markup.add(button_geo);
    return markup
