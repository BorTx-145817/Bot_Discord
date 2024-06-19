# modals.py
import discord
import requests
import tempfile
import time
import asyncio
from youtubesearchpython import VideosSearch
from pytube import YouTube
import aiohttp
import openai
from urllib import parse
import os



class CariYouTubeModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Cari di YouTube')

        self.search_query = discord.ui.TextInput(
            label='Pencarian',
            placeholder='Masukkan istilah pencarian...',
            required=True
        )
        self.add_item(self.search_query)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        query = self.search_query.value
        videos_search = VideosSearch(query, limit=1)
        result = videos_search.result()

        if result['result']:
            video = result['result'][0]
            judul = video['title']
            url = video['link']
            await interaction.followup.send(f"Hasil pencarian teratas:\n**{judul}**\n{url}")
        else:
            await interaction.followup.send("Tidak ada hasil ditemukan.", ephemeral=True)

class YouTubeDownloaderModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='YouTube Downloader Mp4')

        self.video_url = discord.ui.TextInput(
            label='URL YouTube',
            placeholder='Masukkan URL YouTube...',
            required=True
        )
        self.add_item(self.video_url)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.download_youtube_video(interaction)

    async def download_youtube_video(self, interaction: discord.Interaction):
        url = self.video_url.value.strip()
        api_url = f"https://aemt.me/download/ytdl?url={requests.utils.quote(url)}"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                if data.get('result') and data.get('status'):
                    download_url = data['result']['mp4']  # Pilih format mp4
                    file_name = "downloaded_video.mp4"  # Gunakan nama file default
                    file_size_str = "8 MB"  # Asumsikan file size sementara karena API tidak memberikan ukuran file
                    
                    # Check if file size exceeds Discord's upload limit
                    discord_upload_limit = 8 * 1024 * 1024  # 8 MB
                    file_size_bytes = 8 * 1024 * 1024  # Asumsi file size sementara
                    
                    if file_size_bytes > discord_upload_limit:
                        await interaction.followup.send(f"Ukuran file {file_size_str} terlalu besar untuk diunggah ke Discord.", ephemeral=True)
                        return

                    # Download the file from the URL
                    file_response = requests.get(download_url)
                    if file_response.status_code == 200:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                            temp_file.write(file_response.content)
                            temp_file_path = temp_file.name

                        await interaction.followup.send("Berhasil mengunduh video dari YouTube. Mengirim file...", ephemeral=True)
                        await interaction.followup.send(file=discord.File(temp_file_path))

                        os.remove(temp_file_path)
                    else:
                        await interaction.followup.send("Gagal mengunduh file dari URL yang diberikan.", ephemeral=True)
                else:
                    await interaction.followup.send("Tidak ada tautan unduhan yang ditemukan dalam respons.", ephemeral=True)
            else:
                await interaction.followup.send("Gagal mendapatkan tautan unduhan YouTube.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan: {e}", ephemeral=True)

class YouTubeDownloaderAudioModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='YouTube Downloader')

        self.video_url = discord.ui.TextInput(
            label='URL YouTube',
            placeholder='Masukkan URL YouTube...',
            required=True
        )
        self.add_item(self.video_url)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.download_youtube_audio(interaction)

    async def download_youtube_audio(self, interaction: discord.Interaction):
        url = self.video_url.value.strip()
        api_url = f"https://aemt.me/download/ytdl?url={requests.utils.quote(url)}"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                if data.get('result') and data.get('status'):
                    download_url = data['result']['mp3']  # Pilih format mp3
                    file_name = "downloaded_audio.mp3"  # Gunakan nama file default
                    
                    # Download the file from the URL
                    file_response = requests.get(download_url)
                    if file_response.status_code == 200:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                            temp_file.write(file_response.content)
                            temp_file_path = temp_file.name

                        await interaction.followup.send("Berhasil mengunduh audio dari YouTube. Mengirim file...", ephemeral=True)
                        await interaction.followup.send(file=discord.File(temp_file_path))

                        os.remove(temp_file_path)
                    else:
                        await interaction.followup.send("Gagal mengunduh file dari URL yang diberikan.", ephemeral=True)
                else:
                    await interaction.followup.send("Tidak ada tautan unduhan yang ditemukan dalam respons.", ephemeral=True)
            else:
                await interaction.followup.send("Gagal mendapatkan tautan unduhan YouTube.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan: {e}", ephemeral=True)

        # Membersihkan: Hapus file sementara yang lebih lama dari 1 jam
        await membersihkan_folder_tmp()

class TikTokTDLModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Tiktok Downloader')
        
        self.video_url = discord.ui.TextInput(
            label='URL Tiktok',
            placeholder='Masukkan URL Tiktok...',
            required=True
        )
        self.add_item(self.video_url)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        url = self.video_url.value
        api_url = f"https://aemt.me/download/tiktokdl?url={url}"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] and data["result"]["status"]:
                video_url = data["result"]["video"]
                video_response = requests.get(video_url)
                
                if video_response.status_code == 200:
                    file_path = os.path.join(TMP_FOLDER, "tiktok.mp4")
                    
                    with open(file_path, "wb") as file:
                        file.write(video_response.content)
                    
                    await interaction.followup.send("Berhasil mengunduh video TikTok. Mengirim video...", ephemeral=True)
                    await interaction.followup.send(file=discord.File(file_path))
                    
                    os.remove(file_path)
                else:
                    await interaction.followup.send("Gagal mengunduh video dari URL yang diberikan.", ephemeral=True)
            else:
                await interaction.followup.send("Respons API tidak valid.", ephemeral=True)
        else:
            await interaction.followup.send("Gagal mendapatkan tautan TikTok.", ephemeral=True)

        await membersihkan_folder_tmp()

class AudioTiktokTDLModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Tiktok Audio Downloader')
        
        self.audio_url = discord.ui.TextInput(
            label='URL Tiktok',
            placeholder='Masukkan URL Tiktok...',
            required=True
        )
        self.add_item(self.audio_url)

    async def on_submit(self, interaction: discord.Interaction):

        url = self.audio_url.value
        api_url = f"https://aemt.me/download/tiktokdl?url={url}"
        response = requests.get(api_url)
        
        print(response.text)  # Tambahkan baris ini untuk mencetak respons dari API
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status", False) and data["result"].get("status", False):
                audio_url = data["result"]["music"]
                audio_response = requests.get(audio_url)
                
                if audio_response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                        temp_file.write(audio_response.content)
                        temp_file_path = temp_file.name
                    
                    await interaction.followup.send("Berhasil mengunduh audio TikTok. Mengirim audio...", ephemeral=True)
                    await interaction.followup.send(file=discord.File(temp_file_path))
                    
                    os.remove(temp_file_path)
                else:
                    await interaction.followup.send("Gagal mengunduh audio dari URL yang diberikan.", ephemeral=True)
            else:
                await interaction.followup.send("Respons API tidak valid.", ephemeral=True)
        else:
            await interaction.followup.send("Gagal mendapatkan tautan TikTok.", ephemeral=True)
         
        await membersihkan_folder_tmp()

class FacebookVideoDownloaderModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Facebook DL')

        self.video_url = discord.ui.TextInput(
            label='URL Video Facebook',
            placeholder='Masukkan URL video Facebook...',
            required=True
        )
        self.add_item(self.video_url)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        url = self.video_url.value.strip()
        api_key = "Barkah"  # Ganti dengan API key yang sesuai
        api_url = f"https://skizo.tech/api/facebook?apikey={api_key}&url={requests.utils.quote(url)}"

        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            # Periksa apakah respons merupakan list
            if isinstance(data, list):
                # Jika ya, ambil video dengan kualitas tertinggi
                video_data = max(data, key=lambda x: x.get('quality', ''))
            else:
                # Jika bukan, gunakan data langsung
                video_data = data

            if video_data.get("url"):
                video_url = video_data["url"]
                video_response = requests.get(video_url)
                
                if video_response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                        temp_file.write(video_response.content)
                        temp_file_path = temp_file.name
                    
                    await interaction.followup.send("Berhasil mengunduh video Facebook. Mengirim video...", ephemeral=True)
                    await interaction.followup.send(file=discord.File(temp_file_path))
                    
                    os.remove(temp_file_path)
                else:
                    await interaction.followup.send("Gagal mengunduh video dari URL yang diberikan.", ephemeral=True)
            else:
                await interaction.followup.send("Tidak ada tautan video yang ditemukan dalam respons.", ephemeral=True)
        else:
            await interaction.followup.send("Gagal mendapatkan tautan video Facebook.", ephemeral=True)

class FacebookAudioDownloaderModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Facebook Audio DL')

        self.video_url = discord.ui.TextInput(
            label='URL Video Facebook',
            placeholder='Masukkan URL video Facebook...',
            required=True
        )
        self.add_item(self.video_url)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        url = self.video_url.value.strip()
        api_key = "Barkah"  # Ganti dengan API key yang sesuai
        api_url = f"https://skizo.tech/api/facebook?apikey={api_key}&url={requests.utils.quote(url)}"

        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            # Periksa apakah respons merupakan list
            if isinstance(data, list):
                # Jika ya, ambil audio dengan kualitas tertinggi
                audio_data = max(data, key=lambda x: x.get('quality', ''))
            else:
                # Jika bukan, gunakan data langsung
                audio_data = data

            if audio_data.get("url"):
                audio_url = audio_data["url"]
                audio_response = requests.get(audio_url)
                
                if audio_response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                        temp_file.write(audio_response.content)
                        temp_file_path = temp_file.name
                    
                    await interaction.followup.send("Berhasil mengunduh audio dari video Facebook. Mengirim audio...", ephemeral=True)
                    await interaction.followup.send(file=discord.File(temp_file_path))
                    
                    os.remove(temp_file_path)
                else:
                    await interaction.followup.send("Gagal mengunduh audio dari URL yang diberikan.", ephemeral=True)
            else:
                await interaction.followup.send("Tidak ada tautan audio yang ditemukan dalam respons.", ephemeral=True)
        else:
            await interaction.followup.send("Gagal mendapatkan tautan audio Facebook.", ephemeral=True)


class ChatGPTModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='ChatGPT')

        self.prompt = discord.ui.TextInput(
            label='Prompt',
            placeholder='Masukkan pertanyaan atau pesan Anda...',
            required=True
        )
        self.add_item(self.prompt)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            prompt = self.prompt.value
            response = await get_chatgpt_response(prompt)

            # Mengirim respons langsung sebagai pesan balasan dari interaksi
            await interaction.followup.send(content=response)
        except Exception as e:
            await interaction.response.send_message(f"Terjadi kesalahan: {str(e)}")

async def get_chatgpt_response(prompt):
    try:
        api_key = "alal"  # Ganti dengan API key yang sesuai
        api_url = f"https://skizo.tech/api/openaiv2?apikey={api_key}&text={requests.utils.quote(prompt)}&system="

        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("result", "Tidak ada respons dari ChatGPT")
        else:
            error_message = response.json().get('error', {}).get('message', 'Terjadi kesalahan')
            return f"Gagal mendapatkan respon dari ChatGPT: {error_message}"
    except requests.exceptions.RequestException as e:
            return f"Terjadi kesalahan saat mengakses API: {str(e)}"
 

class InstagramVideoDownloaderModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Instagram Video DL')

        self.video_url = discord.ui.TextInput(
            label='URL Video Instagram',
            placeholder='Masukkan URL video Instagram...',
            required=True
        )
        self.add_item(self.video_url)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        url = self.video_url.value.strip()
        api_key = "f268e6fb38b2cf4234ddfd20"  # Ganti dengan API key yang sesuai
        api_url = f"https://api.lolhuman.xyz/api/instagram?apikey={api_key}&url={requests.utils.quote(url)}"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                video_urls = data.get("result")

                if video_urls and isinstance(video_urls, list) and len(video_urls) > 0:
                    video_url = video_urls[0]  # Ambil URL video pertama dari hasil
                    video_response = requests.get(video_url)
                    if video_response.status_code == 200:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                            temp_file.write(video_response.content)
                            temp_file_path = temp_file.name
                        
                        await interaction.followup.send("Berhasil mengunduh video Instagram. Mengirim video...", ephemeral=True)
                        await interaction.followup.send(file=discord.File(temp_file_path))
                        
                        os.remove(temp_file_path)
                    else:
                        await interaction.followup.send("Gagal mengunduh video dari URL yang diberikan.", ephemeral=True)
                else:
                    await interaction.followup.send("Tidak ada tautan video yang ditemukan dalam respons.", ephemeral=True)
            else:
                await interaction.followup.send("Gagal mendapatkan tautan video Instagram.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan: {e}", ephemeral=True)

