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

TOKEN = os.environ['DISCORD_TOKEN']
LAST_FM_TOKEN = os.getenv('LAST_FM_TOKEN')
FIREBASE_URL = os.getenv('FIREBASE_URL')

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = 'h.' , intents = intents)
cogs = ['cogs.color' , 'cogs.codeforces' , 'cogs.randomfunc' , 'cog.mars']

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

async def distortImage(im):
    im = im.convert('RGB')
    pixels = im.load()
    for i in range(im.size[0]):
        for j in range(im.size[1]):
            k = (random.randint(0 , int(floor(im.size[0]/66))))
            l = (random.randint(0 , int(floor(im.size[1]/66))))
            k = k**2
            if(i+k<im.size[0] and j+l<im.size[1]):
                tmp = list(pixels[i+k , j+l])
                im.putpixel((i , j) , tuple(tmp))    
    return im

async def randomGen(num):
    val = (random.randint(1 , num))**2
    tmpvar = val
    ans = 0
    for i in range(2):
        ans = ans * 10 + tmpvar%10
        tmpvar = tmpvar/10

    return int(ans)
    
async def randomizeImage(im):
    im = im.convert('RGB')
    pixels = im.load()
    xmax = im.size[0]
    ymid = im.size[1]/2

    
    for i in range(im.size[0]):
        for j in range(im.size[1]):
            tmp = list(pixels[i , j]) 
            k = random.randint(0 , 2)
            l = random.randint(0 , 2)
            random.seed(modes[random.randint(0 , 9)])
            tmp[k] = await randomGen(random.randint(156 , 255))
            tmp[l] = await randomGen(random.randint(1 , 255))
            im.putpixel((i , j) , tuple(tmp))

    return im

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

@client.command(aliases = ['ah'])
async def astrohelp(ctx):
    embed = discord.Embed(title = 'Hugo Astronomy Help' , color = 0x00ffea)
    embed.add_field(name = "Astronomy picture of the day" , value = "h.apod" , inline = False)
    embed.add_field(name = "Mars Rover images" , value = "h.mars <sol number> <camera_type> <rover name as in c for curiosity , o for opportunity and s for spirit>" , inline = False)
    embed.set_footer(text = "requested by a busta")
    embed.set_thumbnail(url = 'https://i.insider.com/502292d36bb3f76241000009?width=1100&format=jpeg&auto=webp')
    await ctx.send(embed = embed)

@client.command(aliases = ['fmh'])
async def fmhelp(ctx):
    embed = discord.Embed(title = 'Hugo FM Help' , color=0x00ffea)
    embed.add_field(name = "Command to set fm account" , value = "h.fmset" , inline = False)
    embed.add_field(name = "Command to see current track" , value = "h.fm" , inline = False)
    embed.add_field(name = "Command to see who knows an artist" , value = "h.fmw `artist` or h.fmw aliases = h.fmwhoknows" , inline = False)
    embed.add_field(name = "Command to see who knows an album" , value = "h.fmwka `<artist> - <albumname>`(aliases = h.fmwa , h.fmwhoknowsalbum) " , inline = False)
    embed.add_field(name = "Command to see who knows a track" , value = "h.fmwkt `<artist> - <trackname>` (aliases = h.fmwt , h.fmwhoknowstrack)" , inline = False)
    embed.set_thumbnail(url = 'https://lh3.googleusercontent.com/proxy/BzW7U-yNC8RjUf2SWOEzDcRxlCjXZBx7RGjiGu7QdDm7g4aKHC3tE815KW-cyut1yBF-qOKhR0r5i919Fa2nPnYqITbp-bg4Rqs_dxE8b976G3bi9SMUIC88Qkw8RIOphMD7rrIsggvBzwtcZdwTSvqVVM-vzhdeQtc')
    embed.set_footer(text = 'requested by a busta')
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
async def apod(ctx):
    try: 
        gres = requests.get('https://api.nasa.gov/planetary/apod?api_key=' + API_TOKEN)
        gdata = gres.json()
        embed = discord.Embed(title = 'Astronomy Picture Of the Day' , color = 0x0000ff)
        embed.add_field(name = 'Date' , value = gdata['date'])
        # embed.add_field(name = gdata['title'] , value = gdata['explanation'])
        embed.set_image(url = gdata['hdurl'])
        await ctx.send(embed = embed)
    except: 
        await ctx.send('Error in sending picture :pensive:')


