import telebot
from telebot import types
from datetime import datetime
import random
import json

LOGFILE = 'Bot_logs.json'
HELP = """
/help - вывести список доступных команд
/start - начать с начала
/add <date> <task> - добавить задачу в список
/random - добавить случайную задачу на дату Сегодня
/show <date> or /print <date> - вывести все задачи на заданную дату
/datelist - показать даты, на которые есть задания
/showall - вывести все задачи на все даты
/delete <date> | <task> - удалить задачи на заданную дату
/clearall - очистить список задач
/play - сыграть в игру
/stop, /exit, /quit - завершение работы"""

RANDOM_TASKS = [
    "Записаться к врачу", "Позвонить маме", "Помыть полы", "Испечь торт", "Пойти в бассейн", "Купить хлеб",
    "Почитать книгу", "Проверить почту"
]
WORDS = ['виноград', 'апельсин', 'клубника', 'слива', 'мандарин', 'черешня', 'вишня', 'малина', 'смородина', 'ежевика',
         'лимон', 'грейпфрут', 'манго', 'крыжовник', 'яблоко', 'абрикос', 'ананас', 'персик', 'груша', 'кокос',
         'клюква']

# переменные для реализации игры КАМЕНЬ-НОЖНИЦЫ-БУМАГА
POOL = [1, 2, 4]
THINGS = ['', '  КАМЕНЬ  ', 'НОЖНИЦЫ', '  БУМАГА  ', '  БУМАГА  ']
WIN = {-1, -2, 3}
FAIL = {1, 2, -3}


# функция обеспечивает одну итерацию игры СЛОВА
def words(message):
    user_log = get_data(message.from_user.id)
    letter = message.text.lower()
    if not letter.isalpha():
        bot.send_message(message.chat.id,
                         f'Вводить можно только буквы!\nОсталось {user_log["chances"]} попыток.\nВведите букву:')
        return
    elif len(letter) > 1:
        bot.send_message(message.chat.id,
                         f'Ввести можно только 1 букву!\nОсталось {user_log["chances"]} попыток.\nВведите букву:')
        return
    elif letter in user_log["guessed"]:
        bot.send_message(message.chat.id,
                         f'Вы уже угадали эту букву!\nОсталось {user_log["chances"]} попыток.\nВведите букву:')
        return
    elif letter not in 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя':
        bot.send_message(message.chat.id,
                         f'Введите РУССКУЮ букву!\nОсталось {user_log["chances"]} попыток.\nВведите букву:')
        return
    if letter in user_log["word"]:
        text = "Буква угадана!\n"
        for i, l in enumerate(user_log["word"]):
            if l == letter:
                user_log["guessed"][i] = l
    else:
        text = "Буква не угадана!\n"
    for l in user_log["guessed"]:
        text += l + " "
    if user_log["chances"] > 0 and user_log["guessed"] != list(user_log["word"]):
        text += f'\nОсталось {user_log["chances"]} попыток.\nВведите букву:'
    post_data(message.from_user.id, user_log)
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, text, reply_markup=markup)


# функция обеспечивает одну итерацию игры КАМЕНЬ-НОЖНИЦЫ-БУМАГА
def stone(message):
    user_log = get_data(message.from_user.id)
    user_log["rounds"] += 1
    if message.text.upper() not in {'1', '2', '3', 'КАМЕНЬ', 'НОЖНИЦЫ', 'БУМАГА'}:
        bot.send_message(message.chat.id, "Можно вводить только КАМЕНЬ, НОЖНИЦЫ, БУМАГА или просто цифры 1, 2, 3")
    else:
        formated_choice = 0
        if message.text == '1' or message.text.upper() == 'КАМЕНЬ':
            formated_choice = 1
        if message.text == '2' or message.text.upper() == 'НОЖНИЦЫ':
            formated_choice = 2
        if message.text == '3' or message.text.upper() == 'БУМАГА':
            formated_choice = 4
        computer_choice = random.choice(POOL)
        text = f"Ваш выбор    Выбор компьютера\n{THINGS[formated_choice]}          {THINGS[computer_choice]}"
        result = formated_choice - computer_choice
        if result == 0:
            text += "\nНичья!"
        elif result in WIN:
            text += "\nВы выиграли в этом раунде!"
            user_log["user_win"] += 1
        elif result in FAIL:
            text += "\nВ этом раунде вы проиграли..."
            user_log["computer_win"] += 1
        else:
            text += "\nПроизошла ошибка."
        text += f'\nТекущий счёт {user_log["user_win"]}:{user_log["computer_win"]}'
        post_data(message.from_user.id, user_log)
        bot.send_message(message.chat.id, text)


