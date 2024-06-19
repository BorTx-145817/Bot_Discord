# lib/callbacks.py
# author: Barkah

import discord
from lib.modals import *


# Callback untuk setiap tombol


async def button1_callback(interaction):
    app_info = await interaction.client.application_info()
    owner = app_info.owner
    response = f"Pemilik bot ini adalah: {owner.name}"
    await interaction.response.send_message(response)

async def button4_callback(interaction):
    await interaction.response.send_modal(CariYouTubeModal())

async def button5_callback(interaction):
    await interaction.response.send_modal(YouTubeDownloaderModal())

async def button6_callback(interaction):
    await interaction.response.send_modal(YouTubeDownloaderAudioModal())

async def button7_callback(interaction):
    await interaction.response.send_modal(ChatGPTModal())

async def button8_callback(interaction):
    await interaction.response.send_modal(TikTokTDLModal())

async def button9_callback(interaction):
    await interaction.response.send_modal(AudioTiktokTDLModal())

async def button10_callback(interaction):
    await interaction.response.send_modal(FacebookVideoDownloaderModal())

async def button11_callback(interaction):
    await interaction.response.send_modal(FacebookAudioDownloaderModal())

async def button12_callback(interaction):
    await interaction.response.send_modal(InstagramVideoDownloaderModal())

async def button13_callback(interaction):
    await interaction.response.send_modal(Dalle3Modal())

async def button14_callback(interaction):
    await interaction.response.send_modal(PinterestDownloaderModal())

async def button15_callback(interaction):
    await interaction.response.send_modal(SimiModal())

async def button16_callback(interaction):
    await interaction.response.send_modal(LyricsModal())

async def button17_callback(interaction):
    await interaction.response.send_modal(JadwalTVModal())

async def button18_callback(interaction):
    await interaction.response.send_modal(MediafireDownloaderModal())

async def button19_callback(interaction):
    await interaction.response.send_modal(GoogleDriveDownloaderModal())

async def button20_callback(interaction):
    await interaction.response.send_modal(GeminiModal())

async def button21_callback(interaction):
    await interaction.response.send_modal(GPTPromptModal())

async def button22_callback(interaction):
    await interaction.response.send_modal(TranslateModal())

async def button23_callback(interaction):
    await interaction.response.send_modal(SpotifySearchModal())

async def button24_callback(interaction):
    await interaction.response.send_modal(SpotifyDownloadModal())

async def button25_callback(interaction):
    await interaction.response.send_modal(AnimeSearchModal())

async def button26_callback(interaction):
    await interaction.response.send_modal(ApkDownloaderModal())