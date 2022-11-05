import telebot
from telebot import types
from datetime import datetime
import random

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

POOL = [1, 2, 4]
THINGS = ['', '  КАМЕНЬ  ', 'НОЖНИЦЫ', '  БУМАГА  ', '  БУМАГА  ']
WIN = {-1, -2, 3}
FAIL = {1, 2, -3}


def words(message):
    chances, word = [get_attr(message.from_user.id, x) for x in [5, 6]]
    guessed = get_guessed(message.from_user.id)
    letter = message.text.lower()
    if not letter.isalpha():
        bot.send_message(message.chat.id,
                         f"Вводить можно только буквы!\nОсталось {chances} попыток.\nВведите букву:")
        return
    elif len(letter) > 1:
        bot.send_message(message.chat.id,
                         f"Ввести можно только 1 букву!\nОсталось {chances} попыток.\nВведите букву:")
        return
    elif letter in guessed:
        bot.send_message(message.chat.id,
                         f"Вы уже угадали эту букву!\nОсталось {chances} попыток.\nВведите букву:")
        return
    elif letter not in 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя':
        bot.send_message(message.chat.id,
                         f"Введите РУССКУЮ букву!\nОсталось {chances} попыток.\nВведите букву:")
        return
    if letter in word:
        text = "Буква угадана!\n"
        for i, l in enumerate(word):
            if l == letter:
                guessed[i] = l
    else:
        text = "Буква не угадана!\n"
    for l in guessed:
        text += l + " "
    if int(chances) > 0 and guessed != list(word):
        text += f"\nОсталось {chances} попыток.\nВведите букву:"
    write_guessed(message.from_user.id, guessed)
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, text, reply_markup=markup)


def stone(message):
    rounds = int(get_attr(message.from_user.id, 2))
    user_win = int(get_attr(message.from_user.id, 3))
    computer_win = int(get_attr(message.from_user.id, 4))
    rounds += 1
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
            user_win += 1
        elif result in FAIL:
            text += "\nВ этом раунде вы проиграли..."
            computer_win += 1
        else:
            text += "\nПроизошла ошибка."
        text += f"\nТекущий счёт {user_win}:{computer_win}"
        change_attr(message.from_user.id, [2, 3, 4], [str(rounds), str(user_win), str(computer_win)])
        bot.send_message(message.chat.id, text)


# функция возвращает индекс строки лог-файла, в котором хрянится статус пользователя с переданным user_id
# если такого пользователя нет, то возвращает -1
def find_line(user_id):
    with open('Bot_cookies.txt', 'r', encoding='UTF-8') as f:
        file_data = f.readlines()
        for index, line in enumerate(file_data):
            if line.startswith(str(user_id)):
                return index
    return -1


# функция возвращает значение одного атрибута из лог-файла
def get_attr(user_id, attr_index):
    index = -1
    with open('Bot_cookies.txt', 'r', encoding='UTF-8') as f:
        file_data = f.readlines()
        for ind, line in enumerate(file_data):
            if line.startswith(str(user_id)):
                index = ind
                break
#если вдруг каким-то образом пользователь уклонился от знакомства, то формируем его атрибуты в лог-файле
    if index == -1:
        new_line = make_line(user_id)
        cooky = new_line.split(';')
        with open('Bot_cookies.txt', 'a', encoding='UTF-8') as f:
            f.write(new_line)
    else:
        cooky = file_data[index].split(';')
    return cooky[attr_index]


# в игре СЛОВА угаданные буквы представлены списком, функция получает кусок строки из лог-файла и преобразует в список
def get_guessed(user_id):
    cooky = get_attr(user_id, 7)
    guessed = []
    for char in cooky:
        guessed.append(char)
    guessed.pop(0)
    guessed.pop()
    return guessed


# из лог-файла извлекаем словарь со списком дел
def get_tasks(user_id):
    line = get_attr(user_id, 8).strip('{}')
    if line == '':
        return {}
    cooky = line.split(',')
    cooky.pop()
    cooky.pop()
    tasks = {}
    date = 'other'
    for substr in cooky:
        if ':' in substr:
            word = substr.split(':')
            date = word[0].strip()
            task = word[1].strip(' [')
            tasks[date] = [task]
        elif substr == ' ]':
            continue
        else:
            tasks[date].append(substr.strip())
    return tasks


