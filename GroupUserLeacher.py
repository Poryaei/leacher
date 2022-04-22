#------- Import Library's
from operator import le
from subprocess import call
from typing import Counter
from telethon.sync import TelegramClient, functions, types, events, errors
from telethon.tl.custom import Button
from telethon.tl import types as tl_telethon_types

import os
import time


#--------- Creating folders
for item in ['Database', 'Sessions']:
    if not os.path.exists(item):
        os.mkdir(item)
#--------- Connect Bot
token = "" # BOT TOKEN FROM (@botfather)
bot = TelegramClient('Sessions/Bot', 1210549, '40c4bb8ee22346e4fa8c69565cb87440',)
bot.start(bot_token=token)
print('Bot Connected Successfully !')

#--------- Connect Leacher
Leacher = TelegramClient('Sessions/leacher', 1210549, '40c4bb8ee22346e4fa8c69565cb87440')
Leacher.start()
print('Leacher Connected Successfully !')

#--------- Functions
def online_within(participant):
    status = participant.status
    if isinstance(status, tl_telethon_types.UserStatusOnline):
        return True
    elif isinstance(status, tl_telethon_types.UserStatusRecently):
        return True
    else:
        print(status)
        return False


async def join(event, link):
    try:
        if '@' in link:
            await Leacher(functions.channels.JoinChannelRequest(channel=link))
        else:
            await Leacher(functions.messages.ImportChatInviteRequest(hash=link.split('/')[-1]))
            
        return True
    except errors.UserAlreadyParticipantError:
        return True 

    except errors.rpcerrorlist.AuthKeyDuplicatedError:
        return -3

    except errors.UserDeactivatedBanError:
        return -1

    except errors.UserDeactivatedError:
        return -1

    except errors.SessionExpiredError:
        return -2

    except errors.SessionRevokedError:
        return -2

    except errors.rpcerrorlist.ChannelPrivateError:
        return -4

    except errors.rpcerrorlist.InviteHashExpiredError:
        await event.reply("** link is invalid ! **")

    except errors.rpcerrorlist.FloodWaitError :
        await event.reply(f"**FloodWaitError**")
        return None

    except Exception as e :
        print (":::::::::::::::::::" , e.__class__ , str(e))
        return -1


#-------- Start Receiving Message's
leach = False
async def answer(event):
    global leach
    text = event.raw_text
    user_id = event.sender_id

    #--- Ping
    if text == "/start":
        await event.reply('Hi, example: /leach @ID 🤘🏻😃')
    
    #--- Leach 
    elif text.startswith('/leach '):
        now_time = time.time()
        link = text.split('/leach ')[1]
        keu = link

        #--- Reply
        m = await event.reply('⏳')

        #--- Find keu
        if '@' in link:
            keu = link.split('@')[1]
        elif 'joinchat' in link:
            keu = link.split('/')[-1]
        elif 't.me/' in link:
            keu = link.split('/')[-1]
            link = keu
            
        else:
            await event.reply('Bad Link!')
            return
        
        print(f"Leaching {keu}")

        ww = await join(event, link)
        if (ww == None):
            pass
            #ww = await join(event, link)

        elif (ww == -4 ):
            await event.reply(" ** I Baned from this chat ! **")

        elif (ww == -2 ):
            await event.reply(" **Session SessionRevokedError /  SessionExpiredError **")

        elif (ww == -3) :
            await event.reply(" **  AuthKeyDuplicatedError  **")

        elif ww == True:
            #--- Open DB File
            file_Onlines = open(f'Database/{keu}-Onlines.txt','w')
            file_Recently = open(f'Database/{keu}-Recently.txt','w')


            #--- data
            onlines = 0
            recents = 0
            counter = 0
            updateTime = time.time()

            #--- Get All users
            offset = 0
            limit = 100
            all_participants = []
            leach = True

            while leach:
                participants = await Leacher(functions.channels.GetParticipantsRequest(
                    link, types.ChannelParticipantsSearch(''), offset, limit,
                    hash=0
                ))
                if not participants.users:
                    break
                all_participants.extend(participants.users)
                offset += len(participants.users)
                for item in participants.users:
                    if item.username != None:
                        status = item.status
                        #--- Add Online users
                        if isinstance(status, tl_telethon_types.UserStatusOnline):
                            file_Onlines.write(str(item.username) + '\n')
                            counter+=1
                            onlines += 1

                        #--- Add Recently users
                        elif isinstance(status, tl_telethon_types.UserStatusRecently):
                            file_Recently.write(str(item.username) + '\n')
                            counter+=1
                            recents += 1
                        
                        #--- Alert
                        if time.time() - updateTime >= 6:
                            bt = [
                                [Button.inline(f"Online", 'none'), Button.inline(f"LastSeenRecently", 'none')],
                                [Button.inline(f"{onlines}", 'none'), Button.inline(f"{recents}", 'none')],
                                [Button.inline(f"❌ STOP ❌", 'stop-leach')]
                            ]
                            await m.edit('📊 Leaching Status:', buttons=bt)
                            
                        if not leach:
                            break
                
            #--- Close file
            file_Onlines.close()
            file_Recently.close()

            #--- Process time
            proc_time = int(time.time()) - int(now_time)
            await m.delete()

            #--- Btns 
            btn = [
                [Button.inline('Send File 📤', f'send-{keu}-{onlines}-{recents}')],
                [Button.inline('Close','Close')]
            ]

            await bot.send_message(user_id, f"🎗 Total `{counter}` Leached Users.\n➖➖➖➖➖\n**Online**: {onlines}\n➖➖➖➖➖\n**LastSeenRecently**: {recents}\n➖➖➖➖➖\n**ProcessTime**: {proc_time}S", buttons=btn)
            #await bot.send_file(user_id, f'Database/{keu}.txt', caption=f"🎗 Total `{counter}` Leached Users.\n➖➖➖➖➖\n**Online**: {onlines}\n➖➖➖➖➖\n**LastSeenRecently**: {recents}\n➖➖➖➖➖\n**ProcessTime**: {proc_time}S")

#------- Answer Callback data
async def callback(events):
    global leach
    callback = events.data.decode()
    user_id = events.sender_id
    sender = await events.get_sender()
    username = sender.username
    
    #--- send-file
    if callback.startswith('send-'):
        keu = callback.split('-')[1]
        fl_Onlines = f'Database/{keu}-Onlines.txt'
        fl_Recently = f'Database/{keu}-Recently.txt'

        #--- Counts
        count_Onlines = callback.split('-')[2]
        count_Recently = callback.split('-')[3]

        #--- Send files
        await bot.send_file(user_id, fl_Onlines, caption=f"🎗 Total `{count_Onlines}` **Online** Users.")
        await bot.send_file(user_id, fl_Recently, caption=f"🎗 Total `{count_Recently}` **LastSeenRecently** Users.")
    
    #--- Close btns
    elif callback == "Close":
        await events.delete()
    
    #--- stop
    elif callback == "stop-leach":
        await events.answer('🔄 در حال پردازش لطفا منتظر باشید ...')
        leach = False

#------- Handler
@bot.on(events.NewMessage)
async def my_event_handler(event):
    await answer(event)

@bot.on(events.CallbackQuery)
async def handler(events):
    await callback(events)

bot.run_until_disconnected()