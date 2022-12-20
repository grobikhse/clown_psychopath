import telebot
from telebot import types
from random import choice
from unittest.mock import Mock

bot = telebot.TeleBot(' ')


bots = '\U0001F92A'  # задаю игровые параметры
players = '\U0001F921'
size = 3
field = None
keyboard = None
buttons = None
vacant_fields = []


class GameField: # в этом классе создается поле
    def __init__(self, size):
        self.grid = []
        self.size = size
        for _ in range(size):  # создание игрового поля
            tmp = []
            for _ in range(size):
                tmp.append(' ')
            self.grid.append(tmp)

            
    def get_cols(self):  # столбцы
        cols = []
        for i in range(self.size):
            cols.append([row[i] for row in self.grid])
        return cols

      
    def get_diags(self):  # диагонали
        return [[self.grid[i][i] for i in range(self.size)],
                [self.grid[self.size - i - 1][i] for i in range(self.size)]]

      
    def make_move(self, x, y, symbol):  # сделать ход
        self.grid[x][y] = symbol
        
        
    def check_wincons(self):  # проверка условий выигрыша клоунов или психопатов
        wincons = self.grid + self.get_cols() + self.get_diags()
        # print(wincons)
        if ['\U0001F921'] * (self.size) in wincons:
            return '\U0001F921'
        if ['\U0001F92A'] * (self.size) in wincons:
            return '\U0001F92A'
        return None

    def is_vacant(self, x, y): # если клетка не занята, то там, удивительно, пустота
        return self.grid[x][y] == ' '

    def as_string(self):
        rows = [' '.join(row) for row in self.grid]
        return '\n'.join(rows)


def new_game(buttons, keyboard):  # начало новой игры (сброс поля, сброс клавиш в телеге)
    global field
    global vacant_fields
    vacant_fields = []
    field = GameField(size)
    for i in range(size):
        for j in range(size):
            vacant_fields.append([i, j])
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    # buttons, keyboard = 
    return build_buttons(buttons, keyboard)


bot.edit_message_text = Mock() # инициализируем мок

def build_buttons(buttons, keyboard):  # сброс клавиш в телеге 
    flattened_grid = []
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=3)

    for row in field.grid:
        for el in row:
            flattened_grid.append(el)
    for i in range(len(flattened_grid)):
        buttons.append(types.InlineKeyboardButton(flattened_grid[i], callback_data=str(i//3) + ',' + str(i%3)))
    keyboard.row(*buttons[:3])
    keyboard.row(*buttons[3:6])
    keyboard.row(*buttons[6:])
    return buttons, keyboard


@bot.message_handler(content_types=['text'])  # обработчик текстовых команд (при команде старт передаёт управление обработчику клавиатуры)
def get_text_messages(message):
    if message.text == "/start": #начинается игра
        bot.send_message(message.from_user.id, "Сыграем.")
    elif message.text == "/help": #ну в чем тут может быть нужна помощь, просто на старт нажми, ей-богу
        bot.send_message(message.from_user.id, "Type /start to start")
    keyboard = types.InlineKeyboardMarkup() #человек должен стать клоуном или психопатом
    keyboard.row(types.InlineKeyboardButton('\U0001F921', callback_data='\U0001F921'), types.InlineKeyboardButton('\U0001F92A', callback_data='\U0001F92A'))
    bot.send_message(message.from_user.id, "Выберите свою сторону.", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)  # обработчик клавиатуры (той что в телеге)
def callbackInline(call):  # вот тут и происходит сражение (если игрок за психопата, то первый ход делает бот, иначе игрок)
    if (call.message):
        global buttons
        global keyboard
        global field
        global vacant_fields

        if call.data in ['\U0001F921', '\U0001F92A']:
            global players
            global bots

            players = call.data
            bots = '\U0001F92A' if players == '\U0001F921' else '\U0001F921'

            buttons, keyboard = new_game(buttons, keyboard)
            if players == '\U0001F92A':  # первый ход делает бот, если игрок играет за психопата
                random_cell = choice(vacant_fields)
                print(random_cell)
                field.make_move(*random_cell, bots) # бот беспощадно рандомит
                vacant_fields.remove(random_cell)
                buttons, keyboard = build_buttons(buttons, keyboard)
            bot.send_message(call.message.chat.id, "Place your symbol", reply_markup=keyboard)
        else:
            x, y = call.data.split(',')
            x, y = int(x), int(y)
            if field.is_vacant(x, y):  
                field.make_move(x, y, players)
                vacant_fields.remove([x, y])
                if field.check_wincons() == players:
                    buttons, keyboard = build_buttons(buttons, keyboard) # обновление кнопок
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Игра окончена.", reply_markup=keyboard) # редактируем сообщение с игровым полем
                    bot.send_message(call.message.chat.id, "Вы выиграли.")
                    bot.send_message(call.message.chat.id, "To start new game send /start")
                elif not vacant_fields: # если кончились пустые поля, но игрок не победил после своего хода — ничья
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Game has ended", reply_markup=keyboard)
                    bot.send_message(call.message.chat.id, "Победила дружба.")
                    bot.send_message(call.message.chat.id, "To start new game send /start")
                else:
                    print(vacant_fields)
                    random_cell = choice(vacant_fields) # бот выбирает рандомное поле из свободных
                    print(random_cell)
                    field.make_move(*random_cell, bots) # ход бота
                    vacant_fields.remove(random_cell)
                    if field.check_wincons() == bots: # проверяем на победу бота
                        buttons, keyboard = build_buttons(buttons, keyboard)
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Game has ended", reply_markup=keyboard)
                        bot.send_message(call.message.chat.id, "Вы проиграли.")
                        bot.send_message(call.message.chat.id, "To start new game send /start")
                    elif not vacant_fields: # снова проверяем на ничью
                        buttons, keyboard = build_buttons(buttons, keyboard)
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Игра окончена.", reply_markup=keyboard)
                        bot.send_message(call.message.chat.id, "Победила дружба.")
                        bot.send_message(call.message.chat.id, "To start new game send /start")
                    else:
                        buttons, keyboard = build_buttons(buttons, keyboard)
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите свою сторону.", reply_markup=keyboard)
            assert 1 >= bot.edit_message_text.call_count # типа не хотим чтобы больше одного раза обновлялось сообщение
            bot.edit_message_text.call_count = 0 # сбрасываем счётчик
            print(field.as_string())



bot.polling(none_stop=True, interval=0)
