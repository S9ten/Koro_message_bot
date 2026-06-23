import logging
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
from telegram import Message
from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler
import asyncio
import sqlite3
import db_session
from friends import Friend

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
TOKEN = ''
# reply_keyboard = [['/start', '/reg', '/about_session']]
buttons = [['войти в сессию', 'выйти из сессии']]
markup = ReplyKeyboardMarkup(buttons)
session = []


# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.
async def start(update, context):
    await update.message.reply_text('Привет', reply_markup=markup)


# async def button(update, context):
#     query = update.callback_query
#     query.answer()
#     if query.data == 'button1':
#         await query.edit_message_text(text="Вы нажали на кнопку 1!")
#     elif query.data == 'button2':
#         await query.edit_message_text(text="Вы нажали на кнопку 2!")
async def reg(update, context):
    db_sess = db_session.create_session()
    objects = db_sess.query(Friend).all()
    for i in objects:
        if str(update.message.from_user.id) in i.list_id:
            await update.message.reply_text(
                f"вы уже в сессии",
                reply_markup=markup)
            break
    else:
        if not objects:
            sess = Friend()
            sess.list_id = f"{update.message.from_user.id}"
            db_sess.add(sess)
            await update.message.reply_text(
                f"вы в сессии",
                reply_markup=markup)

            await context.bot.send_message(chat_id=update.message.from_user.id,
                                           text='дождитесь собеседника')
            db_sess.commit()
            return
        else:
            for i in objects:
                if len(i.list_id.split(', ')) == 1:
                    await context.bot.send_message(chat_id=i.list_id,
                                                   text='собеседник присоединился')
                    i.list_id = i.list_id + f', {update.message.from_user.id}'

                    await update.message.reply_text(
                        f"вы в сессии",
                        reply_markup=markup)
                    await context.bot.send_message(chat_id=update.message.from_user.id,
                                                   text='собеседник присоединился')
                    break
            else:
                sess = Friend()
                sess.list_id = f"{update.message.from_user.id}"
                db_sess.add(sess)
        db_sess.commit()


# async def echo(update, context):
#     if update.effective_user.id in allowed_users:
#         context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
#     else:
#         context.bot.send_message(chat_id=update.effective_chat.id, text="Вы не авторизованы для общения с ботом.")
async def about_session(update, context):
    await update.message.reply_text(f"в сессии {session}",
                                    reply_markup=markup)


async def leave_session(update, context):
    db_sess = db_session.create_session()
    objects = db_sess.query(Friend).all()
    for i in objects:
        if f'{update.effective_user.id}' in i.list_id:
            s = i.list_id.split(', ')
            s.remove(f'{update.effective_user.id}')
            i.list_id = ', '.join(s)
            break
    if session:
        await context.bot.send_message(chat_id=session[0],
                                       text='собеседник покинул чат')
    db_sess.commit()
    clear_db()
    await update.message.reply_text(
        f"вы вышли из сессии",
        reply_markup=markup)


async def echo(update, context):
    db_sess = db_session.create_session()
    objects = db_sess.query(Friend).all()

    for i in objects:
        if f'{update.effective_user.id}' in i.list_id:
            s = i.list_id.split(', ')
            s.remove(f'{update.effective_user.id}')
            break
    else:
        await update.message.reply_text(
            f"вы не в сессии",
            reply_markup=markup)
        return
    if s:
        await context.bot.send_message(chat_id=s[0],
                                       text=update.message.text)
    else:
        await update.message.reply_text(
            f"дождитесь собеседника",
            reply_markup=markup)


def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.Regex('войти в сессию'), reg))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Regex('выйти из сессии'), leave_session))
    application.add_handler(MessageHandler(filters.TEXT, echo))
    # Запускаем приложение.
    application.run_polling()


def clear_db(r=False):
    db_sess = db_session.create_session()
    objects = db_sess.query(Friend).all()
    if r:
        for i in objects:
            db_sess.delete(i)
    else:
        for i in objects:
            if not str(i.list_id):
                db_sess.delete(i)
    db_sess.commit()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    db_session.global_init("db/sessions.db")
    clear_db(r=True)
    main()
