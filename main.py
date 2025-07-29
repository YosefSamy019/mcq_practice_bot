import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
import database
import runtime_cache
import random
import time

bot = telebot.TeleBot(config.TELEBOT_TOKEN)

questions_list = []


@bot.message_handler(commands=['start'])
def start(message):
    msg = (
        "📚 *MCQ Practice Bot is Here!*\n\n"
        "Welcome! This bot allows you to practice multiple-choice questions (MCQs) in various subjects such as:\n"
        "- 🧠 General Knowledge\n"
        "- 💻 Programming\n"
        "- 🌍 Science & Geography\n"
        "- 🔢 Math\n\n"
        "🟢 To get started, type /quiz and begin answering.\n"
        "_Each correct answer gives +1 point. A wrong answer ends the game._\n\n"
        "Good luck and have fun! 🎯"
    )
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    runtime_cache.delete_user(message.from_user.id)


@bot.message_handler(commands=['quiz'])
def quiz(message):
    first = message.from_user.first_name or ""
    last = message.from_user.last_name or ""
    user_name = (first + " " + last).strip()

    msg = (
        f"👋 Welcome *{user_name}*!\n\n"
        "🧩 Each correct answer gives you *+1 point*.\n"
        "❌ One wrong answer ends the game.\n\n"
        "Let’s begin!"
    )

    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    cache_user = runtime_cache.create_new_user(message.from_user.id, None, None)
    _create_send_inline_keyboard(message, cache_user)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id

    if not runtime_cache.user_is_found(user_id):
        msg = "⚠️ *Your session was lost.*\nPlease type /start to begin again."
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
    else:
        runtime_cache_user = runtime_cache.get_user(user_id)

        try:
            ques_id, user_answer_id = map(int, call.data.split('-'))
            question = questions_list[ques_id]
            is_correct = user_answer_id == question.right_answer_index
        except Exception:
            bot.answer_callback_query(call.id, "Something went wrong.")
            return

        if is_correct:
            runtime_cache_user.points += 1
            _create_send_inline_keyboard(call.message, runtime_cache_user)
        else:
            _game_over(user_id, call.message, runtime_cache_user)


def _create_send_inline_keyboard(message, runtime_cache_user):
    global questions_list
    question_id = random.randint(0, len(questions_list) - 1)
    question = questions_list[question_id]

    msg = f"📝 {question.question.capitalize()}"

    keyboard = InlineKeyboardMarkup(row_width=1)
    for i, answer in enumerate(question.answers):
        callback_data = f"{question_id}-{i}"
        keyboard.add(InlineKeyboardButton(text=f"{chr(65 + i)}. {answer}", callback_data=callback_data))

    if runtime_cache_user.ques_message_id is None:
        q_msg = bot.send_message(message.chat.id, msg, reply_markup=keyboard)
    else:
        q_msg = bot.edit_message_text(msg, message.chat.id, runtime_cache_user.ques_message_id,
                                      reply_markup=keyboard)

    runtime_cache_user.last_active_time = time.time()
    runtime_cache_user.ques_message_id = q_msg.message_id
    runtime_cache_user.last_ques_id = question_id


def _game_over(user_id, message, runtime_cache_user):
    msg = f"⛔ *Game Over!*\n\nYour final score: *{runtime_cache_user.points}*"
    try:
        bot.edit_message_text(msg, message.chat.id,
                              runtime_cache_user.ques_message_id,
                              parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    runtime_cache.delete_user(user_id)


def main():
    global questions_list
    print('🔄 Loading questions...')
    questions_list = database.load_questions()
    print("✅ Bot is running...")
    bot.polling()


if __name__ == '__main__':
    main()
