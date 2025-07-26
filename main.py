import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from parser import check_wash_machines
import json
import asyncio

with open('tg_token.txt') as f:
    TG_TOKEN = f.read()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Автоматический парсер

async def parser(app):
    while True:
        print('---------\nпарсинг\n---------')
        check_wash_machines()
        await asyncio.sleep(120) 

async def on_startup(app):
    app.create_task(parser(app))

# Старт бота

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '''Бот готов к работе'''
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def check_mach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ''
    check_wash_machines()
    with open('mach_status.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for i in range(1, 5):
            text += f'{i}: {data[str(i)]}\n'
        # text = json.dumps(data, ensure_ascii=False, indent=2)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

# Таймер на машинку

async def t_m(update, context):
    timer = context.args
    stop = False
    if len(timer) == 1 and (int(timer[0]) > 0 and int(timer[0]) < 5):
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Таймер запущен')
        while not stop:
            with open('mach_status.json', 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                stat = data[timer[0]]
            if stat == 'Свободно':
                stop = True
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f'{timer[0]} стиралка свободна')                
            print('Проверяю машинку', stat)
            await asyncio.sleep(60)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Введите номаер машинки в формате /timer_machine <номер машинки>')

async def timer_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asyncio.create_task(t_m(update, context))

# Уведомление если появится свободная стиралка

async def a_m(update, context):
    stop = False
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Сообщу, если какая-либо стиралка будет свободна')
    while not stop:
        with open('mach_status.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            stat = [data[str(i)] for i in range(1, 5)]
        if 'Свободно' in stat:
            stop = True
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Есть свободная стиралка')                
        await asyncio.sleep(60)

async def any_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asyncio.create_task(a_m(update, context))

# Работа бота

if __name__ == '__main__':
    application = ApplicationBuilder().token(TG_TOKEN).post_init(on_startup).build()

    start_handler = CommandHandler('start', start)
    check_mach_handler = CommandHandler('check_mach', check_mach)
    timer_machine_handler = CommandHandler('timer_machine', timer_machine)
    any_machine_handler = CommandHandler('any_machine', any_machine)

    application.add_handler(start_handler)
    application.add_handler(check_mach_handler)
    application.add_handler(timer_machine_handler)
    application.add_handler(any_machine_handler)

    application.run_polling()
