import random
import inspect
import html
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timedelta

import telebot
from telebot import types


                                                              
           
                                                              

                                                                
                                                               
                                                         
TOKEN = os.getenv('BOT_TOKEN', '').strip()
if not TOKEN:
    raise RuntimeError('Не задана переменная окружения BOT_TOKEN')

                                                           
                                                              
                                                  
LOG_CHAT_ID = -1004456405151
LOG_CHAT_CONFIGURED = LOG_CHAT_ID != -1001234567890

                                                            
                                                            
                                                         
OWNER_ID = 6425532273
OWNER_USERNAME = "@vvar51"

bot = telebot.TeleBot(TOKEN)


                                                              
                                                       
                                                              

DATA_FILE = "bot_data.json"


def load_data():

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Не удалось прочитать {DATA_FILE}: {e}")

    return {
        "known_chats": {},
        "users": {},
        "known_users": {},
        "profiles": {},
        "admin_ranks": {},
        "warnings": {},
        "coins": {},
        "prize_cooldowns": {},
        "group_rules": {}
    }


DATA = load_data()
DATA.setdefault("known_chats", {})
DATA.setdefault("users", {})
DATA.setdefault("known_users", {})
DATA.setdefault("profiles", {})
DATA.setdefault("admin_ranks", {})
DATA.setdefault("warnings", {})
DATA.setdefault("coins", {})
DATA.setdefault("prize_cooldowns", {})
DATA.setdefault("group_rules", {})


def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DATA, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] Не удалось сохранить {DATA_FILE}: {e}")


def register_chat(chat):

    if chat.type not in ("group", "supergroup"):
        return

    DATA["known_chats"][str(chat.id)] = {
        "title": chat.title or "",
        "type": chat.type
    }

    save_data()


def remove_known_chat(chat_id):
    DATA["known_chats"].pop(str(chat_id), None)
    save_data()


def touch_user(chat_id, user, when=None):

    if user is None or user.is_bot:
        return

    chat_key = str(chat_id)
    users = DATA["users"].setdefault(chat_key, {})
    user_key = str(user.id)

    entry = users.get(user_key, {"message_count": 0})
    entry["id"] = user.id
    entry["first_name"] = user.first_name
    entry["username"] = user.username
    entry["last_seen"] = when or int(datetime.now().timestamp())
    entry["message_count"] = entry.get("message_count", 0) + 1

    users[user_key] = entry

                                                                      
    profile = DATA["profiles"].setdefault(user_key, {})
    if not profile.get("nickname"):
        profile["nickname"] = user.first_name or user.username or str(user.id)

                                                                     
    DATA["known_users"][user_key] = {
        "first_name": user.first_name or "",
        "username": user.username or "",
        "last_seen": entry["last_seen"]
    }
    save_data()

                                                              
                         
                                                              

try:
    TELEBOT_VERSION = getattr(
        telebot,
        "__version__",
        "unknown"
    )

except Exception:
    TELEBOT_VERSION = "unknown"


print(
    f"pyTelegramBotAPI: {TELEBOT_VERSION}"
)


                                                              
                
                                                              

PUNISH_MESSAGES = [
    "💀 {user} так много выёбывался, что получил мут на {time}.",
    "🖕 {user} послан нахуй в режим тишины на {time}.",
    "🤬 {user} доебался до чата — чат доебался в ответ. Мут: {time}.",
    "🔇 {user} заткнут к хуям на {time}.",
    "💥 {user} словил ебучий банхаммер тишины на {time}.",
    "🤫 {user}, пиздец дискуссии окончен. Молчишь {time}.",
    "🪦 {user} слишком много пиздел — теперь тишина на {time}.",
    "💢 {user} заебал чат и отправлен молчать на {time}.",
    "🛑 {user} хватит хуйню писать. Мут на {time}.",
    "🥴 {user} нёс такую хуйню, что пришлось выключить микрофон на {time}.",
    "🔨 {user} получил пиздюлей от банхаммера на {time}.",
    "☠️ {user} отправлен в режим «не пизди» на {time}.",

    "💀 Я отпиздил {user} и он в коме на {time}.",
    "🔨 {user} словил удар по ебалу и не может говорить {time}.",
    "🚑 {user} был отпизжен и отправился в реанимацию на {time}.",
    "☠️ {user} временно пошел нахуй из группы на {time}.",
    "👊 Администрация провела отпиздила {user}. Он обиделся на {time}.",
    "🪦 {user} слишком много выёбывался и получил {time}.",
    "🚓 {user} задержан полицией здравого смысла на {time}.",
    "📵 {user} отключён от интернета на {time}.",
    "🤕 После столкновения с правилами {user} отдыхает {time}.",
    "⚰️ {user} проиграл PvP против администрации на {time}.",

    "🔇 Я заткнул {user} на {time}.",
    "🎤 Микрофон у {user} временно изъят. Срок: {time}.",
    "🩹 {user} отправлен на курс молчаливой терапии на {time}.",
    "📦 {user} упакован в коробку тишины на {time}.",
    "🧵 Рот {user} зашит административной ниткой на {time}.",
    "🪦 Слова {user} официально похоронены на {time}.",
    "🚫 {user} лишён права портить воздух сообщениями ещё {time}.",
    "🔨 Я починил чат. Для этого пришлось выключить {user} на {time}.",
    "📡 Передатчик {user} заглушен на {time}.",
    "🛏️ {user} отправлен отдыхать от собственных мыслей на {time}.",
    "🎭 {user} играет роль немого персонажа ещё {time}.",
    "🗿 {user} успешно превращён в декоративный камень на {time}.",
    "🧯 Поток сообщений от {user} потушен на {time}.",
    "⚰️ Голосовые связки {user} временно архивированы на {time}.",

    "🔨 Я отпиздил {user}. Восстановление займёт {time}.",
    "☠️ {user} отправлен в административную кому на {time}.",
    "🚑 {user} вынесен с поля боя модерации на {time}.",
    "🪦 Для {user} наступила временная смерть сроком {time}.",
    "🚀 {user} запущен в открытый космос на {time}.",
    "📤 {user} экспортирован из реальности на {time}.",
    "⚰️ {user} помещён в банхаммерную капсулу на {time}.",
    "🧹 Я вымел {user} отсюда на {time}.",
    "🦶 {user} получил ускорение ботинком модератора на {time}.",
    "🏥 {user} находится в отделении интенсивного перевоспитания ещё {time}.",
    "🚧 Доступ для {user} перекрыт бетонной плитой на {time}.",
    "🗑️ {user} временно перемещён в корзину на {time}.",
    "🌋 {user} сброшен в жерло бюрократического вулкана на {time}.",
    "🛰️ Сигнал от {user} потерян на {time}.",
    "👊 {user} встретился с банхаммером. Итог: {time} изоляции.",
]


                                                               
TIMED_BAN_MESSAGES = [
    "💀 {user} так охуел, что получил бан на {time}.",
    "🖕 {user} отправлен нахуй из чата на {time}.",
    "🔨 {user} получил ебучий банхаммер на {time}.",
    "🤬 {user} заебал администрацию — бан на {time}.",
    "🪦 {user} закопан за очередную хуйню. Срок: {time}.",
    "🚪 {user} пиздует из чата на {time}.",
    "💥 {user} устроил хуету и получил бан на {time}.",

    "💀 Я отъебашил {user} и теперь он в коме на {time} (бан {time}).",
    "🔨 {user} получил люлей и вылетел из чата на {time}.",
    "🚑 {user} увезли на скорой, вернётся через {time}.",
    "☠️ {user} отправлен в кому строгого режима на {time}.",
    "🪦 {user} закопан временно, откопают через {time}.",
    "🚀 {user} улетел в космос без права возврата на {time}.",
    "🧊 {user} заморожен в криокамере на {time}.",
    "🏝️ {user} сослан на необитаемый остров на {time}.",
    "🗿 {user} превращён в статую на площади на {time}.",
    "🕳️ {user} провалился в чёрную дыру на {time}.",
    "🔒 {user} закрыт на амбарный замок ещё {time}.",
    "🚧 Вход для {user} перекрыт шлагбаумом на {time}.",
    "🩸 {user} истёк кровью в бане на {time}.",
    "🎢 {user} отправлен в бесконечное падение на {time}.",
    "🛸 {user} похищен инопланетянами на {time}.",
]

                                                
PERMANENT_BAN_MESSAGES = [
    "💀 {user} настолько заебал, что получил вечный бан.",
    "🖕 {user} послан нахуй из этого чата навсегда.",
    "🔨 {user} получил вечный ебучий банхаммер.",
    "🤬 {user} окончательно доебался до администрации. Бан навсегда.",
    "🪦 {user} похоронен за всю ту хуйню, что успел устроить.",
    "🚪 {user} вышвырнут нахуй без обратного билета.",

    "💀 Я отъебашил {user} и он больше сюда не вернётся.",
    "☠️ {user} отправлен в чат для мёртвых душ. Навсегда.",
    "🔨 {user} получил вечный банхаммер по голове.",
    "🪦 {user} официально похоронен в этом чате навечно.",
    "🚀 {user} улетел в открытый космос без обратного билета.",
    "🗑️ {user} вынесен на свалку истории. Насовсем.",
    "⛓️ {user} закован в цепи и выброшен из чата навсегда.",
    "🧟 {user} стал нежитью за пределами этого чата. Навсегда.",
    "🕳️ {user} провалился в чёрную дыру без шанса на возврат.",
    "🚫 {user} внесён в чёрный список этого чата навечно.",
]


                                                              
                                
                                                              

