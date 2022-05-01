# Ein Discord-Bot um den Status eines Minecraft servers und die Spieler-Liste in einen discord chat zu schreiben.
#
# @author (FireIP)
# @version (0.13.0)
#
#
#	added dns checker


import discord

import asyncio
import time

from threading import Thread

from mcstatus import MinecraftServer

import os

import json


# Konstanten------------------
global dataJsonPath
dataJsonPath = "data.json"

global dns
dns = ["tum-v6.serveminecraft.net", "tum.serveminecraft.net"]


# Variablen-------------------
global _loop
_loop = None

global serverDict
serverDict = {"000000000000000000": 0}  #replace with discord server ID of server the bot is on

global SSchannel
SSchannel = []
global SSchannelID
SSchannelID = [[000000000000000000]]    #replace with channel id of channel the bot should write to

client = discord.Client()

global admins
admins = [[000000000000000000]] #replace with discord user ID of admin

global owner
owner = 000000000000000000      #replace with discord user ID of admin
global ownerDM


@client.event
async def on_ready():
    global _loop
    global SSchannel
    global SSchannelID
    global ownerDM
    global owner

    ownerDM = client.get_user(owner)

    _loop = asyncio.get_event_loop()
    for s in range(len(SSchannelID)):
        SSchannel.append([])
        for i in range(len(SSchannelID[s])):
            SSchannel[s].append(client.get_channel(SSchannelID[s][i]))


    # for s in range(len(SSchannelID)):
    #     for i in range(len(SSchannelID[s])):
    #         SSchannel[s][i] = client.get_channel(SSchannelID[s][i])

    sendToAll("Bot is online")
    print("Bot is online and connected to Discord")

    for sId in serverDict.keys():
        if len(admins[serverDict[sId]]) == 0:
            if not sendToServer("Es gibt keine admins auf diesem Server.", sId):
                asyncio.run_coroutine_threadsafe(ownerDM.send("Es gibt keine admins auf diem Server: \'" + sId + "\'"), _loop)

    qt.start()
    dt.start()


@client.event
async def on_message(message):
    global SSchannel
    global q
    global sOnline
    global lastQuery
    global admins
    global ownerDM

    if message.content == "cookie":
        await message.channel.send(":cookie:")

    elif message.content.startswith("s-"):

        if message.content == "s-stopQuery":
            if message.author.id in admins[serverDict[str(message.guild.id)]]:
                q = False

                print("Query stoped!")
                await message.channel.send("Query stoped!")

        elif message.content == "s-startQuery":
            if message.author.id in admins[serverDict[str(message.guild.id)]]:
                if q == False:
                    q = True

                    qt = Thread(target=queryThread)
                    qt.start()

                print("Query started!")
                await message.channel.send("Query started!")

        elif message.content == "s-restartQuery":
            if message.author.id in admins[serverDict[str(message.guild.id)]]:
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

        elif message.content == "s-addThisChannel":
            if not serverDict.keys().__contains__(str(message.guild.id)):
                serverDict[str(message.guild.id)] = serverDict.keys().__len__()
                SSchannelID.append([message.channel.id])
                SSchannel.append([message.channel])
                sendToServer("This server does not jet have an Admin promoting sender of s-addThisChannel.", message.guild.id)
                admins.append([message.author.id])
                saveCurrData()
                await message.channel.send("Channel was added.")

            elif message.author.id in admins[serverDict[str(message.guild.id)]]:
                SSchannelID[serverDict[str(message.guild.id)]].append(message.channel.id)
                SSchannel[serverDict[str(message.guild.id)]].append(message.channel)
                saveCurrData()
                await message.channel.send("Channel was added.")

        elif message.content[:13] == "s-promoteById":
            if message.author.id in admins[serverDict[str(message.guild.id)]]:
                admins[serverDict[str(message.guild.id)]].append(int(message.content[14:]))
                saveCurrData()
                await message.channel.send("Promoted " + message.content[14:])
            else:
                await message.channel.send("Du bist kein Admin!")

        elif message.content[:10] == "s-addWatch":
            if message.author.id == owner:
                names[message.content[11:]] = False
                saveCurrData()

                await message.channel.send("Added " + message.content[11:] + " to watchlist.")

        elif message.content[:10] == "s-remWatch":
            if message.author.id == owner:
                del names[message.content[11:]]
                saveCurrData()

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

                for actI in range(dns.__len__()):
                    if not dnsStat[actI]:
                        await message.channel.send(dns[actI] + " is offline.")

                    if dnsStat[actI]:
                        await message.channel.send(dns[actI] + " is online.")
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
                "Admin:\n**s-stopQuery** *stops the query*\n**s-startQuery** *starts the query*\n**s-restartQuery** "
                "*restarts the query*\n**s-addThisChannel** *adds this channel to list of info "
                "channels*\n\nUser:\n**s-Players (s-p, s-P)** *lists players on server*\n**s-Status (s-s, "
                "s-S)** *checks if server is online*\n**s-Version (s-v, s-V)** *returns the version number the server "
                "is running*\n**s-motd (s-m, s-M)** *returns the message of the day/description of the server*\n**s-h "
                "(s-help)** *shows this list*\n**cookie** *spawns a cookie*")


