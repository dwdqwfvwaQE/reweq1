from aiogram import F, types
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from knopki import main_menu, req_kb, req_m_kb 
from states import RequisitesStates, GroupStates 
from save import save_req_txt, get_req
from ank.anke import handle_s_group_k, register_ank
from ank.manages.am import get_a_ids, get_anketa, f_anketa_admin, upd_ank, delete_anketa


def r_knopki_h(dp, bot, ADM):
    
    register_ank(dp) 
    
    @dp.message(F.text == "/anket" and F.from_user.id == ADM)
    async def list_ankety(msg: types.Message):
        if msg.chat.type != ChatType.PRIVATE:
            try:
                await msg.delete()
            except Exception:
                pass
            return

        anketa_ids = get_a_ids()
        
        if not anketa_ids:
            return await msg.answer("Активных анкет нет.")
            
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=str(ank_id), callback_data=f"open_anketa_{ank_id}")]
            for ank_id in anketa_ids
        ])
        
        await msg.answer("Активные заявки:", reply_markup=kb, parse_mode="Markdown")


    @dp.callback_query(lambda c: c.data.startswith("open_anketa_"))
    async def handle_op_ank(call: types.CallbackQuery):
        anketa_id = int(call.data.split('_')[-1])
        anketa_data = get_anketa(anketa_id)
        
        if not anketa_data:
            await call.answer("Анкета не найдена", show_alert=True)
            return await call.message.delete()
        
        management_kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Удалить", callback_data=f"anketa_delete_{anketa_id}"),
                InlineKeyboardButton(text="Закрыть", callback_data=f"anketa_close_{anketa_id}")
            ]
        ])

        formatted_text = f_anketa_admin(anketa_data)
        
        await call.message.edit_text(formatted_text, reply_markup=management_kb, parse_mode="Markdown")
        await call.answer()


    @dp.callback_query(lambda c: c.data.startswith("anketa_close_"))
    async def handle_cls_ank(call: types.CallbackQuery):
        anketa_id = int(call.data.split('_')[-1])
        
        if upd_ank (anketa_id, 'status', 'Закрыт'):
            updated_data = get_anketa(anketa_id)
            if updated_data:
                await call.message.edit_text(f_anketa_admin(updated_data), reply_markup=call.message.reply_markup, parse_mode="Markdown")
                await call.answer(f"Анкета №{anketa_id} закрыта.", show_alert=False)
            else:
                await call.answer("Ошибка при обновлении статуса.", show_alert=True)
        else:
            await call.answer("Анкета не найдена.", show_alert=True)


    @dp.callback_query(lambda c: c.data.startswith("anketa_delete_"))
    async def handle_del_anketa(call: types.CallbackQuery):
        anketa_id = int(call.data.split('_')[-1])
        
        if delete_anketa(anketa_id):
            await call.message.edit_text(f"Анкета №{anketa_id} удалена.", parse_mode="Markdown")
            await call.answer(f"Анкета №{anketa_id} удалена.", show_alert=False)
        else:
            await call.answer("Ошибка: Анкета не найдена.", show_alert=True)

    @dp.message(F.text == "💳 Реквизиты")
    async def open_req(msg: types.Message):
        user_id = msg.from_user.id
        req_txt = get_req(user_id)


        if req_txt:
            await msg.answer(
                f"Ваши сохраненные реквизиты:\n\n{req_txt}",
                reply_markup=req_m_kb,
                parse_mode="Markdown" 
            )
        else:
            await msg.answer("Выберите тип для заполнения:", reply_markup=req_kb)


    @dp.callback_query(F.data == "req_modify")
    async def modify_requisites(call: types.CallbackQuery, state: FSMContext):

        await call.answer("Выберите тип реквизитов", show_alert=False)

        await call.message.delete()
        
        await call.message.answer("Выберите тип реквизитов,", reply_markup=req_kb)
        await call.answer()


    @dp.callback_query(F.data == "req_back")
    async def back_from_requisites_view(call: types.CallbackQuery, state: FSMContext):
        await call.message.delete()
        await call.answer() 

    @dp.message(F.text == "📋 Продать группу")
    async def sell_group_handler(msg: types.Message, state: FSMContext):
        await handle_s_group_k(msg, state) 
    
    @dp.message(F.text == "🔙 Назад")
    async def go_back(msg: types.Message, state: FSMContext):
        await state.clear() 
        await msg.answer("Меню:", reply_markup=main_menu)


    @dp.message(F.text == "🔸 TON Кошелек")
    async def choose_ton(msg: types.Message, state: FSMContext):
        await state.clear() 
        await msg.answer("Введите адрес TON-кошелька (на английском):")
        await state.set_state(RequisitesStates.ton)

    @dp.message(F.text.in_({"🇷🇺 Карты РФ", "🇺🇦 Карты Украины"}))
    async def choose_cards(msg: types.Message, state: FSMContext):
        await state.clear() 
        country = "RU" if "РФ" in msg.text else "UA"
        await state.update_data(country=country)
        await msg.answer("Укажи название банка:")
        await state.set_state(RequisitesStates.bank)

    @dp.message(RequisitesStates.ton)
    async def process_ton(msg: types.Message, state: FSMContext):
        addr = msg.text.strip()
        await state.update_data(requisites=addr, country="TON", bank="-", card_number="-", phone="-")
        data = await state.get_data()
        path = save_req_txt(msg.from_user, data)
        await bot.send_document(ADM, FSInputFile(path), caption=f"Новые реквизиты от {msg.from_user.id}")
        await msg.answer("Реквизиты отправлены.", reply_markup=main_menu)
        await state.clear()
        
    @dp.message(RequisitesStates.bank)
    async def process_bank(msg: types.Message, state: FSMContext):
        bank = msg.text.strip()
        await state.update_data(bank=bank)
        await state.set_state(RequisitesStates.card_number)
        await msg.answer("Введите номер карты:")

    @dp.message(RequisitesStates.card_number)
    async def process_card(msg: types.Message, state: FSMContext):
        card = msg.text.strip()
        await state.update_data(card_number=card)
        await state.set_state(RequisitesStates.phone)
        await msg.answer("Введите номер телефона:")

    @dp.message(RequisitesStates.phone)
    async def process_phone(msg: types.Message, state: FSMContext):
        phone = msg.text.strip()
        await state.update_data(phone=phone)
        data = await state.get_data()
        path = save_req_txt(msg.from_user, data)
        await bot.send_document(ADM, FSInputFile(path), caption=f"Новые реквизиты от {msg.from_user.id}")
        await msg.answer("Реквизиты отправлены.", reply_markup=main_menu)
        await state.clear()