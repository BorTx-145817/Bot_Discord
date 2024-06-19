# bot.py
# author: Barkah

import discord
from discord.ext import commands
import json
import os
import time
import asyncio
import aiohttp
import openai
from hijri_converter import Gregorian
import datetime
from lib.callbacks import *
from lib.print import custom_print
from lib.spinner import start_spinner, stop_spinner, succeed_spinner, spinner



# Variabel konfigurasi
SYSTEM_FOLDER = 'system'
CONFIG_FILE = 'system/config.json'
DATABASE_FILE = 'system/database.json'

if not os.path.exists(CONFIG_FILE):
    # Contoh isi config.json, sesuaikan dengan kebutuhan Anda
    config_data = {
        'token': 'Token_here',
        'prefix': '!',
        'limit': 25,
        'status': 'free',
        'nama': 'Ar BorTx Official'
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

# Baca token dari config.json
with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)
    token = config['token']
    default_limit = config['limit']
    status = config['status']
    nama = config['nama']

# Inisialisasi bot dan definisi event serta commandnya
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  # Menambahkan intent untuk guild
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

start_time = time.time()

# Fungsi untuk mereset limit setiap hari pukul 05:05
async def reset_limit():
    while True:
        now = time.localtime()
        reset_time = time.struct_time((now.tm_year, now.tm_mon, now.tm_mday, 5, 5, 0, now.tm_wday, now.tm_yday, now.tm_isdst))
        seconds_until_reset = time.mktime(reset_time) - time.time()
        if seconds_until_reset < 0:
            seconds_until_reset += 86400  # Tambahkan satu hari jika sudah lewat pukul 05:05 hari ini
        await asyncio.sleep(seconds_until_reset)

        # Reset limit untuk semua pengguna kecuali owner
        user_data = load_user_data()
        for user_id in user_data:
            if user_data[user_id]['status'] != 'owner':
                user_data[user_id]['limit'] = default_limit
        save_user_data(user_data)

        print(f"Limit direset pada {time.strftime('%H:%M:%S', time.localtime())}")
        await bot.change_presence(activity=discord.Game(name=f"{status}\nLimit: {default_limit}"))

# Memuat data pengguna dari database.json
def load_user_data():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    return {}

# Menyimpan data pengguna ke database.json
def save_user_data(data):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    global owner
    app_info = await bot.application_info()
    owner = app_info.owner

    custom_print(f'Bot {bot.user.name} telah berhasil masuk sebagai {bot.user} di server Discord!', "Info")
    succeed_spinner("Bot is ready!")
    start_spinner()
    await bot.change_presence(activity=discord.Game(name=f"{status}\nLimit: {default_limit}"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    runtime = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
    custom_print(f'{message.author}: {message.content}', "User Chat", user=message.author.name, runtime=runtime)

    user_data = load_user_data()
    user_id = str(message.author.id)
    if user_id not in user_data:
        user_data[user_id] = {
            'nama': message.author.name,
            'status': 'free',
            'limit': default_limit,
        }
    save_user_data(user_data)

    await bot.process_commands(message)

@bot.command(name='menu')
async def menu(ctx):
    user_data = load_user_data()
    user_id = str(ctx.author.id)

    is_owner = ctx.author == owner
    if user_id not in user_data:
        user_data[user_id] = {
            'nama': ctx.author.name,
            'status': 'free',
            'limit': default_limit,
        }

    if is_owner:
        user_data[user_id]['status'] = 'owner'
        user_data[user_id]['limit'] = 'unlimited'  # Simpan sebagai unlimited untuk owner
    else:
        user_limit = int(user_data[user_id]['limit'])
        if user_limit > 0:
            user_limit -= 1
            user_data[user_id]['limit'] = user_limit  # Simpan perubahan limit
        else:
            await ctx.send(f'Limit Bot Anda Telah Habis ❎\nSilahkan tunggu Limit anda Akan Direset Setiap Hari Pukul 05.05')
            return
    
    save_user_data(user_data)
    limit = user_data[user_id]['limit']
    status = 'owner' if is_owner else 'free'

    current_time = time.localtime()
    current_time_masehi = (current_time.tm_year, current_time.tm_mon, current_time.tm_mday)

    # Konversi tanggal Masehi ke Hijriah
    current_time_hijriah = Gregorian(current_time_masehi[0], current_time_masehi[1], current_time_masehi[2]).to_hijri()
    tanggal_islam = f"{current_time_hijriah.year:04}-{current_time_hijriah.month:02}-{current_time_hijriah.day:02}"

    user_info = f"""
    ╭──✎ *[ User Info ]*
    | ⎆ Name Bot : {nama}
    | ⎆ Nama Pengguna : {ctx.author.name}
    | ⎆ Jam: {time.strftime('%H:%M:%S', time.localtime())}
    | ⎆ Tanggal Masehi : {time.strftime('%Y-%m-%d', current_time)}
    | ⎆ Tanggal Islam : {tanggal_islam}
    | ⎆ Number : {ctx.author.id}
    | ⎆ Status : {status}
    | ⎆ Limit : {limit}
    ╰──────────────────
    """

    await ctx.send(user_info)

    
    view1 = discord.ui.View()
    view2 = discord.ui.View()

    buttons = [
        discord.ui.Button(label='Owner', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Google', style=discord.ButtonStyle.link, url='https://www.google.com'),
        discord.ui.Button(label='Hub Owner', style=discord.ButtonStyle.link, url='https://wa.me/6285880743812'),
        discord.ui.Button(label='Search Youtube', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Youtube video', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Youtube audio', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='ChatGPT', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='TikTok TDL', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Audio TikTok TDL', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='FB Dl', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='FB Audio Dl', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Instagram', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Dalle3', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Pinterest', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='SIMI', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Lyrics', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Jadwal TV', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Mediafire', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Gdrive', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Gemini', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Gpt Prompt', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Translate', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Spotify Search', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Spotify Downloader', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Anime Search', style=discord.ButtonStyle.primary),
        discord.ui.Button(label='Apk Downloader', style=discord.ButtonStyle.primary)
    ]

    # Menambahkan callback pada tombol
    buttons[0].callback = button1_callback
    buttons[3].callback = button4_callback
    buttons[4].callback = button5_callback
    buttons[5].callback = button6_callback
    buttons[6].callback = button7_callback
    buttons[7].callback = button8_callback
    buttons[8].callback = button9_callback
    buttons[9].callback = button10_callback
    buttons[10].callback = button11_callback
    buttons[11].callback = button12_callback
    buttons[12].callback = button13_callback
    buttons[13].callback = button14_callback
    buttons[14].callback = button15_callback
    buttons[15].callback = button16_callback
    buttons[16].callback = button17_callback
    buttons[17].callback = button18_callback
    buttons[18].callback = button19_callback
    buttons[19].callback = button20_callback
    buttons[20].callback = button21_callback
    buttons[21].callback = button22_callback
    buttons[22].callback = button23_callback
    buttons[23].callback = button24_callback
    buttons[24].callback = button25_callback
    buttons[25].callback = button26_callback

    # Membagi tombol menjadi dua View
    for i in range(25):
        view1.add_item(buttons[i])
    for i in range(25, 26):
        view2.add_item(buttons[i])

    await ctx.send('Shilakan pilih Menu 1:', view=view1)
    await ctx.send('Shilakan pilih Menu 2:', view=view2)

async def start_spinner_loop():
    while True:
        start_spinner()
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.create_task(start_spinner_loop())
loop.create_task(reset_limit())

bot.run(token)