def make_mute_permissions():
    """
    Создаёт ChatPermissions, совместимый
    с разными версиями pyTelegramBotAPI.
    """

    parameters = inspect.signature(
        types.ChatPermissions
    ).parameters

    kwargs = {
        "can_send_messages": False
    }

    if "can_send_media_messages" in parameters:
        kwargs["can_send_media_messages"] = False

    optional_permissions = [
        "can_send_audios",
        "can_send_documents",
        "can_send_photos",
        "can_send_videos",
        "can_send_video_notes",
        "can_send_voice_notes",
        "can_send_polls",
        "can_send_other_messages",
        "can_add_web_page_previews",
    ]

    for permission in optional_permissions:
        if permission in parameters:
            kwargs[permission] = False

    return types.ChatPermissions(**kwargs)


def make_unmute_permissions():
    """
    Создаёт полный набор разрешений,
    совместимый с разными версиями pyTelegramBotAPI.
    """

    parameters = inspect.signature(
        types.ChatPermissions
    ).parameters

    kwargs = {
        "can_send_messages": True
    }

    if "can_send_media_messages" in parameters:
        kwargs["can_send_media_messages"] = True

    optional_permissions = [
        "can_send_audios",
        "can_send_documents",
        "can_send_photos",
        "can_send_videos",
        "can_send_video_notes",
        "can_send_voice_notes",
        "can_send_polls",
        "can_send_other_messages",
        "can_add_web_page_previews",
    ]

    for permission in optional_permissions:
        if permission in parameters:
            kwargs[permission] = True

    return types.ChatPermissions(**kwargs)


                                                              
                 
                                                              

def is_bot_creator(user_id):
    """Создатель бота — полный доступ на уровне логики бота."""
    return int(user_id) == OWNER_ID


def get_admin_rank(chat_id, user_id):
    """Определяет фактический ранг Telegram-админа по его правам.
    1 — удаление, 2 — модерация, 3 — управление чатом, 4 — повышение.
    Создатель чата всегда имеет ранг 4.
    """
    if is_bot_creator(user_id):
        return 4
    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status == "creator":
            return 4
        if member.status != "administrator":
            return 0
        if getattr(member, "can_promote_members", False):
            return 4
        if getattr(member, "can_change_info", False):
            return 3
        if getattr(member, "can_restrict_members", False):
            return 2
        if getattr(member, "can_delete_messages", False):
            return 1
    except Exception as e:
        print(f"[ERROR] Определение ранга {chat_id}/{user_id}: {e}")
    return 0


def is_admin(chat_id, user_id):
    """Надёжная проверка админа. Создатель бота имеет полный доступ
    на уровне логики бота, а Telegram-админы проверяются через API."""
    try:
        if is_bot_creator(user_id):
            return True

        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")

    except Exception as e:
        print(f"[ERROR] Проверка администратора {chat_id}/{user_id}: {e}")
        return False


def is_chat_creator(chat_id, user_id):
    """Проверяет именно создателя конкретного чата."""
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status == "creator"
    except Exception as e:
        print(f"[ERROR] Проверка создателя чата {chat_id}/{user_id}: {e}")
        return False


def get_reply_target(message):
    """
    Возвращает пользователя, на которого ответили,
    или None, если ответ невозможен (например, реплай
    на анонимного админа/канал, у которого нет from_user).
    """

    if not message.reply_to_message:
        return None

    return message.reply_to_message.from_user


def resolve_target(message):
    """Цель модерации: reply или @username. Числовые ID отключены."""
    args = (message.text or "").split()
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        if user is None:
            bot.reply_to(message, "❌ Не удалось определить пользователя (анонимный админ или канал).")
            return None
        return {"id": user.id, "name": user.first_name or user.username or str(user.id), "rest": args[1:]}
    if len(args) < 2:
        bot.reply_to(message, "❗ Укажи пользователя: ответь на его сообщение или укажи @username.")
        return None
    token=args[1]
    if token.lstrip("-").isdigit():
        bot.reply_to(message, "❌ Числовые ID для модерации отключены. Используй reply или @username.")
        return None
    if token.startswith("@"):
        wanted=token[1:].lower()
        known=DATA.get("users",{}).get(str(message.chat.id),{})
        for uid,entry in known.items():
            if str(entry.get("username") or "").lstrip("@").lower()==wanted:
                return {"id":int(uid),"name":entry.get("first_name") or token,"rest":args[2:]}
        for uid,entry in DATA.get("known_users",{}).items():
            if str(entry.get("username") or "").lstrip("@").lower()==wanted:
                try:
                    member=bot.get_chat_member(message.chat.id,int(uid))
                    return {"id":member.user.id,"name":member.user.first_name or token,"rest":args[2:]}
                except Exception:
                    continue
        bot.reply_to(message, f"⚠️ Не удалось найти {token}. Пользователь должен хотя бы один раз написать в этом чате при работающем боте.")
        return None
    bot.reply_to(message,"❗ Укажи пользователя через reply или @username.")
    return None


                                                              
                                
                                                              