@client.command(aliases = ['sg'])
#@commands.cooldown(1, 30, commands.BucketType.user)
async def shoegaze(ctx , member :  discord.Member): 
    ext = 'png'
    im = Image.open(requests.get(member.avatar_url , stream = True).raw)
    if(im.format=='GIF'):
        im.seek(0)
    im = randomizeImage(im)   
    buffer = BytesIO()
    im.save(buffer , "png")
    buffer.seek(0)
    fil = discord.File(filename = 'avatar.' + ext , fp = buffer)
    embed = discord.Embed(title = "Here is a shoegaze version of the avatar")
    embed.set_image(url = 'attachment://avatar.' + ext)  
    await ctx.send(file = fil , embed = embed) 
             
@shoegaze.error
async def shoegaze_err(ctx , err):
     if isinstance(err , commands.MissingRequiredArgument):
        im = Image.open(requests.get(ctx.message.author.avatar_url, stream = True).raw)
        if(im.format=='GIF'):
            im.seek(0)
        im = randomizeImage(im)  
        buffer = BytesIO()  
        im.save(buffer , "png")
        buffer.seek(0)
        fil = discord.File(filename = 'avatar.png' , fp = buffer)
        embed = discord.Embed(title = "Here is a shoegaze version of the avatar")
        embed.set_image(url = 'attachment://avatar.png')  
        await ctx.send(file = fil , embed = embed) 
        

     if isinstance(err , commands.BadArgument):
         await ctx.send('Dude atleast tag a valid member :unamused:')

@client.command(aliases = ['sgd'])
#@commands.cooldown(1, 30, commands.BucketType.user)
async def shoegazedistort(ctx , member :  discord.Member): 
    im = Image.open(requests.get(member.avatar_url, stream = True).raw)
    if(im.format=='GIF'):
        im.seek(0)
    im = randomizeImage(im)   
    im = distortImage(im)
    ext = 'png' 
    buffer = BytesIO()
    im.save(buffer , "png")
    buffer.seek(0)
    fil = discord.File(filename = 'avatar.' + ext , fp = buffer)
    embed = discord.Embed(title = "Here is a shoegaze version of the avatar with distortion")
    embed.set_image(url = 'attachment://avatar.' + ext)  
    await ctx.send(file = fil , embed = embed) 
             
@shoegazedistort.error
async def shoegazed_err(ctx , err):
     if isinstance(err , commands.MissingRequiredArgument):
        im = Image.open(requests.get(ctx.message.author.avatar_url, stream = True).raw)
        if(im.format=='GIF'):
            im.seek(0)
        im = randomizeImage(im)    
        im = distortImage(im)
        buffer = BytesIO()
        im.save(buffer , "png")
        fil = discord.File(filename = 'avatar.png' , fp = buffer)
        buffer.seek(0)
        embed = discord.Embed(title = "Here is a shoegaze version of the avatar with distortion")
        embed.set_image(url = 'attachment://avatar.png')  
        await ctx.send(file = fil , embed = embed) 

     if isinstance(err , commands.BadArgument):
         await ctx.send('Dude atleast tag a valid member :unamused:')

@client.command(aliases = ['sgi'])
#@commands.cooldown(1, 30, commands.BucketType.user)
async def shoegazeimage(ctx , *args):
    try: 
        im = Image.open(requests.get(args[0], stream = True).raw)
        if(im.format=='GIF'):
            im.seek(0)
        im = await randomizeImage(im)
        addage = ""
        if(len(args)==2 and args[1]=='-d'):
            im = await distortImage(im)
            addage = " with distortion"
        buffer = BytesIO()
        im.save(buffer , "png")
        buffer.seek(0)
        fil = discord.File(filename = 'avatar.png' , fp  = buffer)
        embed = discord.Embed(title = "Here is a shoegaze version of the image" + addage)
        embed.set_image(url = 'attachment://avatar.png')  
        await ctx.send(file = fil , embed = embed) 
    except:
        await ctx.send("invalid url :pensive:")

#FM COMMANDS


