import logging
import time

import telebot
from django.core.management.base import BaseCommand
from django.utils import timezone
from telebot import types

from core.models import Program, ProgramType, Product, Property

bot = telebot.TeleBot('8183114713:AAG_m1zbHCQMyITMIvVETYELzbyCJmYKH6o')

articles = []


# Приветствие при старте
@bot.message_handler(commands=['start'])
def start_command(message):
    # Извлекаем текст сообщения
    # Извлекаем параметры из команды /start
    command_text = message.text.strip()
    if len(command_text.split()) > 1:
        params = command_text.split()[1]  # Получаем параметры после /start
        article_numbers = params.split('-')  # Разделяем артикулы по тире
        for article in article_numbers:
            articles.append(article)

        logging.info(f"Получены артикулы: {article_numbers}")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(
            "Сформировать программу ухода за лицом")
        btn2 = types.KeyboardButton("Отключить уведомления!")
        btn3 = types.KeyboardButton("Удалить программу")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id,
                         "Привет,{0.first_name}! "
                         "Добро пожаловать в бот для "
                         "программы ухода за вашим лицом!".format(
                             message.from_user), reply_markup=markup)
        bot.send_message(message.chat.id,
                         f"Получены артикулы: {', '.join(article_numbers)} "
                         f"и по ним будет составлена программа ухода!")


@bot.message_handler(content_types=['text'])
def func(message):
    if (message.text == "Сформировать программу ухода за лицом"):
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
                             text="Программа формируется")
            create_programm(message)
    elif (message.text == "Отключить уведомления!"):
        bot.send_message(message.chat.id,
                         text="Уведомления с сайта отключены!")

    elif (message.text == "Удалить программу"):
        stop_notifications(message)

    elif message.text == "Что я могу?":
        bot.send_message(message.chat.id,
                         text="Поздороваться с читателями")

    elif (message.text == "Вернуться в главное меню"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("? Поздороваться")
        button2 = types.KeyboardButton("❓ Задать вопрос")
        markup.add(button1, button2)
        bot.send_message(message.chat.id,
                         text="Вы вернулись в главное меню",
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id,
                         text="На такую комманду я не запрограммировал..")


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
    print(articles)
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
    bot.send_message(user_id,
                     "Программа ухода составлена! Вы будете получать уведомления утром и вечером.")
    send_program_to_bot(user_id, morning_program, "Утренняя")
    time.sleep(3)
    send_program_to_bot(user_id, evening_program, "Вечерняя")


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