global names
names = {}

def saveCurrData():
    global serverDict, SSchannelID, admins, owner, names
    if os.path.isfile(dataJsonPath):
        os.remove(dataJsonPath)

    remF = open(dataJsonPath, 'x')
    remD = [serverDict, SSchannelID, admins, owner, names]
    json.dump(remD, remF)
    remF.close()


def loadCurrData():
    global serverDict, SSchannelID, admins, owner, names
    if os.path.isfile(dataJsonPath):
        remF = open(dataJsonPath, 'r')
        serverDict, SSchannelID, admins, owner, names = json.load(remF)
        remF.close()
    names.setdefault("404", False)


def sendToAll(message):
    global SSchannel, admins, owner, names, _loop
    for s in SSchannel:
        for i in s:
            asyncio.run_coroutine_threadsafe(i.send(message), _loop)


def sendToServer(message, serverId):
    global serverDict, SSchannel, admins, owner, names, _loop
    s = serverDict[str(serverId)]
    for i in SSchannel[s]:
        try:
            asyncio.run_coroutine_threadsafe(i.send(message), _loop)
            return True
        except:
            return False



global q
q = True

global qStat
qStat = False

global server
serverAdress = "000.000.000.000"    #replace with own IP adress or domain
serverPort = 25565                  #replace with querry port of server

server = MinecraftServer(serverAdress, serverPort)

global dnsServ
dnsServ = []
for i in range(dns.__len__()):
    dnsServ.append(MinecraftServer(dns[i], 25565))

global dnsStat
dnsStat = []
for i in range(dns.__len__()):
    dnsStat.append(True)

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
    global ownerDM

    while q:
        # timeout = Timeout(5)

        #----dns Query----
        for actI in range(dns.__len__()):
            try:
                dnsServ[actI].status()
            except:
                if dnsStat[actI]:
                    sendToAll(dns[actI] + " is offline.")
                    dnsStat[actI] = False
            else:
                if not dnsStat[actI]:
                    sendToAll(dns[actI] + " is online.")
                    dnsStat[actI] = True

        try:
            query = server.query(tries=1)

        except:
            if sOnline != False:
                sendToAll("Server is offline.")
                sOnline = False
                lastQuery = None

        else:
            lastQuery = query

            if sOnline != True:
                sendToAll("Server is online.")
                sOnline = True

            for i in names.keys():
                if not lastQuery.players.names.__contains__(i):
                    if names[i]:
                        time.sleep(0.75)
                        try:
                            tempQuery = server.query(tries=1)
                        except:
                            tempQuery = lastQuery

                        if not tempQuery.players.names.__contains__(i):
                            asyncio.run_coroutine_threadsafe(ownerDM.send(i + " is offline."), _loop)
                            names[i] = False
                else:
                    if not names[i]:
                        time.sleep(0.75)
                        try:
                            tempQuery = server.query(tries=1)
                        except:
                            tempQuery = lastQuery

                        if tempQuery.players.names.__contains__(i):
                            asyncio.run_coroutine_threadsafe(ownerDM.send(i + " is online."), _loop)
                            names[i] = True

        finally:
            # timeout.cancel()
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

            time.sleep(15)

            if qStat == False:
                asyncio.run_coroutine_threadsafe(SSchannel.send(
                    "Querry thread did not answer for 15 seconds.\n--> Assuming crash --> Restarting..."), _loop)

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

    sendToAll("Restarting Query...")
    Thread.join(qt)
    sendToAll("Query stoped!")
    print("Query stoped!")

    q = True
    qt = Thread(target=queryThread)
    qt.start()

    sendToAll("Query started!")
    print("Query started!")
    sendToAll("Query sucessfully restarted!")


def restartDiagnostic():
    global monitor
    global qStat

    global dt

    monitor = False
    qStat = False

    sendToAll("Restarting Self-Diagnose...")
    Thread.join(dt)
    sendToAll("Self-Diagnose stoped!")
    print("Self-Diagnose stoped!")

    monitor = True
    dt = Thread(target=selfDiagnose)
    dt.start()

    sendToAll("Self-Diagnose started!")
    print("Self-Diagnose started!")
    sendToAll("Self-Diagnose sucessfully restarted!")


time.sleep(10)

global qt
qt = Thread(target=queryThread)
global dt
dt = Thread(target=selfDiagnose)

#----------------------------start
loadCurrData()

client.run("xxxxxxxxxxxxxxxxxxxxxxxx.xxxxxx.xxxxxxxxx-xxxxxxxxxxxxxxxxx")  # Replace token with your bots token