@client.command()
async def fmset(ctx , *args):
    userid = str(ctx.message.author.id)
    fmuname = args[0]


    for key, value in data.items(): 
        if(key==userid or value==fmuname):
            await ctx.send("User is already there")
            return 0
        else:
            res = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user=' + fmuname + '&api_key=' + LAST_FM_TOKEN + '&format=json')
            content = json.loads(res.text)
            if("message" in content and content["message"]=="User not found"):
                await ctx.send("User not found :(")
                return 0

    data[userid] = fmuname
    tmp = {userid : fmuname}
    firebaseObj.post('/lastfm' , tmp)
    await ctx.send("User successfully added :vampire:")

@client.command()
async def fm(ctx):
    userid = str(ctx.message.author.id)
    if(userid not in data):
        await ctx.send("Please set your last fm account first")
    else:
        fmuname = data[userid]
        res = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + fmuname + '&api_key=' + LAST_FM_TOKEN + '&format=json') 
        content = json.loads(res.text)
        track = content["recenttracks"]["track"][0]
        trackartist = track["artist"]["#text"]
        trackalbum = track["album"]["#text"]  
        trackname = track["name"] 
        trackimg = track["image"][2]["#text"]
        print(trackname + " " + trackalbum + " " + trackartist)
        embed = discord.Embed(title = 'Now Playing/Recent Track' , color=0x00ffea)
        embed.add_field(name = "Track Name" , value = trackname  , inline = False)
        embed.add_field(name = "Artist Name" , value = trackartist , inline = False)
        embed.add_field(name = "Album Name", value = trackalbum if(trackalbum!=None) else "-" , inline = False)
        embed.set_image(url = trackimg)
        await ctx.send(embed = embed)


@client.command(aliases = ['fmwhoknows' , 'fmwk'])
async def fmw(ctx , *, args):
    artist = args
    leaderBoard = dict()
    image = ""
    async for member in ctx.guild.fetch_members(limit = None):
        memberID = str(member.id)
        if(memberID in data):
            uname = data[memberID]
            nick = member.name
            unparsedURL = {'artist' : artist , 'username' : uname , 'api_key' : LAST_FM_TOKEN , 'format' : 'json'}
            parsedURL = urllib.parse.urlencode(unparsedURL)
            res2 = requests.get('http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&' + parsedURL)
            content = json.loads(res2.text)
            playCount = content['artist']['stats']['userplaycount']
            image = content['artist']['image'][1]['#text']
            if(playCount!='0'):
                leaderBoard[nick] = int(playCount)
        
    leaderBoard =  sorted(leaderBoard.items(), key=lambda item: item[1] , reverse= True)
    labels = []
    values = []
    for x,y in leaderBoard:
        labels.append(x)
        values.append(y)

    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/4, values, width, label='Men')
    ax.set_ylabel('Play Count for ' + artist)
    ax.set_title('Who knows ' + artist)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.bar_label(rects1, padding=3)
    fig.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer , format = "png")
    buffer.seek(0)
    plt.close()
    fil = discord.File(filename = 'whoknows.png' , fp = buffer)
    # embed = discord.Embed(title = 'WHO KNOWS **' + artist + '**' , color=0x00ffea)
    # for key,value in leaderBoard:
    #     embed.add_field(name = key, value = value , inline = False)
    await ctx.send(file = fil)

@fmw.error
async def fmwerror(ctx , err):
    if isinstance(err , commands.MissingRequiredArgument):
        artist = ""
        userid = str(ctx.message.author.id)
        if(userid not in data):
            await ctx.send("Please set your last fm account first")
            return ;
        else:
            fmuname = data[userid]
            res = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + fmuname + '&api_key=' + LAST_FM_TOKEN + '&format=json') 
            content = json.loads(res.text)
            track = content["recenttracks"]["track"][0]
            artist = track["artist"]["#text"]

        leaderBoard = dict()
        image = ""
        async for member in ctx.guild.fetch_members(limit = None):
            memberID = str(member.id)
            if(memberID in data):
                uname = data[memberID]
                nick = member.name
                unparsedURL = {'artist' : artist , 'username' : uname , 'api_key' : LAST_FM_TOKEN , 'format' : 'json'}
                parsedURL = urllib.parse.urlencode(unparsedURL)
                res2 = requests.get('http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&' + parsedURL)
                content = json.loads(res2.text)
                playCount = content['artist']['stats']['userplaycount']
                image = content['artist']['image'][1]['#text']
                if(playCount!='0'):
                    leaderBoard[nick] = int(playCount)
        
        leaderBoard =  sorted(leaderBoard.items(), key=lambda item: item[1] , reverse= True)
        labels = []
        values = []
        for x,y in leaderBoard:
            labels.append(x)
            values.append(y)

        x = np.arange(len(labels))
        width = 0.35
        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width/4, values, width, label='Men')
        ax.set_ylabel('Play Count for ' + artist)
        ax.set_title('Who knows ' + artist)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.bar_label(rects1, padding=3)
        fig.tight_layout()
        buffer = BytesIO()
        plt.savefig(buffer , format = "png")
        buffer.seek(0)
        plt.close()
        fil = discord.File(filename = 'whoknows.png' , fp = buffer)
        # embed = discord.Embed(title = 'WHO KNOWS **' + artist + '**' , color=0x00ffea)
        # for key,value in leaderBoard:
        #     embed.add_field(name = key, value = value , inline = False)
        await ctx.send(file = fil)

