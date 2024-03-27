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

        await add_admin_with_permissions(client, message, chat_id, user_id, privileges)

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

        await add_admin_with_permissions(client, message, chat_id, user_id, privileges)

    except UserNotParticipant:
        await message.reply("The user must be a member of the group to use this command.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

async def add_admin_with_permissions(client, message, chat_id, user_id, privileges):
    try:
        await client.promote_chat_member(chat_id, user_id, privileges=privileges)
        await message.reply("User added as an admin with specified privileges.")
    except Exception as e:
        if "not enough rights" in str(e):
            insufficient_permissions = []

            # Check which privileges the bot doesn't have sufficient permissions for
            if not privileges.can_change_info:
                insufficient_permissions.append("change_info")
            if not privileges.can_post_messages:
                insufficient_permissions.append("post_messages")
            if not privileges.can_edit_messages:
                insufficient_permissions.append("edit_messages")
            if not privileges.can_delete_messages:
                insufficient_permissions.append("delete_messages")
            if not privileges.can_invite_users:
                insufficient_permissions.append("invite_users")
            if not privileges.can_manage_chat:
                insufficient_permissions.append("manage_chat")
            if not privileges.can_manage_video_chats:
                insufficient_permissions.append("manage_video_chats")
            if not privileges.can_promote_members:
                insufficient_permissions.append("promote_members")

            # Remove insufficient permissions from privileges
            for permission in insufficient_permissions:
                setattr(privileges, permission, False)

            await client.promote_chat_member(chat_id, user_id, privileges=privileges)
            await message.reply(f"User added as an admin with modified privileges: {', '.join(insufficient_permissions)} skipped.")
        else:
            await message.reply(f"An error occurred: {str(e)}")
            