@bot.message_handler(
    func=lambda m: not (m.content_type == "text" and ((m.text or "").lstrip().startswith("/") or (m.text or "").lstrip().lower().startswith("+правила"))),
    content_types=[
        "text", "photo", "video", "document", "sticker",
        "voice", "audio", "video_note", "animation",
        "location", "contact", "poll"
    ]
)
def track_activity(message):
    """
    Фоновый учёт: запоминает чат и обновляет "последний раз
    писал" для каждого пользователя. Нужен для /участники, /актив, /алл — Bot API не даёт
    получить полный список участников чата напрямую, поэтому
    бот запоминает только тех, кого реально видел пишущим.
    """

    register_chat(message.chat)
    touch_user(message.chat.id, message.from_user, message.date)


def _track_bot_membership(update):
    """
    Отслеживает добавление/удаление бота из чатов
    (список чатов сохраняется на случай, если понадобится
    в будущем).
    """

    new_status = update.new_chat_member.status

    if new_status in ("member", "administrator", "creator"):
        register_chat(update.chat)

    elif new_status in ("left", "kicked"):
        remove_known_chat(update.chat.id)


if hasattr(bot, "my_chat_member_handler"):
    bot.my_chat_member_handler()(_track_bot_membership)
else:
    print(
        "[WARN] Эта версия pyTelegramBotAPI не поддерживает "
        "my_chat_member_handler — бот узнает о новом чате только "
        "после того, как в нём кто-то напишет сообщение."
    )


                                                              
      
                                                              

def _display_nickname(user):
    profile = DATA.get("profiles", {}).get(str(getattr(user, "id", "")), {})
    return profile.get("nickname") or getattr(user, "first_name", None) or getattr(user, "username", None) or str(getattr(user, "id", "?"))


def send_log(action, admin, target, reason="-", chat=None):
    if not LOG_CHAT_CONFIGURED:
        return
    if chat is None:
        chat_title = "-"
    else:
        chat_title = getattr(chat, "title", None) or "Личные сообщения"
    if str(action).startswith("MUTE"):
        action_text = "замутил"
    elif str(action).startswith("UNMUTE"):
        action_text = "снял мут с"
    elif str(action).startswith("BAN"):
        action_text = "забанил"
    elif str(action).startswith("UNBAN"):
        action_text = "разбанил"
    elif str(action).startswith("WARN"):
        action_text = "выдал варн"
    elif str(action).startswith("PROMOTE"):
        action_text = "повысил"
    elif str(action).startswith("DEMOTE"):
        action_text = "понизил"
    elif str(action).startswith("RULES"):
        action_text = "изменил правила в"
    else:
        action_text = str(action).lower()
    now = datetime.now()
    text = (
        f"👮 <b>{html.escape(_display_nickname(admin))}</b> {action_text} "
        f"<b>{html.escape(_display_nickname(target))}</b>\n"
        f"группа: {html.escape(chat_title)}\n"
        f"время: {now.strftime('%H:%M:%S')}\n"
        f"ид обоих: {admin.id} | {target.id}\n"
        f"дата: {now.strftime('%d.%m.%Y')}"
    )
    if reason and reason != "-":
        text += f"\nпричина: {html.escape(str(reason))}"
    try:
        bot.send_message(LOG_CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        print(f"[ERROR] Не удалось отправить лог: {e}")


                                                              
        
                                                              

@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.type == "private":
        text = (
            "👋 <b>Привет! Я RISBOT 51!</b>\n\n"
            "🤖 Я бот для управления Telegram-группами, модерации и администраторских прав.\n"
            "👤 Внутри бота можно настроить свой ник и отслеживать активность.\n\n"
            "📚 Напиши <b>/help</b>, чтобы увидеть команды.\n"
            "💡 В группе я могу помогать с модерацией, админскими рангами, предупреждениями и правилами."
        )
    else:
        text = (
            "👋 <b>RISBOT 51 на связи!</b>\n\n"
            "🛡️ Модерация, админские ранги, предупреждения, правила и активность участников.\n"
            "📚 Используй <b>/help</b> для списка команд.\n"
            "⚙️ Для модерации боту нужны соответствующие права администратора."
        )
    bot.reply_to(message, text, parse_mode="HTML")


                                                              
       
                                                              

@bot.message_handler(commands=["help", "хелп", "помощь"])
def help_command(message):
    bot.reply_to(message,
        "📚 <b>RISBOT 51 — помощь</b>\n\n"
        "👋 <b>Основные</b>\n"
        "/start — приветствие и информация о боте.\n"
        "/help — эта справка.\n"
        "/id — ID пользователя или чата.\n/test — проверить работу бота.\n/баланс — посмотреть коины.\n/приз — получить случайный приз.\n"
        "👤 <b>Профиль</b>\n"
        "/мойник — показать ник в RISBOT.\n"
        "/сменитьник Новый ник — бесплатно сменить ник.\n\n"
        "🛡️ <b>Модерация</b>\n"
        "/ban /бан — заблокировать пользователя.\n"
        "/unban /разбан — снять бан.\n"
        "/mute /мут — выдать мут.\n"
        "/unmute /размут — снять мут.\n/варн /warn — выдать предупреждение.\n"
        "⚠️ Для модерации цель указывается через reply или @username. Числовые ID отключены.\n\n"
        "👑 <b>Администраторы</b>\n"
        "/staff — список администраторов и рангов.\n"
        "/ранг /rank — узнать ранг.\n"
        "/повысить1–4 /promote /rang — повысить до ранга 1–4.\n"
        "/понизить /разжаловать /demote — понизить или снять админку.\n/правила — показать правила группы.\n+правила Текст — установить и закрепить правила.\n\n"
        "👥 <b>Участники</b>\n"
        "/участники /members — известные участники.\n"
        "/актив /active — активность (5+ сообщений).\n"
        "/алл /all — упомянуть участников.\n\n"
        "📢 <b>Рассылки</b>\n"
        "/рассылка — рассылка по чатам.\n"
        "/рассылкалс — рассылка пользователям.\n"
        "/рассылкагруппа — рассылка по группам.\n"
        "/массрассылка — массовая рассылка.\n\n"
        "💡 Многие команды можно писать без символа /.",
        parse_mode="HTML")


                                                              
      
                                                              

@bot.message_handler(commands=["ban", "бан"])
def ban_user(message):

    if not is_admin(
        message.chat.id,
        message.from_user.id
    ):
        return

    target = resolve_target(message)

    if target is None:
        return

                                 
    if target["id"] == message.from_user.id and not is_bot_creator(message.from_user.id):
        bot.reply_to(message, "🤨 Самого себя банить нельзя.")
        return

    rest = target["rest"]

    days = 7
    permanent = False
    reason = "Не указана"

    if rest:

        first_arg = rest[0].lower()

                                   
        if first_arg in ("навсегда", "форевер", "forever", "perm"):

            permanent = True

            if len(rest) > 1:
                reason = " ".join(rest[1:])

                            
        elif rest[0].isdigit():

            days = int(rest[0])

            if days <= 0:
                bot.reply_to(
                    message,
                    "❌ Количество дней должно быть больше 0."
                )
                return

            if len(rest) > 1:
                reason = " ".join(rest[1:])

                                                                          
        else:
            reason = " ".join(rest)

    until_date = None

    if not permanent:
        until_date = int(
            (
                datetime.now()
                + timedelta(days=days)
            ).timestamp()
        )

    try:

        if until_date:

            bot.ban_chat_member(
                chat_id=message.chat.id,
                user_id=target["id"],
                until_date=until_date
            )

            time_label = f"{days} дн."

            text = random.choice(
                TIMED_BAN_MESSAGES
            ).format(
                user=target["name"],
                time=time_label
            )

            action_label = f"BAN ({days} дн.)"

        else:

            bot.ban_chat_member(
                chat_id=message.chat.id,
                user_id=target["id"]
            )

            text = random.choice(
                PERMANENT_BAN_MESSAGES
            ).format(
                user=target["name"]
            )

            action_label = "BAN (навсегда)"

        bot.send_message(
            message.chat.id,
            f"{text}\nПричина: {reason}"
        )

        send_log(
            action_label,
            message.from_user,
            types.User(
                id=target["id"],
                is_bot=False,
                first_name=target["name"]
            ),
            reason,
            message.chat
        )

    except Exception as e:

        bot.reply_to(
            message,
            "Ошибка, попробуйте снова или позже."
        )


                                                              
        
                                                              

@bot.message_handler(commands=["unban", "разбан"])
def unban_user(message):
    if not is_admin(message.chat.id, message.from_user.id):
        return
    target=resolve_target(message)
    if target is None: return
    try:
        bot.unban_chat_member(message.chat.id,target["id"])
        bot.reply_to(message,f"✅ Пользователь {html.escape(target['name'])} разбанен.",parse_mode="HTML")
        send_log("UNBAN", message.from_user, types.User(id=target["id"], is_bot=False, first_name=target["name"]), "-", message.chat)
    except Exception as e:
        bot.reply_to(message,f"❌ Ошибка разбана:\n{e}")


                                                              
       
                                                              

@bot.message_handler(commands=["mute", "мут"])
def mute_user(message):

    if not is_admin(
        message.chat.id,
        message.from_user.id
    ):
        return

    target = resolve_target(message)

    if target is None:
        return

    rest = target["rest"]

    minutes = 30
    reason = "Не указана"

    if rest:

        if rest[0].isdigit():

            minutes = int(rest[0])

            if minutes <= 0:
                bot.reply_to(
                    message,
                    "❌ Количество минут должно быть больше 0."
                )
                return

            if len(rest) > 1:
                reason = " ".join(rest[1:])

        else:
            reason = " ".join(rest)

    until_date = int(
        (
            datetime.now()
            + timedelta(minutes=minutes)
        ).timestamp()
    )

    permissions = (
        make_mute_permissions()
    )

    try:

        bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target["id"],
            permissions=permissions,
            until_date=until_date
        )

        text = random.choice(
            PUNISH_MESSAGES
        ).format(
            user=target["name"],
            time=f"{minutes} мин."
        )

        bot.send_message(
            message.chat.id,
            text
        )

        send_log(
            "MUTE",
            message.from_user,
            types.User(
                id=target["id"],
                is_bot=False,
                first_name=target["name"]
            ),
            reason,
            message.chat
        )

    except Exception as e:

        bot.reply_to(
            message,
            "Ошибка, попробуйте снова или позже."
        )


                                                              
         
                                                              

