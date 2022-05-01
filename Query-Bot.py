# Ein Discord-Bot um den Status eines Minecraft servers und die Spieler-Liste in einen discord chat zu schreiben.
#
# @author (FireIP)
# @version (0.11)
#
#
#	Customized Login notifications


import discord

import asyncio
import time

from threading import Thread

from mcstatus import MinecraftServer

global _loop
_loop = None

global SSchannel
SSchannel = None

client = discord.Client()


@client.event
async def on_ready():
    global _loop
    global SSchannel

    SSchannel = client.get_channel(000000000000000000)  #replace with channel id of channel the bot should write to

    await SSchannel.send("Bot is online")
    print("Bot is online and connected to Discord")

    _loop = asyncio.get_event_loop()

    qt.start()
    dt.start()


@client.event
async def on_message(message):
    global SSchannel
    global q
    global sOnline
    global lastQuery

    if message.content == "cookie":
        await message.channel.send(":cookie:")

    elif message.content.startswith("s-"):

        if message.content == "s-stopQuery":
            if message.author.id == 000000000000000000:   #replace with discord user ID of admin
                q = False

                print("Query stoped!")
                await message.channel.send("Query stoped!")

        elif message.content == "s-startQuery":
            if message.author.id == 000000000000000000:   #replace with discord user ID of admin
                if q == False:
                    q = True

                    qt = Thread(target=queryThread)
                    qt.start()

                print("Query started!")
                await message.channel.send("Query started!")

        elif message.content == "s-restartQuery":
            if message.author.id == 000000000000000000:   #replace with discord user ID of admin
                q = False

                await message.channel.send("Restarting Query...")

                time.sleep(5)

                print("Query stoped!")
                await message.channel.send("Query stoped!")

                q = True

                qt = Thread(target=queryThread)
                qt.start()
                time.sleep(1)
                print("Query started!")
                await message.channel.send("Query started!")
                await message.channel.send("Query sucessfully restarted!")

        elif message.content[:10] == "s-addWatch":
            if message.author.id == 000000000000000000:   #replace with discord user ID of admin
                temp = []
                for n in names.keys():
                    temp.append(n + '\n')

                temp.append(message.content[11:] + '\n')
                nameFile = open("Names.txt", 'w')
                nameFile.writelines(temp)
                nameFile.close()
                names[message.content[11:]] = False

                await message.channel.send("Added " + message.content[11:] + " to watchlist.")

        elif message.content[:10] == "s-remWatch":
            if message.author.id == 000000000000000000:   #replace with discord user ID of admin
                del names[message.content[11:]]
                temp = []
                for n in names.keys():
                    temp.append(n + '\n')

                nameFile = open("Names.txt", 'w')
                nameFile.writelines(temp)
                nameFile.close()

                await message.channel.send("Removed " + message.content[11:] + " from watchlist.")


        elif message.content == "s-Players" or message.content == "s-p" or message.content == "s-P":
            if q == True and sOnline == True:
                await message.channel.send(
                    "The server has the following players online: {0}".format(", ".join(lastQuery.players.names)))
            elif q == False:
                await message.channel.send("Query is inactive at the moment. Ask the server owner to start it.")
            elif sOnline == False:
                await message.channel.send("The server is offline.")

        elif message.content in ("s-Status", "s-s", "s-S"):
            if q == True:
                if sOnline == True:
                    await message.channel.send("Server is online")
                else:
                    await message.channel.send("Server is offline")
            else:
                await message.channel.send("Query is inactive at the moment. Ask the server owner to start it.")

        elif message.content in ("s-Version", "s-v", "s-V"):
            if q == True:
                if sOnline == True:
                    await message.channel.send("The server is running version {0}".format(lastQuery.raw["version"]))
                else:
                    await message.channel.send("The server is offline.")
            else:
                await message.channel.send("Query is inactive at the moment. Ask the server owner to start it.")

        elif message.content in ("s-motd", "s-m", "s-M"):
            if q == True:
                if sOnline == True:
                    await message.channel.send("The message of the day is {0}".format(lastQuery.motd))
                else:
                    await message.channel.send("The server is offline.")
            else:
                await message.channel.send("Query is inactive at the moment. Ask the server owner to start it.")

        elif message.content == "s-h" or message.content == "s-help":
            await message.channel.send(
                "Admin:\n**s-stopQuery** *stops the query*\n**s-startQuery** *starts the query*\n**s-restartQuery** *restarts the query*\n\nUser:\n**s-Players (s-p, s-P)** *lists players on server*\n**s-Status (s-s, s-S)** *checks if server is online*\n**s-Version (s-v, s-V)** *returns the version number the server is running*\n**s-motd (s-m, s-M)** *returns the message of the day/description of the server*\n**s-h (s-help)** *shows this list*\n**cookie** *spawns a cookie*")


