from telethon import TelegramClient, events, Button
from datetime import datetime, timedelta
import json
import asyncio


api_id = 25765102
api_hash = 'ea1f34752c0860fa799b4153da5c5554'
bot_token = '2082565967:AAGhPEPgHnOD278B1aDm_Fv27ERPlebKGVU'
admin_id = 1453581059  

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)


def load_clients():
    try:
        with open('clients.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_clients(clients):
    with open('clients.json', 'w') as file:
        json.dump(clients, file)


clients = load_clients()


user_states = {}


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


@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    
    if event.chat_id == admin_id:
        await send_main_menu(event.chat_id)
    else:
        
        if event.chat_id in [info['chat_id'] for info in clients.values()]:
            messaggio = "Benvenuto, ecco le tue scadenze:\n"
            for cliente, info in clients.items():
                if info['chat_id'] == event.chat_id:
                    for prodotto, scadenza in info['prodotti'].items():
                        messaggio += f"{prodotto}: Scadenza il {scadenza}\n"
            await client.send_message(event.chat_id, messaggio)
        else:
            await client.send_message(event.chat_id, "Benvenuto, non hai nessuna scadenza.")


async def handle_user_state(event, state, response=None):
    chat_id = event.chat_id  

    
    if state == 'add_client':
        if response is None:
            await event.edit("Inserisci il nome del cliente (username con @), il prodotto e la data di scadenza nel formato: @nome_cliente Prodotto YYYY-MM-DD",
                             buttons=[Button.inline("Indietro", b"go_back")])
        else:
            try:
                username_cliente, prodotto, data_scadenza = response.split()

                
                scadenza = datetime.strptime(data_scadenza, '%Y-%m-%d')

                
                cliente_entity = await client.get_entity(username_cliente)

                
                if username_cliente in clients:
                    clients[username_cliente]['prodotti'][prodotto] = data_scadenza
                else:
                    clients[username_cliente] = {'chat_id': cliente_entity.id, 'prodotti': {prodotto: data_scadenza}}
                
                save_clients(clients)

                await client.send_message(chat_id, f"Cliente {username_cliente} aggiunto/aggiornato con il prodotto '{prodotto}' e scadenza {data_scadenza}.")
            except ValueError:
                await client.send_message(chat_id, "Formato non corretto. Usa: @nome_cliente Prodotto YYYY-MM-DD")
            except Exception as e:
                await client.send_message(chat_id, f"Errore: {str(e)}. Assicurati che l'username sia corretto e che il cliente abbia già avviato il bot.")
            finally:
                user_states.pop(chat_id, None)
                await send_main_menu(chat_id)

    
    elif state == 'list_clients':
        messaggio = "Ecco la lista dei clienti:\n"
        for cliente, info in clients.items():
            messaggio += f"{cliente} (ID: {info['chat_id']})\n"
            for prodotto, scadenza in info['prodotti'].items():
                messaggio += f"  - {prodotto}: Scadenza {scadenza}\n"
        await client.send_message(chat_id, messaggio)
        user_states.pop(chat_id, None)
        await send_main_menu(chat_id)

    
    elif state == 'remove_client':
        if response is None:
            await event.edit("Inserisci l'username del cliente da rimuovere (es: @username):",
                             buttons=[Button.inline("Indietro", b"go_back")])
        else:
            username_cliente = response.strip()
            if username_cliente in clients:
                del clients[username_cliente]
                save_clients(clients)
                await client.send_message(chat_id, f"Cliente {username_cliente} rimosso con successo.")
            else:
                await client.send_message(chat_id, f"Cliente {username_cliente} non trovato.")
            user_states.pop(chat_id, None)
            await send_main_menu(chat_id)

    
    elif state == 'renew_client':
        if response is None:
            await event.edit("Inserisci l'username del cliente, il prodotto e la nuova data di scadenza nel formato: @nome_cliente Prodotto YYYY-MM-DD",
                             buttons=[Button.inline("Indietro", b"go_back")])
        else:
            try:
                username_cliente, prodotto, nuova_data = response.split()

                if username_cliente in clients and prodotto in clients[username_cliente]['prodotti']:
                    clients[username_cliente]['prodotti'][prodotto] = nuova_data
                    save_clients(clients)
                    await client.send_message(chat_id, f"Scadenza del prodotto '{prodotto}' per {username_cliente} rinnovata al {nuova_data}.")
                else:
                    await client.send_message(chat_id, f"Errore: cliente o prodotto non trovato.")
            except ValueError:
                await client.send_message(chat_id, "Formato non corretto. Usa: @nome_cliente Prodotto YYYY-MM-DD")
            user_states.pop(chat_id, None)
            await send_main_menu(chat_id)

    
    elif state == 'send_message_to_all':
        if response is None:
            await event.edit("Inserisci il messaggio da inviare a tutti i clienti:",
                             buttons=[Button.inline("Indietro", b"go_back")])
        else:
            messaggio = response.strip()
            for cliente, info in clients.items():
                await client.send_message(info['chat_id'], messaggio)
            await client.send_message(chat_id, "Messaggio inviato a tutti i clienti.")
            user_states.pop(chat_id, None)
            await send_main_menu(chat_id)

    
    elif state == 'go_back':
        await send_main_menu(chat_id)
        user_states.pop(chat_id, None)


@client.on(events.CallbackQuery)
async def on_button_click(event):
    chat_id = event.chat_id
    callback_data = event.data.decode("utf-8")  

    
    user_states[chat_id] = callback_data
    
    
    await handle_user_state(event, callback_data)


@client.on(events.NewMessage)
async def on_new_message(event):
    chat_id = event.chat_id
    if chat_id in user_states:
        state = user_states[chat_id]
        await handle_user_state(event, state, response=event.raw_text)


async def check_deadlines():
    while True:
        now = datetime.now()
        for cliente, info in clients.items():
            for prodotto, scadenza in info['prodotti'].items():
                data_scadenza = datetime.strptime(scadenza, '%Y-%m-%d')
                giorni_rimanenti = (data_scadenza - now).days

                if giorni_rimanenti == 3:
                    await client.send_message(admin_id, f"Avviso: mancano 3 giorni alla scadenza del prodotto '{prodotto}' per {cliente}.")
                    await client.send_message(info['chat_id'], f"Ciao {cliente}, il tuo prodotto '{prodotto}' scade tra 3 giorni (il {scadenza}).")

                if giorni_rimanenti == 0:
                    await client.send_message(admin_id, f"Avviso: oggi scade il prodotto '{prodotto}' per {cliente}.")
                    await client.send_message(info['chat_id'], f"Ciao {cliente}, il tuo prodotto '{prodotto}' scade oggi ({scadenza}).")

        await asyncio.sleep(86400)  


asyncio.ensure_future(check_deadlines())


print("Bot avviato...")
client.run_until_disconnected()
