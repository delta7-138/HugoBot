import discord
import os
import random
import requests
import datetime as dt
from math import *
from firebase import firebase
import datetime
import pytz

import json
from discord.ext import commands
from PIL import Image
from listofnames import first_names,last_names
from io import BytesIO
import urllib.parse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

TOKEN = os.getenv('DISCORD_TOKEN')
LAST_FM_TOKEN = os.getenv('LAST_FM_TOKEN')
FIREBASE_URL = os.getenv('FIREBASE_URL')

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = 'h.' , intents = intents)
cogs = ['cogs.color' , 'cogs.codeforces' , 'cogs.randomfunc' , 'cogs.mars' , 'cogs.lastfm' , 'cogs.user' , 'cogs.quotes' , 'cogs.teleport' , 'cogs.covid' , 'cogs.shoegaze']

for cog in cogs:
    client.load_extension(cog)
    
client.remove_command('help')
modes = [100 , 200 , 127 , 265 , 246 , 110 , 1 , 34 , 124 , 245]
firebaseObj = firebase.FirebaseApplication(FIREBASE_URL)
tmpdata = firebaseObj.get('/lastfm' , None)
data = dict()
thumb = 'https://promomsclub.com/wp-content/uploads/2019/02/help-153094_1280.png'
for key,value in tmpdata.items(): 
     for subKey, subVal in value.items():
         data[subKey] = subVal

async def add_time(obj1 , obj2):
    h1 = obj1.hour;
    h2 = obj2.hour;

    m1 = obj1.minute;
    m2 = obj2.minute;

    s1 = obj1.second;
    s2 = obj2.second;

    carry_s = int((s1 + s2)/60)
    sum_s = int((s1+s2)%60)

    carry_m = int((m1 + m2 + carry_s)/60)
    sum_m = int((m1 + m2 + carry_s)%60)

    sum_h = int((h1 + h2 + carry_m))
    finaltime = "{sum_h}:{sum_m}:{sum_s}".format(sum_h = sum_h , sum_m = sum_m , sum_s = sum_s)
    finaltimeobj = datetime.datetime.strptime(finaltime , "%H:%M:%S")
    return finaltimeobj

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="my life"))
    print('We have logged in as {0.user}'.format(client))


#help commands
@client.command()
async def help(ctx):
    embed = discord.Embed(title = 'Hugo Help' , color=0x00ffea)
    embed.add_field(name = "Color commands help" , value = "h.colorhelp or h.ch" , inline = True)
    embed.add_field(name = "Command to generate random name" , value = "h.randomname ``number_of_names``" , inline = True)
    embed.add_field(name = "Command to get random number" , value = "h.randomnum or h.nrand ``lowerbound`` ``upperbound``" , inline = True)
    embed.add_field(name = "Astronomy commands help" , value = "h.astrohelp or h.ah"  , inline = False)
    #embed.add_field(name = "Command to get shoegaze avatar" , value = "h.shoegaze or h.sg" , inline = True)
    #embed.add_field(name = "Command to get shoegaze filter on an image" , value = "h.shoegazeimage or h.sgi ``url`` Add **-d** tag to get distorted version of the same" , inline = True)
    #embed.add_field(name = "Command to get a **Distorted** shoegaze filter on avatar" , value = "h.shoegazedistort or h.sgd" , inline = True)
    embed.add_field(name = "To get Last fm help" , value = "h.fmhelp" , inline = False)
    embed.add_field(name = "To get advice" , value = "h.adv" , inline = True)
    embed.add_field(name = "To get anime quote" , value = "h.aniq" , inline = True)
    embed.add_field(name = "To get Teleport City Summary" , value = "h.standardofliving <city name> aliases = h.sol" , inline = False)
    embed.add_field(name = "Help for COVID info commands" , value = "h.cvhelp" , inline = False)
    embed.set_thumbnail(url = thumb)
    embed.set_footer(text = "requested by a busta")
    await ctx.send(embed = embed)


@client.command(aliases = ['cvh'])
async def cvhelp(ctx):
    member = ctx.message.author
    name = member.name
    if(member.nick!=None):
        name = member.nick
    embed = discord.Embed(title = "Hugo COVID commands help")
    embed.add_field(name = "Command for deaths, recoveries and confirmed cases overall" , value = "h.cvw -d | -r | -c" , inline = False) 
    embed.add_field(name = "Command for deaths,recoveries and confirmed cases by country" , value = "h.cvc <country> -d | -r | -c" , inline = False)
    embed.set_footer(text = 'requsted by ' + str(name))
    embed.set_thumbnail(url = 'https://www.statnews.com/wp-content/uploads/2020/02/Coronavirus-CDC-645x645.jpg')
    await ctx.send(embed = embed)


@client.command()
async def urmom(ctx , member : discord.Member):
    res = requests.get('https://api.yomomma.info/')
    content = json.loads(res.text)
    joke = content["joke"]
    mention = member.mention
    await ctx.send(mention + " " + joke)

@urmom.error
async def urmomiserror(ctx , err):
    if isinstance(err , commands.MissingRequiredArgument):
        res = requests.get('https://api.yomomma.info/')
        content = json.loads(res.text)
        joke = content["joke"]
        mention = ctx.message.author.mention
        await ctx.send(mention + " " + joke)


@client.command(aliases = ['tpdne' , 'ne'])
async def thispersondoesnotexist(ctx):
    im = Image.open(requests.get('https://thispersondoesnotexist.com/image', stream = True).raw)
    buffer = BytesIO()
    im.save(buffer , "png")
    fil = discord.File(filename = "ne.png" , fp = buffer)
    buffer.seek(0)
    await ctx.send(file = fil)

