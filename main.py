from telethon import TelegramClient, events, Button
from datetime import datetime, timedelta
import json
import asyncio

# Dati del bot (da ottenere da @BotFather)
api_id = 25765102
api_hash = 'ea1f34752c0860fa799b4153da5c5554'
bot_token = '2082565967:AAGhPEPgHnOD278B1aDm_Fv27ERPlebKGVU'
admin_id = 123456789  # Inserisci il tuo chat ID come admin

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Funzioni per la gestione dei clienti
def load_clients():
    try:
        with open('clients.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_clients(clients):
    with open('clients.json', 'w') as file:
        json.dump(clients, file)

# Carichiamo i clienti all'avvio
clients = load_clients()

# Stato delle conversazioni per gestire le risposte degli utenti
user_states = {}

# Funzione per creare il menu principale
async def send_main_menu(chat_id, event=None):
    buttons = [
        [Button.inline("Aggiungi Cliente", b"add_client")],
        [Button.inline("Lista Clienti", b"list_clients")],
        [Button.inline("Rimuovi Cliente", b"remove_client")],
        [Button.inline("Rinnova Scadenza", b"renew_client")],
        [Button.inline("Invia Messaggio Generale", b"send_message_to_all")]
    ]
    if event:
        await event.edit("Seleziona un'opzione:", buttons=buttons)
    else:
        await client.send_message(chat_id, "Seleziona un'opzione:", buttons=buttons)

# Gestione del menu principale
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await send_main_menu(event.chat_id)

# Gestione pulsante "Indietro"
@client.on(events.CallbackQuery(data=b"go_back"))
async def go_back(event):
    # Reset dello stato dell'utente
    user_states.pop(event.chat_id, None)
    await send_main_menu(event.chat_id, event)

# Funzione per gestire lo stato dell'utente e il flusso delle conversazioni
async def handle_user_state(event, state, response=None):
    chat_id = event.chat_id
    
    # Aggiungi Cliente
    if state == 'add_client':
        if response is None:
            await event.edit("Inserisci il nome del cliente (username con @) e la data di scadenza nel formato: @nome_cliente YYYY-MM-DD",
                             buttons=[Button.inline("Indietro", b"go_back")])
        else:
            try:
                username_cliente, data_scadenza = response.split()

                # Controllo formattazione della data
                scadenza = datetime.strptime(data_scadenza, '%Y-%m-%d')

                # Otteniamo l'entità del cliente usando l'username
                cliente_entity = await client.get_entity(username_cliente)

                clients[username_cliente] = {'chat_id': cliente_entity.id, 'scadenza': data_scadenza}
                save_clients(clients)

                await client.send_message(chat_id, f"Cliente {username_cliente} aggiunto con scadenza {data_scadenza}.")
            except ValueError:
                await client.send_message(chat_id, "Formato non corretto. Usa: @nome_cliente YYYY-MM-DD")
            except Exception as e:
                await client.send_message(chat_id, f"Errore: {str(e)}. Assicurati che l'username sia corretto e che il cliente abbia già avviato il bot.")
            finally:
                # Reset dello stato dell'utente
                user_states.pop(chat_id, None)
                await send_main_menu(chat_id)

    # Rimuovi Cliente
    elif state == 'remove_client':
        if response is None:
            messaggio = "Inserisci il nome del cliente da rimuovere. Ecco la lista:\n"
            for cliente, info in clients.items():
                messaggio += f"{cliente} (ID: {info['chat_id']}) - Scadenza: {info['scadenza']}\n"
            await event.edit(messaggio, buttons=[Button.inline("Indietro", b"go_back")])
        else:
            if response in clients:
                del clients[response]
                save_clients(clients)
                await client.send_message(chat_id, f"Cliente {response} rimosso.")
            else:
                await client.send_message(chat_id, "Cliente non trovato.")
            # Reset dello stato dell'utente
            user_states.pop(chat_id, None)
            await send_main_menu(chat_id)

    # Rinnova Scadenza
    elif state == 'renew_client':
        if response is None:
            messaggio = "Inserisci il nome del cliente da rinnovare. Ecco la lista:\n"
            for cliente, info in clients.items():
                messaggio += f"{cliente} (ID: {info['chat_id']}) - Scadenza: {info['scadenza']}\n"
            await event.edit(messaggio, buttons=[Button.inline("Indietro", b"go_back")])
        else:
            if response in clients:
                # Estendi la scadenza di un mese
                nuova_scadenza = datetime.strptime(clients[response]['scadenza'], '%Y-%m-%d') + timedelta(days=30)
                clients[response]['scadenza'] = nuova_scadenza.strftime('%Y-%m-%d')
                save_clients(clients)

                # Notifica all'utente con la nuova data di scadenza
                await client.send_message(clients[response]['chat_id'], f"Ciao {response}, la tua nuova scadenza è il {clients[response]['scadenza']}.")

                await client.send_message(chat_id, f"Scadenza per {response} rinnovata fino al {clients[response]['scadenza']}.")
            else:
                await client.send_message(chat_id, "Cliente non trovato.")
            # Reset dello stato dell'utente
            user_states.pop(chat_id, None)
            await send_main_menu(chat_id)

    # Invia Messaggio Generale
    elif state == 'send_message_to_all':
        if response is None:
            await event.edit("Inserisci il messaggio da inviare a tutti i clienti registrati:", buttons=[Button.inline("Indietro", b"go_back")])
        else:
            for cliente, info in clients.items():
                await client.send_message(info['chat_id'], response)
            await client.send_message(chat_id, "Messaggio inviato a tutti i clienti.")
            # Reset dello stato dell'utente
            user_states.pop(chat_id, None)
            await send_main_menu(chat_id)

# Gestione pulsanti che impostano lo stato dell'utente
@client.on(events.CallbackQuery(data=b"add_client"))
@client.on(events.CallbackQuery(data=b"remove_client"))
@client.on(events.CallbackQuery(data=b"renew_client"))
@client.on(events.CallbackQuery(data=b"send_message_to_all"))
async def on_button_click(event):
    chat_id = event.chat_id
    user_states[chat_id] = event.data.decode("utf-8")
    await handle_user_state(event, user_states[chat_id])

# Gestione delle risposte degli utenti
@client.on(events.NewMessage)
async def on_new_message(event):
    chat_id = event.chat_id
    if chat_id in user_states:
        state = user_states[chat_id]
        await handle_user_state(event, state, response=event.raw_text)

# Funzione per verificare le scadenze e inviare notifiche
async def check_deadlines():
    while True:
        now = datetime.now()
        for cliente, info in clients.items():
            scadenza = datetime.strptime(info['scadenza'], '%Y-%m-%d')
            giorni_rimanenti = (scadenza - now).days

            if giorni_rimanenti == 3:
                # Notifica all'admin
                await client.send_message(admin_id, f"Avviso: mancano 3 giorni alla scadenza dell'abbonamento per {cliente} ({info['scadenza']}).")

                # Notifica all'utente
                await client.send_message(info['chat_id'], f"Ciao {cliente}, il tuo abbonamento scade il {info['scadenza']}. Non dimenticare di rinnovarlo!")

        # Controlliamo ogni 24 ore
        await asyncio.sleep(86400)

# Avviamo il task in background per il controllo delle scadenze
client.loop.create_task(check_deadlines())

# Avvio del bot
print("Bot avviato...")
client.run_until_disconnected()
