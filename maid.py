# maid.py
#
# MPU Maid Bot
#
# Creator: Johnathan Tiong <johnathan.tiong@gmail.com>
#
import os
import secrets
import mysql.connector
import valve.rcon

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

token = os.getenv('DISCORD_TOKEN')
server_address = (os.getenv('SERVER_HOST'), os.getenv('SERVER_PORT'))
server_password = os.getenv('SERVER_PASS')

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

@bot.command(name='hello', help='Responds to a hello message from a user')
async def hello(ctx):
    msg = "Hello there, {0.author.mention}!".format(ctx.message)
    await ctx.send(msg)

@bot.command(name='roll', help='roll [number of dice] [number of sides per die]')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(secretsGenerator.randrange(1, number_of_sides + 1))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='whitelist', help='whitelist [player-minecraft-name]')
async def whitelist(ctx, minecrafter: str):
    with valve.rcon.RCON(server_address, server_password) as rcon:
        print(rcon("whitelist add {minecrafter}"))
        print(rcon("whitelist reload"))
    msg = "Player {minecrafter} has now been whitelisted".format(ctx.message)
    await ctx.send(msg)

@bot.event
async def on_ready():
    print('Logged in as ')
    print(bot.user.name)
    print('-------------')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send(":x: Can't send response correctly (message too long)")

bot.run(token)

