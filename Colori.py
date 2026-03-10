from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
import random

# ==================== CONFIGURAZIONE ====================

# 🔴 ID DEGLI ADMIN AUTORIZZATI
ADMIN_IDS = [6710922454, 7127377678, 1059198431, 6499718935, 5631411226]

# Colori disponibili (9 totali)
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
DEFAULT_LENGTH = 7  # Default: 7 colori
MIN_LENGTH = 7
MAX_LENGTH = 9

# ================================================================

# Stato del gioco per ogni chat
games = {}

def get_game(chat_id):
    if chat_id not in games:
        games[chat_id] = {
            'target_combo': None,
            'combo_length': DEFAULT_LENGTH,  # Lunghezza scelta (7/8/9)
            'starter_id': None,
            'starter_name': None,
            'found_count': 0,  # Quanti colori in fila sono stati trovati (0-7/8/9)
            'current_progress': [],  # Lista dei colori trovati finora
            'winner': None,
            'attempts_count': 0
        }
    return games[chat_id]

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def normalize_input(text: str) -> str:
    return text.strip().replace(' ', '').replace('\n', '')

def validate_combination(text: str, expected_length: int) -> tuple:
    """
    Valida l'input dell'utente
    """
    clean_text = normalize_input(text)
    
    # Estrai solo gli emoji colori
    found_colors = []
    for char in clean_text:
        if char in COLOR_EMOJIS:
            found_colors.append(char)
    
    # Controlla lunghezza
    if len(found_colors) != expected_length:
        return False, [], f"Devi inserire esattamente {expected_length} colori! (hai messo {len(found_colors)})"
    
    # Controlla duplicati
    if len(set(found_colors)) != len(found_colors):
        return False, [], "I colori non devono ripetersi!"
    
    return True, found_colors, ""

def format_progress(found_count: int, total: int, progress_list: list) -> str:
    """Formatta la barra di progresso"""
    # Colori trovati + ❓ per quelli mancanti
    display = progress_list.copy()
    while len(display) < total:
        display.append('❓')
    return ' '.join(display)

def format_combo(combo: list) -> str:
    return ' '.join(combo)

