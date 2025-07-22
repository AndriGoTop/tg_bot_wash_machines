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

async def parser(app):
    while True:
        print('---------\nпарсинг\n---------')
        check_wash_machines()
        await asyncio.sleep(120) 

async def on_startup(app):
    app.create_task(parser(app))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '''Это бот, который поможет следить за статусом стиральных машин
/check_mach -- Проверить статус машинок'''
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def check_mach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ''
    check_wash_machines()
    with open('mach_status.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        text = json.dumps(data, ensure_ascii=False, indent=2)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def t_m(update, context):
    timer = context.args
    if len(timer) == 1 and (int(timer[0]) > 0 and int(timer[0]) < 5):
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Таймер запущен')
        while True:
            with open('mach_status.json', 'r') as json_file:
                data = json.load(json_file)
                stat = data[timer[0]]
            if stat == 'Свободно':
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f'{timer[0]} стиралка свободна')                
            await asyncio.sleep(60)

async def timer_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asyncio.create_task(t_m(update, context))

if __name__ == '__main__':
    application = ApplicationBuilder().token(TG_TOKEN).post_init(on_startup).build()

    start_handler = CommandHandler('start', start)
    check_mach_handler = CommandHandler('check_mach', check_mach)
    timer_machine_handler = CommandHandler('timer_macine', timer_machine)

    application.add_handler(start_handler)
    application.add_handler(check_mach_handler)
    application.add_handler(timer_machine_handler)

    application.run_polling()