names = {}
with open("Names.txt") as f:
    for line in f:

        if line[-1:] == "\n":
            X = line[:-1]
            names[X] = False
        else:
            names.append(line)

names.setdefault("404", False)

global q
q = True

global qStat
qStat = False

global server
serverAdress = "000.000.000.000"    #replace with own IP adress or domain
serverPort = 25565                  #replace with querry port of server

server = MinecraftServer(serverAdress, serverPort)

global lastQuery
lastQuery = None

global sOnline
sOnline = False


def queryThread():
    global q
    global qStat

    global server
    global lastQuery
    global sOnline
    global SSchannel
    global _loop

    while q:
        try:
            server.status(tries=1)

        except:
            if sOnline != False:
                asyncio.run_coroutine_threadsafe(SSchannel.send("Server is offline."), _loop)
                sOnline = False
                lastQuery = None

        else:
            query = server.query()
            lastQuery = query

            if sOnline != True:
                asyncio.run_coroutine_threadsafe(SSchannel.send("Server is online."), _loop)
                sOnline = True

            for i in lastQuery.players.names:
                if names.__contains__(i):
                    if not names[i]:
                        asyncio.run_coroutine_threadsafe(SSchannel.send(i + " is online."), _loop)
                        names[i] = True

            for i in names.keys():
                if not lastQuery.players.names.__contains__(i):
                    if names[i]:
                        asyncio.run_coroutine_threadsafe(SSchannel.send(i + " is offline."), _loop)
                        # tempName = names.copy()
                        names[i] = False

        qStat = True


global monitor
monitor = True


def selfDiagnose():
    global q
    global qStat

    while (monitor):
        time.sleep(30)

        if q:
            qStat = False

            time.sleep(10)

            if qStat == False:
                asyncio.run_coroutine_threadsafe(SSchannel.send(
                    "Querry thread did not answer for 10 seconds.\n--> Assuming crash --> Restarting..."), _loop)

                rQ = Thread(target=restartQuery)
                rQ.start()

                rD = Thread(target=restartDiagnostic)
                rD.start()


def restartQuery():
    global q
    global qStat

    global qt

    q = False
    qStat = False

    asyncio.run_coroutine_threadsafe(SSchannel.send("Restarting Query..."), _loop)
    Thread.join(qt)
    asyncio.run_coroutine_threadsafe(SSchannel.send("Query stoped!"), _loop)
    print("Query stoped!")

    q = True
    qt = Thread(target=queryThread)
    qt.start()

    asyncio.run_coroutine_threadsafe(SSchannel.send("Query started!"), _loop)
    print("Query started!")
    asyncio.run_coroutine_threadsafe(SSchannel.send("Query sucessfully restarted!"), _loop)


def restartDiagnostic():
    global monitor
    global qStat

    global dt

    monitor = False
    qStat = False

    asyncio.run_coroutine_threadsafe(SSchannel.send("Restarting Self-Diagnose..."), _loop)
    Thread.join(dt)
    asyncio.run_coroutine_threadsafe(SSchannel.send("Self-Diagnose stoped!"), _loop)
    print("Self-Diagnose stoped!")

    monitor = True
    dt = Thread(target=selfDiagnose)
    dt.start()

    asyncio.run_coroutine_threadsafe(SSchannel.send("Self-Diagnose started!"), _loop)
    print("Self-Diagnose started!")
    asyncio.run_coroutine_threadsafe(SSchannel.send("Self-Diagnose sucessfully restarted!"), _loop)


time.sleep(10)

global qt
qt = Thread(target=queryThread)
global dt
dt = Thread(target=selfDiagnose)

client.run("xxxxxxxxxxxxxxxxxxxxxxxx.xxxxxx.xxxxxxxxx-xxxxxxxxxxxxxxxxx")  # Replace token with your bots token