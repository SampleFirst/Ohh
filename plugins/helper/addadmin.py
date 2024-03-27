from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import ChatPrivileges
from info import ADMINS

@Client.on_message(filters.command("addchanneladmin") & filters.private)
async def add_channel_admin(client, message):
    if message.from_user.id not in ADMINS:
        await message.reply("You must be an admin to use this command.")
        return

    if len(message.command) != 3:
        await message.reply("Usage: /addchanneladmin user_id chat_id")
        return

    user_id = int(message.command[1])
    chat_id = int(message.command[2])
    status_message = "Privileges status:\n"

    try:
        privileges = ChatPrivileges(
            can_change_info=True,
            can_post_messages=True,
            can_edit_messages=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_manage_chat=True,
            can_manage_video_chats=True,
            can_promote_members=True
        )

        for privilege, value in privileges.items():
            try:
                await client.promote_chat_member(chat_id, user_id, privileges={privilege: value})
                status_message += f"{privilege}: ✅\n"
            except Exception as e:
                status_message += f"{privilege}: ❌\n"

        await message.reply("User added as an admin in the channel with specified privileges.\n" + status_message)
    except UserNotParticipant:
        await message.reply("The user must be a member of the channel to use this command.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

@Client.on_message(filters.command("addgroupadmin") & filters.private)
async def add_group_admin(client, message):
    if message.from_user.id not in ADMINS:
        await message.reply("You must be an admin to use this command.")
        return

    if len(message.command) != 3:
        await message.reply("Usage: /addgroupadmin user_id chat_id")
        return

    user_id = int(message.command[1])
    chat_id = int(message.command[2])
    status_message = "Privileges status:\n"

    try:
        privileges = ChatPrivileges(
            can_change_info=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_promote_members=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_manage_chat=True,
            can_manage_video_chats=True,
            is_anonymous=True
        )

        for privilege, value in privileges.items():
            try:
                await client.promote_chat_member(chat_id, user_id, privileges={privilege: value})
                status_message += f"{privilege}: ✅\n"
            except Exception as e:
                status_message += f"{privilege}: ❌\n"

        await message.reply("User added as an admin in the group with specified privileges.\n" + status_message)
    except UserNotParticipant:
        await message.reply("The user must be a member of the group to use this command.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
        
