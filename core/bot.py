import logging

import telebot
from django.utils import timezone
from telebot import types

from core.models import Program, ProgramType, Product, Property, Category

# bot = telebot.TeleBot('8183114713:AAG_m1zbHCQMyITMIvVETYELzbyCJmYKH6o')
bot = telebot.TeleBot('7652258523:AAEm6V-2-2Evqvconn5FWX8wi90N7MbEBvA')
articles = []
user_states = {}  # Словарь для хранения состояний пользователей


def set_user_state(user_id, state):
    user_states[user_id] = state


def get_user_state(user_id):
    return user_states.get(user_id, 'main_menu')


# Укажите имя канала
CHANNEL_USERNAME = '@volkov_cosmetic'  # Замените на имя вашего канала


def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        print(f"Проверка подписки для пользователя {user_id}: {status}")
        return status in ['creator', 'administrator', 'member', 'left']
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False


def send_subscription_prompt(user_id):
    markup = types.InlineKeyboardMarkup()
    btn_subscribe = types.InlineKeyboardButton(text='Подписаться на канал',
                                               url=f'https://t.me/{CHANNEL_USERNAME.lstrip("@")}')
    btn_check = types.InlineKeyboardButton(text='Я подписался',
                                           callback_data='check_subscription')
    markup.add(btn_subscribe)
    markup.add(btn_check)
    bot.send_message(user_id,
                     "Чтобы пользоваться ботом, пожалуйста, подпишитесь на наш канал.",
                     reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data == 'check_subscription')
def check_subscription(call):
    user_id = call.from_user.id
    print(f"Проверка подписки для пользователя {user_id}")
    try:
        if is_subscribed(user_id):
            print(f"Пользователь {user_id} подписан.")
            bot.answer_callback_query(call.id, "Спасибо за подписку!")
            show_main_menu(call.message)
            bot.delete_message(chat_id=user_id,
                               message_id=call.message.message_id)
        else:
            print(f"Пользователь {user_id} не подписан.")
            bot.answer_callback_query(call.id, "Вы ещё не подписаны на канал.")
    except Exception as e:
        print(f"Ошибка при проверке подписки для {user_id}: {e}")
        bot.answer_callback_query(call.id,
                                  "Произошла ошибка. Попробуйте снова.")


def subscription_required(func):
    def wrapper(message):
        user_id = message.chat.id
        if is_subscribed(user_id):
            return func(message)
        else:
            send_subscription_prompt(user_id)

    return wrapper


@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.chat.id
    if is_subscribed(user_id):
        show_main_menu(message)
    else:
        send_subscription_prompt(user_id)


def show_main_menu(message):
    # Извлекаем текст сообщения
    # Извлекаем параметры из команды /start
    user_id = message.chat.id
    set_user_state(user_id, 'main_menu')
    command_text = message.text.strip()
    if len(command_text.split()) > 1:
        params = command_text.split()[1]  # Получаем параметры после /start
        article_numbers = params.split('-')  # Разделяем артикулы по тире
        for article in article_numbers:
            articles.append(article)

        logging.info(f"Получены артикулы: {article_numbers}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Сформировать программу ухода за лицом")
    btn2 = types.KeyboardButton("Получить утреннюю программу")
    btn3 = types.KeyboardButton("Получить вечернюю программу")
    btn4 = types.KeyboardButton("Редактировать программу")
    btn5 = types.KeyboardButton("Консультация с косметологом")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id,
                     f"Привет, {message.from_user.first_name}! "
                     f"Добро пожаловать в бот для "
                     f"программы ухода за вашим лицом! "
                     f"Сформируйте программу для ухода за лицом",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Назад")