#функция формирует строку с атрибутами пользователя, чтобы править формат cookies в одном месте
def make_line(user_id, name='', rounds='0', user_win='0', computer_win='0', chances='0', word='', guessed='[]', tasks='{}', time=''):
    if time == '':
        time = datetime.now()
    my_list = [str(user_id), name, rounds, user_win, computer_win, chances, word, guessed, tasks, time.strftime('%Y-%m-%d %H:%M:%S'), '\n']
    line = ';'.join(my_list)
    return line


# функция меняет значение атрибутов пользователя в лог-файле, аргументы - идентификатор пользователя,
# список порядковых номеров атрибутов, список новых значений атрибутов
def change_attr(user_id, attr_index, attribute):
    index = -1
    with open('Bot_cookies.txt', 'r', encoding='UTF-8') as f:
        file_data = f.readlines()
        for ind, line in enumerate(file_data):
            if line.startswith(str(user_id)):
                index = ind
                break
#если вдруг каким-то образом пользователь уклонился от знакомства, то формируем его атрибуты в лог-файле
        if index == -1:
            new_line = make_line(user_id)
            cooky = new_line.split(';')
            with open('Bot_cookies.txt', 'a', encoding='UTF-8') as f:
                f.write(new_line)
            index = ind + 1
            file_data.append(new_line)
        else:
            cooky = line.split(';')
#    print(cooky)
    for number, ind in enumerate(attr_index):
        cooky[ind] = attribute[number]
    time = datetime.now()
    cooky[-2] = time.strftime('%Y-%m-%d %H:%M:%S')
    my_str = ';'.join(cooky)
    file_data[index] = my_str
    with open('Bot_cookies.txt', 'w', encoding='UTF-8') as f:
        for line in file_data:
            f.write(line)


def change_line(user_id, new_line):
    index = -1
    with open('Bot_cookies.txt', 'r', encoding='UTF-8') as f:
        file_data = f.readlines()
        for ind, line in enumerate(file_data):
            if line.startswith(str(user_id)):
                index = ind
                break
# если вдруг каким-то образом пользователь уклонился от знакомства, то вместо замены записываем новую строку в лог-файл
    if index == -1:
        with open('Bot_cookies.txt', 'a', encoding='UTF-8') as f:
            f.write(new_line)
    else:
        file_data[index] = new_line
        with open('Bot_cookies.txt', 'w', encoding='UTF-8') as f:
            for line in file_data:
                f.write(line)


# в игре СЛОВА угаданные буквы представлены списком, функция сохраняет это в лог-файл
def write_guessed(user_id, guessed):
    my_string = '['
    for i in range(len(guessed)):
        my_string += str(guessed[i])
    my_string += ']'
    change_attr(user_id, [7], [my_string])


# словарь tasks преобразуем в строку, функция сохраняет это в лог-файл
def write_tasks(user_id, tasks):
    my_string = '{'
    for date in tasks:
        my_string += date + ': ['
        for task in tasks[date]:
            my_string += task + ', '
        my_string += '], '
    my_string += '}'
    change_attr(user_id, [8], [my_string])


token = ''

bot = telebot.TeleBot(token)


#функция формирует кнопки основного меню
def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_add = types.KeyboardButton("Добавить задачу")
    btn_delete = types.KeyboardButton("Удалить задачу")
    btn_display = types.KeyboardButton("Вывести список дел")
    btn_help = types.KeyboardButton("Вернуться в меню")
    markup.add(btn_add, btn_delete, btn_display, btn_help)
    return markup


