from random import SystemRandom
from string import ascii_letters, digits
from telegram.ext import CommandHandler
from threading import Thread
from time import sleep
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup, deleteMessage, delete_all_messages, update_all_messages, sendStatusMessage, sendLog, sendPrivate, sendtextlog, auto_delete
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.status_utils.clone_status import CloneStatus
from bot import dispatcher, LOGGER, STOP_DUPLICATE, download_dict, download_dict_lock, Interval, BOT_PM
from bot.helper.ext_utils.bot_utils import is_gdrive_link, is_gdtot_link, new_thread, is_appdrive_link
from bot.helper.mirror_utils.download_utils.direct_link_generator import gdtot
from bot.helper.ext_utils.parser import appdrive
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from bot.helper.telegram_helper.button_build import ButtonMaker

def _clone(message, bot, multi=0):
    if BOT_PM:
      try:
        msg1 = f'Added your Requested Link to Downloads'
        send = bot.sendMessage(message.from_user.id, text=msg1, )
        send.delete()
      except Exception as e:
        LOGGER.warning(e)
        bot_d = bot.get_me()
        b_uname = bot_d.username
        uname = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
        buttons = ButtonMaker()
        buttons.buildbutton("Start Me", f"http://t.me/{b_uname}")
        buttons.buildbutton("Updates Channel", "http://t.me/BaashaXclouD")
        reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
        message = sendMarkup(f"Hey Bro {uname}👋,\n\n<b>I Found That You Haven't Started Me In PM Yet 😶</b>\n\nFrom Now on i Will links in PM Only 😇", bot, update, reply_markup=reply_markup)     
        return
    try:
        user = bot.get_chat_member("-1001762089232", message.from_user.id)
        LOGGER.error(user.status)
        if user.status not in ('member','creator','administrator'):
            buttons = ButtonMaker()
            buttons.buildbutton("Join Updates Channel", "https://t.me/BaashaXclouD")
            reply_markup = InlineKeyboardMarkup(buttons.build_menu(1))
            sendMarkup(f"<b>⚠️You Have Not Joined My Updates Channel</b>\n\n<b>Join Immediately to use the Bot.</b>", bot, update, reply_markup)
            return
    except:
        pass
    args = message.text.split(maxsplit=1)
    reply_to = message.reply_to_message
    uname = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
    uid= f"<a>{message.from_user.id}</a>"
    link = ''
    if len(args) > 1:
        link = args[1].strip()
        if link.isdigit():
            multi = int(link)
            link = ''
        elif message.from_user.username:
            tag = f"@{message.from_user.username}"
        else:
            tag = message.from_user.mention_html(message.from_user.first_name)
    if reply_to:
        if len(link) == 0:
            link = reply_to.text.strip()
        if reply_to.from_user.username:
            tag = f"@{reply_to.from_user.username}"
        else:
            tag = reply_to.from_user.mention_html(reply_to.from_user.first_name)
    is_gdtot = is_gdtot_link(link)
    is_appdrive = is_appdrive_link(link)
    if is_gdtot:
        try:
            msg = sendMessage(f"💤𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 𝗚𝗗𝗧𝗼𝗧 𝗟𝗶𝗻𝗸: <code>{link}</code>", bot, message)
            link = gdtot(link)
            deleteMessage(bot, msg)
        except DirectDownloadLinkException as e:
            deleteMessage(bot, msg)
            return sendMessage(str(e), bot, message)
    if is_appdrive:
        msg = sendMessage(f"💤𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 𝗔𝗽𝗽𝗱𝗿𝗶𝘃𝗲/𝗗𝗿𝗶𝘃𝗲𝗮𝗽𝗽 𝗟𝗶𝗻𝗸: <code>{link}</code>", bot, message)
        try:
            apdict = appdrive(link)
            link = apdict.get('gdrive_link')
            deleteMessage(bot, msg)
        except DirectDownloadLinkException as e:
            deleteMessage(bot, msg)
            return sendMessage(str(e), bot, message)
    if is_gdrive_link(link):
        gd = GoogleDriveHelper()
        res, size, name, files = gd.helper(link)
        if res != "":
            return sendMessage(res, bot, message)
        if STOP_DUPLICATE:
            LOGGER.info('Checking File/Folder if already in Drive...')
            smsg, button = gd.drive_list(name, True, True)
            if smsg:
                msg3 = "File/Folder is already available in Drive.\nHere are the search results:"
                return sendMarkup(msg3, bot, message, button)
        if multi > 1:
            sleep(4)
            nextmsg = type('nextmsg', (object, ), {'chat_id': message.chat_id, 'message_id': message.reply_to_message.message_id + 1})
            nextmsg = sendMessage(args[0], bot, nextmsg)
            nextmsg.from_user.id = message.from_user.id
            multi -= 1
            sleep(4)
            Thread(target=_clone, args=(nextmsg, bot, multi)).start()
        if files <= 20:
            sendtextlog(f"<b>User: {uname}</b>\n<b>User ID:</b> <code>/warn {uid}</code>\n\n<b>Link Sended:</b>\n<code>{link}</code>\n\n#GDrive", bot, message)
            msg = sendMessage(f"♻️𝗖𝗹𝗼𝗻𝗶𝗻𝗴: <code>{link}</code>", bot, message)
            result, button = gd.clone(link)
            deleteMessage(bot, msg)
        else:
            sendtextlog(f"<b>User: {uname}</b>\n<b>User ID:</b> <code>/warn {uid}</code>\n\n<b>Link Sended:</b>\n<code>{link}</code>\n\n#GDrive", bot, message)
            drive = GoogleDriveHelper(name)
            gid = ''.join(SystemRandom().choices(ascii_letters + digits, k=12))
            clone_status = CloneStatus(drive, size, message, gid)
            with download_dict_lock:
                download_dict[message.message_id] = clone_status
            sendStatusMessage(message, bot)
            result, button = drive.clone(link)
            with download_dict_lock:
                del download_dict[message.message_id]
                count = len(download_dict)
            try:
                if count == 0:
                    Interval[0].cancel()
                    del Interval[0]
                    delete_all_messages()
                else:
                    update_all_messages()
            except IndexError:
                pass
        if message.from_user.username:
            uname = f'@{message.from_user.username}'
        else:
            uname = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
        if uname is not None:
            cc = f'\n\n𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝗲𝗱 𝗕𝗬: {uname}'
            men = f'{uname}'
            msg_g = f"\n\n - 𝗗𝗼𝗻'𝘁 𝗦𝗵𝗮𝗿𝗲 𝘁𝗵𝗲 𝗜𝗻𝗱𝗲𝘅 𝗟𝗶𝗻𝗸"
            fwdpm = f"\n\n𝙄'𝙫𝙚 𝙎𝙚𝙣𝙙 𝙩𝙝𝙚 𝙇𝙞𝙣𝙠𝙨 𝙏𝙤 𝙔𝙤𝙪𝙧 𝙋𝙈 & 𝙇𝙤𝙜 𝘾𝙝𝙖𝙣𝙣𝙚𝙡"
        if button == "cancelled" or button == "":
            sendMessage(men + result, bot, message)
        else:
            sendLog(result + cc + msg_g, bot, message, button)
            auto = sendMessage(result + cc + fwdpm, bot, message)
            Thread(target=auto_delete, args=(bot, message, auto)).start()
            sendPrivate(result + cc + msg_g, bot, message, button)
        if is_gdtot:
            gd.deletefile(link)
        elif is_appdrive:
            if apdict.get('link_type') == 'login':
                LOGGER.info(f"Deleting: {link}")
                gd.deletefile(link)
    else:
        sendMessage('Send Gdrive or gdtot or appdrive/drivelink link along with command or by replying to the link by command', bot, message)

@new_thread
def cloneNode(update, context):
    _clone(update.message, context.bot)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)