@client.command(aliases = ['fmwka' , 'fmwa'])
async def fmwhoknowsalbum(ctx , * , args):
    artistAlbum = args.split("-")
    artistAlbum = [i.strip() for i in artistAlbum]
    album = artistAlbum[1]
    artist = artistAlbum[0]
    leaderBoard = dict()
    image = ""
    async for member in ctx.guild.fetch_members(limit = None):
        memberID = str(member.id)
        if(memberID in data):
            uname = data[memberID]
            nick = member.name
            unparsedURL = {'artist' : artist , 'album' : album , 'username' : uname , 'api_key' : LAST_FM_TOKEN , 'format' : 'json'}
            parsedURL = urllib.parse.urlencode(unparsedURL)
            res2 = requests.get('http://ws.audioscrobbler.com/2.0/?method=album.getinfo&' + parsedURL)
            content = json.loads(res2.text)
            playCount = content['album']['userplaycount']
            image = content['album']['image'][2]['#text']
            if(playCount!='0'):
                leaderBoard[nick] = int(playCount)
        
    leaderBoard =  sorted(leaderBoard.items(), key=lambda item: item[1] , reverse= True)
    embed = discord.Embed(title = 'WHO KNOWS **' + artist + '** - ' + '**' + album + '**' , color=0x00ffea)
    ctr = 0
    for key,value in leaderBoard:
        ctr+=1
        embed.add_field(name = str(ctr) + '. ' + key + '  -  ' + '**' + str(value) + '** plays' , value = '\u200b' , inline = False)
    embed.set_image(url = image)
    await ctx.send(embed = embed) 

@fmwhoknowsalbum.error
async def fmwhoknowsalbumerr(ctx , err):
    if isinstance(err , commands.MissingRequiredArgument):
        artist = ""
        album = ""
        userid = str(ctx.message.author.id)
        if(userid not in data):
            await ctx.send("Please set your last fm account first")
            return ;
        else:
            fmuname = data[userid]
            res = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + fmuname + '&api_key=' + LAST_FM_TOKEN + '&format=json') 
            content = json.loads(res.text)
            track = content["recenttracks"]["track"][0]
            artist = track["artist"]["#text"]
            album = track["album"]["#text"]
    
    leaderBoard = dict()
    image = ""
    async for member in ctx.guild.fetch_members(limit = None):
        memberID = str(member.id)
        if(memberID in data):
            uname = data[memberID]
            nick = member.name
            unparsedURL = {'artist' : artist , 'album' : album , 'username' : uname , 'api_key' : LAST_FM_TOKEN , 'format' : 'json'}
            parsedURL = urllib.parse.urlencode(unparsedURL)
            res2 = requests.get('http://ws.audioscrobbler.com/2.0/?method=album.getinfo&' + parsedURL)
            content = json.loads(res2.text)
            playCount = content['album']['userplaycount']
            image = content['album']['image'][2]['#text']
            if(playCount!='0'):
                leaderBoard[nick] = int(playCount)
        
    leaderBoard =  sorted(leaderBoard.items(), key=lambda item: item[1] , reverse= True)
    embed = discord.Embed(title = 'WHO KNOWS **' + artist + '** - ' + '**' + album + '**' , color=0x00ffea)
    ctr = 0
    for key,value in leaderBoard:
        ctr+=1
        embed.add_field(name = str(ctr) + '. ' + key + '  -  ' + '**' + str(value) + '** plays' , value = '\u200b' , inline = False)
    embed.set_image(url = image)
    await ctx.send(embed = embed) 