@bot.message_handler(commands=["unmute", "размут"])
def unmute_user(message):

    if not is_admin(
        message.chat.id,
        message.from_user.id
    ):
        return

    target = resolve_target(message)

    if target is None:
        return

    permissions = (
        make_unmute_permissions()
    )

    try:

        bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target["id"],
            permissions=permissions
        )

        bot.send_message(
            message.chat.id,
            f"🔊 {target['name']} снова может писать."
        )

        send_log(
            "UNMUTE",
            message.from_user,
            types.User(
                id=target["id"],
                is_bot=False,
                first_name=target["name"]
            ),
            "-",
            message.chat
        )

    except Exception as e:

        bot.reply_to(
            message,
            f"❌ Ошибка снятия мута:\n{e}"
        )



                                                              
                                               
  
                                                              
                 
                                                              

def get_coins(user_id):
    return int(DATA.get("coins", {}).get(str(user_id), 0))


def add_coins(user_id, amount):
    key = str(user_id)
    DATA["coins"][key] = get_coins(user_id) + int(amount)
    save_data()


@bot.message_handler(commands=["выдатькоин"])
def give_coins(message):
    if not is_bot_creator(message.from_user.id):
        bot.reply_to(message, "⚠️ Эта команда доступна только создателю бота.")
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    parts = (message.text or "").strip().split()
    amount_token = None
    if target is not None:
        amount_token = parts[1] if len(parts) > 1 else None
    elif len(parts) >= 3 and parts[1].startswith("@"):
        username = parts[1][1:].lower()
        known = DATA.get("known_users", {})
        for uid, info in known.items():
            if str(info.get("username") or "").lstrip("@").lower() == username:
                target = types.SimpleNamespace(id=int(uid), first_name=info.get("first_name") or parts[1], username=info.get("username"))
                break
        amount_token = parts[2] if target else None
    if target is None:
        bot.reply_to(message, "❗ Укажи пользователя через reply или @username и количество коинов.")
        return
    if not amount_token or not amount_token.lstrip("-").isdigit() or int(amount_token) <= 0:
        bot.reply_to(message, "❗ Укажи положительное количество коинов.")
        return
    amount = int(amount_token)
    add_coins(target.id, amount)
    bot.reply_to(message, f"✅ Пользователю {html.escape(target.first_name or str(target.id))} выдано <b>{amount}</b> коинов.\n💰 Баланс: <b>{get_coins(target.id)}</b>", parse_mode="HTML")


@bot.message_handler(commands=["баланс", "balance", "coins"])
def balance(message):
    bot.reply_to(message, f"💰 Твой баланс: <b>{get_coins(message.from_user.id)}</b> коинов.", parse_mode="HTML")


@bot.message_handler(commands=["приз", "prize"])
def prize(message):
    key = str(message.from_user.id)
    now = int(datetime.now().timestamp())
    cooldown_until = int(DATA.get("prize_cooldowns", {}).get(key, 0) or 0)
    if now < cooldown_until and not is_bot_creator(message.from_user.id):
        left = cooldown_until - now
        h = left // 3600
        m = (left % 3600) // 60
        bot.reply_to(message, f"⏳ Приз пока недоступен. Осталось примерно {h} ч {m} мин.")
        return
    amount = random.randint(100, 500)
    add_coins(message.from_user.id, amount)
                                                       
    if not is_bot_creator(message.from_user.id):
        DATA["prize_cooldowns"][key] = now + random.randint(1, 24) * 3600
        save_data()
    bot.reply_to(message, f"🎁 Тебе выпало <b>{amount}</b> коинов!\n💰 Баланс: <b>{get_coins(message.from_user.id)}</b>", parse_mode="HTML")


                                                              
       
                                                              

