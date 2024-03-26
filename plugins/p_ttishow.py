from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, MELCOW_NEW_USERS, MELCOW_VID, CHNL_LNK, GRP_LNK
from database.users_chats_db import db
from database.ia_filterdb import Media, Media2,  db as clientDB, db2 as clientDB2
from utils import add_new_chat_members, get_size, temp, get_settings
from Script import script
from pyrogram.errors import ChatAdminRequired, ChannelPrivate
import asyncio 
from pytz import timezone
from datetime import datetime



@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    new_members = [member.id for member in message.new_chat_members]
    if temp.ME in new_members:
        if not await db.get_chat(message.chat.id):
            tz = timezone('Asia/Kolkata')
            now = datetime.now(tz)
            time = now.strftime('%I:%M:%S %p')
            today = now.date()
            total_members = await bot.get_chat_members_count(message.chat.id)
            total_chat = await db.total_chat_count() + 1
            daily_chats = await db.daily_chats_count(today) + 1
            referrer = message.from_user.mention if message.from_user else "Anonymous"
            await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(a=message.chat.title, b=message.chat.id, c=message.chat.username, d=total_members, e=total_chats, f=daily_chats, g=str(today), h=time, i=referrer, j=temp.B_NAME, k=temp.U_NAME))
            await db.add_chat(message.chat.id, message.chat.title, message.chat.username)

        if message.chat.id in temp.BANNED_CHATS:
            buttons = [[
                InlineKeyboardButton('Support', url=GRP_LNK)
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            message_text = '<b>CHAT NOT ALLOWED 🐞\n\nMy admins have restricted me from working here! If you want to know more about it, contact support.</b>'
            sent_message = await message.reply(
                text=message_text,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )

            try:
                await sent_message.pin()
            except Exception as e:
                print(e)

            await bot.leave_chat(message.chat.id)
            return

        buttons = [[
            InlineKeyboardButton('ℹ️ Help', url=f"https://t.me/{temp.U_NAME}?start=help"),
            InlineKeyboardButton('📢 Updates', url=CHNL_LNK)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)

        welcome_message = f"<b>Thank you for adding me to {message.chat.title} ❣️\n\nIf you have any questions or doubts about using me, contact support.</b>"
        await message.reply_text(
            text=welcome_message,
            reply_markup=reply_markup,
        )
    else:
        settings = await get_settings(message.chat.id)
        invite_link = None  # Initialize invite_link to None
    
        # Generate or get the invite link for this chat
        chat_id = message.chat.id
        if invite_link is None:
            invite_link = await db.get_chat_invite_link(chat_id)
            if invite_link is None:
                try:
                    invite_link = await bot.export_chat_invite_link(chat_id)
                except ChatAdminRequired:
                    invite_link = "Not an Admin"
                    return
                await db.save_chat_invite_link(chat_id, invite_link)
    
        if settings["welcome"]:
            for new_member in new_members:
                if temp.MELCOW.get('welcome') is not None:
                    try:
                        await temp.MELCOW['welcome'].delete()
                    except Exception as e:
                        print(e)
    
                welcome_message = script.MELCOW_ENG.format(new_member.mention, message.chat.title)
                temp.MELCOW['welcome'] = await message.reply_photo(
                    photo=MELCOW_PIC,
                    caption=welcome_message,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton('Support Group', url=GRP_LNK),
                                InlineKeyboardButton('Updates Channel', url=CHNL_LNK)
                            ]
                        ]
                    ),
                    parse_mode=enums.ParseMode.HTML
                )
    
                # Log new members joining the group
                tz = timezone('Asia/Kolkata')
                now = datetime.now(tz)
                time = now.strftime('%I:%M:%S %p')
                date = now.date()
                total_members = await bot.get_chat_members_count(message.chat.id)
    
                for new_member in new_members:
                    await bot.send_message(LOG_CHANNEL, script.NEW_MEMBER.format(
                        a=message.chat.title,
                        b=message.chat.id,
                        c=message.chat.username,
                        d=total_members,
                        e=invite_link,
                        f=new_member.mention,
                        g=new_member.id,
                        h=new_member.username,
                        i=date,
                        j=time,
                        k=temp.U_NAME
                    ))
        else:
            # Log new members joining the group
            tz = timezone('Asia/Kolkata')
            now = datetime.now(tz)
            time = now.strftime('%I:%M:%S %p')
            date = now.date()
            total_members = await bot.get_chat_members_count(message.chat.id)
    
            for new_member in new_members:
                await bot.send_message(LOG_CHANNEL, script.NEW_MEMBER.format(
                    a=message.chat.title,
                    b=message.chat.id,
                    c=message.chat.username,
                    d=total_members,
                    e=invite_link,
                    f=new_member.mention,
                    g=new_member.id,
                    h=new_member.username,
                    i=date,
                    j=time,
                    k=temp.U_NAME
                ))

        if settings["auto_delete"]:
            await asyncio.sleep(600)
            await temp.MELCOW['welcome'].delete()
            