async def setcolors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Imposta il numero di colori (7, 8 o 9) - SOLO ADMIN"""
    user = update.message.from_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Solo gli admin possono usare questo comando!")
        return
    
    chat_id = update.message.chat_id
    game = get_game(chat_id)
    
    # Controlla se c'è una partita attiva
    if game['target_combo'] is not None:
        await update.message.reply_text(
            "❌ Non puoi cambiare durante una partita!\n"
            "Termina prima con /end"
        )
        return
    
    # Parsing argomento
    if not context.args:
        await update.message.reply_text(
            f"🎨 *Imposta numero colori*\n\n"
            f"Attuale: *{game['combo_length']}* colori\n\n"
            f"Uso: `/setcolors [7-9]`\n"
            f"Esempio: `/setcolors 8`",
            parse_mode="Markdown"
        )
        return
    
    try:
        new_length = int(context.args[0])
        if new_length < MIN_LENGTH or new_length > MAX_LENGTH:
            await update.message.reply_text(
                f"⚠️ Devi scegliere un numero tra {MIN_LENGTH} e {MAX_LENGTH}!"
            )
            return
        
        game['combo_length'] = new_length
        await update.message.reply_text(
            f"✅ *Impostato: {new_length} colori*\n\n"
            f"Usa /start per iniziare la partita!",
            parse_mode="Markdown"
        )
        
    except ValueError:
        await update.message.reply_text("❌ Inserisci un numero valido! (7, 8 o 9)")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Avvia una nuova partita - SOLO ADMIN"""
    user = update.message.from_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Solo gli admin possono avviare il gioco!")
        return
    
    chat_id = update.message.chat_id
    game = get_game(chat_id)
    
    length = game['combo_length']
    
    # Genera combinazione casuale senza ripetizioni
    game['target_combo'] = random.sample(COLOR_EMOJIS, length)
    game['starter_id'] = user.id
    game['starter_name'] = user.first_name
    game['found_count'] = 0
    game['current_progress'] = []
    game['winner'] = None
    game['attempts_count'] = 0
    
    target = game['target_combo']
    
    # Manda la combinazione in privato all'admin
    private_sent = False
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=f"🎨 *COMBINAZIONE SEGRETA ({length} colori)*\n\n"
                 f"{format_combo(target)}\n\n"
                 f"Non rivelarla a nessuno! 🤫\n\n"
                 f"🔢 Ordine: 1°→2°→3°→... sequenziale!",
            parse_mode="Markdown"
        )
        private_sent = True
    except Exception:
        pass
    
    # Messaggio in gruppo
    progress_display = format_progress(0, length, [])
    
    info_text = (
        f"🎨 *COLOR MASTER* 🎨\n\n"
        f"👤 Organizzatore: {user.first_name}\n"
        f"🎯 Combinazione: *{length} colori diversi*\n"
        f"📊 Progresso: {progress_display}\n\n"
        f"*Colori disponibili:*\n"
        f"{' '.join(COLOR_EMOJIS)}\n\n"
        f"*🎮 REGOLA SPECIALE:*\n"
        f"_I colori vengono svelati in ORDINE!_\n"
        f"_Prima il 1°, poi il 2°, poi il 3°..._\n"
        f"_Non puoi sapere il 4° prima di aver trovato il 3°!_\n\n"
        f"*Come giocare:*\n"
        f"Scrivi i {length} colori in ordine\n"
        f"Esempio: `{'🔴🟢🔵🟡🟣⚪🟤'[:length*2]}`\n\n"
        f"_Il gruppo scopre la combinazione IN FILA!_"
    )
    
    if not private_sent:
        info_text += "\n\n⚠️ L'organizzatore deve avviarmi in privato!"
    
    await update.message.reply_text(info_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce i tentativi dei giocatori - ORDINE SEQUENZIALE OBBLIGATORIO"""
    chat_id = update.message.chat_id
    game = get_game(chat_id)
    user = update.message.from_user
    
    # Nessuna partita attiva
    if game['target_combo'] is None:
        return
    
    # Partita già vinta
    if game['winner'] is not None:
        return
    
    length = game['combo_length']
    
    # Validazione input
    text = update.message.text
    valid, attempt, error = validate_combination(text, length)
    
    if not valid:
        return  # Silenzioso se non valido
    
    game['attempts_count'] += 1
    target = game['target_combo']
    found_count = game['found_count']
    
    # 🔴 CONTROLLO SEQUENZIALE
    # Verifica solo la prossima posizione da scoprire
    next_position = found_count  # 0-based: se ho trovato 3, controllo la 3 (la 4ª)
    
    new_discoveries = []
    
    # Controllo rigoroso: solo in ordine 1→2→3→4→5→6→7...
    if next_position < length:
        # Controllo la prossima posizione richiesta
        if attempt[next_position] == target[next_position]:
            # TROVATO! Aggiungi alla lista
            new_discoveries.append(next_position)
            game['current_progress'].append(attempt[next_position])
            game['found_count'] += 1
            
            # Ora controlla se con questo tentativo ha trovato anche i successivi
            # (se ha azzeccato la sequenza in fila)
            check_pos = next_position + 1
            while check_pos < length and attempt[check_pos] == target[check_pos]:
                new_discoveries.append(check_pos)
                game['current_progress'].append(attempt[check_pos])
                game['found_count'] += 1
                check_pos += 1
    
    # Verifica vittoria
    if game['found_count'] == length:
        # VITTORIA!
        game['winner'] = user.first_name
        
        await update.message.reply_text(
            f"🎉🎉🎉 *COMBINAZIONE COMPLETATA!* 🎉🎉🎉\n\n"
            f"👤 *{user.first_name}* ha trovato l'ultimo colore!\n\n"
            f"🎨 Combinazione: {format_combo(target)}\n"
            f"🏆 Vincitore: *{user.first_name}*\n"
            f"📊 Tentativi totali: {game['attempts_count']}",
            parse_mode="Markdown"
        )
        return
    
    # Messaggio di progresso
    if new_discoveries:
        progress_display = format_progress(game['found_count'], length, game['current_progress'])
        
        # Formatta le posizioni trovate (1-based per leggibilità)
        positions_str = ', '.join([str(p+1) + '°' for p in new_discoveries])
        
        # Messaggio diverso se è il primo o successivi
        if len(new_discoveries) == 1 and new_discoveries[0] == 0:
            # Primo colore trovato!
            await update.message.reply_text(
                f"🎯 *PRIMO COLORE TROVATO!*\n\n"
                f"👤 {user.first_name}\n"
                f"✅ Posizione 1°: *{game['current_progress'][0]}*\n\n"
                f"📊 Progresso: {progress_display}\n"
                f"🔍 Trovati: {game['found_count']}/{length}\n"
                f"🎲 Tentativo #{game['attempts_count']}\n\n"
                f"_Ora tutti sanno che inizia con {game['current_progress'][0]}!_",
                parse_mode="Markdown"
            )
        else:
            # Colori successivi
            await update.message.reply_text(
                f"✅ *NUOVO COLORE!* {'✅' * len(new_discoveries)}\n\n"
                f"👤 {user.first_name}\n"
                f"🎯 Posizione {positions_str} trovata!\n\n"
                f"📊 Progresso: {progress_display}\n"
                f"🔍 Trovati: {game['found_count']}/{length}\n"
                f"🎲 Tentativo #{game['attempts_count']}",
                parse_mode="Markdown"
            )
    else:
        # Nessun progresso - reazione silenziosa
        try:
            await update.message.set_reaction("🤔")
        except:
            pass

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra lo stato attuale"""
    chat_id = update.message.chat_id
    game = get_game(chat_id)
    
    if game['target_combo'] is None:
        current_length = game.get('combo_length', DEFAULT_LENGTH)
        await update.message.reply_text(
            f"🎨 Nessuna partita attiva.\n"
            f"Impostato: *{current_length}* colori\n"
            f"Solo gli admin possono avviare con /start"
        )
        return
    
    length = game['combo_length']
    progress_display = format_progress(game['found_count'], length, game['current_progress'])
    organizer = game['starter_name'] or "Sconosciuto"
    
    status_text = (
        f"📊 *STATO PARTITA*\n\n"
        f"👤 Organizzatore: {organizer}\n"
        f"🎯 Lunghezza: {length} colori\n"
        f"📊 Progresso: {progress_display}\n"
        f"🔍 Trovati: {game['found_count']}/{length}\n"
        f"🎲 Tentativi: {game['attempts_count']}\n"
    )
    
    if game['winner']:
        status_text += f"\n🏆 Vincitore: *{game['winner']}*"
    else:
        # Mostra qual è il prossimo colore da trovare
        next_pos = game['found_count'] + 1
        status_text += f"\n⏳ Prossimo obiettivo: *{next_pos}° colore*"
        status_text += f"\n\n*Colori disponibili:*\n{' '.join(COLOR_EMOJIS)}"
    
    await update.message.reply_text(status_text, parse_mode="Markdown")

async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Termina la partita - SOLO ADMIN"""
    user = update.message.from_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Solo gli admin possono terminare il gioco!")
        return
    
    chat_id = update.message.chat_id
    game = get_game(chat_id)
    
    if game['target_combo'] is None:
        await update.message.reply_text("❌ Nessuna partita attiva!")
        return
    
    target = game['target_combo']
    length = game['combo_length']
    
    await update.message.reply_text(
        f"🛑 *PARTITA TERMINATA*\n\n"
        f"🎨 La combinazione era: {format_combo(target)}\n"
        f"📏 Lunghezza: {length} colori\n"
        f"👤 Organizzatore: {game['starter_name']}\n"
        f"📊 Tentativi totali: {game['attempts_count']}",
        parse_mode="Markdown"
    )
    
    # Reset
    games[chat_id] = {
        'target_combo': None,
        'combo_length': game['combo_length'],  # Mantieni l'ultima impostazione
        'starter_id': None,
        'starter_name': None,
        'found_count': 0,
        'current_progress': [],
        'winner': None,
        'attempts_count': 0
    }

def main():
    TOKEN = "8731861433:AAFlCOxdcnnkTkcnE7UI_n8nmjDFsPYeZUA"
    
    application = Application.builder().token(TOKEN).build()
    
    # Handler comandi
    application.add_handler(CommandHandler("setcolors", setcolors))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("end", end_game))
    
    # Handler messaggi
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🎨 Color Master Bot avviato!")
    print(f"🎯 Default: {DEFAULT_LENGTH} colori (7-9 settabili)")
    print("📝 Comandi: /setcolors | /start (admin) | /status | /end (admin)")
    print("🔒 Ordine sequenziale: 1°→2°→3°→...")
    application.run_polling()

if __name__ == '__main__':
    main()