@bot.message_handler(commands=["варн", "warn"])
def warn_user(message):
    if not is_admin(message.chat.id, message.from_user.id):
        return
    target = resolve_target(message)
    if target is None:
        return
    if target["id"] == message.from_user.id and not is_bot_creator(message.from_user.id):
        bot.reply_to(message, "🤨 Себя предупреждать нельзя.")
        return
    reason = " ".join(target["rest"]).strip() or "Не указана"
    chat_key = str(message.chat.id)
    warns = DATA["warnings"].setdefault(chat_key, {})
    uid = str(target["id"])
    warns[uid] = int(warns.get(uid, 0)) + 1
    count = warns[uid]
    save_data()
    try:
        bot.send_message(message.chat.id, f"⚠️ {target['name']} получил предупреждение. Всего предупреждений: {count}.\nПричина: {reason}")
        send_log("WARN", message.from_user, types.SimpleNamespace(id=target["id"], first_name=target["name"], username=None), reason, message.chat)
    except Exception as e:
        print(f"[ERROR] /варн: {e}")
        bot.reply_to(message, "Ошибка, попробуйте снова или позже.")


                                                              
       
                                                              

@bot.message_handler(commands=["тест", "test"])
def bot_test(message):
    bot.reply_to(message, "🤖 Бот работает.")


                                                              
                                   
                                                              

@bot.message_handler(func=lambda m: m.content_type == "text" and (m.text or "").strip().lower().startswith("+правила"))
def set_rules(message):
    if message.chat.type not in ("group", "supergroup"):
        bot.reply_to(message, "⚠️ Правила можно установить только в группе.")
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "⚠️ Устанавливать правила может только администратор.")
        return
    raw = (message.text or "").strip()
    rules = raw[len("+правила"):].strip()
    if not rules:
        bot.reply_to(message, "❗ Использование: +правила Текст правил")
        return
    try:
        sent = bot.send_message(message.chat.id, f"📜 <b>Правила группы</b>\n\n{html.escape(rules)}", parse_mode="HTML")
        bot.pin_chat_message(message.chat.id, sent.message_id, disable_notification=True)
        DATA["group_rules"][str(message.chat.id)] = rules
        save_data()
        bot.reply_to(message, "✅ Правила установлены и закреплены.")
        send_log("RULES", message.from_user, message.from_user, f"Установлены правила: {rules}", message.chat)
    except Exception as e:
        print(f"[ERROR] +правила: {e}")
        bot.reply_to(message, "Ошибка, попробуйте снова или позже.")


@bot.message_handler(commands=["правила", "rules"])
def show_rules(message):
    if message.chat.type not in ("group", "supergroup"):
        bot.reply_to(message, "📜 Правила доступны в группах.")
        return
    rules = DATA.get("group_rules", {}).get(str(message.chat.id)) if isinstance(DATA.get("group_rules"), dict) else None
    if rules:
        bot.reply_to(message, f"📜 <b>Правила группы</b>\n\n{html.escape(rules)}", parse_mode="HTML")
    else:
        bot.reply_to(message, "📜 Правил нет. Бебебе 😄 Установи их командой +правила Текст правил")


@bot.message_handler(commands=["сменитьник"])
def change_nickname(message):
    """Бесплатно меняет ник внутри RISBOT."""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        bot.reply_to(message, "✏️ Использование: /сменитьник Новый ник\n\nСмена ника в боте бесплатная.")
        return
    nickname = parts[1].strip()
    if len(nickname) > 32:
        bot.reply_to(message, "⚠️ Ник не должен быть длиннее 32 символов.")
        return
    user_key = str(message.from_user.id)
    profile = DATA["profiles"].setdefault(user_key, {})
    profile["nickname"] = nickname
    save_data()
    bot.reply_to(message, f"✅ Ник в боте изменён на: <b>{html.escape(nickname)}</b>", parse_mode="HTML")


@bot.message_handler(commands=["мойник"])
def my_nickname(message):
    user_key = str(message.from_user.id)
    profile = DATA["profiles"].setdefault(user_key, {})
    if not profile.get("nickname"):
        profile["nickname"] = message.from_user.first_name or message.from_user.username or str(message.from_user.id)
    save_data()
    bot.reply_to(message, f"👤 <b>Твой ник в RISBOT:</b> {html.escape(profile['nickname'])}", parse_mode="HTML")


@bot.message_handler(commands=["id"])
def show_id(message):

                                                      
    if message.reply_to_message:

        user = message.reply_to_message.from_user

        if user is None:

                                                                 
            sender_chat = message.reply_to_message.sender_chat

            if sender_chat:
                bot.reply_to(
                    message,
                    "🆔 Информация об отправителе:\n\n"
                    f"Название: {sender_chat.title}\n"
                    f"ID: {sender_chat.id}\n"
                    f"Тип: {sender_chat.type}"
                )
                return

            bot.reply_to(
                message,
                "❌ Не удалось определить пользователя."
            )
            return

        text = (
            "🆔 Информация о пользователе:\n\n"
            f"Имя: {user.first_name}"
        )

        if user.last_name:
            text += f" {user.last_name}"

        text += f"\nID: {user.id}"

        if user.username:
            text += f"\nUsername: @{user.username}"

        bot.reply_to(
            message,
            text
        )
        return

                                              
    chat = message.chat

    text = (
        "🆔 Информация о чате:\n\n"
        f"Название: {chat.title or '-'}\n"
        f"ID: {chat.id}\n"
        f"Тип: {chat.type}"
    )

    text += f"\n\nТвой ID: {message.from_user.id}"

    bot.reply_to(
        message,
        text
    )


                                                              
        
                                                              

@bot.message_handler(commands=["staff"])
def staff_list(message):
    try:
        admins = bot.get_chat_administrators(message.chat.id)
    except Exception as e:
        bot.reply_to(message, f"❌ Не удалось получить список админов:\n{e}")
        return

    lines = ["👮 <b>Администрация чата</b>:\n"]
    for admin in admins:
        user = admin.user
        if user.is_bot:
            continue
        rank = 4 if admin.status == "creator" else get_admin_rank(message.chat.id, user.id)
        role = "👑 Создатель" if admin.status == "creator" else f"🛡️ Админ • ранг {rank}/4"
        name = html.escape(user.first_name or "Без имени")
        if user.username:
            name += f" (@{html.escape(user.username)})"
        lines.append(f"{role} — {name}")

    lines.append("\n⭐ Ранги: 1 — удаление, 2 — модерация, 3 — управление чатом, 4 — повышение админов.")
    bot.reply_to(message, "\n".join(lines), parse_mode="HTML")