@client.command(aliases = ['stz'])
async def settimezone(ctx , *args):
    tz = args[0]
    tmp = {str(ctx.message.author.id) : {"timezone" : tz , "logs" : ["0"]}}
    result = firebaseObj.post('/study' , tmp)
    print(result)
    await ctx.message.add_reaction("✅")
    await ctx.reply("Successfully added" , mention_author = True)

@client.command(aliases = ['astl' , 'astlog'])
async def addstudylog(ctx , *args):
    studydata = firebaseObj.get('/study' , None)
    studylogs = list(studydata.values())
    author_id = str(ctx.message.author.id)
    index = 0
    for i in range(len(studylogs)):
        tmp = studylogs[i]
        for key,value in tmp.items():
            if(key==author_id):
                index = i
    
    studydata_id = list(studydata.keys())[index]
    tz = studylogs[index][author_id]["timezone"]
    logs = studylogs[index][author_id]["logs"]
    now_time_utc = datetime.datetime.now(pytz.timezone("UTC"))
    actual_now = now_time_utc.astimezone(pytz.timezone(tz))
    start = args[0]
    end = args[1]
    obj1 = datetime.datetime.strptime(start , "%H%M")
    obj2 = datetime.datetime.strptime(end , "%H%M")
    if(obj2<obj1):
        tmp = start
        start = end
        end = tmp
        tmp = obj1 
        obj1 = obj2
        obj2 = tmp

    diff_time = str(obj2 - obj1)
    user = ctx.message.author
    nick = user.name
    if(user.nick!=None):
        nick = user.nick
    embed = discord.Embed(title = "Study Log for " + actual_now.strftime('%d-%m-%Y') , color = 0x573ed6)
    embed.add_field(name = "Start" , value = start , inline = True)
    embed.add_field(name = "End" , value = end , inline = True)
    embed.add_field(name = "Time Spent" , value = diff_time , inline = False)
    embed.set_thumbnail(url = "https://cdn.corporatefinanceinstitute.com/assets/10-Poor-Study-Habits-Opener.jpeg")
    embed.set_footer(text = "requested by {}".format(nick))
    log = {"str" : start , "end" : end , "diff" : diff_time , "date" : actual_now.strftime('%d-%m-%Y')}
    logs.append(log)
    res = firebaseObj.put('/study/' + studydata_id + '/' + author_id , "logs" , logs)
    await ctx.message.add_reaction("✅")
    await ctx.reply(embed = embed , mention_author = True)

@client.command(aliases = ['caltotdate' , 'caldate' , 'cltd'])
async def calculatetotaltimebydate(ctx , *args):
    date = args[0]  
    studydata = firebaseObj.get('/study' , None)
    studylogs = list(studydata.values())
    author_id = str(ctx.message.author.id)
    index = 0
    for i in range(len(studylogs)):
        tmp = studylogs[i]
        for key,value in tmp.items():
            if(key==author_id):
                index = i

    logs = studylogs[index][author_id]["logs"]
    timeobj = datetime.datetime.strptime("0:00:00" , "%H:%M:%S")
    for i in logs[1:]:
        if(i["date"]==date):
            tmp = datetime.datetime.strptime(i["diff"] , "%H:%M:%S")
            timeobj = await add_time(timeobj , tmp)
    await ctx.message.add_reaction("✅")
    await ctx.reply("You studied for time equal to **" + str(timeobj.time()) + "** on " + date , mention_author = True)

@client.command(aliases = ['deletelog'  'dellog' , 'dstl'])
async def deletestudylog(ctx , *args):
    message_id = args[0]
    msg = await ctx.fetch_message(message_id)
    if(msg.author!=client.user):
        await ctx.send("invalid message :rage:")
    else:
        embeds = msg.embeds
        res = embeds[0].to_dict()
        title = str(res["title"])
        author = res["fields"][0]["value"]
        if(title.startswith("Study Log for") and str(author)==str(ctx.message.author)):
            await msg.delete()
        
@client.command(aliases = ['inv'])
async def invite(ctx):
    member = ctx.message.author
    name = member.name
    if(member.nick!=None):
        name = member.nick
    embed = discord.Embed(title = "Invite to HugoBot" , color = 0xff00ea , url = 'https://discord.com/api/oauth2/authorize?client_id=785077511758675988&permissions=0&scope=bot')
    embed.set_thumbnail(url = 'https://images-ext-1.discordapp.net/external/KP2KA04tKe-XdJlC9tEKDmbUml0irWvC60-3dHNoDsA/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/785077511758675988/d5d96bcb287f37c6351c5378870fcce2.webp?width=595&height=595')
    embed.set_footer(text = 'requested by ' + name)
    await ctx.send(embed = embed)

@client.command()
async def count(ctx):
    serverCount = len(list(client.guilds))
    await ctx.send('I am lurking around in ' + str(serverCount) + ' servers')

@client.command()
async def contrib(ctx):
    embed = discord.Embed(title = "HugoBot Github Repository" , url = "https://github.com/delta7-138/HugoBot.git" , description = "_Github repo containing the code to this project. Feel free to contribute._" , color = 0xff00ea)
    embed.set_footer(text = "requested by " + ctx.message.author.name)
    embed.set_thumbnail(url = "https://avatars.githubusercontent.com/u/53052253?v=4")
    await ctx.reply(embed = embed , mention_author = True)

client.run(TOKEN)
