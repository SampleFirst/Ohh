from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import ChatPrivileges
from info import ADMINS

@Client.on_message(filters.command("addadmin") & filters.private)
async def add_admin(client, message):
    if message.from_user.id not in ADMINS:
        await message.reply("You must be an admin to use this command.")
        return

    if len(message.command) != 3:
        await message.reply("Usage: /addadmin user_id chat_id")
        return

    user_id = int(message.command[1])
    chat_id = int(message.command[2])

    try:
        chat_info = await client.get_chat(chat_id)
        bot_privileges = chat_info.privileges

        # Construct permissions for the new admin based on the bot's current permissions
        admin_privileges = ChatPrivileges(
            can_change_info=bot_privileges.can_change_info,
            can_post_messages=bot_privileges.can_post_messages,
            can_edit_messages=bot_privileges.can_edit_messages,
            can_delete_messages=bot_privileges.can_delete_messages,
            can_invite_users=bot_privileges.can_invite_users,
            can_manage_chat=bot_privileges.can_manage_chat,
            can_manage_voice_chats=bot_privileges.can_manage_voice_chats,
            can_restrict_members=bot_privileges.can_restrict_members,
            can_pin_messages=bot_privileges.can_pin_messages,
            can_promote_members=bot_privileges.can_promote_members,
            is_anonymous=bot_privileges.is_anonymous,
            can_send_messages=True  # Example: Let the new admin send messages
        )

        await client.promote_chat_member(
            chat_id,
            user_id,
            permissions=admin_privileges,
        )
        await message.reply("User added as an admin with specified privileges.")
    except UserNotParticipant:
        await message.reply("The user must be a member of the chat to use this command.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
