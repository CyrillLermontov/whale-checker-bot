from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import emoji


'''Main client's keyboard'''
kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton(f'{emoji.emojize("📄")}My watchlist{emoji.emojize("📄")}')
b2 = KeyboardButton(f'{emoji.emojize("👍🏿")}Pay respect{emoji.emojize("👍🏿")}')
b3 = KeyboardButton(f'{emoji.emojize("💲")}Check wallet balance{emoji.emojize("💲")}')
kb_client.add(b1).add(b3).add(b2)


'''Inline keyboard for actions with watchlist'''
wlistkb = InlineKeyboardMarkup(row_width=2)
wlistAdd = InlineKeyboardButton(text=f'{emoji.emojize("➕")}Add to watchlist{emoji.emojize("➕")}', callback_data='Add')
wlistDel = InlineKeyboardButton(text=f'{emoji.emojize("❌")}Delete from watchlist{emoji.emojize("❌")}', callback_data='Delete')
wlistStart = InlineKeyboardButton(text=f'{emoji.emojize("▶️")}Start stalkering{emoji.emojize("▶️")}', callback_data='Start')
wlistkb.add(wlistAdd).add(wlistDel).add(wlistStart)


'''Inline keyboard to pay respect)'''
urlkb = InlineKeyboardMarkup(row_width=2)
urlTwitter = InlineKeyboardButton(text='Twitter', url='https://twitter.com/itwasreallycool')
urlGit = InlineKeyboardButton(text='GitHub', url='https://github.com/CyrillLermontov')
urlkb.row(urlTwitter).row(urlGit)
