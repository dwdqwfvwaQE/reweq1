from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ChatMemberUpdated 
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
import asyncio
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties
import os
from knopki import main_menu 
from h_knopok.handlers import r_knopki_h
from save import save_user 
from ank.text.txt import price
from ank.anke import set_ank_h, handle_s_group_k, register_ank
from ank.manages.am import f_l_open_anketa, upd_ank, chat_anketa, p_open_anketa_id


load_dotenv()
TOKEN = os.getenv("TOKEN")
ADM_STR = os.getenv("ADM")
try:
    ADM = int(ADM_STR)
except (TypeError, ValueError):
    ADM = 0


bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    save_user(msg.from_user.id, msg.from_user.full_name)
    text = f"Привет, {msg.from_user.first_name}!\nПриветсвую тебя в моем боте по продаже старых групп, все инфа идет по кнопкам не забудь вводить реквизиты для получения оплаты"
    await msg.answer(text, reply_markup=main_menu)


@dp.my_chat_member()
async def added_to_group(event: ChatMemberUpdated):

    if event.new_chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
        

        chat_id = event.chat.id


        user_who_added_id = event.from_user.id
        
        anketa_data = chat_anketa(user_who_added_id, chat_id)
        
        if anketa_data:
            await bot.send_message(
                chat_id, 
                f"Группа успешно привязана к анкете №{anketa_data['id']}."
            )
        else:
            await bot.send_message(
                chat_id, 
                "Не найдено активной анкеты,"
            )

@dp.chat_member()
async def member_update(event: ChatMemberUpdated):
    user_id_new = event.new_chat_member.user.id
    new_status = event.new_chat_member.status
    chat_id = event.chat.id 
    

    if user_id_new == ADM and new_status == "creator":
        

        anketa_data = p_open_anketa_id(chat_id) 
        
        if anketa_data:
            anketa_id = anketa_data['id']
            

            if upd_ank(anketa_id, 'owner_status', 'Передана'):
                await bot.send_message(ADM,text=f"Овнерка успешно передана, №{anketa_id}.")

                await bot.send_message(anketa_data['user_id'], "Вам передали владельца группы, произведите оплату")
                
            else:
                print(f"Не удалось обновить статус овнерки для анкеты №{anketa_id}.")
        else:
             print(f"Не найдено открытых анкет для группы {chat_id}.")

async def main():
    set_ank_h(dp, bot)
    r_knopki_h(dp, bot, ADM)
    print("Up to Sky...")
    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