@subscription_required
def go_back(message):
    user_id = message.chat.id
    current_state = get_user_state(user_id)

    if current_state == 'editing_program':
        # Если пользователь находится в меню редактирования программы, возвращаем его в главное меню
        set_user_state(user_id, 'main_menu')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Получить утреннюю программу")
        btn2 = types.KeyboardButton("Получить вечернюю программу")
        btn3 = types.KeyboardButton("Редактировать программу")
        btn4 = types.KeyboardButton("Консультация с косметологом")
        markup.add(btn1, btn2)
        markup.add(btn3, btn4)
        bot.send_message(user_id, "Вы вернулись в главное меню.",
                         reply_markup=markup)

    elif current_state == 'adding_product' or current_state == 'deleting_product':
        # Возвращаемся в меню редактирования программы
        set_user_state(user_id, 'editing_program')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить продукт")
        btn2 = types.KeyboardButton("Удалить продукт")
        btn3 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3)
        bot.send_message(user_id,
                         "Вы вернулись в меню редактирования программы.",
                         reply_markup=markup)

    else:
        # По умолчанию возвращаем в главное меню
        set_user_state(user_id, 'main_menu')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Получить утреннюю программу")
        btn2 = types.KeyboardButton("Получить вечернюю программу")
        btn3 = types.KeyboardButton("Редактировать программу")
        btn4 = types.KeyboardButton("Консультация с косметологом")
        markup.add(btn1, btn2)
        markup.add(btn3, btn4)
        bot.send_message(user_id, "Вы вернулись в главное меню.",
                         reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.text == "Получить утреннюю программу")
@subscription_required
def send_morning_program(message):
    user_id = message.chat.id
    morning_program = Program.objects.filter(user_id=user_id,
                                             program_type__name="Утренняя программа").first()
    if morning_program and morning_program.products.exists():
        send_program_to_bot(user_id, morning_program.products.all(),
                            "Утренняя")
    else:
        bot.send_message(user_id,
                         "У вас нет сохранённой утренней программы. Пожалуйста, создайте её или добавьте продукты.")


@bot.message_handler(
    func=lambda message: message.text == "Получить вечернюю программу")
@subscription_required
def send_evening_program(message):
    user_id = message.chat.id
    evening_program = Program.objects.filter(user_id=user_id,
                                             program_type__name="Вечерняя программа").first()
    if evening_program and evening_program.products.exists():
        send_program_to_bot(user_id, evening_program.products.all(),
                            "Вечерняя")
    else:
        bot.send_message(user_id,
                         "У вас нет сохранённой вечерней программы. Пожалуйста, создайте её или добавьте продукты.")


@bot.message_handler(
    func=lambda message: message.text == "Консультация с косметологом")
@subscription_required
def start_consultation(message):
    # Замените 'cosmetologist_username' на реальный username косметолога или ссылку на чат
    cosmetologist_username = 'cosmetologist_username'  # Например, 'cosmetologist_bot' или 'cosmetologist_channel'

    # Отправляем сообщение с ссылкой на чат косметолога
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="Перейти к косметологу",
                                     url=f"https://t.me/{cosmetologist_username}")
    markup.add(btn)
    bot.send_message(message.chat.id,
                     "Нажмите на кнопку ниже, чтобы связаться с косметологом:",
                     reply_markup=markup)


@bot.message_handler(
    func=lambda
            message: message.text == "Сформировать программу ухода за лицом")
def func(message):
    user_id = message.chat.id
    # Проверяем, существует ли программа для данного пользователя
    existing_program = Program.objects.filter(
        user_id=user_id).exists()
    if existing_program:
        # Если программа уже существует, отправляем сообщение
        bot.send_message(message.chat.id,
                         text="Ваша программа уже сформирована!")
    else:
        # Логика для создания программы
        bot.send_message(message.chat.id,
                         text="Программа сформирована")
        create_programm(message)


# Словарь для хранения временных данных пользователей
user_data = {}


@bot.message_handler(
    func=lambda message: message.text == "Редактировать программу")
