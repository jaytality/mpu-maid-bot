# maid.py
#
# MPU Maid Bot
#
# Creator: Johnathan Tiong <johnathan.tiong@gmail.com>
#
import os
import discord
import secrets
import mysql.connector

from dotenv import load_dotenv
from discord.ext import commands, tasks
from mcrcon import MCRcon
from mcstatus import MinecraftServer

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!maid ')
secretsGenerator = secrets.SystemRandom()

try:
    mydb = mysql.connector.connect(
        host = os.getenv('DB_HOST'),
        user = os.getenv('DB_USER'),
        passwd = os.getenv('DB_PASS'),
        database = os.getenv('DB_NAME'),
    )

    if mydb.is_connected():
        cursor = mydb.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("Connection to DB established: ", record)
        print('-----------------------------------------')

        maidCreateLogTableSQL = """
        CREATE TABLE IF NOT EXISTS maid_log (
            id INT AUTO_INCREMENT,
            user VARCHAR(200),
            action TEXT,
            time INT,
            PRIMARY KEY (id))"""

        cursor.execute(maidCreateLogTableSQL)

except Error as e:
    print("Error connecting to DB: ", e)


server = MinecraftServer.lookup(os.getenv('SERVER_HOST'))

#
# Hello test command
#
@bot.command(name='hello', help='Responds to a hello message from a user')
async def hello(ctx):
    msg = "Hello there, {0.author.mention}!".format(ctx.message)
    await ctx.send(msg)

#
# DnD/TableTop dice rolling
#
@bot.command(name='roll', help='roll [number of dice] [number of sides per die]')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(secretsGenerator.randrange(1, number_of_sides + 1))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

#
# Minecraft Whitelisting
#
@bot.command(name='whitelist', help='whitelists [player-minecraft-name] on our minecraft server')
async def whitelist(ctx, minecrafter: str):
    with MCRcon(os.getenv('SERVER_HOST'), os.getenv('SERVER_PASS')) as mcr:
        resp = mcr.command("/whitelist add " + minecrafter)
        print(resp)
    msg = "Whitelisted " + minecrafter + "! They can now connect to the server".format(ctx.message)
    await ctx.send(msg)

#
# On Bot Ready
#
@bot.event
async def on_ready():
    mcServerStatus.start()
    print('Logged in as: ' + bot.user.name)
    print('-------------')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send(":x: Can't send response correctly (message too long)")

#
# Minecraft Status Update (every 30 seconds)
#
@tasks.loop(seconds=30)
async def mcServerStatus():
    status = server.status()
    statusMsg = "Minecraft: {0} Online".format(status.players.online)
    await bot.change_presence(activity=discord.Game(name=statusMsg))

bot.run(token)