# функция формирует словарь с данными пользователя
def new_user_log(name="", rounds=0, user_win=0, computer_win=0, chances=0, word="", guessed=[], tasks={}, time=""):
    my_dict = {}
    my_dict["name"] = name
    my_dict["rounds"] = rounds
    my_dict["user_win"] = user_win
    my_dict["computer_win"] = computer_win
    my_dict["chances"] = chances
    my_dict["word"] = word
    my_dict["guessed"] = guessed
    my_dict["tasks"] = tasks
    if time == "":
        time = datetime.now()
        my_dict["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        my_dict["timestamp"] = time
    return my_dict


# функция возвращает словарь (json) с данными пользователя из лог-файла (для нового пользователя запишет пустой словарь)
def get_data(user_id):
    my_dict = {}
    with open('Bot_logs.json', 'r', encoding='utf-8') as f_read:
        data = json.load(f_read)
        if str(user_id) in data:
            my_dict = data[str(user_id)]
        else:
            my_dict = new_user_log()
            data[str(user_id)] = my_dict
            with open('Bot_logs.json', 'w', encoding='utf-8') as f_write:
                json.dump(data, f_write, indent=2, ensure_ascii=False)
    return my_dict


# функция записывает словарь (json) с данными пользователя в лог-файл
def post_data(user_id, user_log):
    data = {}
    if not user_log:
        user_log = new_user_log()
    with open('Bot_logs.json', 'r', encoding='utf-8') as f_read:
        data = json.load(f_read)
    data[str(user_id)] = user_log
    with open('Bot_logs.json', 'w', encoding='utf-8') as f_write:
        json.dump(data, f_write, indent=2, ensure_ascii=False)


token = '5368592214:AAFi3lYagLygS8m1Zyiy2YaOO758c1dneMM'

bot = telebot.TeleBot(token)


# функция формирует кнопки основного меню
def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_add = types.KeyboardButton("Добавить задачу")
    btn_delete = types.KeyboardButton("Удалить задачу")
    btn_display = types.KeyboardButton("Вывести список дел")
    btn_help = types.KeyboardButton("Вернуться в меню")
    markup.add(btn_add, btn_delete, btn_display, btn_help)
    return markup


# функция формирует кнопки в меню добавления задачи
def menu_add():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_today = types.KeyboardButton("Сегодня")
    btn_tommorrow = types.KeyboardButton("Завтра")
    btn_random = types.KeyboardButton("Случайная")
    btn_back = types.KeyboardButton("Назад")
    markup.add(btn_today, btn_tommorrow, btn_random, btn_back)
    return markup


# обработчик команды /start, здороваемся и спрашиваем имя пользователя
@bot.message_handler(commands=["start"])
def start(message):
    text = "Вас приветствует эхо-Бот с полезными функциями.\n"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    user_log = get_data(message.from_user.id)
    if user_log["name"] == "":
        text += "Давай знакомиться. Как тебя зовут?"
    else:
        text += f'Привет, {user_log["name"]}!\nХочешь, чтобы я обращался к тебе иначе?'
        yes_button = types.KeyboardButton("Да,\nсейчас напишу новое имя")
        no_button = types.KeyboardButton("Нет,\nменя всё устраивает")
        markup.add(yes_button, no_button)
    bot.send_message(message.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(message, get_name)


# функция принимает и сохраняет имя пользователя в лог-файле
def get_name(message):
    if message.text == "Нет,\nменя всё устраивает":
        bot.send_message(message.chat.id, "ОК.\nДавай напомню, что я умею:")
        show_help(message)
    elif message.text == "Да,\nсейчас напишу новое имя":
        bot.send_message(message.chat.id, "Внимательно слушаю...")
        bot.register_next_step_handler(message, get_name)
    elif message.text.startswith('/'):
        bot.send_message(message.chat.id, "Ожидается имя, а не команда. Повторите ввод:")
        bot.register_next_step_handler(message, get_name)
    else:
# если пользователь напишет имя с переносом строки, то символ \n нарушит структуру лог-файла, поэтому берём только первую строку
        user_log = get_data(message.from_user.id)
        user_log["name"] = message.text.split('\n')[0]
        post_data(message.from_user.id, user_log)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("Что ты умеешь?")
        markup.add(button)
        bot.send_message(message.chat.id, f'Приятно познакомиться, {user_log["name"]}. Я запомню твоё имя.', reply_markup=markup)


# функция показывает справку по командам бота
@bot.message_handler(commands=["help"])
def show_help(message):
    bot.send_message(message.chat.id, HELP)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    plan = types.KeyboardButton("Перейти к списку дел")
    play = types.KeyboardButton("Играть")
    markup.add(plan, play)
    bot.send_message(message.chat.id, "Чем займёмся?", reply_markup=markup)


# функция запоминает дату и запрашивает задачу после траектории Добавить задачу -> Сегодня / Завтра / Случайная
def add_date(message):
    date = message.text.lower()
    if date == "назад":
        bot.send_message(message.chat.id, "Что дальше?", reply_markup=menu())
    elif date == "случайная":
        random_add(message)
        bot.send_message(message.chat.id, "Что дальше?", reply_markup=menu_add())
        bot.register_next_step_handler(message, add_date)
    elif date.startswith('/'):
        bot.send_message(message.chat.id, "Ожидается дата, а не команда. Повторите ввод:")
        bot.register_next_step_handler(message, add_date)
    else:
        bot.send_message(message.chat.id, "Введите задачу:")
        bot.register_next_step_handler(message, ask_task, date)


# функция обрабатывает введённую задачу (дата уже есть и передаётся дальше)
def ask_task(message, date):
    task = message.text.strip()
    if len(task) < 3:
        text = "Задача слишком короткая. Напишите подробнее."
        bot.register_next_step_handler(message, ask_task, date)
    elif task.startswith('/'):
        bot.send_message(message.chat.id, "Ожидается задача, а не команда. Повторите ввод:")
        bot.register_next_step_handler(message, ask_task, date)
    else:
        success = add_todo(message.from_user.id, date, task)
        if success:
            text = f'Задача "{task}" добавлена на дату {date.upper()}'
        else:
            text = f'В списке дел уже есть задача "{task}"'
    bot.send_message(message.chat.id, text, reply_markup=menu_add())
    bot.register_next_step_handler(message, add_date)


# функция добавления задачи на определённую дату при навигации по кнопкам
def add_todo(user_id, date, task):
    user_log = get_data(user_id)
    tasks = user_log["tasks"]
    if date in tasks:
        if task in tasks[date]:
            return False
        tasks[date].append(task)
    else:
        tasks[date] = [task]
    user_log["tasks"] = tasks
    post_data(user_id, user_log)
    return True


# обработчик команды /add <date> <task> - добавить задачу в список
@bot.message_handler(commands=["add", "todo"])
def add(message):
    command = message.text.split(maxsplit=2)
    if len(command) < 3:
        text = "Введите команду в формате\n/add <date> <task>"
    else:
        date = command[1].lower()
        task = command[2].strip()
        if len(task) < 3:
            text = "Задача слишком короткая. Напишите подробнее."
        else:
            success = add_todo(message.from_user.id, date, task)
            if success:
                text = f'Задача "{task}" добавлена на дату {date.upper()}'
            else:
                text = f'В списке дел уже есть задача "{task}"'
    bot.send_message(message.chat.id, text)


# функция добавления случайной задачи проверяет, чтобы не было дубликатов
@bot.message_handler(commands=["random"])
def random_add(message):
    date = "сегодня"
    task = random.choice(RANDOM_TASKS)
    success = add_todo(message.from_user.id, date, task)
    if success:
        text = f'Задача "{task}" добавлена на дату {date}'
    else:
        text = f'В списке дел уже есть задача "{task}"'
    bot.send_message(message.chat.id, text)


# функция обрабатывает навигацию по кнопкам Вывести список дел -> Сегодня / Завтра / Весь список
def show_menu(message):
    date = message.text.lower()
    if date == 'весь список':
        showall(message)
    elif date == "вывести только даты":
        datelist(message)
    else:
        show_date(message, date)
    bot.send_message(message.chat.id, "Что дальше?", reply_markup=menu())


# функция выводит список дат, на которые есть задачи, т.е. ключи нашего словаря
@bot.message_handler(commands=["datelist"])
def datelist(message):
    user_log = get_data(message.from_user.id)
    tasks = user_log["tasks"]
    text = "На эти даты есть задачи:"
    for date in tasks:
        text = text + "\n- " + date.upper()
    if text == "На эти даты есть задачи:":
        text = "Расписание пусто."
    bot.send_message(message.chat.id, text)


# функция выводит список дел на определённую дату при навигации по кнопкам
def show_date(message, date):
    user_log = get_data(message.from_user.id)
    tasks = user_log["tasks"]
    if date in tasks:
        text = f"Список задач на {date.upper()}:"
        count = 1
        for task in tasks[date]:
#            text = text + "\n- " + task
            text += f"\n{count}. {task}"
            count += 1
    else:
        text = "Задач на эту дату нет."
    bot.send_message(message.chat.id, text)


# обработчик команды /show <date> or /print <date> - вывести все задачи на заданную дату
@bot.message_handler(commands=["show", "print"])
def show(message):
    command = message.text.split(maxsplit=1)
    if len(command) < 2:
        bot.send_message(message.chat.id, "Введите команду в формате\n" + message.text + " <date>")
    else:
        date = command[1].lower()
        show_date(message, date)


# вывод всех задач на все даты
@bot.message_handler(commands=["showall"])
def showall(message):
    text = ""
    user_log = get_data(message.from_user.id)
    tasks = user_log["tasks"]
    for date in tasks:
        text += "Список задач на " + date.upper() + ":"
        for task in tasks[date]:
            text += "\n- " + task
        text += "\n\n"
    if text == "":
        text = "В расписании нет задач."
    bot.send_message(message.chat.id, text)


# функция обрабатывает навигацию по кнопкам Удалить задачу -> Сегодня / Завтра / Удалить всё
def delete_menu(message):
    date = message.text.lower()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if date == "удалить всё":
        text = "Вы уверены, что хотите полностью очистить список дел?"
        yes_button = types.KeyboardButton("Да,\nудалить всё")
        no_button = types.KeyboardButton("Нет,\nя передумал")
        markup.add(yes_button, no_button)
        bot.register_next_step_handler(message, confirm_delete_all)
    else:
        user_log = get_data(message.from_user.id)
        tasks = user_log["tasks"]
        if date in tasks:
            text = f"Из списка {date.upper()} можно удалить одну или сразу все задачи. Введите номер задачи или её текст:"
            btn_one = types.KeyboardButton("1")
            btn_two = types.KeyboardButton("2")
            btn_three = types.KeyboardButton("3")
            btn_all = types.KeyboardButton("Все")
            markup.add(btn_one, btn_two, btn_three, btn_all, row_width=4)
            bot.register_next_step_handler(message, delete_task, date)
        else:
            text = "В расписании нет такой даты."
            markup = menu()
    bot.send_message(message.chat.id, text, reply_markup=markup)


# функция удаляет одну задачу из списка или все задачи на определённую дату
def delete_task(message, date):
    task = message.text
    user_log = get_data(message.from_user.id)
    tasks = user_log["tasks"]
    rewrite = False
    if task == 'Все':
        tasks.pop(date)
        rewrite = True
        text = f"Дата {date.upper()} со всеми задачами удалена из расписания."
    else:
        task_list = tasks[date]
        if task.isdigit() == True:
            if int(task) > len(task_list):
                text = f"На дату {date.upper()} нет задачи с номером {task}."
            else:
                task_list.pop(int(task)-1)
                rewrite = True
                text = f"Задача номер {task} успешно удалена из списка {date.upper()}."
        elif task in task_list:
            task_list.remove(task)
            rewrite = True
            text = f"Задача успешно удалена из списка {date.upper()}."
        else:
            text = f"Такой задачи в списке {date.upper()} не найдено."
        if task_list == []:
            tasks.pop(date)
            text += f"\nНа дату {date.upper()} не осталось задач. Дата удалена из расписания."
        if rewrite and task_list != []:
            tasks[date] = task_list
    if rewrite:
        user_log["tasks"] = tasks
        post_data(message.from_user.id, user_log)
    bot.send_message(message.chat.id, text, reply_markup=menu())


# обработчик команды /delete <date> | <task> - удалить задачи на заданную дату
@bot.message_handler(commands=["delete"])
def delete(message):
    command = message.text.split(maxsplit=2)
    if len(command) < 2:
        text = "Вы не указали дату. Введите команду в формате\n/delete <date> | <task>"
    else:
        date = command[1].lower()
        user_log = get_data(message.from_user.id)
        tasks = user_log["tasks"]
        if date not in tasks:
            text = "В расписании нет такой даты."
        else:
            rewrite = False
            if len(command) < 3:
                tasks.pop(date)
                rewrite = True
                text = f"Все задачи на дату {date.upper()} удалены."
            else:
                task = command[2].strip()
                task_list = tasks[date]
                if task.isdigit() == True and int(task) <= len(task_list):
                    task_list.pop(int(task)-1)
                    rewrite = True
                    text = f"Задача номер {task} успешно удалена."
                elif task in task_list:
                    task_list.remove(task)
                    rewrite = True
                    text = f'Задача "{task}" успешно удалена.'
                else:
                    text = f'Такой задачи в списке {date.upper()} не найдено.'
                if task_list == []:
                    tasks.pop(date)
                    text += f"\nНа дату {date.upper()} не осталось задач. Дата удалена из расписания."
                if rewrite and task_list != []:
                    tasks[date] = task_list
            if rewrite:
                user_log["tasks"] = tasks
                post_data(message.from_user.id, user_log)
    bot.send_message(message.chat.id, text)


def confirm_delete_all(message):
    if message.text == "Да,\nудалить всё":
        clearall(message)
    else:
        bot.send_message(message.chat.id, "Удаление отменено.\nВозвращаюсь в главное меню:")
    show_help(message)


# очистить список задач
@bot.message_handler(commands=["clearall"])
def clearall(message):
    user_log = get_data(message.from_user.id)
    user_log["tasks"] = {}
    post_data(message.from_user.id, user_log)
    bot.send_message(message.chat.id, "Список задач очищен.")


# функция подчищает все логи пользователя кроме id
@bot.message_handler(commands=["exit", "stop", "quit"])
def stop(message):
    user_log = new_user_log()
    post_data(message.from_user.id, user_log)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("Перезапустить")
    markup.add(button)
    bot.send_message(message.chat.id, "Спасибо за использование! До свидания!", reply_markup=markup)


# обработчик команды /play, предлагает две игры на выбор
@bot.message_handler(commands=["play"])
def play_games(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    game1 = types.KeyboardButton("Угадай слово")
    game2 = types.KeyboardButton("Камень-ножницы-\nбумага")
    markup.add(game1, game2)
    bot.send_message(message.chat.id, "Выбери игру:", reply_markup=markup)


@bot.message_handler(content_types=["text"])
def echo(message):
# если пользователь сейчас играет в К-Н-Б, то rounds > 0, а если играет в слова, то chances > 0
    user_log = get_data(message.from_user.id)
    rounds = user_log["rounds"]
    chances = user_log["chances"]
    last_time = datetime.strptime(user_log["timestamp"], '%Y-%m-%d %H:%M:%S')
# пользователю не разрешено отправлять сообщения чаще, чем раз в секунду (кнопки позволяют заспамить бота)
    delta = datetime.now() - last_time
    if delta.seconds < 1:
        return
    if message.text == "Что ты умеешь?" or message.text.lower() == "помощь" or message.text == "Вернуться в меню":
        show_help(message)
    elif message.text == "Перезапустить":
        start(message)
    elif message.text.lower() == "играть" or message.text.lower() == "сыграть ещё":
        play_games(message)
    elif message.text == "Перейти к списку дел":
        bot.send_message(message.chat.id,
                         "Ты можешь добавить новую или случайную задачу в расписание, а также вывести список дел.",
                         reply_markup=menu())
    elif message.text == "Добавить задачу":
        bot.send_message(message.chat.id,
                         "На какую дату добавить задачу? Сделай выбор или напечатай:",
                         reply_markup=menu_add())
        bot.register_next_step_handler(message, add_date)
    elif message.text == "Удалить задачу":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_today = types.KeyboardButton("Сегодня")
        btn_tommorrow = types.KeyboardButton("Завтра")
        btn_all = types.KeyboardButton("Удалить всё")
        btn_help = types.KeyboardButton("Вернуться в меню")
        markup.add(btn_today, btn_tommorrow, btn_all, btn_help)
        bot.send_message(message.chat.id,
                         "Из какого списка удалить задачу? Выбери вариант или напечатай:",
                         reply_markup=markup)
        bot.register_next_step_handler(message, delete_menu)
    elif message.text == "Вывести список дел":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_today = types.KeyboardButton("Сегодня")
        btn_tommorrow = types.KeyboardButton("Завтра")
        btn_all = types.KeyboardButton("Весь список")
        btn_list = types.KeyboardButton("Вывести только даты")
#        markup.add(btn_today, btn_tommorrow, btn_all, btn_list)
        markup.add(btn_today, btn_tommorrow)
        markup.add(btn_all, btn_list)
        bot.send_message(message.chat.id,
                         "Отобразить весь список или на определённую дату? Сделай выбор или напечатай:",
                         reply_markup=markup)
        bot.register_next_step_handler(message, show_menu)
    elif message.text == "Угадай слово":
        word = random.choice(WORDS)
        chances = len(word) + 3
        text = "Игра угадай слово. Подсказка: это фрукт или ягода.\nУ вас " + str(chances) + " попыток.\n"
        guessed = ['_'] * len(word)
        for letter in guessed:
            text += letter + " "
        text += "\nВведите букву:"
        post_data(message.from_user.id, new_user_log(user_log["name"], 0, 0, 0, chances, word, guessed, user_log["tasks"], ""))
        bot.send_message(message.chat.id, text)
    elif message.text == "Камень-ножницы-\nбумага":
        post_data(message.from_user.id, new_user_log(user_log["name"], 1, 0, 0, 0, "", [], user_log["tasks"], ""))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        var1 = types.KeyboardButton("КАМЕНЬ")
        var2 = types.KeyboardButton("НОЖНИЦЫ")
        var3 = types.KeyboardButton("БУМАГА")
        markup.add(var1, var2, var3)
        text = "Давайте сыграем в игру КАМЕНЬ-НОЖНИЦЫ-БУМАГА!\nИгра ведётся до трёх побед.\nРаунд №1\nСделайте свой выбор:\n1 - КАМЕНЬ\n2 - НОЖНИЦЫ\n3 - БУМАГА\n"
        bot.send_message(message.chat.id, text, reply_markup=markup)
    elif chances > 0:
        chances -= 1
        user_log["chances"] -= 1
        post_data(message.from_user.id, user_log)
        words(message)
        user_log = get_data(message.from_user.id)
        word = user_log["word"]
        guessed = user_log["guessed"]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        but1 = types.KeyboardButton("Сыграть ещё")
        but2 = types.KeyboardButton("Вернуться в меню")
        markup.add(but1, but2)
        if chances == 0 and guessed != list(word):
            bot.send_message(message.chat.id,
                             "Попытки закончились! Вы проиграли...\nБыло загадано слово: " + word.upper(),
                             reply_markup=markup)
            post_data(message.from_user.id, new_user_log(user_log["name"], 0, 0, 0, 0, "", [], user_log["tasks"], ""))
        if guessed == list(word):
            post_data(message.from_user.id, new_user_log(user_log["name"], 0, 0, 0, 0, "", [], user_log["tasks"], ""))
            bot.send_message(message.chat.id, "Поздравляем, Вы победили!\nБыло загадано слово: " + word.upper(),
                             reply_markup=markup)
    elif rounds > 0:
        stone(message)
        user_log = get_data(message.from_user.id)
        rounds = user_log["rounds"]
        user_win = user_log["user_win"]
        computer_win = user_log["computer_win"]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        but1 = types.KeyboardButton("Сыграть ещё")
        but2 = types.KeyboardButton("Вернуться в меню")
        markup.add(but1, but2)
        if user_win == 3:
            post_data(message.from_user.id, new_user_log(user_log["name"], 0, 0, 0, 0, "", [], user_log["tasks"], ""))
            bot.send_message(message.chat.id, "Поздравляем, Вы победили!", reply_markup=markup)
        elif computer_win == 3:
            post_data(message.from_user.id, new_user_log(user_log["name"], 0, 0, 0, 0, "", [], user_log["tasks"], ""))
            bot.send_message(message.chat.id, "К сожалению, Вы проиграли...", reply_markup=markup)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            var1 = types.KeyboardButton("КАМЕНЬ")
            var2 = types.KeyboardButton("НОЖНИЦЫ")
            var3 = types.KeyboardButton("БУМАГА")
            markup.add(var1, var2, var3)
            text = f'Раунд №" {rounds}"\nСделайте свой выбор:\n1 - КАМЕНЬ\n2 - НОЖНИЦЫ\n3 - БУМАГА\n'
            bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    bot.polling(none_stop=True)