@subscription_required
def edit_program(message):
    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Добавить продукт")
    btn2 = types.KeyboardButton("Удалить продукт")
    btn3 = types.KeyboardButton("Назад")
    markup.add(btn1, btn2, btn3)
    bot.send_message(user_id,
                     "Выберите действие для редактирования программы:",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Добавить продукт")
def add_product_step1(message):
    user_id = message.chat.id
    set_user_state(user_id, 'adding_product_step1')

    # Получаем список категорий
    categories = Category.objects.all()
    if categories.exists():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                           one_time_keyboard=True)
        for category in categories:
            markup.add(types.KeyboardButton(category.name))
        markup.add(types.KeyboardButton("Назад"))
        msg = bot.send_message(user_id, "Выберите категорию продукта:",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, add_product_step2)
    else:
        bot.send_message(user_id,
                         "Категорий пока нет. Пожалуйста, добавьте категории в систему.")
        edit_program(message)


def add_product_step2(message):
    user_id = message.chat.id
    category_name = message.text.strip()

    if category_name == "Назад":
        edit_program(message)
        return

    category = Category.objects.filter(name=category_name).first()
    if not category:
        bot.send_message(user_id,
                         "Категория не найдена. Пожалуйста, выберите категорию из списка.")
        add_product_step1(message)
        return

    user_data[user_id] = {'category': category}
    set_user_state(user_id, 'adding_product_step2')

    # Получаем продукты из выбранной категории
    products = Product.objects.filter(category=category)
    if products.exists():
        # Предлагаем выбрать продукт
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                           one_time_keyboard=True)
        for product in products:
            markup.add(types.KeyboardButton(
                f"{product.name} (Артикул: {product.article_number})"))
        markup.add(types.KeyboardButton("Назад"))
        msg = bot.send_message(user_id, "Выберите продукт из категории:",
                               reply_markup=markup)
        user_data[user_id]['products_list'] = list(products)
        bot.register_next_step_handler(msg, add_product_step3)
    else:
        bot.send_message(user_id, "В этой категории пока нет продуктов.")
        add_product_step1(message)


def add_product_step3(message):
    user_id = message.chat.id
    product_choice = message.text.strip()

    if product_choice == "Назад":
        add_product_step1(message)
        return

    selected_product = None
    for product in user_data[user_id]['products_list']:
        product_display_name = f"{product.name} (Артикул: {product.article_number})"
        if product_choice == product_display_name:
            selected_product = product
            break

    if not selected_product:
        bot.send_message(user_id, "Пожалуйста, выберите продукт из списка.")
        add_product_step2(message)
        return

    # Сохраняем выбранный продукт
    user_data[user_id]['product'] = selected_product

    # Добавляем продукт в соответствующие программы
    add_product_to_programs(user_id, selected_product)

    # Очищаем временные данные пользователя
    user_data.pop(user_id, None)
    set_user_state(user_id, 'editing_program')

    # Возвращаемся в меню редактирования программы
    edit_program(message)


def add_product_to_programs(user_id, product):
    # Получаем все программы пользователя
    programs = Program.objects.filter(user_id=user_id)

    # Если программ нет, создаём их
    if not programs.exists():
        morning_type = ProgramType.objects.get(name="Утренняя программа")
        evening_type = ProgramType.objects.get(name="Вечерняя программа")
        Program.objects.create(user_id=user_id, program_type=morning_type)
        Program.objects.create(user_id=user_id, program_type=evening_type)
        programs = Program.objects.filter(user_id=user_id)

    # Получаем программы, связанные со свойствами продукта
    property_program_types = ProgramType.objects.filter(
        properties__in=product.properties.all()).distinct()

    if not property_program_types.exists():
        bot.send_message(user_id,
                         f"Продукт '{product.name}' не связан ни с одной программой по своим свойствам.")
        return

    for program_type in property_program_types:
        program = Program.objects.get(user_id=user_id,
                                      program_type=program_type)
        if program.products.filter(id=product.id).exists():
            bot.send_message(user_id,
                             f"Продукт '{product.name}' уже добавлен в {program_type.name.lower()} программу.")
        else:
            program.products.add(product)
            bot.send_message(user_id,
                             f"Продукт '{product.name}' успешно добавлен в {program_type.name.lower()} программу.")


