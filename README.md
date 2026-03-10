# Danyela-
Ok
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
import random
import os

ADMIN_IDS = [6710922454, 7127377678, 1059198431, 6499718935, 5631411226]

COLORS = {
    '⚪': 'bianco',
    '🟤': 'marrone', 
    '🔴': 'rosso',
    '🟠': 'arancione',
    '🟡': 'giallo',
    '🟢': 'verde',
    '🔵': 'blu',
    '🟣': 'viola',
    '⚫': 'nero'
}

COLOR_EMOJIS = list(COLORS.keys())
DEFAULT_LENGTH = 7
MIN_LENGTH = 7
MAX_LENGTH = 9

games = {}

def get_game(chat_id):
    if chat_id not in games:
        games[chat_id] = {
            'target_combo': None,
            'combo_length': DEFAULT_LENGTH,
            'starter_id': None,
            'starter_name': None,
            'found_count': 0,
            'current_progress': [],
            'winner': None,
            'attempts_count': 0
        }
    return games[chat_id]

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def normalize_input(text: str) -> str:
    return text.strip().replace(' ', '').replace('\n', '')

def validate_combination(text: str, expected_length: int) -> tuple:
    clean_text = normalize_input(text)
    found_colors = []
    for char in clean_text:
        if char in COLOR_EMOJIS:
            found_colors.append(char)
    
    if len(found_colors) != expected_length:
        return False, [], f"Devi inserire esattamente {expected_length} colori!"
    
    if len(set(found_colors)) != len(found_colors):
        return False, [], "I colori non devono ripetersi!"
    
    return True, found_colors, ""

def format_progress(found_count: int, total: int, progress_list: list) -> str:
    display = progress_list.copy()
    while len(display) < total:
        display.append('❓')
    return ' '.join(display)

def format_combo(combo: list) -> str:
    return ' '.join(combo)