@client.command(aliases = ['fmwt' , 'fmwkt'])
async def fmwhoknowstrack(ctx , * , args):
    artistTrack = args.split("-")
    artistTrack = [i.strip() for i in artistTrack]
    track = artistTrack[1]
    artist = artistTrack[0]
    leaderBoard = dict()
    image = ""
    async for member in ctx.guild.fetch_members(limit = None):
        memberID = str(member.id)
        if(memberID in data):
            uname = data[memberID]
            nick = member.name
            unparsedURL = {'artist' : artist , 'track' : track, 'username' : uname , 'api_key' : LAST_FM_TOKEN , 'format' : 'json'}
            parsedURL = urllib.parse.urlencode(unparsedURL)
            res2 = requests.get('http://ws.audioscrobbler.com/2.0/?method=track.getinfo&' + parsedURL)
            content = json.loads(res2.text)
            playCount = content['track']['userplaycount']
            image = content['track']["album"]['image'][2]['#text']
            if(playCount!='0'):
                leaderBoard[nick] = int(playCount)
        
    leaderBoard =  sorted(leaderBoard.items(), key=lambda item: item[1] , reverse= True)
    embed = discord.Embed(title = 'WHO KNOWS **' + artist + '** - ' + '**' + track + '**' , color=0x00ffea)
    ctr = 0
    for key,value in leaderBoard:
        ctr+=1
        embed.add_field(name = str(ctr) + '. ' + key + '  -  ' + '**' + str(value) + '** plays' , value = '\u200b' , inline = False)
    embed.set_image(url = image)
    await ctx.send(embed = embed) 

@fmwhoknowstrack.error
async def fmwhoknowstrackerr(ctx , err):
    if isinstance(err , commands.MissingRequiredArgument):
        artist = ""
        track= ""
        userid = str(ctx.message.author.id)
        if(userid not in data):
            await ctx.send("Please set your last fm account first")
            return ;
        else:
            fmuname = data[userid]
            res = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + fmuname + '&api_key=' + LAST_FM_TOKEN + '&format=json') 
            content = json.loads(res.text)
            trackitem = content["recenttracks"]["track"][0]
            artist = trackitem["artist"]["#text"]
            track = trackitem["name"]
    
    leaderBoard = dict()
    image = ""
    async for member in ctx.guild.fetch_members(limit = None):
        memberID = str(member.id)
        if(memberID in data):
            uname = data[memberID]
            nick = member.name
            unparsedURL = {'artist' : artist , 'track' : track , 'username' : uname , 'api_key' : LAST_FM_TOKEN , 'format' : 'json'}
            parsedURL = urllib.parse.urlencode(unparsedURL)
            res2 = requests.get('http://ws.audioscrobbler.com/2.0/?method=track.getinfo&' + parsedURL)
            content = json.loads(res2.text)
            playCount = content['track']['userplaycount']
            image = content['track']['album']['image'][2]['#text']
            if(playCount!='0'):
                leaderBoard[nick] = int(playCount)
        
    leaderBoard =  sorted(leaderBoard.items(), key=lambda item: item[1] , reverse= True)
    embed = discord.Embed(title = 'WHO KNOWS **' + artist + '** - ' + '**' + track + '**' , color=0x00ffea)
    ctr = 0
    for key,value in leaderBoard:
        ctr+=1
        embed.add_field(name = str(ctr) + '. ' + key + '  -  ' + '**' + str(value) + '** plays' , value = '\u200b' , inline = False)
    embed.set_image(url = image)
    await ctx.send(embed = embed) 

@client.command(aliases = ['adv'])
async def advice(ctx):
    member = ctx.message.author
    uname = member.name
    if(member.nick!=None):
        uname = member.nick
    res = requests.get('https://api.adviceslip.com/advice')
    content = json.loads(res.text)
    adviceMsg = content["slip"]["advice"]
    embed = discord.Embed(title = "Advice for stupid people" , description = adviceMsg , color = 0x00ffea)
    embed.set_thumbnail(url = 'https://i0.wp.com/www.brainpickings.org/wp-content/uploads/2014/10/nietzsche1.jpg?w=680&ssl=1')
    embed.set_footer(text = 'requested by ' + uname)
    await ctx.send(embed = embed)

