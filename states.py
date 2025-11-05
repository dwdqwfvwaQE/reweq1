from aiogram.fsm.state import State, StatesGroup

class RequisitesStates(StatesGroup):
    ton = State()
    bank = State()
    card_number = State()
    phone = State()

class GroupStates(StatesGroup):
    waiting_for_anketa = State()