@bot.message_handler(func=lambda message: message.text == "Удалить продукт")
@subscription_required
def delete_product_step1(message):
    user_id = message.chat.id
    set_user_state(user_id, 'deleting_product')
    # Предлагаем выбрать программу
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                       one_time_keyboard=True)
    btn1 = types.KeyboardButton("Утренняя программа")
    btn2 = types.KeyboardButton("Вечерняя программа")
    btn3 = types.KeyboardButton("Отмена")
    markup.add(btn1, btn2, btn3)
    msg = bot.send_message(user_id,
                           "Из какой программы вы хотите удалить продукт?",
                           reply_markup=markup)
    bot.register_next_step_handler(msg, delete_product_step2)


def delete_product_step2(message):
    user_id = message.chat.id
    if message.text == "Назад":
        go_back(message)
        return
    program_choice = message.text.strip()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Добавить продукт")
    btn2 = types.KeyboardButton("Удалить продукт")
    btn3 = types.KeyboardButton("Назад")
    markup.add(btn1, btn2, btn3)

    if program_choice == "Отмена":
        bot.send_message(user_id, "Операция отменена.")
        return

    if program_choice not in ["Утренняя программа", "Вечерняя программа"]:
        bot.send_message(user_id,
                         "Пожалуйста, выберите программу из предложенных вариантов.")
        return

    # Сохраняем выбор программы
    user_data[user_id] = {'program_choice': program_choice}

    # Получаем соответствующую программу пользователя
    program = Program.objects.filter(user_id=user_id,
                                     program_type__name=program_choice).first()

    if not program or not program.products.exists():
        bot.send_message(user_id,
                         f"У вас нет продуктов в {program_choice.lower()}.",
                         reply_markup=markup)
        return

    # Формируем список продуктов для выбора
    products = program.products.all()
    product_list = "\n".join(
        [f"{idx + 1}. {prod.name} (Артикул: {prod.article_number})" for
         idx, prod in enumerate(products)])
    msg = bot.send_message(user_id,
                           f"Ваши продукты в {program_choice.lower()}:\n{product_list}\n\nВведите номер продукта, который хотите удалить:")
    bot.register_next_step_handler(msg, delete_product_step3, program,
                                   products)


def delete_product_step3(message, program, products):
    user_id = message.chat.id
    choice = message.text.strip()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Добавить продукт")
    btn2 = types.KeyboardButton("Удалить продукт")
    btn3 = types.KeyboardButton("Назад")
    markup.add(btn1, btn2, btn3)
    try:
        product_index = int(choice) - 1
        if product_index < 0 or product_index >= len(products):
            raise ValueError

        product_to_delete = products[product_index]

        # Удаляем продукт из программы
        program.products.remove(product_to_delete)
        bot.send_message(user_id,
                         f"Продукт '{product_to_delete.name}' удален из {program.program_type.name.lower()}.")

        # Проверяем, остались ли продукты в программе
        if not program.products.exists():
            bot.send_message(user_id,
                             f"В вашей {program.program_type.name.lower()} больше нет продуктов.",
                             reply_markup=markup)

    except ValueError:
        bot.send_message(user_id,
                         "Пожалуйста, введите корректный номер продукта.")
    # Возвращаем пользователя в меню редактирования программы
    bot.send_message(user_id,
                     "Вы вернулись в меню редактирования программы.",
                     reply_markup=markup)


def send_program_to_bot(chat_id, program, program_name):
    """
    Отправляет пользователю программу (утреннюю или вечернюю) через бота.
    """
    message = f"{program_name} программа ухода:\n"

    # Проходим по каждому продукту в программе
    for idx, product in enumerate(program, 1):
        message += f"{idx}.(Свойства: {', '.join([prop.name for prop in product.properties.all()])}) - {product.name}\n"

    # Отправляем сообщение пользователю
    bot.send_message(chat_id=chat_id, text=message)


