from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
import os
from states import GroupStates
from ank.text.txt import price
from knopki import main_menu 
from .manages.am import save_anketa, get_anketa, delete_anketa


load_dotenv()
ADM = os.getenv("ADM")
try:
    ADM_ID = int(ADM)
except (TypeError, ValueError):
    ADM_ID = 0

BOT_INSTANCE: Bot = None
DP_INSTANCE: Dispatcher = None


def set_ank_h(dispatcher: Dispatcher, bot_instance: Bot):
    global BOT_INSTANCE, DP_INSTANCE
    BOT_INSTANCE = bot_instance
    DP_INSTANCE = dispatcher


    @dispatcher.callback_query(lambda c: c.data.startswith("approve_"))
    async def approve(call: CallbackQuery):
        anketa_id_str = call.data.split("_")[1]
        try:
            anketa_id = int(anketa_id_str)
        except ValueError:
            await call.answer("Ошибка ID анкеты.", show_alert=True)
            return

        anketa = get_anketa(anketa_id)
        if not anketa:
            await call.answer("Анкета не найдена или уже удалена.", show_alert=True)
            return

        user_id = anketa["user_id"]
        await call.message.edit_text(f"Принято. Анкета #{anketa_id}")

        try:
            await BOT_INSTANCE.send_message(
                user_id,
                "<blockquote>✅ Ваша анкета принята!\nОбязательно добавьте бота с АДМИН ПРАВАМИ в группу и мой аккаунт @DIPZEX.</blockquote>", parse_mode="HTML"
            )
        except Exception:
            await call.answer("Не удалось отправить сообщение пользователю.", show_alert=True)




    @dispatcher.callback_query(lambda c: c.data.startswith("reject_"))
    async def reject(call: CallbackQuery):
        anketa_id_str = call.data.split("_")[1]
        try:
            anketa_id = int(anketa_id_str)
        except ValueError:
            await call.answer("Ошибка ID анкеты.", show_alert=True)
            return

        anketa = get_anketa(anketa_id)
        if not anketa:
            await call.answer("Анкета не найдена или уже удалена.", show_alert=True)
            return

        user_id = anketa["user_id"]
        await call.message.edit_text(f"Отклонено. Анкета #{anketa_id}")


        delete_anketa(anketa_id)

        try:
            await BOT_INSTANCE.send_message(user_id, "<blockquote>❌ Ваша анкета отклонена. Попробуйте позже.</blockquote>", parse_mode="HTML")
        except Exception:
            await call.answer("Не удалось отправить сообщение пользователю.", show_alert=True)


async def handle_s_group_k(msg: types.Message, state: FSMContext):
    await msg.answer(price, parse_mode="HTML") 
    await state.set_state(GroupStates.waiting_for_anketa)


async def process_anketa(msg: types.Message, state: FSMContext): 
    
    anketa_text = msg.text
    user_id = msg.from_user.id
    
    anketa_data = save_anketa(
        user_id=user_id,
        user_name=msg.from_user.username or msg.from_user.full_name,
        anketa_text=anketa_text
    )
    anketa_id = anketa_data['id']
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
 
            InlineKeyboardButton(text="✅", callback_data=f"approve_{anketa_id}"),
            InlineKeyboardButton(text="❌", callback_data=f"reject_{anketa_id}")
        ],
    ])
    admin_message = (
        f"Заявка\n"
        f"Номер анкеты: **{anketa_id}**\n"
        f"От: @{msg.from_user.username or user_id}\n\n"
        f"**Текст анкеты:**\n{anketa_text}"
    )
    await BOT_INSTANCE.send_message(ADM_ID, admin_message, reply_markup=kb, parse_mode="Markdown")
    
    await msg.answer("Анкета отправлена!.", reply_markup=main_menu)
    await state.clear()


def register_ank(dp):

    dp.message.register(process_anketa, GroupStates.waiting_for_anketa)