@client.command(aliases = ['aniq'])
async def animequote(ctx):
    res = requests.get('https://animechan.vercel.app/api/random')
    content =json.loads(res.text)
    quote = content["quote"]
    character = content["character"]
    anime = content["anime"]
    embed = discord.Embed(title = "Anime Quote" , description = '*' + quote + '*'  , color = 0x00ffea)
    embed.set_footer(text = 'by - ' + character + '\n from - ' + anime)
    embed.set_thumbnail(url = 'https://i.pinimg.com/474x/89/08/61/8908616ffb91db2dbd1b640a374a1ee2.jpg')
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

@client.command(aliases = ['sol'])
async def standardofliving(ctx , * , args):
    queryCity = urllib.parse.urlencode({'search' : args})
    res1 = requests.get('https://api.teleport.org/api/cities/?' + queryCity)
    content1 = json.loads(res1.text)
    nextUrl = content1['_embedded']['city:search-results'][0]['_links']['city:item']['href']

    if(nextUrl):
        try:
            res2 = requests.get(nextUrl)
            content2 = json.loads(res2.text)
            nextnextUrl = content2['_links']['city:urban_area']['href'] + 'scores'
            res3 = requests.get(nextnextUrl)
            content3 = json.loads(res3.text)
            city_score = content3['teleport_city_score']
            embed = discord.Embed(title = 'Teleport City Summary for ' + args.upper(), color = 0x00ffea)
            embed.add_field(name = 'Teleport City Score' , value = str(city_score) , inline = False)
            categories = content3['categories']
            flip = True
            ctr = 1
            for i in content3['categories']:
                if(ctr%3==0):
                    flip = False
                else:
                    flip = True

                ctr+=1
                embed.add_field(name = i['name'] , value = i['score_out_of_10'] , inline = flip)

            embed.set_footer(text = 'data provided by Teleport api')
            embed.set_thumbnail(url = 'https://www.plantemoran.com/-/media/images/insights-images/2018/04/thinking-about-becoming-a-smart-city.jpg?h=704&w=1100&la=en&hash=0F4F54BBECD3E501765A064202A24F8851D74E04')
            await ctx.send(embed = embed)
        except: 
            await ctx.send("City not available :pensive: :v:")
    else:
        await ctx.send('invalid input :pensive:')

@client.command(aliases = ['cvw' , 'covidwld' , 'covw' , 'covidw'])
async def covidworld(ctx , *args):
    res = requests.get('https://covid-api.mmediagroup.fr/v1/cases')
    content = json.loads(res.text)
    param = ""
    if(len(args)<1):
        await ctx.send("Missin Arguments :nerd:")
        return ;

    if(args[0]=='-d'):
        param = "deaths"
    elif(args[0]=='-r'):
        param = "recovered"
    elif(args[0]=='-c'):
        param = "confirmed"
    else:
        await ctx.send("Send appropriate argument :rage:")
        return ;
    
    resDict = dict()
    for key,value in content.items():
        deaths = int(value["All"][param])
        resDict[key] = deaths
    
    resDict = sorted(resDict.items(), key=lambda item: item[1] , reverse= True)
    countries = list()
    numbers = list()
    for i in range(10):
        countries.append(resDict[i][0])
        numbers.append(resDict[i][1])
    
    fig, ax = plt.subplots(figsize =(16, 9))
    ax.barh(countries, numbers)
    ax.set_title("COVID " + param.upper()) 

    for s in ['top', 'bottom', 'left', 'right']:
        ax.spines[s].set_visible(False)
    
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

    ax.xaxis.set_tick_params(pad = 5)
    ax.yaxis.set_tick_params(pad = 10)

    for i in ax.patches:
        ax.text(i.get_width()+0.2, i.get_y()+0.5, str(round((i.get_width()), 2)),fontsize = 20, fontweight ='bold',color ='grey')
    buffer = BytesIO()
    plt.savefig(buffer , format = "png")
    buffer.seek(0)
    plt.close()
    fil = discord.File(filename = 'cvwd.png' , fp = buffer)
    await ctx.send(file = fil)