@bot.message_handler(commands=["понизить", "разжаловать", "demote"])
def demote_user(message):
    """Понижение до ранга 1–3 или полное снятие админки."""
    if not (is_chat_creator(message.chat.id, message.from_user.id) or is_bot_creator(message.from_user.id)):
        bot.reply_to(message, "⚠️ Понижать админов может только создатель чата или создатель бота.")
        return

    parts = (message.text or "").strip().split()
    target = message.reply_to_message.from_user if message.reply_to_message else None
    target_token = None
    new_rank = 0

                                                                   
    cmd = parts[0].split("@", 1)[0].lower() if parts else ""
    suffix = cmd.lstrip("/")[len("понизить"):]
    if suffix.isdigit():
        new_rank = int(suffix)
        target_token = parts[1] if len(parts) > 1 else None
    else:
        if len(parts) > 1 and parts[1].isdigit():
            new_rank = int(parts[1])
            target_token = parts[2] if len(parts) > 2 else None
        else:
            target_token = parts[1] if len(parts) > 1 else None

    if new_rank < 0 or new_rank > 3:
        bot.reply_to(message, "❗ Новый ранг должен быть 1, 2 или 3. Для полного снятия прав используй /понизить без ранга.")
        return

    if target is None and target_token:
        if target_token.lstrip("-").isdigit():
            bot.reply_to(message, "❌ Числовые ID отключены. Используй reply или @username.")
            return
        if target_token.startswith("@"):
            known = DATA.get("users", {}).get(str(message.chat.id), {})
            found = next((v for v in known.values() if str(v.get("username") or "").lstrip("@").lower() == target_token[1:].lower()), None)
            if found:
                target = types.SimpleNamespace(id=int(found["id"]), first_name=found.get("first_name") or target_token)

    if target is None:
        bot.reply_to(message, "❗ Укажи цель: reply или @username.")
        return
    if target.id == message.from_user.id:
        bot.reply_to(message, "🤨 Себя понижать этой командой нельзя.")
        return
    if is_chat_creator(message.chat.id, target.id):
        bot.reply_to(message, "❌ Создателя чата нельзя понизить.")
        return

                                                                        
    if not is_bot_creator(message.from_user.id):
        caller_rank = get_admin_rank(message.chat.id, message.from_user.id)
        target_rank = get_admin_rank(message.chat.id, target.id)
        if target_rank >= caller_rank:
            bot.reply_to(message, "🚫 Нельзя понижать администратора с рангом, равным или выше твоего.")
            return

    rank_permissions = {
        1: dict(can_change_info=False, can_delete_messages=True, can_invite_users=False,
                can_restrict_members=False, can_pin_messages=False, can_promote_members=False,
                can_manage_chat=False, can_manage_video_chats=False),
        2: dict(can_change_info=False, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False,
                can_manage_chat=True, can_manage_video_chats=True),
        3: dict(can_change_info=True, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False,
                can_manage_chat=True, can_manage_video_chats=True),
    }
    try:
        bot_member = bot.get_chat_member(message.chat.id, bot.get_me().id)
        if bot_member.status != "administrator" or not getattr(bot_member, "can_promote_members", False):
            bot.reply_to(message, "⚠️ Боту нужны права администратора с разрешением «Добавлять администраторов».")
            return
        if new_rank == 0:
            bot.promote_chat_member(
                message.chat.id, target.id,
                can_change_info=False, can_post_messages=False, can_edit_messages=False,
                can_delete_messages=False, can_invite_users=False, can_restrict_members=False,
                can_pin_messages=False, can_promote_members=False, can_manage_chat=False,
                can_manage_video_chats=False
            )
            DATA.get("admin_ranks", {}).setdefault(str(message.chat.id), {}).pop(str(target.id), None)
            result = "админские права полностью сняты"
        else:
            bot.promote_chat_member(message.chat.id, target.id, **rank_permissions[new_rank])
            DATA.get("admin_ranks", {}).setdefault(str(message.chat.id), {})[str(target.id)] = new_rank
            result = f"понижен до ранга {new_rank}/4"
        save_data()
        bot.reply_to(message, f"⬇️ <b>{html.escape(target.first_name or str(target.id))}</b>: {result}.", parse_mode="HTML")
        send_log("DEMOTE", message.from_user, target, result, message.chat)
    except Exception as e:
        bot.reply_to(message, f"❌ Не удалось изменить права администратора.\n{e}")


