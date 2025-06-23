from aiogram.fsm.state import StatesGroup, State

class AddProxy(StatesGroup):
    wait_value = State()

class AddTxtProxy(StatesGroup):
    wait_value = State()

class AddConvProxy(StatesGroup):
    wait_value = State()

class AddTxtConvProxy(StatesGroup):
    wait_value = State()

class ManageUser(StatesGroup):
    wait_value = State()

class ManageGroup(StatesGroup):
    wait_value = State()

class AddGroupByID(StatesGroup):
    wait_value = State()

class DeleteGroupByID(StatesGroup):
    wait_value = State()

class CalcWhatsApp(StatesGroup):
    wait_value = State()

class CalcTelegram(StatesGroup):
    wait_value = State()

class AddPhones(StatesGroup):
    wait_value = State()

class AddText(StatesGroup):
    wait_value = State()

class EditText(StatesGroup):
    wait_value = State()

class EditLimitCount(StatesGroup):
    wait_value = State()

class AllEditLimitCount(StatesGroup):
    wait_value = State()

class CalcWhatsApp2(StatesGroup):
    wait_value = State()

class CalcTelegram2(StatesGroup):
    wait_value = State()

class AddPhone(StatesGroup):
    wait_value = State()

class AddPhones(StatesGroup):
    wait_value = State()

class AddPhoneTg(StatesGroup):
    wait_value = State()

class AddPhonesTg(StatesGroup):
    wait_value = State()

class SearchPhone(StatesGroup):
    wait_value = State()

class PhoneSearch(StatesGroup):
    wait_value = State()

class UserIdSearch(StatesGroup):
    wait_value = State()

class CustomMinutes(StatesGroup):
    wait_value = State()

class EditUserCalcAmount(StatesGroup):
    wait_value = State()

class EditUserRefPercent(StatesGroup):
    wait_value = State()

class EditUserBalance(StatesGroup):
    wait_value = State()

class EditUserRefBalance(StatesGroup):
    wait_value = State()

class EditGroupCalcAmount(StatesGroup):
    wait_value = State()

class SetCalcAmount(StatesGroup):
    wait_value = State()

class SetCalcAmountGroup(StatesGroup):
    wait_value = State()

class SetMainCalcAmount(StatesGroup):
    wait_value = State()

class SetNewValue(StatesGroup):
    wait_value = State()

class AddExceptions(StatesGroup):
    wait_value = State()

class OtlegaAdd(StatesGroup):
    wait_value = State()

class OtlegaGetTdata(StatesGroup):
    wait_value = State()

class OtlegaEditAccountsCount(StatesGroup):
    wait_value = State()

class DepositBalance(StatesGroup):
    wait_value = State()

class DepositBalanceCryptoBot(StatesGroup):
    wait_value = State()

class UnloadAccounts(StatesGroup):
    wait_value = State()

class WithdrawClient(StatesGroup):
    wait_value = State()

class SendAllDrops(StatesGroup):
    wait_value = State()

class SendAllClients(StatesGroup):
    wait_value = State()

class CountBuy(StatesGroup):
    wait_value = State()
