import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============================================================
# ⬇️⬇️⬇️ INSERISCI QUI IL TUO TOKEN ⬇️⬇️⬇️
TOKEN = "8324526218:AAFGRH8ZC1OocSQPssXlQu-opTbN2Yxsqg8"
# ============================================================

# ADMIN IDs autorizzati ad avviare partite
ADMIN_IDS = [6710922454, 7127377678, 1059198431, 6499718935, 5631411226]

# 30 FRUTTI
FRUTTI = [
    "🍎 Mela", "🍌 Banana", "🍇 Uva", "🍊 Arancia", "🍓 Fragola", 
    "🍑 Pesca", "🍒 Ciliegia", "🥝 Kiwi", "🍍 Ananas", "🥭 Mango",
    "🍉 Anguria", "🍋 Limone", "🍐 Pera", "🫐 Mirtillo", "🍈 Melone",
    "🥥 Cocco", "🥑 Avocado", "🍅 Pomodoro", "🍆 Melanzana", "🥒 Cetriolo",
    "🌶️ Peperoncino", "🌽 Mais", "🥕 Carota", "🧅 Cipolla", "🧄 Aglio",
    "🥔 Patata", "🍠 Patata Dolce", "🥜 Arachide", "🌰 Noce", "🫒 Oliva"
]

partite = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🐺🍎 *Lupo Mangia Frutta - Admin Only!*\n\n"
        "👑 *Solo gli admin possono avviare partite*\n"
        "👥 *Modalità multi-vincitore disponibile*\n\n"
        "🎮 /nuova - Avvia configurazione (solo admin)\n"
        "🛑 /stop - Ferma partita",
        parse_mode='Markdown'
    )

async def nuova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Solo admin possono avviare"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Solo gli admin possono avviare partite!")
        return
    
    if update.effective_chat.type == "private":
        await update.message.reply_text("👥 Usa questo comando in un gruppo!")
        return
    
    # Step 1: Quanti frutti?
    tastiera = [
        [InlineKeyboardButton("20 Frutti", callback_data="cfg:20")],
        [InlineKeyboardButton("30 Frutti", callback_data="cfg:30")]
    ]
    
    await update.message.reply_text(
        "🎮 *Nuova Partita - Step 1/3*\n\nQuanti frutti?",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(tastiera)
    )