def create_programm(message):
    """Функция для создания программ пользователя"""
    user_id = message.chat.id
    logging.info(articles)
    # Получаем список артикулов с сайта (предположим, передали с сайта)
    article_numbers = articles  # Пример данных

    # Получаем утренний и вечерний типы программ
    morning_type = ProgramType.objects.get(name="Утренняя программа")
    evening_type = ProgramType.objects.get(name="Вечерняя программа")
    # Получаем утреннюю программу
    morning_program = get_program_for_user(article_numbers,
                                           program_type_name="Утренняя программа")

    # Получаем вечернюю программу
    evening_program = get_program_for_user(article_numbers,
                                           program_type_name="Вечерняя программа")

    # Фильтруем продукты по артикулу и типу программы (утренняя)
    morning_properties = Property.objects.filter(
        program_types=morning_type)

    morning_products = Product.objects.filter(
        article_number__in=article_numbers,
        properties__in=morning_properties
    ).order_by('properties__order')

    # Фильтруем продукты для вечерней программы
    evening_properties = Property.objects.filter(
        program_types=evening_type)

    evening_products = Product.objects.filter(
        article_number__in=article_numbers,
        properties__in=evening_properties
    ).order_by('properties__order')

    # Создание программы для утреннего ухода
    morning_program_in_bd = Program.objects.create(user_id=user_id,
                                                   program_type=morning_type)
    morning_program_in_bd.products.add(*morning_products)
    morning_program_in_bd.save()

    # Создание программы для вечернего ухода
    evening_program_bd = Program.objects.create(user_id=user_id,
                                                program_type=evening_type)
    evening_program_bd.products.add(*evening_products)
    evening_program_bd.save()
    articles.clear()


# Функция для отправки уведомлений
def send_routine_notification():
    now = timezone.now().time()
    current_date = timezone.now().date()

    # Ищем программы, которые нужно отправить
    programs = Program.objects.filter(
        program_type__time_to_send=now
    )

    for program in programs:
        # Вычисляем, нужно ли сегодня отправлять продукт с учетом частоты
        products_to_send = []
        for product in program.products.all():
            last_usage_day = (current_date - program.start_date).days
            if last_usage_day % product.frequency_of_use == 0:
                products_to_send.append(product.name)

        # Отправляем уведомление пользователю
        if products_to_send:
            routine_message = f"Сегодняшняя программа: {', '.join(products_to_send)}"
            bot.send_message(program.user_id, routine_message)


# Команда для отключения уведомлений
@bot.message_handler(commands=['stop'])
def stop_notifications(message):
    # Логика для отключения уведомлений (например, удаление программ из БД)
    Program.objects.filter(user_id=message.chat.id).delete()
    bot.send_message(message.chat.id, "Программа удалена.")


# Планировщик, который каждые 24 часа будет запускать отправку уведомлений
def schedule_notifications():
    from apscheduler.schedulers.blocking import BlockingScheduler
    scheduler = BlockingScheduler()

    # Утреннее уведомление в 8:00
    scheduler.add_job(send_routine_notification, 'cron', hour=8,
                      minute=0)

    # Вечернее уведомление в 18:00
    scheduler.add_job(send_routine_notification, 'cron', hour=18,
                      minute=0)

    scheduler.start()


def get_program_for_user(article_numbers, program_type_name):
    """
    Возвращает отсортированный список продуктов для определённой программы ухода (утренняя или вечерняя).
    """
    # Находим соответствующий тип программы (например, утренняя или вечерняя)
    program_type = ProgramType.objects.get(name=program_type_name)

    # Находим свойства, которые соответствуют данному типу программы
    properties_for_program = Property.objects.filter(
        program_types=program_type)

    # Находим продукты по артикулу, которые имеют эти свойства
    products = Product.objects.filter(
        article_number__in=article_numbers,
        properties__in=properties_for_program).distinct()

    # Сортируем продукты по полю 'order', которое теперь находится в модели Property
    sorted_products = products.order_by('properties__order')

    return sorted_products


# Запуск бота
def start_bot():
    bot.infinity_polling()