async def setcolors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Solo gli admin!")
        return
    
    chat_id = update.message.chat_id
    game = get_game(chat_id)
    
    if game['target_combo'] is not None:
        await update.message.reply_text("❌ Termina prima con /end")
        return
    
    if not context.args:
        await update.message.reply_text(
            f"🎨 *Imposta numero colori*\n\n"
            f"Attuale: *{game['combo_length']}*\n"
            f"Uso: `/setcolors [7-9]`",
            parse_mode="Markdown"
        )
        return
    
    try:
        new_length = int(context.args[0])
        if new_length < MIN_LENGTH or new_length > MAX_LENGTH:
            await update.message.reply_text(f"⚠️ Scegli tra {MIN_LENGTH} e {MAX_LENGTH}!")
            return
        
        game['combo_length'] = new_length
        await update.message.reply_text(
            f"✅ *Impostato: {new_length} colori*\nUsa /start!",
            parse_mode="Markdown"
        )
    except ValueError:
        await update.message.reply_text("❌ Numero valido! (7, 8 o 9)")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Solo gli admin!")
        return
    
    chat_id = update.message.chat_id
    game = get_game(chat_id)
    length = game['combo_length']
    
    game['target_combo'] = random.sample(COLOR_EMOJIS, length)
    game['starter_id'] = user.id
    game['starter_name'] = user.first_name
    game['found_count'] = 0
    game['current_progress'] = []
    game['winner'] = None
    game['attempts_count'] = 0
    
    target = game['target_combo']
    
    private_sent = False
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=f"🎨 *COMBINAZIONE ({length} colori)*\n\n{format_combo(target)}",
            parse_mode="Markdown"
        )
        private_sent = True
    except Exception:
        pass
    
    progress_display = format_progress(0, length, [])
    
    info_text = (
        f"🎨 *COLOR MASTER*\n\n"
        f"👤 Organizzatore: {user.first_name}\n"
        f"🎯 {length} colori | Progresso: {progress_display}\n\n"
        f"{' '.join(COLOR_EMOJIS)}\n\n"
        f"*🎮 REGOLA:* _Ordine sequenziale 1°→2°→3°..._\n"
        f"Scrivi: `{'🔴🟢🔵🟡🟣⚪🟤'[:length*2]}`"
    )
    
    if not private_sent:
        info_text += "\n\n⚠️ Avvia il bot in privato!"
    
    await update.message.reply_text(info_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    game = get_game(chat_id)
    user = update.message.from_user
    
    if game['target_combo'] is None or game['winner'] is not None:
        return
    
    length = game['combo_length']
    text = update.message.text
    valid, attempt, error = validate_combination(text, length)
    
    if not valid:
        return
    
    game['attempts_count'] += 1
    target = game['target_combo']
    found_count = game['found_count']
    next_position = found_count
    
    new_discoveries = []
    
    if next_position < length:
        if attempt[next_position] == target[next_position]:
            new_discoveries.append(next_position)
            game['current_progress'].append(attempt[next_position])
            game['found_count'] += 1
            
            check_pos = next_position + 1
            while check_pos < length and attempt[check_pos] == target[check_pos]:
                new_discoveries.append(check_pos)
                game['current_progress'].append(attempt[check_pos])
                game['found_count'] += 1
                check_pos += 1
    
    if game['found_count'] == length:
        game['winner'] = user.first_name
        await update.message.reply_text(
            f"🎉 *VITTORIA!* 🎉\n\n"
            f"🏆 {user.first_name}\n"
            f"🎨 {format_combo(target)}\n"
            f"📊 {game['attempts_count']} tentativi",
            parse_mode="Markdown"
        )
        return
    
    if new_discoveries:
        progress_display = format_progress(game['found_count'], length, game['current_progress'])
        positions_str = ', '.join([str(p+1) + '°' for p in new_discoveries])
        
        await update.message.reply_text(
            f"✅ *{positions_str} trovato!*\n\n"
            f"👤 {user.first_name}\n"
            f"📊 {progress_display}\n"
            f"🔍 {game['found_count']}/{length}",
            parse_mode="Markdown"
        )
    else:
        try:
            await update.message.set_reaction("🤔")
        except:
            pass

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    game = get_game(chat_id)
    
    if game['target_combo'] is None:
        await update.message.reply_text("🎨 Nessuna partita. /start per iniziare (admin)")
        return
    
    length = game['combo_length']
    progress_display = format_progress(game['found_count'], length, game['current_progress'])
    
    status_text = (
        f"📊 *STATO*\n\n"
        f"👤 {game['starter_name']}\n"
        f"📊 {progress_display}\n"
        f"🔍 {game['found_count']}/{length}\n"
        f"🎲 {game['attempts_count']} tentativi"
    )
    
    if game['winner']:
        status_text += f"\n🏆 {game['winner']}"
    else:
        status_text += f"\n⏳ Cerca il {game['found_count']+1}° colore"
        status_text += f"\n{' '.join(COLOR_EMOJIS)}"
    
    await update.message.reply_text(status_text, parse_mode="Markdown")

async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Solo admin!")
        return
    
    chat_id = update.message.chat_id
    game = get_game(chat_id)
    
    if game['target_combo'] is None:
        await update.message.reply_text("❌ Nessuna partita!")
        return
    
    await update.message.reply_text(
        f"🛑 *FINITO*\n\n"
        f"🎨 {format_combo(game['target_combo'])}\n"
        f"📊 {game['attempts_count']} tentativi"
    )
    
    games[chat_id] = {
        'target_combo': None,
        'combo_length': game['combo_length'],
        'starter_id': None,
        'starter_name': None,
        'found_count': 0,
        'current_progress': [],
        'winner': None,
        'attempts_count': 0
    }

def main():
    TOKEN = os.environ.get("BOT_TOKEN", "8731861433:AAFlCOxdcnnkTkcnE7UI_n8nmjDFsPYeZUA")
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("setcolors", setcolors))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("end", end_game))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🎨 Bot avviato su Railway!")
    application.run_polling()

if __name__ == '__main__':
    main()
