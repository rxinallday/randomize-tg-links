import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from gtts import gTTS
import io


def generate_captcha_text():
    return ''.join(random.choices("0123456789", k=5))


def generate_voice_captcha(captcha_text):
    spaced_text = ' '.join(captcha_text)

    tts = gTTS(text=spaced_text, lang='ru')

    mp3_byte_arr = io.BytesIO()
    tts.write_to_fp(mp3_byte_arr)
    mp3_byte_arr.seek(0)

    return mp3_byte_arr


async def generate_one_time_link(context: CallbackContext):
    chat_id = 'chat_id_ur_channel'
    invite_link = await context.bot.create_chat_invite_link(
        chat_id=chat_id,
        member_limit=1,
        expire_date=None
    )
    return invite_link.invite_link


async def start(update: Update, context: CallbackContext):
    captcha_text = generate_captcha_text()
    context.user_data['captcha'] = captcha_text

    voice_byte_arr = generate_voice_captcha(captcha_text)
    await update.message.reply_voice(voice=InputFile(voice_byte_arr, filename="captcha.mp3"),
                                     caption="Введите цифры, которые вы услышали.")


async def check_captcha(update: Update, context: CallbackContext):
    user_answer = update.message.text.strip()
    correct_answer = context.user_data.get('captcha')

    if user_answer == correct_answer:
        one_time_link = await generate_one_time_link(context)

        keyboard = [
            [InlineKeyboardButton("Перейти в канал", url=one_time_link)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Вы прошли капчу.", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Вы не прошли капчу.")


def main():
    token = 'bottoken'

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_captcha))

    application.run_polling()


if __name__ == '__main__':
    main()
