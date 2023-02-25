import discord
from discord.ext import commands
from discord import app_commands

import asyncio
import json
import uuid
from logger import logger
import traceback
import os
from typing import List

import magic
from pytube import YouTube

with open('config.json') as f:
    config = json.load(f)

MSG_DURATION: int = 2
DISCORD_TOKEN: str = config['DISCORD_TOKEN']
MOD_ROLES: List[str] = config['MOD_ROLES']

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

dump_path = 'intros.json'
intros = {}

def has_audio(file_name: str) -> bool:
    magic_instance = magic.Magic(mime=True)
    mimestart = magic_instance.from_file(file_name)

    if mimestart != None:
        return 'video' in mimestart or 'audio' in mimestart

    return False

def save_state():
    with open(dump_path, 'w') as fout:
        json.dump(intros, fout)

@client.event
async def on_ready() -> None:
    await tree.sync()
    logger.info('synced tree')

@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    member_id = str(member.id)
    if member_id not in intros:
        return

    if before.channel is None and after.channel is not None:
        source = discord.FFmpegPCMAudio(intros[member_id])

        channel = after.channel
        voice = await channel.connect()
        voice.play(source)

        while voice.is_playing():
            await asyncio.sleep(1)

        await voice.disconnect()

def download_youtube_audio(url: str, file_id: str) -> None:
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    video.download(filename=file_id)

async def set_intro(interaction: discord.Interaction, user_id: int, url: str) -> None:
    user_id = str(user_id)
    file_id = str(uuid.uuid4()) + '.intro'
    logger.info(f'{user_id} set intro to {url}')
    try:
        if 'youtu' in url:
            download_youtube_audio(url, file_id)
        else:
            os.system(f'wget {url} -O {file_id}')
            if not has_audio(file_id):
                raise ValueError('File does not contain audio')

        if user_id in intros and os.path.exists(intros[user_id]):
            os.remove(intros[user_id])
        intros[user_id] = file_id
        save_state()
        await interaction.response.send_message('Done!', ephemeral=True, delete_after=MSG_DURATION)
    except:
        if os.path.exists(file_id):
            os.remove(file_id)
        logger.error(f'Error reading file {url}')
        await interaction.response.send_message(f'Error reading file', ephemeral=True, delete_after=MSG_DURATION)
        traceback.print_exc()

@tree.command(name='setotherupload')
@app_commands.checks.has_any_role(*MOD_ROLES)
async def _set_other_attachment(interaction: discord.Interaction, other: discord.User, attachment: discord.Attachment) -> None:
    await set_intro(interaction, other.id, attachment.url)

@tree.command(name='setother')
@app_commands.checks.has_any_role(*MOD_ROLES)
async def _set_other_url(interaction: discord.Interaction, other: discord.User, url: str) -> None:
    await set_intro(interaction, other.id, url)

@tree.command(name='setupload', description='Set intro to uploaded attachment')
async def _set_intro_attachment(interaction: discord.Interaction, attachment: discord.Attachment) -> None:
    await set_intro(interaction, interaction.user.id, attachment.url)

@tree.command(name='set', description='Set intro to media in URL')
async def _set_intro_url(interaction: discord.Interaction, url: str) -> None:
    await set_intro(interaction, interaction.user.id, url)

async def unset(interaction: discord.Interaction, user_id: int) -> None:
    user_id = str(user_id)
    if user_id in intros:
        if os.path.exists(intros[user_id]):
            os.remove(intros[user_id])
        del intros[user_id]
        save_state()
        await interaction.response.send_message('Done!', ephemeral=True, delete_after=MSG_DURATION)
    else:
        await interaction.response.send_message('No current intro set.', ephemeral=True, delete_after=MSG_DURATION)

@tree.command(name='remove', description='Remove your current intro')
async def _unset_intro(interaction: discord.Interaction) -> None:
    await unset(interaction, interaction.user.id)

@tree.command(name='removeother')
@app_commands.checks.has_any_role(*MOD_ROLES)
async def _unset_other(interaction: discord.Interaction, user: discord.User) -> None:
    await unset(interaction, user.id)


if os.path.exists(dump_path):
    with open(dump_path, 'r') as fin:
        logger.info('Loaded previous dump')
        intros = json.load(fin)

client.run(DISCORD_TOKEN, log_handler=None)