@bot.message_handler(commands=["start"])
def start(message):
    text = "Вас приветствует эхо-Бот с полезными функциями.\n"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if find_line(message.from_user.id) == -1 or get_attr(message.from_user.id, 1) == '':
        text += "Давай знакомиться. Как тебя зовут?"
    else:
        name = get_attr(message.from_user.id, 1)
        text = text + "Привет, " + name + "!\nХочешь, чтобы я обращался к тебе иначе?"
        yes_button = types.KeyboardButton("Да,\nсейчас напишу новое имя")
        no_button = types.KeyboardButton("Нет,\nменя всё устраивает")
        markup.add(yes_button, no_button)
    bot.send_message(message.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(message, get_name)


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
        name = message.text.split('\n')[0]
        if find_line(message.from_user.id) == -1:
            with open('Bot_cookies.txt', 'a', encoding='UTF-8') as f:
                f.write(make_line(message.from_user.id, name))
        else:
            change_attr(message.from_user.id, [1], [name])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("Что ты умеешь?")
        markup.add(button)
        bot.send_message(message.chat.id, f"Приятно познакомиться, {name}. Я запомню твоё имя.", reply_markup=markup)


@bot.message_handler(commands=["help"])
def show_help(message):
    bot.send_message(message.chat.id, HELP)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    plan = types.KeyboardButton("Перейти к списку дел")
    play = types.KeyboardButton("Играть")
    markup.add(plan, play)
    bot.send_message(message.chat.id, "Чем займёмся?", reply_markup=markup)


# функция запоминает дату и запрашивает задачу после траектории Добавить задачу -> Сегодня / Завтра / Случайная
def add_menu(message):
    date = message.text.lower()
    if date == "вернуться в меню":
        show_help(message)
    elif date == "случайная":
        random_add(message)
        bot.send_message(message.chat.id, "Что дальше?", reply_markup=menu())
    elif date.startswith('/'):
        bot.send_message(message.chat.id, "Ожидается дата, а не команда. Повторите ввод:")
        bot.register_next_step_handler(message, add_menu)
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
            text = f"Задача {task} добавлена на дату {date.upper()}"
        else:
            text = f"В списке дел уже есть задача {task}"
    bot.send_message(message.chat.id, text, reply_markup=menu())


# функция добавления задачи на определённую дату
def add_todo(user_id, date, task):
    tasks = get_tasks(user_id)
    if date in tasks:
        if task in tasks[date]:
            return False
        tasks[date].append(task)
    else:
        tasks[date] = [task]
    write_tasks(user_id, tasks)
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
                text = f"Задача {task} добавлена на дату {date.upper()}"
            else:
                text = f"В списке дел уже есть задача {task}"
    bot.send_message(message.chat.id, text)


# функция добавления случайной задачи проверяет, чтобы не было дубликатов
@bot.message_handler(commands=["random"])
def random_add(message):
    date = "сегодня"
    task = random.choice(RANDOM_TASKS)
    success = add_todo(message.from_user.id, date, task)
    if success:
        text = f"Задача {task} добавлена на дату {date}"
    else:
        text = f"В списке дел уже есть задача {task}"
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
    tasks = get_tasks(message.from_user.id)
    text = "На эти даты есть задачи:"
    for date in tasks:
        text = text + "\n- " + date.upper()
    if text == "На эти даты есть задачи:":
        text = "Расписание пусто."
    bot.send_message(message.chat.id, text)


# функция выводит список дел на определённую дату
def show_date(message, date):
    tasks = get_tasks(message.from_user.id)
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
    tasks = get_tasks(message.from_user.id)
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
        tasks = get_tasks(message.from_user.id)
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
            btn_add = types.KeyboardButton("Добавить задачу")
            btn_delete = types.KeyboardButton("Удалить задачу")
            btn_display = types.KeyboardButton("Вывести список дел")
            btn_help = types.KeyboardButton("Вернуться в меню")
            markup.add(btn_add, btn_delete, btn_display, btn_help)
    bot.send_message(message.chat.id, text, reply_markup=markup)


#функция удаляет одну задачу из списка или все задачи на определённую дату
def delete_task(message, date):
    task = message.text
    tasks = get_tasks(message.from_user.id)
    rewrite = False
    if task == 'Все':
        tasks.pop(date)
        rewrite = True
        text = f"Дата {date.upper()} со всеми задачами удалена из расписания."
    else:
        task_list = tasks[date]
        if task == '1' or task == '2' or task == '3':
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
        write_tasks(message.from_user.id, tasks)
    bot.send_message(message.chat.id, text, reply_markup=menu())


# обработчик команды /delete <date> | <task> - удалить задачи на заданную дату
@bot.message_handler(commands=["delete"])
def delete(message):
    command = message.text.split(maxsplit=2)
    if len(command) < 2:
        text = "Вы не указали дату. Введите команду в формате\n/delete <date> | <task>"
    else:
        date = command[1].lower()
        tasks = get_tasks(message.from_user.id)
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
                    text = f"Задача {task} успешно удалена."
                else:
                    text = f"На дату {date.upper()} нет задачи {task}."
                if task_list == []:
                    tasks.pop(date)
                    text += f"\nНа дату {date.upper()} не осталось задач. Дата удалена из расписания."
                if rewrite and task_list != []:
                    tasks[date] = task_list
            if rewrite:
                write_tasks(message.from_user.id, tasks)
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
    change_attr(message.from_user.id, [8], ['{}'])
    bot.send_message(message.chat.id, "Список задач очищен.")


@bot.message_handler(commands=["exit", "stop", "quit"])
def stop(message):
    change_line(message.from_user.id, make_line(message.from_user.id))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Перезапустить")
    markup.add(button)
    bot.send_message(message.chat.id, "Спасибо за использование! До свидания!", reply_markup=markup)


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
    rounds = int(get_attr(message.from_user.id, 2))
    chances = int(get_attr(message.from_user.id, 5))
    last_time = datetime.strptime(get_attr(message.from_user.id, 9), '%Y-%m-%d %H:%M:%S')
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
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn_today = types.KeyboardButton("Сегодня")
        btn_tommorrow = types.KeyboardButton("Завтра")
        btn_random = types.KeyboardButton("Случайная")
        btn_help = types.KeyboardButton("Вернуться в меню")
        markup.add(btn_today, btn_tommorrow, btn_random, btn_help)
        bot.send_message(message.chat.id,
                         "На какую дату добавить задачу? Сделай выбор или напечатай:",
                         reply_markup=markup)
        bot.register_next_step_handler(message, add_menu)
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
        change_attr(message.from_user.id, [2, 3, 4, 5, 6], ['0', '0', '0', str(chances), word])
        write_guessed(message.from_user.id, guessed)
        bot.send_message(message.chat.id, text)
    elif message.text == "Камень-ножницы-\nбумага":
        change_attr(message.from_user.id, [2, 3, 4, 5, 6, 7], ['1', '0', '0', '0', '', '[]'])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        var1 = types.KeyboardButton("КАМЕНЬ")
        var2 = types.KeyboardButton("НОЖНИЦЫ")
        var3 = types.KeyboardButton("БУМАГА")
        markup.add(var1, var2, var3)
        text = "Давайте сыграем в игру КАМЕНЬ-НОЖНИЦЫ-БУМАГА!\nИгра ведётся до трёх побед.\nРаунд №1\nСделайте свой выбор:\n1 - КАМЕНЬ\n2 - НОЖНИЦЫ\n3 - БУМАГА\n"
        bot.send_message(message.chat.id, text, reply_markup=markup)
    elif chances > 0:
        chances -= 1
        change_attr(message.from_user.id, [5], [str(chances)])
        words(message)
        word = get_attr(message.from_user.id, 6)
        guessed = get_guessed(message.from_user.id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        but1 = types.KeyboardButton("Сыграть ещё")
        but2 = types.KeyboardButton("Вернуться в меню")
        markup.add(but1, but2)
        if chances == 0 and guessed != list(word):
            bot.send_message(message.chat.id,
                             "Попытки закончились! Вы проиграли...\nБыло загадано слово: " + word.upper(),
                             reply_markup=markup)
            change_attr(message.from_user.id, [5, 6, 7], ['0', '', '[]'])
        if guessed == list(word):
            change_attr(message.from_user.id, [5, 6, 7], ['0', '', '[]'])
            bot.send_message(message.chat.id, "Поздравляем, Вы победили!\nБыло загадано слово: " + word.upper(),
                             reply_markup=markup)
    elif rounds > 0:
        stone(message)
#        rounds, user_win, computer_win = list(map(get_attr, [message.from_user.id]*3, [2, 3, 4]))
        rounds, user_win, computer_win = [get_attr(message.from_user.id, i) for i in [2, 3, 4]]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        but1 = types.KeyboardButton("Сыграть ещё")
        but2 = types.KeyboardButton("Вернуться в меню")
        markup.add(but1, but2)
        if user_win == '3':
            change_attr(message.from_user.id, [2, 3, 4], ['0', '0', '0'])
            bot.send_message(message.chat.id, "Поздравляем, Вы победили!", reply_markup=markup)
        elif computer_win == '3':
            change_attr(message.from_user.id, [2, 3, 4], ['0', '0', '0'])
            bot.send_message(message.chat.id, "К сожалению, Вы проиграли...", reply_markup=markup)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            var1 = types.KeyboardButton("КАМЕНЬ")
            var2 = types.KeyboardButton("НОЖНИЦЫ")
            var3 = types.KeyboardButton("БУМАГА")
            markup.add(var1, var2, var3)
            text = "Раунд №" + rounds + "\nСделайте свой выбор:\n1 - КАМЕНЬ\n2 - НОЖНИЦЫ\n3 - БУМАГА\n"
            bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, message.text)


bot.polling(none_stop=True)