@client.command(aliases = ['cvc'])
async def covidcountry(ctx , *args):
    res = requests.get('https://covid-api.mmediagroup.fr/v1/cases')
    content = json.loads(res.text)
    country = ""
    for i in range(len(args)-1):
        country = country + " " + args[i]
    
    print(country)
    country = country.strip()
    param = ""
    try:
        countrydata = content[country]
        if(len(args)<2):
            await ctx.send("Missin Arguments :nerd:")
            return ;

        if(args[-1]=='-d'):
            param = "deaths"
        elif(args[-1]=='-r'):
            param = "recovered"
        elif(args[-1]=='-c'):
            param = "confirmed"
        else:
            await ctx.send("Send appropriate argument :rage:")
            return ;
        
        resDict = dict()
        for key,value in countrydata.items():
            tmp = int(value[param])
            resDict[key] = tmp
        
        resDict = sorted(resDict.items(), key=lambda item: item[1] , reverse= True)
        states = list()
        numbers = list()
        maxrange = 10 if(len(resDict)>=10) else len(resDict) 

        for i in range(maxrange):
            states.append(resDict[i][0])
            numbers.append(resDict[i][1])
        
        fig, ax = plt.subplots(figsize =(16, 9))
        ax.barh(states, numbers)
        ax.set_title("COVID " + param.upper()) 

        for s in ['top', 'bottom', 'left', 'right']:
            ax.spines[s].set_visible(False)
        
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')

        ax.xaxis.set_tick_params(pad = 5)
        ax.yaxis.set_tick_params(pad = 10)

        for i in ax.patches:
            ax.text(i.get_width()+0.2, i.get_y()+0.5, str(round((i.get_width()), 2)),fontsize = 20, fontweight ='bold',color ='grey')
        buffer = BytesIO()
        plt.savefig(buffer , format = "png")
        buffer.seek(0)
        plt.close()
        fil = discord.File(filename = 'cvc.png' , fp = buffer)
        embed = discord.Embed(title = "Summary for " + country.upper() , color = 0xff0000)
        embed.set_footer(text = 'data provided by https://covid-api.mmediagroup.fr/v1/')
        await ctx.send(file = fil , embed = embed)
    except:
        await ctx.send("Invalid Country name :rage:")

@client.command(aliases = ['tpdne' , 'ne'])
async def thispersondoesnotexist(ctx):
    im = Image.open(requests.get('https://thispersondoesnotexist.com/image', stream = True).raw)
    buffer = BytesIO()
    im.save(buffer , "png")
    fil = discord.File(filename = "ne.png" , fp = buffer)
    buffer.seek(0)
    await ctx.send(file = fil)

@client.command(aliases = ['ronq'])
async def ronswansonquote(ctx):
    urls = ['https://hips.hearstapps.com/digitalspyuk.cdnds.net/17/18/1493816780-ron-swanson.jpg' , 'https://imagesvc.meredithcorp.io/v3/mm/image?url=https%3A%2F%2Fstatic.onecms.io%2Fwp-content%2Fuploads%2Fsites%2F13%2F2016%2F10%2F16%2FRon-Swanson-e1476642015275.jpg&q=85' , 'https://i.pinimg.com/originals/50/26/8f/50268f506228d83a5253f57225672c42.png']
    member = ctx.message.author
    name = member.name
    if(member.nick!=None):
        name = member.nick
    res = requests.get("https://ron-swanson-quotes.herokuapp.com/v2/quotes")
    content = json.loads(res.text)
    embed = discord.Embed(title = "Ron Swanson Quote" , description = content[0] , color = 0xff0000)
    embed.set_thumbnail(url = urls[random.randint(0 , len(urls)-1)])
    embed.set_footer(text = "requested by " + name)
    await ctx.send(embed = embed)

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

@client.command(aliases = ['av' , 'avtr'])
async def avatar(ctx , member : discord.Member):
    embed = discord.Embed(title = "Member avatar" , color = 0xff00ff)
    embed.set_image(url = member.avatar_url)
    await ctx.reply(embed = embed , mention_author = True)

@avatar.error
async def avatar_err(ctx , err):
    if isinstance(err , commands.MissingRequiredArgument):
        member = ctx.message.author
        embed = discord.Embed(title = "Member avatar" , color = 0xff00ff)
        embed.set_image(url = member.avatar_url)
        await ctx.reply(embed = embed ,mention_author = True)
        
    if isinstance(err , commands.BadArgument):
        await ctx.reply("Wrong argument" , mention_author = True)      
          
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
client.run(TOKEN)