async def config_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i vari step di configurazione"""
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    
    if query.data.startswith("cfg:"):
        num_frutti = int(query.data.split(":")[1])
        context.chat_data['temp'] = {'frutti': num_frutti}
        
        # Step 2: Quanti tentativi?
        tastiera = [
            [InlineKeyboardButton("1 Tentativo", callback_data="tent:1")],
            [InlineKeyboardButton("2 Tentativi", callback_data="tent:2")],
            [InlineKeyboardButton("3 Tentativi", callback_data="tent:3")]
        ]
        
        await query.edit_message_text(
            f"🎮 *Step 2/3*\nFrutti: *{num_frutti}*\n\nQuanti tentativi a testa?",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(tastiera)
        )
    
    elif query.data.startswith("tent:"):
        tentativi = int(query.data.split(":")[1])
        context.chat_data['temp']['tentativi'] = tentativi
        
        # Step 3: Quanti vincitori?
        tastiera = [
            [InlineKeyboardButton("🏆 1 Vincitore", callback_data="vinc:1")],
            [InlineKeyboardButton("🏆🏆 2 Vincitori", callback_data="vinc:2")],
            [InlineKeyboardButton("🏆🏆🏆 3 Vincitori", callback_data="vinc:3")],
            [InlineKeyboardButton("🏆🏆🏆🏆 4 Vincitori", callback_data="vinc:4")]
        ]
        
        await query.edit_message_text(
            f"🎮 *Step 3/3*\n"
            f"Frutti: *{context.chat_data['temp']['frutti']}*\n"
            f"Tentativi: *{tentativi}*\n\n"
            f"Quanti possono vincere?",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(tastiera)
        )
    
    elif query.data.startswith("vinc:"):
        num_vincitori = int(query.data.split(":")[1])
        temp = context.chat_data['temp']
        
        # Avvia partita
        await avvia_partita(query, chat_id, temp['frutti'], temp['tentativi'], num_vincitori, update.effective_user.id)

async def avvia_partita(query, chat_id, num_frutti, tentativi, num_vincitori, admin_id):
    """Avvia la partita e manda messaggio privato all'admin"""
    
    # Seleziona frutti casuali
    frutti_scelti = random.sample(FRUTTI, num_frutti)
    
    # Scegli N frutti vincenti (diversi tra loro)
    frutti_vincenti = random.sample(frutti_scelti, num_vincitori)
    
    # Salva partita - AGGIUNTO: frutti_provati per tenere traccia
    partite[chat_id] = {
        'frutti': frutti_scelti,
        'vincenti': frutti_vincenti,
        'vincitori_trovati': [],  # Lista di tuple (user_id, username, frutto)
        'tentativi_max': tentativi,
        'tentativi_giocatori': {},  # user_id: tentativi_usati
        'frutti_provati': {},  # user_id: set di indici frutti provati
        'attiva': True
    }
    
    # MESSAGGIO PRIVATO ALL'ADMIN
    vincenti_text = "\n".join([f"  {i+1}. {f}" for i, f in enumerate(frutti_vincenti)])
    
    try:
        bot = query._bot
        await bot.send_message(
            chat_id=admin_id,
            text=(
                f"🔐 *MESSAGGIO SEGRETO ADMIN* 🔐\n\n"
                f"👑 Hai avviato una partita nel gruppo!\n\n"
                f"🎯 *Frutti Vincenti ({num_vincitori}):*\n{vincenti_text}\n\n"
                f"🤫 *Non dirlo a nessuno!*"
            ),
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Errore messaggio privato: {e}")
    
    # Tastiera gruppo
    tastiera = crea_tastiera(frutti_scelti, partite[chat_id]['frutti_provati'], {})
    
    await query.edit_message_text(
        f"🎮 *PARTITA AVVIATA!* 🐺\n\n"
        f"📊 *Configurazione:*\n"
        f"• Frutti: *{num_frutti}*\n"
        f"• Tentativi a testa: *{tentativi}*\n"
        f"• Vincitori possibili: *{num_vincitori}* 🏆\n\n"
        f"_Il lupo ha scelto {num_vincitori} frutti segreti..._\n"
        f"_Chi li trova per primo vince!_\n\n"
        f"👇 *Clicca un frutto:*",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(tastiera)
    )

def crea_tastiera(frutti, frutti_provati, tentativi_giocatori):
    """Crea tastiera nascondendo frutti già provati"""
    tastiera = []
    riga = []
    
    for i, frutto in enumerate(frutti):
        # Controlla se qualcuno ha già provato questo frutto
        provato = False
        for user_id, frutti_set in frutti_provati.items():
            if i in frutti_set:
                provato = True
                break
        
        if provato:
            # Frutto già provato - mostra come disabilitato (❌)
            riga.append(InlineKeyboardButton(f"❌ {frutto}", callback_data="usato"))
        else:
            riga.append(InlineKeyboardButton(frutto, callback_data=f"try:{i}"))
        
        if len(riga) == 3:
            tastiera.append(riga)
            riga = []
    
    if riga:
        tastiera.append(riga)
    
    tastiera.append([InlineKeyboardButton("ℹ️ Info", callback_data="info")])
    return tastiera

async def tentativo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce tentativo giocatore"""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    # Ignora click su frutti già usati
    if query.data == "usato":
        await query.answer("❌ Questo frutto è già stato provato!", show_alert=True)
        return
    
    if chat_id not in partite or not partite[chat_id]['attiva']:
        await query.answer("❌ Nessuna partita!", show_alert=True)
        return
    
    partita = partite[chat_id]
    
    # Controlla se ha già vinto
    vincitori_ids = [v[0] for v in partita['vincitori_trovati']]
    if user_id in vincitori_ids:
        await query.answer("🏆 Hai già vinto! Aspetta la prossima partita.", show_alert=True)
        return
    
    # Controlla se tutti i vincitori sono stati trovati
    if len(partita['vincitori_trovati']) >= len(partita['vincenti']):
        await query.answer("🏁 Partita finita!", show_alert=True)
        return
    
    # Controlla tentativi
    usati = partita['tentativi_giocatori'].get(user_id, 0)
    if usati >= partita['tentativi_max']:
        await query.answer(f"⛔ {username}, hai esaurito tutti i tentativi ({partita['tentativi_max']}/{partita['tentativi_max']})!", show_alert=True)
        return
    
    # Ottieni frutto scelto
    frutto_idx = int(query.data.split(":")[1])
    frutto_scelto = partita['frutti'][frutto_idx]
    
    # Controlla se questo giocatore ha già provato questo frutto
    if user_id not in partita['frutti_provati']:
        partita['frutti_provati'][user_id] = set()
    
    if frutto_idx in partita['frutti_provati'][user_id]:
        await query.answer("❌ Hai già provato questo frutto!", show_alert=True)
        return
    
    # Registra frutto provato
    partita['frutti_provati'][user_id].add(frutto_idx)
    
    # Registra tentativo
    partita['tentativi_giocatori'][user_id] = usati + 1
    rimasti = partita['tentativi_max'] - partita['tentativi_giocatori'][user_id]
    
    # Controlla se è vincente
    if frutto_scelto in partita['vincenti']:
        # VITTORIA!
        partita['vincitori_trovati'].append((user_id, username, frutto_scelto))
        vincitori_rimanenti = len(partita['vincenti']) - len(partita['vincitori_trovati'])
        
        if vincitori_rimanenti == 0:
            # ULTIMO VINCITORE! Partita finita
            partita['attiva'] = False
            
            # Crea lista completa vincitori
            lista_vincitori = "\n".join([
                f"🏆 {i+1}. *{v[1]}* → {v[2]}" 
                for i, v in enumerate(partita['vincitori_trovati'])
            ])
            
            await query.edit_message_text(
                f"🎉🎉🎉 *PARTITA TERMINATA!* 🎉🎉🎉\n\n"
                f"👑 *TUTTI I VINCITORI ({len(partita['vincenti'])}):*\n"
                f"{lista_vincitori}\n\n"
                f"🐺: 'Complimenti a tutti!'\n\n"
                f"/nuova per rigiocare!"
            )
        else:
            # VINCITA PARZIALE
            await query.answer(f"🎉 HAI VINTO! Trovato: {frutto_scelto}", show_alert=True)
            
            # Aggiorna tastiera (rimuovi frutto vincente)
            tastiera = crea_tastiera(partita['frutti'], partita['frutti_provati'], partita['tentativi_giocatori'])
            
            # Mostra chi ha vinto finora
            vincitori_temp = "\n".join([f"🏆 {v[1]} → {v[2]}" for v in partita['vincitori_trovati']])
            
            await query.edit_message_text(
                f"🎮 *PARTITA IN CORSO* 🐺\n\n"
                f"👑 *Vincitori finora:*\n{vincitori_temp}\n\n"
                f"⏳ Mancano ancora *{vincitori_rimanenti}* vincitori!\n"
                f"Continua a giocare... 👇",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(tastiera)
            )
    
    else:
        # Sbagliato
        if rimasti > 0:
            await query.answer(f"❌ {frutto_scelto} non è vincente! Rimasti: {rimasti}", show_alert=True)
            
            # Aggiorna tastiera per mostrare frutto come usato
            tastiera = crea_tastiera(partita['frutti'], partita['frutti_provati'], partita['tentativi_giocatori'])
            
            await query.edit_message_text(
                f"🎮 *PARTITA IN CORSO* 🐺\n\n"
                f"❌ {username} ha provato {frutto_scelto}\n"
                f"📊 Ti rimangono *{rimasti}* tentativi\n\n"
                f"👇 Prova con un altro:",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(tastiera)
            )
        else:
            # Ultimo tentativo sbagliato
            await query.answer(f"💔 Tentativi esauriti! Non puoi più giocare.", show_alert=True)
            
            # Controlla se tutti hanno finito
            tutti_finiti = True
            for uid in partita['tentativi_giocatori']:
                if partita['tentativi_giocatori'][uid] < partita['tentativi_max']:
                    # Qualcuno ha ancora tentativi
                    if uid not in [v[0] for v in partita['vincitori_trovati']]:
                        tutti_finiti = False
                        break
            
            if tutti_finiti and len(partita['vincitori_trovati']) < len(partita['vincenti']):
                # Nessuno può più vincere
                partita['attiva'] = False
                vincitori_temp = "\n".join([f"🏆 {v[1]} → {v[2]}" for v in partita['vincitori_trovati']]) if partita['vincitori_trovati'] else "Nessuno"
                
                await query.edit_message_text(
                    f"💀 *GAME OVER* 💀\n\n"
                    f"👑 Vincitori trovati: {len(partita['vincitori_trovati'])}/{len(partita['vincenti'])}\n"
                    f"{vincitori_temp}\n\n"
                    f"🍎 Frutti vincenti erano:\n" + 
                    "\n".join([f"  • {f}" for f in partita['vincenti']]) +
                    f"\n\n/nuova per rigiocare!"
                )

async def info_partita(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Info partita"""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    if chat_id not in partite:
        return
    
    partita = partite[chat_id]
    
    # Stato giocatori
    giocatori_text = []
    for uid, tent in partita['tentativi_giocatori'].items():
        rimasti = partita['tentativi_max'] - tent
        status = "✅" if rimasti > 0 else "❌"
        nome = "???"
        for v in partita['vincitori_trovati']:
            if v[0] == uid:
                nome = v[1] + " 👑"
                break
        if nome == "???":
            # Cerca nei tentativi precedenti (semplificato)
            nome = f"Giocatore {uid}"
        giocatori_text.append(f"{status} {nome}: {tent}/{partita['tentativi_max']}")
    
    info = (
        f"📊 Info Partita:\n\n"
        f"🏆 Vincitori: {len(partita['vincitori_trovati'])}/{len(partita['vincenti'])}\n"
        f"👥 Partecipanti: {len(partita['tentativi_giocatori'])}\n\n"
        f"📈 Tentativi:\n" + "\n".join(giocatori_text)
    )
    
    await query.answer(info, show_alert=True)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ferma partita (solo admin)"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Solo admin!")
        return
    
    if chat_id in partite:
        partite[chat_id]['attiva'] = False
        await update.message.reply_text("🛑 Partita fermata!")
    else:
        await update.message.reply_text("Nessuna partita attiva.")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nuova", nuova))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CallbackQueryHandler(config_step, pattern="^(cfg:|tent:|vinc:)"))
    app.add_handler(CallbackQueryHandler(tentativo, pattern="^(try:|usato)"))
    app.add_handler(CallbackQueryHandler(info_partita, pattern="^info$"))
    
    print("🐺 Bot Admin-MultiVincitore avviato!")
    app.run_polling()

if __name__ == "__main__":
    main()
