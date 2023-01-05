"""
Bot Discord for Minecraft Server
"""

# Librerias
import json
import discord
from discord.ext import commands
from python_aternos import Client, Status, ServerStartError, atserver, atwss

with open('settings.json') as file:
    data = json.load(file)

token = data["Discord"]["discord-token"]
mychannel = data["Discord"]["discord-channel"]
username = data["Aternos"]["username"]
password = data["Aternos"]["password"]
server = data["Aternos"]["server-number"]

# Inicializando el Bot de Discord
bot = commands.Bot(command_prefix='!', intents=discord.Intents(messages=True, guilds=True, message_content=True))

# Obtener la secion de Aternos
def sesion(user = username, pswd = password):
    return Client.from_credentials(user,pswd)

# Obtener el Servidor
def selec_server(server = server):
    return sesion().list_servers()[server]

# Websocket
socket = selec_server().wss()

# Bot en linea
@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')
    channel = bot.get_channel(mychannel)
    await channel.send('Hola! Listos para jugar.')

# Evento para obtener los datos del servidor
@bot.command(name="info", pass_context=True, help="Informacion del servidor")
@commands.has_role("Jugador")
async def server(ctx):
    myServer = selec_server()
    embed = discord.Embed(title="Datos del Servidor", color=0x00FF00)
    embed.add_field(name='Nombre del servidor',value=f' {myServer.subdomain}',inline=False)
    embed.add_field(name='Dirección del servidor',value=f' {myServer.domain}',inline=False)
    embed.add_field(name='Puerto',value=f' {myServer.port}',inline=False)
    await ctx.send(embed=embed)

# Evento para conocer el estado del servidor
@bot.command(name="status", pass_context=True, help="Obtener el estado del servidor")
@commands.has_role("Jugador")
async def status(ctx):
    if ctx.channel.id == mychannel:
        embed = None
        myServer = selec_server()
        if myServer.status_num == Status.off:
            embed = discord.Embed(title="Desconectado", color=0xFE2E2E)
        if myServer.status_num == Status.on:
            embed = discord.Embed(title="En Linea",color=0x00FF00)
        await ctx.send(embed=embed)

# Evento para obtener los jugadores activos
@bot.command(name="players", pass_context=True, help="Obtener los jugadores conectados")
@commands.has_role("Jugador")
async def players(ctx):
    if ctx.channel.id == mychannel:
        myServer = selec_server()
        cad = ""
        for c in myServer.players_list:
            cad += "\n" + c
        await ctx.send(embed=discord.Embed(title=f"Jugadores {myServer.players_count}/{myServer.slots}",description=cad,color=0x00FF00))

# Evento para iniciar el servidor
@bot.command(name="star", pass_context=True, help="Inicia el servidor")
@commands.has_role("Jugador")
async def star(ctx):
    await socket.connect()
    myServer = selec_server()
    if ctx.channel.id == mychannel:
        try:
            if myServer.status_num == Status.off:
                myServer.start()
                await ctx.send(embed=discord.Embed(title=f"Iniciando el servidor {myServer.subdomain}",color=0xFFBF00))
            else:
                await ctx.send(embed=discord.Embed(title=f"El Servidor {myServer.subdomain} esta en Linea",color=0x00FF00))
        except ServerStartError as err:
            await ctx.send(embed=discord.Embed(title=f'No se pudo iniciar el servidor {myServer.subdomain}\n{err.MESSAGE}', color=0xFE2E2E))

# Evento para parar el servidor
@bot.command(name="stop", pass_context=True, help="Para el servidor")
@commands.has_role("Admin")
async def stop(ctx):
    myServer = selec_server()
    if ctx.channel.id == mychannel:
        try:
            if myServer.status_num == Status.on:
                myServer.stop()
                await ctx.send(embed=discord.Embed(title=f"Se apagara el servidor {myServer.subdomain}",color=0xFFBF00))
            else:
                await ctx.send(embed=discord.Embed(title=f"El Servidor {myServer.subdomain} esta en Apagado",color=0xFFBF00))
        except ServerStartError as err:
            await ctx.send(embed=discord.Embed(title=f'{myServer.subdomain}\n{err.MESSAGE}', color=0xFE2E2E))

# Capturar el error
@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.CommandNotFound):
        print("Comando no valido")
    elif isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
        print("No eres admin")
    else:
        print(error)

bot.run(token)