class Dalle3Modal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Dalle3')

        self.prompt = discord.ui.TextInput(
            label='Prompt',
            placeholder='Masukkan deskripsi gambar...',
            required=True
        )
        self.add_item(self.prompt)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        prompt = self.prompt.value

        try:
            # Menggunakan API dari skizo.tech untuk menghasilkan gambar
            api_url = f"https://skizo.tech/api/dalle3?apikey=Barkah&prompt={requests.utils.quote(prompt)}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 200:
                    image_url = data.get('url')
                    image_response = requests.get(image_url)

                    if image_response.status_code == 200:
                        # Simpan gambar sementara
                        tmp_folder = 'tmp'
                        os.makedirs(tmp_folder, exist_ok=True)
                        image_path = os.path.join(tmp_folder, 'generated_image.png')

                        with open(image_path, 'wb') as f:
                            f.write(image_response.content)
                        
                        # Kirim gambar ke pengguna
                        await interaction.followup.send(
                            content=f"Gambar yang dihasilkan untuk prompt '{prompt}':",
                            file=discord.File(image_path)
                        )

                        # Hapus file sementara setelah dikirim
                        os.remove(image_path)
                    else:
                        await interaction.followup.send(f"Gagal mengunduh gambar: {image_response.status_code}")
                else:
                    await interaction.followup.send(f"Gagal menghasilkan gambar: {data.get('message', 'Unknown error')}")
            else:
                await interaction.followup.send(f"Terjadi kesalahan saat mengakses API: {response.status_code}")

        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan saat menghasilkan gambar: {e}")

class PinterestDownloaderModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Pinterest Image Downloader')

        self.search_query = discord.ui.TextInput(
            label='Kata Kunci Pencarian',
            placeholder='Masukkan kata kunci pencarian...',
            required=True
        )
        self.add_item(self.search_query)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        query = self.search_query.value.strip()
        api_key = "Barkah"  # Ganti dengan API key yang sesuai
        api_url = f"https://skizo.tech/api/pinterest?apikey={api_key}&search={requests.utils.quote(query)}"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 200:
                    images = [item["media"]["url"] for item in data.get("data", [])]
                    if images:
                        embed = discord.Embed(title=f"Hasil pencarian untuk '{query}'")
                        for image_url in images[:50]:  # Batasi hingga lima gambar
                            embed.set_image(url=image_url)
                            await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send("Tidak ada gambar ditemukan untuk pencarian ini.", ephemeral=True)
                else:
                    await interaction.followup.send("Gagal mendapatkan gambar dari Pinterest.", ephemeral=True)
            else:
                await interaction.followup.send("Gagal menghubungi API Pinterest.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan: {e}", ephemeral=True)

class SimiModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Simi Chat')

        self.input_text = discord.ui.TextInput(
            label='Teks',
            placeholder='Tuliskan pertanyaan atau pesan Anda...',
            required=True
        )
        self.add_item(self.input_text)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        text = self.input_text.value.strip()
        response = simi_api.chat(text)  # Menggunakan fungsi chat dari class SimiAPI
        
        await interaction.followup.send(response)

class SimiAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://skizo.tech/api/simi'

    # Fungsi untuk mengirim permintaan chat ke API Simi
    def chat(self, text):
        params = {'apikey': self.api_key, 'text': text, 'level': 100}
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            return response.json().get('result', 'Tidak ada respons dari Simi.')
        else:
            return 'Terjadi kesalahan saat mengakses API Simi.'

# Inisialisasi instance SimiAPI dengan API key
simi_api = SimiAPI('Barkah') 
        
class LyricsModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Cari Lirik Lagu')

        self.song_title = discord.ui.TextInput(
            label='Judul Lagu',
            placeholder='Masukkan judul lagu...',
            required=True
        )
        self.add_item(self.song_title)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.search_lyrics(interaction)

    async def search_lyrics(self, interaction: discord.Interaction):
        try:
            song_title = self.song_title.value
            api_url = f"https://aemt.me/lirik?text={requests.utils.quote(song_title)}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status'):
                    lyrics = data.get('result').get('lyrics')
                    if len(lyrics) <= 2000:
                        await interaction.followup.send(
                            content=f"Lirik lagu\n**{song_title}**:\n{lyrics}"
                        )
                    else:
                        await interaction.followup.send(
                            content=f"Lirik lagu **{song_title}** terlalu panjang untuk ditampilkan dalam satu pesan."
                        )
                else:
                    await interaction.followup.send("Lirik lagu tidak ditemukan.")
            else:
                await interaction.followup.send(f"Error accessing API: {response.status_code}")

        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan: {e}")

class JadwalTVModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Jadwal TV')

        self.channel_name = discord.ui.TextInput(
            label='Nama Saluran TV',
            placeholder='Masukkan nama saluran TV...',
            required=True
        )
        self.add_item(self.channel_name)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.fetch_tv_schedule(interaction)

    async def fetch_tv_schedule(self, interaction: discord.Interaction):
        try:
            channel_name = self.channel_name.value
            api_url = f"https://aemt.me/jadwaltv?tv={requests.utils.quote(channel_name)}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result'):
                    schedule = data['result'].get('result')
                    if schedule:
                        schedule_text = "\n".join([f"- {program['date']}: {program['event']}" for program in schedule])
                        await interaction.followup.send(
                            content=f"Jadwal TV untuk **{channel_name}**:\n{schedule_text}"
                        )
                    else:
                        await interaction.followup.send("Jadwal TV tidak ditemukan.")
                else:
                    await interaction.followup.send("Nama saluran TV tidak valid.")
            else:
                await interaction.followup.send(f"Error accessing API: {response.status_code}")

        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan: {e}")

class MediafireDownloaderModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Mediafire Downloader')

        self.file_url = discord.ui.TextInput(
            label='URL Mediafire',
            placeholder='Masukkan URL Mediafire...',
            required=True
        )
        self.add_item(self.file_url)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.download_mediafire_file(interaction)

    async def download_mediafire_file(self, interaction: discord.Interaction):
        url = self.file_url.value.strip()
        api_url = f"https://aemt.me/mediafire?link={requests.utils.quote(url)}"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                if data.get('result'):
                    download_url = data['result']['link']
                    file_name = data['result']['title']
                    file_size_str = data['result']['size'].strip()
                    
                    # Convert size string to bytes for comparison
                    size_units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
                    size_value, size_unit = float(file_size_str[:-2]), file_size_str[-2:].upper()
                    file_size_bytes = size_value * size_units.get(size_unit, 1)

                    # Check if file size exceeds Discord's upload limit
                    discord_upload_limit = 8 * 1024 * 1024  # 8 MB
                    if file_size_bytes > discord_upload_limit:
                        await interaction.followup.send(f"Ukuran file {file_size_str} terlalu besar untuk diunggah ke Discord.", ephemeral=True)
                        return

                    # Download the file from the URL
                    file_response = requests.get(download_url)
                    if file_response.status_code == 200:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp_file:
                            temp_file.write(file_response.content)
                            temp_file_path = temp_file.name

                        await interaction.followup.send("Berhasil mengunduh file dari Mediafire. Mengirim file...", ephemeral=True)
                        await interaction.followup.send(file=discord.File(temp_file_path))

                        os.remove(temp_file_path)
                    else:
                        await interaction.followup.send("Gagal mengunduh file dari URL yang diberikan.", ephemeral=True)
                else:
                    await interaction.followup.send("Tidak ada tautan unduhan yang ditemukan dalam respons.", ephemeral=True)
            else:
                await interaction.followup.send("Gagal mendapatkan tautan unduhan Mediafire.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan: {e}", ephemeral=True)

class GoogleDriveDownloaderModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Google Drive Downloader')

        self.file_url = discord.ui.TextInput(
            label='URL Google Drive',
            placeholder='Masukkan URL Google Drive...',
            required=True
        )
        self.add_item(self.file_url)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.download_google_drive_file(interaction)

    async def download_google_drive_file(self, interaction: discord.Interaction):
        url = self.file_url.value.strip()
        api_url = f"https://aemt.me/download/gdrive?url={requests.utils.quote(url)}"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                if data.get('result') and data['result'].get('status'):
                    download_url = data['result']['data']
                    file_name = data['result']['fileName']
                    file_size_str = data['result']['fileSize'].strip()
                    
                    # Convert size string to bytes for comparison
                    size_units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
                    size_value, size_unit = float(file_size_str[:-2]), file_size_str[-2:].upper()
                    file_size_bytes = size_value * size_units.get(size_unit, 1)

                    # Check if file size exceeds Discord's upload limit
                    discord_upload_limit = 8 * 1024 * 1024  # 8 MB
                    if file_size_bytes > discord_upload_limit:
                        await interaction.followup.send(f"Ukuran file {file_size_str} terlalu besar untuk diunggah ke Discord.", ephemeral=True)
                        return

                    # Download the file from the URL
                    file_response = requests.get(download_url)
                    if file_response.status_code == 200:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp_file:
                            temp_file.write(file_response.content)
                            temp_file_path = temp_file.name

                        await interaction.followup.send("Berhasil mengunduh file dari Google Drive. Mengirim file...", ephemeral=True)
                        await interaction.followup.send(file=discord.File(temp_file_path))

                        os.remove(temp_file_path)
                    else:
                        await interaction.followup.send("Gagal mengunduh file dari URL yang diberikan.", ephemeral=True)
                else:
                    await interaction.followup.send("Tidak ada tautan unduhan yang ditemukan dalam respons.", ephemeral=True)
            else:
                await interaction.followup.send("Gagal mendapatkan tautan unduhan Google Drive.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan: {e}", ephemeral=True)


class GeminiModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Gemini')

        self.text_input = discord.ui.TextInput(
            label='Prompt',
            placeholder='Masukkan pertanyaan',
            required=True
        )
        self.add_item(self.text_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        text_to_translate = self.text_input.value

        api_url = f"https://aemt.me/gemini?text={requests.utils.quote(text_to_translate)}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') and data.get('result'):
                            translated_text = data['result']
                            await interaction.followup.send(f"**Nama:** {interaction.user.mention}\n\n**Gemini:**\n{translated_text}", ephemeral=True)
                    else:
                        await interaction.followup.send("Gagal melakukan permintaan ke server", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan: {str(e)}", ephemeral=True)

class GPTPromptModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='GPT Prompt')

        self.prompt_input = discord.ui.TextInput(
            label='Prompt',
            placeholder='Masukkan prompt untuk GPT...',
            required=True
        )
        self.add_item(self.prompt_input)

        self.text_input = discord.ui.TextInput(
            label='Text',
            placeholder='Masukkan teks untuk diproses...',
            required=True
        )
        self.add_item(self.text_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        prompt = self.prompt_input.value
        text = self.text_input.value

        # Use parse.quote to encode prompt and text for URL
        encoded_prompt = parse.quote(prompt)
        encoded_text = parse.quote(text)

        api_url = f"https://aemt.me/prompt/gpt?prompt={encoded_prompt}&text={encoded_text}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') and data.get('result'):
                            gpt_result = data['result']
                            await interaction.followup.send(f"**Prompt:**\n{prompt}\n\n**Text:**\n{text}\n\n**GPT Result:**\n{gpt_result}", ephemeral=True)
                        else:
                            await interaction.followup.send("Gagal mendapatkan hasil dari GPT.", ephemeral=True)
                    else:
                        await interaction.followup.send("Gagal melakukan permintaan ke server.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan: {str(e)}", ephemeral=True)

class TranslateModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Translate')

        self.language_input = discord.ui.TextInput(
            label='Bahasa',
            placeholder='Masukkan kode bahasa (misal: en, id)',
            required=True
        )
        self.add_item(self.language_input)

        self.text_input = discord.ui.TextInput(
            label='Teks',
            placeholder='Masukkan teks yang ingin Anda terjemahkan',
            required=True
        )
        self.add_item(self.text_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        language_code = self.language_input.value
        text_to_translate = self.text_input.value

        api_url = f"https://skizo.tech/api/translate?apikey=Barkah&text={parse.quote(text_to_translate)}&lang={language_code}"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 200 and 'result' in data:
                    translated_text = data['result']
                    await interaction.followup.send(f"**Bahasa:** {language_code}\n\n**Teks:**\n{text_to_translate}\n\n**Terjemahan:**\n{translated_text}", ephemeral=True)
                else:
                    await interaction.followup.send("Gagal mendapatkan hasil terjemahan.", ephemeral=True)
            else:
                await interaction.followup.send("Gagal melakukan permintaan ke server.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan: {str(e)}", ephemeral=True)

class SpotifySearchModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Spotify Search')

        self.search_query = discord.ui.TextInput(
            label='Search Query',
            placeholder='Cari nama artis yang ini anda temukan',
            required=True
        )
        self.add_item(self.search_query)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        query = self.search_query.value.strip()
        api_key = "f268e6fb38b2cf4234ddfd20"  # Ganti dengan API key yang sesuai
        api_url = f"https://api.lolhuman.xyz/api/spotifysearch?apikey={api_key}&query={requests.utils.quote(query)}"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                results = data.get("result")

                if results and isinstance(results, list) and len(results) > 0:
                    embed = discord.Embed(title="Spotify Search Results", description=f"Results for: {query}", color=discord.Color.green())
                    for i, result in enumerate(results[:10], 1):  # Batasi hasil yang ditampilkan
                        embed.add_field(
                            name=f"{i}. {result['title']} by {result['artists']}",
                            value=f"[Listen on Spotify]({result['external_urls']['spotify']})",
                            inline=False
                        )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.followup.send("No results found.", ephemeral=True)
            else:
                await interaction.followup.send("Api key anda sudah habis", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

class SpotifyDownloadModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Spotify Downloader')

        self.spotify_url = discord.ui.TextInput(
            label='URL Spotify',
            placeholder='Masukkan URL lagu Spotify...',
            required=True
        )
        self.add_item(self.spotify_url)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        url = self.spotify_url.value.strip()
        api_key = "b0db199b0a149a4e6b1a2625"
        api_url = f"https://api.lolhuman.xyz/api/spotify?apikey={api_key}&url={requests.utils.quote(url)}"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                result = data.get("result")

                if result and result.get("link"):
                    download_url = result["link"]
                    song_response = requests.get(download_url)
                    if song_response.status_code == 200:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                            temp_file.write(song_response.content)
                            temp_file_path = temp_file.name
                        
                        await interaction.followup.send("Berhasil mengunduh lagu dari Spotify. Mengirim lagu...", ephemeral=True)
                        await interaction.followup.send(file=discord.File(temp_file_path))
                        
                        os.remove(temp_file_path)
                    else:
                        await interaction.followup.send("Gagal mengunduh lagu dari URL yang diberikan.", ephemeral=True)
                else:
                    await interaction.followup.send("Tidak ada tautan lagu yang ditemukan dalam respons.", ephemeral=True)
            else:
                await interaction.followup.send("Gagal mendapatkan tautan lagu Spotify.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan: {e}", ephemeral=True)


class AnimeSearchModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='Anime Search')

        self.search_query = discord.ui.TextInput(
            label='Search Query',
            placeholder='Masukkan nama anime...',
            required=True
        )
        self.add_item(self.search_query)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        query = self.search_query.value.strip()
        api_key = "b0db199b0a149a4e6b1a2625"
        api_url = f"https://api.lolhuman.xyz/api/anime?apikey={api_key}&query={requests.utils.quote(query)}"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                result = data.get("result")

                if result:
                    title_romaji = result["title"].get("romaji", "N/A")
                    title_english = result["title"].get("english", "N/A")
                    title_native = result["title"].get("native", "N/A")
                    cover_image = result["coverImage"].get("large", "")
                    format = result.get("format", "N/A")
                    episodes = result.get("episodes", "N/A")
                    duration = result.get("duration", "N/A")
                    status = result.get("status", "N/A")
                    season = result.get("season", "N/A")
                    season_year = result.get("seasonYear", "N/A")
                    source = result.get("source", "N/A")
                    genres = ", ".join(result.get("genres", []))
                    start_date = result.get("startDate", {})
                    end_date = result.get("endDate", {})
                    description = result.get("description", "N/A")
                    average_score = result.get("averageScore", "N/A")
                    mal_url = result.get("mal_url", "N/A")
                    
                    start_date_formatted = f"{start_date.get('year', 'N/A')}-{start_date.get('month', 'N/A')}-{start_date.get('day', 'N/A')}"
                    end_date_formatted = f"{end_date.get('year', 'N/A')}-{end_date.get('month', 'N/A')}-{end_date.get('day', 'N/A')}"

                    embed = discord.Embed(title=title_romaji, description=description, color=discord.Color.blue())
                    embed.set_thumbnail(url=cover_image)
                    embed.add_field(name="Title (English)", value=title_english, inline=False)
                    embed.add_field(name="Title (Native)", value=title_native, inline=False)
                    embed.add_field(name="Format", value=format, inline=False)
                    embed.add_field(name="Episodes", value=episodes, inline=False)
                    embed.add_field(name="Duration", value=f"{duration} minutes per episode", inline=False)
                    embed.add_field(name="Status", value=status, inline=False)
                    embed.add_field(name="Season", value=f"{season} {season_year}", inline=False)
                    embed.add_field(name="Source", value=source, inline=False)
                    embed.add_field(name="Genres", value=genres, inline=False)
                    embed.add_field(name="Start Date", value=start_date_formatted, inline=False)
                    embed.add_field(name="End Date", value=end_date_formatted, inline=False)
                    embed.add_field(name="Average Score", value=average_score, inline=False)
                    embed.add_field(name="MyAnimeList URL", value=mal_url, inline=False)

                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.followup.send("No results found.", ephemeral=True)
            else:
                await interaction.followup.send("Api key anda sudah habis", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)


class ApkDownloaderModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title='APK Downloader')

        self.package_name = discord.ui.TextInput(
            label='Package Name',
            placeholder='Masukkan nama package APK...',
            required=True
        )
        self.add_item(self.package_name)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        package_name = self.package_name.value

        # Memanggil API untuk mendapatkan informasi APK
        apk_info = await self.get_apk_info(package_name)

        if apk_info:
            file_path = await self.download_apk(apk_info['apk_link'])

            if file_path:
                await interaction.followup.send("Berhasil mengunduh APK. Berikut adalah file yang diminta:", file=discord.File(file_path))
                os.remove(file_path)  # Hapus file setelah dikirim
            else:
                await interaction.followup.send("Gagal mengunduh file APK.")
        else:
            await interaction.followup.send("Gagal mengunduh APK. Silakan coba lagi nanti.")

    async def get_apk_info(self, package_name):
        url = f"https://api.lolhuman.xyz/api/apkdownloader?apikey=b0db199b0a149a4e6b1a2625&package={package_name}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['status'] == 200:
                        return data['result']
                    else:
                        print(f"Gagal mengunduh APK: {data['message']}")
                else:
                    print(f"Failed to fetch APK info. Status code: {response.status}")

        return None

    async def download_apk(self, apk_url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(apk_url) as response:
                    if response.status == 200:
                        # Membuat file sementara untuk menyimpan APK
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".apk") as temp_file:
                            temp_file.write(await response.read())
                            return temp_file.name
                    else:
                        print(f"Failed to download APK. Status code: {response.status}")
        except Exception as e:
            print(f"Error downloading APK: {e}")

        return None

    def create_apk_embed(self, apk_info):
        embed = discord.Embed(
            title=apk_info['apk_name'],
            description=f"Versi: {apk_info['apk_version']}\nAuthor: {apk_info['apk_author']}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=apk_info['apk_icon'])
        embed.add_field(name="Download Link", value=apk_info['apk_link'], inline=False)
        return embed