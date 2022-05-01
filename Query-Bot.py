
#Ein Discord-Bot um den Status eines Minecraft servers und die Spieler-Liste in einen discord chat zu schreiben.
#
# @author (FireIP)
# @version (0.7.1)
#
#
#	message when bot comes online



import discord
from discord.ext.commands import Bot
from discord.ext import commands

import asyncio
import time

from threading import Thread
from mcstatus import MinecraftServer

global q
q = True

global s
s = ''

global query
global lastquery

global server

serverAdress = "000.000.000.000"    #replace with own IP adress or domain
serverPort = 25565                  #replace with querry port of server

server = MinecraftServer(serverAdress, serverPort)



global Client
Client = discord.Client()  # Initialise Client
global client
client = commands.Bot(command_prefix="?")  # Initialise client bot

global channel
global start


@client.event
async def on_ready():
    global Client
    global client

    global q
    global query
    global lastquery

    global _loop

    global channel
    channel = client.get_channel('000000000000000000')  #replace with channel id of channel the bot should write to

    print("Bot is online and connected to Discord")  # This will be called when the bot connects to the server
    await client.send_message(channel, "Bot is online")

    query = server.query()
    lastquery = query.players.names

    status = server.status()

    print("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))
    print("The server has the following players online: {0}".format(", ".join(query.players.names)))

    _loop = asyncio.get_event_loop()

    t.start()

@client.event
async def on_message(message):
	global Client
	global client

	global q


	global channel

	if message.content == "cookie":
		await client.send_message(message.channel, ":cookie:") #responds with Cookie emoji when someone says "cookie"
#	elif message.content == "!start!":
#		if message.author.id == "000000000000000000":   #replace with discord user ID of admin
#			channel = message.channel
#			start = message
#			print("Query channel changed!")
#			await client.send_message(channel, "Query started!")

	elif message.content == "stopQuery":
		if message.author.id == "000000000000000000":   #replace with discord user ID of admin
			q = False

			print("Query stoped!")
			await client.send_message(channel, "Query stoped!")

	elif message.content == "startQuery":
		if message.author.id == "000000000000000000":   #replace with discord user ID of admin
			q = True
			t = Thread(target=querying)
			t.start()

			print("Query started!")
			await client.send_message(channel, "Query started!")


def querying():
    global q
    global query
    global lastquery

    global server

    global channel

    global Client
    global client

    global _loop

    while q:
        # 'status' is supported by all Minecraft servers that are version 1.7 or higher.
        # status = server.status()
        query = server.query()
        if lastquery != query.players.names:
            # print("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))

            # 'query' has to be enabled in a servers' server.properties file.
            # It may give more information than a ping, such as a full player list or mod information.
            query = server.query()
            print("The server has the following players online: {0}".format(", ".join(query.players.names)))

            lastquery = query.players.names

            asyncio.run_coroutine_threadsafe(client.send_message(channel,
                                                                 "The server has the following players online: {0}".format(
                                                                     ", ".join(query.players.names))), _loop)

        time.sleep(30)


t = Thread(target=querying)

client.run("xxxxxxxxxxxxxxxxxxxxxxxx.xxxxxx.xxxxxxxxx-xxxxxxxxxxxxxxxxx")  # Replace token with your bots token