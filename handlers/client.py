from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import exceptions as exc
from whale_checker_bot import create_bot
from keyboards import kb_client, urlkb, wlistkb
from data import sqlite_db
from ether import ether_cl
import emoji
import asyncio


bot = create_bot.bot


wallet_for_check = ''


class FSMUser(StatesGroup):
    wallet = State()
    description = State()
    balance_wallet = State()
    token_address = State()


async def commands_start(message : types.Message):
    try:
        await bot.send_message(message.from_user.id, 'Greetings my dear friend!\n'
                                                     'I will help you track transactions from whale wallets and other important bumps in web3.)\n'
                                                     "Let's get started!",
                                                     reply_markup=kb_client)
        await message.delete()
    except:
        await message.reply("Communication with the bot is only possible via private messages!\n"
                            "Write to him to continue:\nhttps://t.me/marketmakers_stalker_bot")


async def transact_stalk_start(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Stalker mode has started...")
    while True:
        try:
            wallets = await sqlite_db.sql_for_transactions(callback_query.from_user.id)
            if not wallets:
                await bot.send_message(callback_query.from_user.id, 'Something wrong\n'
                                                                    'Please check your watchlist\n'
                                                                    "Maybe it's empty or wallets is not real")
                break
            for wallet in wallets:
                checksum_wallet = ether_cl.w3.to_checksum_address(wallet[0])
                block = ether_cl.w3.eth.get_block('latest')
                if block and block.transactions:
                    for transaction in block.transactions:
                        tx_hash = transaction.hex()
                        tx = ether_cl.w3.eth.get_transaction(tx_hash)
                        if tx.to != None:
                            if tx.to == checksum_wallet:
                                await bot.send_message(callback_query.from_user.id,
                                                       f'New transactions occured for {wallet[1]}!\n'
                                                       f'\nfrom: {tx["from"]}\n'
                                                       f'value: {ether_cl.w3.from_wei(tx["value"], "ether")}')

        except:
            await bot.send_message(callback_query.from_user.id, 'Something wrong\n'
                                                                'Please check your watchlist\n'
                                                                "Maybe it's empty or wallets is not real")
            break
        await asyncio.sleep(10)


async def send_notifications_transactions(callback_query: types.CallbackQuery):
    loop = asyncio.get_event_loop()
    loop.create_task(transact_stalk_start(callback_query))

        

async def get_wallet_balance(message: types.Message):
    await FSMUser.balance_wallet.set()
    await message.reply('Send me the wallet address.')


async def show_wallet_balance(message: types.Message, state: FSMContext):
    try:
        global wallet_for_check
        wallet_for_check = message.text
        await message.reply(ether_cl.get_wallet_balance(wallet_for_check),
                            reply_markup=InlineKeyboardMarkup().\
                            add(InlineKeyboardButton(f'{emoji.emojize("➕")}Add token contract{emoji.emojize("➕")}', callback_data=f'Contract {wallet_for_check}')))
        await state.finish()
    except (TypeError, AssertionError) as ex:
        await message.reply('This address does not exist on the ETH network(')
        await state.finish()


async def add_token_address(callback_query: types.CallbackQuery):
    await FSMUser.token_address.set()
    await callback_query.message.answer('Send me the token address.')
    await callback_query.answer()


async def show_token_balance(message: types.Message, state: FSMContext):
    try:
        token_address = message.text
        await message.reply(ether_cl.get_balance_with_token(wallet_for_check, token_address))
        await state.finish()
    except (TypeError, AssertionError) as ex:
        await message.reply('This address does not exist on the ERC-20 network(')
        await state.finish()


async def cm_start(callback_query: types.CallbackQuery):
    await FSMUser.wallet.set()
    await callback_query.message.answer('Send me the wallet address.')
    await callback_query.answer()


async def load_wallet(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
        data['wallet'] = message.text
    await FSMUser.next()
    await message.reply('Add a description to this wallet.\n(20 characters max)')


async def load_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await bot.send_message(message.from_user.id, 'Wallet has been added')
    await sqlite_db.sql_add_command(state)
    await state.finish()


async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return    
    await message.reply('Ok')
    await state.finish()


async def check_watchlist(message: types.Message, state: FSMContext):
    try:
        read = await sqlite_db.sql_read(message)
        res = ''
        for wal in read:
            res += f'{wal[1]} : {wal[2]}\n'
        await message.answer(res, reply_markup=wlistkb)
        await state.finish()
    except exc.MessageTextIsEmpty as ex:
        await message.reply('Your watchlist is empty', reply_markup=wlistkb)


async def delete_item(callback_query: types.CallbackQuery, state: FSMContext):
    read = await sqlite_db.sql_read_for_del(callback_query)
    for wal in read:
        await callback_query.message.answer(f'{wal[1]} : {wal[2]}',
                                            reply_markup=InlineKeyboardMarkup().\
                                            add(InlineKeyboardButton(f'Delete', callback_data=f'del {wal[2]}')))
    await callback_query.answer()
    await state.finish()


async def del_callback_run(callback_query: types.CallbackQuery):
    try:
        await sqlite_db.sql_delete_command(callback_query.data.replace('del ', ''), callback_query.from_user.id)
        await callback_query.answer(text='Wallet has been deleted', show_alert=True)
    except exc.MessageError as ex:
        await callback_query.answer(text='Wallet already deleted', show_alert=True)


async def pay_respect_command(message: types.Message, state: FSMContext):
    await message.answer('Socials:', reply_markup=urlkb)
    await state.finish()


async def empty(message: types.Message):
    await message.answer('Bruh...')
    await message.delete()


def register_handlers_client(dp : Dispatcher):
    dp.register_message_handler(commands_start, commands=['start', 'help'])
    dp.register_message_handler(cancel_handler, commands='cancel', state='*')
    dp.register_message_handler(cancel_handler, lambda message: message.text == 'cancel', state='*')
    dp.register_message_handler(check_watchlist, lambda message: message.text == f'{emoji.emojize("📄")}My watchlist{emoji.emojize("📄")}', state='*')
    dp.register_callback_query_handler(delete_item, lambda query: query.data and query.data.startswith('Delete'), state='*')
    dp.register_callback_query_handler(del_callback_run, lambda query: query.data and query.data.startswith('del '))
    dp.register_message_handler(pay_respect_command, lambda message: message.text == f'{emoji.emojize("👍🏿")}Pay respect{emoji.emojize("👍🏿")}', state='*')
    dp.register_message_handler(get_wallet_balance, lambda message: message.text == f'{emoji.emojize("💲")}Check wallet balance{emoji.emojize("💲")}', state='*')
    dp.register_message_handler(show_wallet_balance, state=FSMUser.balance_wallet)
    dp.register_callback_query_handler(add_token_address, lambda query: query.data and query.data.startswith('Contract '), state='*')
    dp.register_message_handler(show_token_balance, state=FSMUser.token_address)
    dp.register_callback_query_handler(send_notifications_transactions, lambda query: query.data and query.data.startswith('Start'), state='*')
    dp.register_callback_query_handler(cm_start, lambda query: query.data and query.data.startswith('Add'), state=None)
    dp.register_message_handler(load_wallet, state=FSMUser.wallet)
    dp.register_message_handler(load_description, state=FSMUser.description)
    dp.register_message_handler(empty)