# Handler for logging members leaving the group
@Client.on_message(filters.left_chat_member & filters.group)
async def goodbye(bot, message):
    invite_link = None  # Initialize invite_link to None

    # Generate or get the invite link for this chat
    chat_id = message.chat.id
    if invite_link is None:
        invite_link = await db.get_chat_invite_link(chat_id)
        if invite_link is None:
            try:
                invite_link = await bot.export_chat_invite_link(chat_id)
            except ChannelPrivate:
                invite_link = "Not an Admin"
                return 
            except ChatAdminRequired:
                invite_link = "Not an Admin"
                return
            await db.save_chat_invite_link(chat_id, invite_link)
    
    # Get total members count
    try:
        total_members = await bot.get_chat_members_count(message.chat.id)
    except ChannelPrivate:
        total_members = "Not an Admin"
        return
    
    # Get current time and date
    tz = timezone('Asia/Kolkata')
    now = datetime.now(tz)
    time = now.strftime('%I:%M:%S %p')
    date = now.date()
    
    # Check if chat exists in the database
    if await db.get_chat(message.chat.id):
        left_member = message.left_chat_member  # Get the left member info
        await bot.send_message(LOG_CHANNEL, script.LEFT_MEMBER.format(
            a=message.chat.title,
            b=message.chat.id,
            c=message.chat.username,
            d=total_members,
            e=invite_link,
            f=left_member.mention,
            g=left_member.id,
            h=left_member.username,
            i=date,
            j=time,
            k=temp.U_NAME
        ))

@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        buttons = [[
            InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text='<b>Hello Friends, \nMy admin has told me to leave from group so i go! If you wanna add me again contact my support group.</b>',
            reply_markup=reply_markup,
        )

        await bot.leave_chat(chat)
        await message.reply(f"left the chat `{chat}`")
    except Exception as e:
        await message.reply(f'Error - {e}')

@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply("Chat Not Found In DB")
    if cha_t['is_disabled']:
        return await message.reply(f"This chat is already disabled:\nReason-<code> {cha_t['reason']} </code>")
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply('Chat Successfully Disabled')
    try:
        buttons = [[
            InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_, 
            text=f'<b>Hello Friends, \nMy admin has told me to leave from group so i go! If you wanna add me again contact my support group.</b> \nReason : <code>{reason}</code>',
            reply_markup=reply_markup)
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("Chat Not Found In DB !")
    if not sts.get('is_disabled'):
        return await message.reply('This chat is not yet disabled.')
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    await message.reply("Chat Successfully re-enabled")


@Client.on_message(filters.command('stats') & filters.incoming)
async def get_ststs(bot, message):
    rju = await message.reply('Fetching stats..')
    #users and chats
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    #primary db
    filesp = await Media.count_documents()
    #secondary db
    totalsec = await Media2.count_documents()
    #primary
    stats = await clientDB.command('dbStats')
    used_dbSize = (stats['dataSize']/(1024*1024))+(stats['indexSize']/(1024*1024))
    free_dbSize = 512-used_dbSize
    #secondary
    stats2 = await clientDB2.command('dbStats')
    used_dbSize2 = (stats2['dataSize']/(1024*1024))+(stats2['indexSize']/(1024*1024))
    free_dbSize2 = 512-used_dbSize2
    await rju.edit(script.STATUS_TXT.format((int(filesp)+int(totalsec)), total_users, totl_chats, filesp, round(used_dbSize, 2), round(free_dbSize, 2), totalsec, round(used_dbSize2, 2), round(free_dbSize2, 2)))


@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    try:
        link = await bot.create_chat_invite_link(chat)
    except ChatAdminRequired:
        return await message.reply("Invite Link Generation Failed, Iam Not Having Sufficient Rights")
    except Exception as e:
        return await message.reply(f'Error {e}')
    await message.reply(f'Here is your Invite Link {link.invite_link}')

@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    # https://t.me/GetTGLink/4185
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply("This might be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(f"{k.mention} is already banned\nReason: {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply(f"Successfully banned {k.mention}")


    
@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply("Thismight be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(f"{k.mention} is not yet banned.")
        await db.remove_ban(k.id)
        temp.BANNED_USERS.remove(k.id)
        await message.reply(f"Successfully unbanned {k.mention}")


    
@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    # https://t.me/GetTGLink/4184
    raju = await message.reply('Getting List Of Users')
    users = await db.get_all_users()
    out = "Users Saved In DB Are:\n\n"
    for user in users:
        out += f"<a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += '( Banned User )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="List Of Users")

@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    raju = await message.reply('Getting List Of chats')
    chats = await db.get_all_chats()
    out = "Chats Saved In DB Are:\n\n"
    for chat in chats:
        out += f"**Title:** `{chat['title']}`\n**- ID:** `{chat['id']}`"
        if chat['chat_status']['is_disabled']:
            out += '( Disabled Chat )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="List Of Chats")