@bot.message_handler(commands=["ранг", "rank"])
def show_rank(message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    if not message.reply_to_message and len((message.text or "").split()) > 1:
        token = (message.text or "").split()[1]
        if token.lstrip("-").isdigit():
            bot.reply_to(message, "❌ Числовые ID отключены. Используй reply или @username.")
            return
        if token.startswith("@"):
            known = DATA.get("users", {}).get(str(message.chat.id), {})
            found = next((v for v in known.values() if str(v.get("username") or "").lstrip("@").lower() == token[1:].lower()), None)
            if found:
                target = types.SimpleNamespace(id=int(found["id"]), first_name=found.get("first_name") or token)
            else:
                bot.reply_to(message, f"⚠️ Не удалось найти {token}. Пользователь должен хотя бы один раз написать в этом чате при работающем боте.")
                return
    rank = get_admin_rank(message.chat.id, target.id)
    if rank == 0:
        bot.reply_to(message, f"👤 {html.escape(target.first_name or str(target.id))} — не администратор.", parse_mode="HTML")
    else:
        names = {1: "Младший админ", 2: "Админ", 3: "Старший админ", 4: "Главный админ"}
        bot.reply_to(message, f"⭐ {html.escape(target.first_name or str(target.id))} — <b>{names[rank]}</b>, ранг {rank}/4.", parse_mode="HTML")


                                                              
                   
                                                              

@bot.message_handler(commands=["acmd"])
def admin_commands(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "⚠️ Ошибка! Проверьте написанное.")
        return
    bot.reply_to(
        message,
        "🛡️ <b>Команды для администраторов</b>\n\n"
        "/ban /бан — бан\n/unban — снять бан\n/mute /мут — мут\n/unmute /размут — снять мут\n"
        "/алл /all — упомянуть участников\n/staff — список админов\n/id — ID\n"
        "/участники — участники\n/актив — активные\n"
        "/повысить1–4 /повысить /promote /rang — повышение\n"
        "/понизить /разжаловать — снятие или понижение админки\n"
        "/ранг /rank — узнать ранг",
        parse_mode="HTML"
    )

@bot.message_handler(commands=["cmdfull"])
def full_commands(message):
    if not is_bot_creator(message.from_user.id):
        bot.reply_to(message, "⚠️ Ошибка! Проверьте написанное.")
        return
    bot.reply_to(
        message,
        "👑 <b>Полный список команд RIS</b>\n\n"
        "/start /help /хелп /помощь\n/id /staff /участники /актив\n"
        "/ban /бан /unban /mute /мут /unmute /размут\n"
        "/повысить /promote /rang /понизить /разжаловать /ранг /алл /all\n"
        "/сменитьник /мойник /баланс /приз /варн /тест /правила\n"
        "/рассылка — везде\n/рассылкалс — в ЛС пользователей\n"
        "/рассылкагруппа — в группы\n/массрассылка — ЛС + группы",
        parse_mode="HTML"
    )

                                                              
                                  
                                                              

def _owner_only(message):
    return is_bot_creator(message.from_user.id)

def _broadcast_payload(message):
    raw = message.text or message.caption or ""
    parts = raw.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else ""

def _send_broadcast(message, target_type):
    if not _owner_only(message):
        return
    text = _broadcast_payload(message)
    if not text:
        bot.reply_to(message, "⚠️ Ошибка! Проверьте написанное.")
        return

    if target_type in ("users", "all"):
        users = list(DATA.get("known_users", {}).keys())
    else:
        users = []
    if target_type in ("groups", "all"):
        groups = list(DATA.get("known_chats", {}).keys())
    else:
        groups = []

    sent = failed = 0
    for uid in users:
        try:
            bot.send_message(int(uid), text)
            sent += 1
        except Exception as e:
            failed += 1
            print(f"[ERROR] ЛС-рассылка {uid}: {e}")
    for cid in groups:
        try:
            bot.send_message(int(cid), text)
            sent += 1
        except Exception as e:
            failed += 1
            print(f"[ERROR] Групповая рассылка {cid}: {e}")

    bot.reply_to(message, f"📢 Рассылка завершена.\nУспешно: {sent}\nОшибок: {failed}")

@bot.message_handler(commands=["рассылкалс"])
def broadcast_users(message):
    _send_broadcast(message, "users")

@bot.message_handler(commands=["рассылкагруппа"])
def broadcast_groups(message):
    _send_broadcast(message, "groups")

@bot.message_handler(commands=["массрассылка"])
def broadcast_everywhere(message):
    _send_broadcast(message, "all")

@bot.message_handler(commands=["рассылка", "broadcast"])
def broadcast_all_chats(message):
                                                      
    _send_broadcast(message, "all")


                                                              
                                                  
                                                              

@bot.message_handler(commands=["алл", "all"])
def mention_all(message):
    _mention_all_impl(message)


def _mention_all_impl(message):
    if not is_admin(message.chat.id, message.from_user.id):
        return

    command_text = message.text or message.caption or ""
    parts = command_text.split(maxsplit=1)
    broadcast_text = parts[1] if len(parts) > 1 else "Внимание, все!"

    chat_key = str(message.chat.id)
    users = DATA["users"].get(chat_key, {})
    if not users:
        bot.reply_to(message, "⚠️ Ошибка! Проверьте написанное.\nБот ещё не видел сообщений участников этого чата.")
        return

    user_ids = list(users.keys())
    chunk_size = 50

    try:
        for i in range(0, len(user_ids), chunk_size):
            chunk = user_ids[i:i + chunk_size]
            mentions = "".join(f'<a href="tg://user?id={uid}">\u200c</a>' for uid in chunk)
            prefix = broadcast_text if i == 0 else ""
            caption = f"{prefix}{mentions}"

                                                                             
            if i == 0 and message.content_type == "photo":
                bot.send_photo(message.chat.id, message.photo[-1].file_id, caption=caption, parse_mode="HTML")
            elif i == 0 and message.content_type == "document":
                bot.send_document(message.chat.id, message.document.file_id, caption=caption, parse_mode="HTML")
            elif i == 0 and message.content_type == "video":
                bot.send_video(message.chat.id, message.video.file_id, caption=caption, parse_mode="HTML")
            elif i == 0 and message.content_type == "animation":
                bot.send_animation(message.chat.id, message.animation.file_id, caption=caption, parse_mode="HTML")
            elif i == 0 and message.content_type == "audio":
                bot.send_audio(message.chat.id, message.audio.file_id, caption=caption, parse_mode="HTML")
            else:
                bot.send_message(message.chat.id, caption, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, "⚠️ Ошибка! Проверьте написанное.\nНе удалось выполнить /алл.")
        print(f"[ERROR] /алл: {e}")


@bot.message_handler(
    func=lambda m: (m.content_type in ("photo", "document", "video", "animation", "audio") and
                    ((m.caption or "").lstrip().lower().startswith(("/алл", "/all", "алл", "all")))),
    content_types=["photo", "document", "video", "animation", "audio"]
)
def mention_all_media(message):
    _mention_all_impl(message)


                                                              
                                                      
                                                              

@bot.message_handler(func=lambda m: (
    m.content_type == "text" and
    (m.text or "").lstrip().split()[0].split("@", 1)[0].lower() in (
        "/повысить", "/promote", "/rang",
        "/повысить1", "/повысить2", "/повысить3", "/повысить4",
        "повысить", "повысить1", "повысить2", "повысить3", "повысить4"
    )
))
def promote_user(message):
    """
    Повышение по рангам 1–4.
    Цель: реплай или @username.
    Поддерживает /повысить4, /повысить 4, /rang 4 и /promote 4.
    """
    if not (is_chat_creator(message.chat.id, message.from_user.id) or
            is_bot_creator(message.from_user.id)):
        bot.reply_to(message,
            "⚠️ Ошибка! Проверьте написанное.\n"
            "🚫 Менять ранги может только создатель чата или создатель бота.")
        return

    parts = (message.text or "").strip().split()
    if not parts:
        return
    cmd = parts[0].split("@", 1)[0].lower()
    rank = None
    target_token = None

    if cmd.lstrip("/").startswith("повысить") and cmd.lstrip("/")[len("повысить"):].isdigit():
        rank = int(cmd.lstrip("/")[len("повысить"):])
        target_token = parts[1] if len(parts) > 1 else None
    elif cmd in ("/повысить", "/rang", "/promote", "повысить", "rang", "promote"):
        rank = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
        target_token = parts[2] if len(parts) > 2 else None

    if rank is None or not 1 <= rank <= 4:
        bot.reply_to(message,
            "❗ Ранг должен быть от 1 до 4.\n"
            "Примеры: /повысить4 (реплай), /rang 4 @username, /promote 3 @username")
        return

                             
    target = message.reply_to_message.from_user if message.reply_to_message else None

    if target is None and target_token:
        if target_token.lstrip("-").isdigit():
            bot.reply_to(message, "❌ Числовые ID отключены. Используй reply или @username.")
            return
        if target_token.startswith("@"):
            known = DATA.get("users", {}).get(str(message.chat.id), {})
            found = next((v for v in known.values() if str(v.get("username") or "").lstrip("@").lower() == target_token[1:].lower()), None)
            if found:
                target = types.SimpleNamespace(id=int(found["id"]), first_name=found.get("first_name") or target_token)

    if target is None:
        bot.reply_to(message, "❗ Укажи цель: ответь на сообщение или укажи @username.")
        return

    if target.id == message.from_user.id:
        bot.reply_to(message, "🤨 Самому себе ранг менять нельзя.")
        return

                                                                   
    if not is_bot_creator(message.from_user.id):
        try:
            requester = bot.get_chat_member(message.chat.id, message.from_user.id)
            if requester.status != "creator" and rank >= 4:
                bot.reply_to(message, "⚠️ Только создатель чата или создатель бота может выдать ранг 4.")
                return
        except Exception:
            bot.reply_to(message, "⚠️ Ошибка! Проверьте написанное.")
            return

    rank_permissions = {
        1: dict(can_change_info=False, can_delete_messages=True, can_invite_users=False,
                can_restrict_members=False, can_pin_messages=False, can_promote_members=False,
                can_manage_chat=False, can_manage_video_chats=False),
        2: dict(can_change_info=False, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False,
                can_manage_chat=True, can_manage_video_chats=True),
        3: dict(can_change_info=True, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False,
                can_manage_chat=True, can_manage_video_chats=True),
        4: dict(can_change_info=True, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=True,
                can_manage_chat=True, can_manage_video_chats=True)
    }

    try:
                                                                   
        bot_member = bot.get_chat_member(message.chat.id, bot.get_me().id)
        if bot_member.status != "administrator" or not getattr(bot_member, "can_promote_members", False):
            bot.reply_to(message, "⚠️ Боту нужны права администратора с разрешением «Добавлять администраторов».")
            return

        bot.promote_chat_member(message.chat.id, target.id, **rank_permissions[rank])
        bot.reply_to(message, f"⭐ {target.first_name} повышен до ранга {rank}/4.")
        send_log(f"PROMOTE RANK {rank}", message.from_user, target, f"Ранг {rank}", message.chat)
    except Exception as e:
        print(f"[ERROR] Повышение {message.chat.id}/{target.id}: {e}")
        bot.reply_to(message, "⚠️ Ошибка! Проверьте написанное.")


                                                              
                   
                                                              

PERIODS = {
    "день": timedelta(days=1),
    "дня": timedelta(days=1),
    "неделя": timedelta(weeks=1),
    "недели": timedelta(weeks=1),
    "месяц": timedelta(days=30),
    "месяца": timedelta(days=30),
    "day": timedelta(days=1),
    "days": timedelta(days=1),
    "week": timedelta(weeks=1),
    "weeks": timedelta(weeks=1),
    "month": timedelta(days=30),
    "months": timedelta(days=30),
}


def format_timedelta(seconds):

    seconds = int(seconds)
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60

    parts = []

    if days:
        parts.append(f"{days} д")

    if hours:
        parts.append(f"{hours} ч")

    if not days:
        parts.append(f"{minutes} мин")

    return " ".join(parts)


TRACKING_NOTE = (
    "\nℹ️ Список основан только на участниках, которые писали "
    "в чате при работающем боте."
)


@bot.message_handler(commands=["актив", "active"])
def active_list(message):

    parts = message.text.split(maxsplit=1)
    period_key = parts[1].lower().strip() if len(parts) > 1 else "день"
    period = PERIODS.get(period_key)

    if period is None:
        bot.reply_to(
            message,
            "❗ Укажи период: день, неделя или месяц.\n"
            "Пример: /актив неделя"
        )
        return

    chat_key = str(message.chat.id)
    users = DATA["users"].get(chat_key, {})
    now = datetime.now().timestamp()
    threshold = period.total_seconds()

                                                                      
                                                                            
    active = [
        info for info in users.values()
        if info.get("message_count", 0) >= 5
        and now - info.get("last_seen", 0) <= threshold
    ]

    if not active:
        bot.reply_to(
            message,
            f"😴 За последние {period_key} активных участников с 5+ сообщениями не найдено."
        )
        return

    active.sort(key=lambda info: info.get("message_count", 0), reverse=True)

    lines = [
        f"🔥 Активные за последние {period_key} (5+ сообщений):\n"
    ]

    for info in active[:20]:
        user_id = str(info.get("id", ""))
        profile = DATA.get("profiles", {}).get(user_id, {})
        label = profile.get("nickname") or info.get("first_name") or info.get("username") or "???"
        count = int(info.get("message_count", 0) or 0)
        lines.append(f"— {html.escape(label)} — {count} сообщений")

    lines.append(TRACKING_NOTE)
    bot.reply_to(message, "\n".join(lines), parse_mode="HTML")


                                                              
            
                                                              

def is_probably_deleted(chat_id, user_id):
    """
    Грубая эвристика для определения удалённого аккаунта:
    Bot API не имеет отдельного флага "аккаунт удалён",
    но для таких пользователей get_chat_member обычно
    возвращает пустое имя/плейсхолдер или падает с ошибкой.
    """

    try:
        member = bot.get_chat_member(chat_id, user_id)

    except Exception:
        return True

    user = member.user

    if not user.first_name or user.first_name == "Deleted Account":
        return True

    return False


@bot.message_handler(commands=["участники", "members"])
def members_list(message):

    chat_key = str(message.chat.id)
    users = DATA["users"].get(chat_key, {})

    if not users:
        bot.reply_to(
            message,
            "Пока нет данных об участниках — бот ещё "
            "не видел их сообщений в этом чате."
        )
        return

    lines = ["👥 Известные участники чата:\n"]

    for user_id_str, info in users.items():

        if is_probably_deleted(message.chat.id, int(user_id_str)):
            continue

        username = info.get("username")
        user_profile = DATA.get("profiles", {}).get(user_id_str, {})
        name = user_profile.get("nickname") or info.get("first_name", "???")

        link = (
            f"https://t.me/{username}"
            if username
            else f"tg://user?id={user_id_str}"
        )

        lines.append(f"— {html.escape(name)}: {link}")

    lines.append(TRACKING_NOTE)

    text = "\n".join(lines)

                                                               
    for i in range(0, len(text), 4000):
        bot.send_message(
            message.chat.id,
            text[i:i + 4000],
            parse_mode="HTML"
        )


                                                              
                                         
                                                              

_TEXT_COMMAND_ALIASES = {
              
    "start": start, "help": help_command, "хелп": help_command, "помощь": help_command,
               
    "ban": ban_user, "бан": ban_user, "unban": unban_user, "разбан": unban_user,
    "mute": mute_user, "мут": mute_user, "unmute": unmute_user, "размут": unmute_user,
                         
    "+ник": change_nickname, "сменитьник": change_nickname,
    "ник": my_nickname, "мойник": my_nickname,
    "баланс": balance, "balance": balance, "coins": balance, "приз": prize, "prize": prize, "выдатькоин": give_coins,
    "варн": warn_user, "warn": warn_user, "тест": bot_test, "test": bot_test, "правила": show_rules, "rules": show_rules,
                
    "id": show_id, "staff": staff_list, "участники": members_list, "members": members_list,
    "актив": active_list, "active": active_list,
    "ранг": show_rank, "rank": show_rank, "понизить": demote_user, "разжаловать": demote_user, "demote": demote_user,
                           
    "acmd": admin_commands, "cmdfull": full_commands,
    "рассылкалс": broadcast_users, "рассылкагруппа": broadcast_groups,
    "массрассылка": broadcast_everywhere, "рассылка": broadcast_all_chats, "broadcast": broadcast_all_chats,
    "алл": mention_all, "all": mention_all,
               
    "повысить": promote_user, "promote": promote_user, "rang": promote_user,
    "повысить1": promote_user, "повысить2": promote_user, "повысить3": promote_user, "повысить4": promote_user,
}


@bot.message_handler(func=lambda m: (
    m.content_type == "text" and bool((m.text or "").strip()) and
    (m.text or "").strip().split()[0].split("@", 1)[0].lower().lstrip("/") in _TEXT_COMMAND_ALIASES
))
def text_command_alias(message):
    """Маршрутизирует команды, написанные без /, в существующие обработчики."""
    first = (message.text or "").strip().split()[0].split("@", 1)[0].lower().lstrip("/")
    handler = _TEXT_COMMAND_ALIASES.get(first)
    if handler:
        handler(message)


                                                              
        
                                                              

def run_health_server():
    port = int(os.getenv("PORT", "10000"))

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = b"RISBOT 51 OK"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"HTTP health server: port {port}")
    server.serve_forever()


def run_bot():
    print("=================================")
    print("🤖 RIS запущен!")
    print(f"pyTelegramBotAPI: {TELEBOT_VERSION}")
    print(f"👑 Создатель бота: {OWNER_USERNAME} (ID {OWNER_ID})")
    print("=================================")

    while True:
        try:
            me = bot.get_me()
            print(f"Telegram: @{me.username} (ID {me.id})")
            if LOG_CHAT_CONFIGURED:
                print(f"Логи: {LOG_CHAT_ID}")
            else:
                print("⚠️ LOG_CHAT_ID не настроен — логи модерации отправляться не будут.")

            try:
                bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
            except TypeError:
                bot.infinity_polling(skip_pending=True)
        except KeyboardInterrupt:
            print("🛑 RIS остановлен.")
            break
        except Exception as e:
            print(f"❌ Ошибка соединения с Telegram: {e}")
            print("🔄 Повторная попытка через 10 секунд...")
            time.sleep(10)


if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    run_bot()
