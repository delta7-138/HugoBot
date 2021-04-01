import discord
import os
import random
import requests
import datetime as dt
from math import *
from firebase import firebase

import json
from discord.ext import commands
from PIL import Image
from listofnames import first_names,last_names
from io import BytesIO



TOKEN = os.environ['DISCORD_TOKEN']
API_TOKEN = os.environ['API_TOKEN']
LAST_FM_TOKEN = os.getenv('LAST_FM_TOKEN')
FIREBASE_URL = os.getenv('FIREBASE_URL')
client = commands.Bot(command_prefix = 'h.')
client.remove_command('help')
modes = [100 , 200 , 127 , 265 , 246 , 110 , 1 , 34 , 124 , 245]
firebaseObj = firebase.FirebaseApplication(FIREBASE_URL)
tmpdata = firebaseObj.get('/lastfm' , None)
data = dict()

for key,value in tmpdata.items(): 
     for subKey, subVal in value.items():
         data[subKey] = subVal

def distortImage(im):
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

def randomGen(num):
    val = (random.randint(1 , num))**2
    tmpvar = val
    ans = 0
    for i in range(2):
        ans = ans * 10 + tmpvar%10
        tmpvar = tmpvar/10

    return int(ans)
    
def randomizeImage(im):
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
            tmp[k] = randomGen(random.randint(156 , 255))
            tmp[l] = randomGen(random.randint(1 , 255))
            im.putpixel((i , j) , tuple(tmp))

    return im

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.command()
async def help(ctx):
    embed = discord.Embed(title = 'Hugo Help' , color=0x00ffea)
    embed.add_field(name = "Command to greet Hugo" , value = "h.hello" , inline = False)
    embed.add_field(name = "Command to generate a random color" , value = "h.color" , inline = False)
    embed.add_field(name = "Command to generate random name" , value = "h.randomname ``number_of_names``" , inline = False)
    embed.add_field(name = "Command to get MARS rover images as per sol" , value = "h.mars ``sol_number`` ``cameratype in [fhaz , rhaz , chemcam, mast ,mahli, mardi, navcam]`` ``rover_name as in [**c** for curiosity , **s** for spirit , **o** for opportunity]``" , inline = False)
    embed.add_field(name = "Command to get Astronomy picture of the Day" , value = "h.apod" , inline = False)
    embed.add_field(name = "Command to get random number" , value = "h.randomnum or h.nrand ``lowerbound`` ``upperbound``" , inline = False)
    embed.add_field(name = "Command to get shoegaze avatar" , value = "h.shoegaze or h.sg" , inline = False)
    embed.add_field(name = "Command to get shoegaze filter on an image" , value = "h.shoegazeimage or h.sgi ``url`` Add **-d** tag to get distorted version of the same" , inline = False)
    embed.add_field(name = "Command to get a **Distorted** shoegaze filter on avatar" , value = "h.shoegazedistort or h.sgd" , inline = False)
    embed.add_field(name = "To get Last fm help" , value = "h.fmhelp" , inline = False)
    await ctx.send(embed = embed)

@client.command()
async def hello(ctx): 
    await ctx.send(f'Hello There!')

@client.command()
async def color(ctx):
    hex_number_string = '#'
    for i in range(6):
        randnum = random.randint(0 , 15)
        hexstr = str(hex(randnum)).upper()
        hexelem = hexstr[2:]
        hex_number_string = hex_number_string + hexelem
        
    hex_int = int(hex_number_string[1:] , 16)
    im = Image.new("RGB" , (100 , 100) , hex_number_string)
    buffer = BytesIO()
    im.save(buffer , "png")
    buffer.seek(0)
    file = discord.File(filename = 'randcolor.png' , fp = buffer)
    embed = discord.Embed(title = 'Random Color' , color = hex_int)
    embed.add_field(name = "Color" , value = hex_number_string)
    embed.set_image(url = 'attachment://randcolor.png')
    await ctx.send(file = file , embed = embed) 

@client.command(aliases = ['rand'])
async def randomname(ctx , *args):
    if(len(args)==1):
        num = int(args[0])
        if(num<=5 and num>0):
            final_msg = ""
            for i in range(num):
                f_ind = random.randint(0 , len(first_names)-1)
                l_ind = random.randint(0 , len(last_names)-1)
                random.shuffle(first_names)
                random.shuffle(last_names)
                name = first_names[f_ind] + " " + last_names[l_ind]
                final_msg = final_msg + name + "\n"
                    
            await ctx.send(final_msg)

        elif(num==0):
            await ctx.send("Do you really want a name or you just want to waste my time?") 
        else:
            await ctx.send("How many names do you need man! :nerd:")
    elif(len(args)==0):
        f_ind = random.randint(0 , len(first_names)-1)
        l_ind = random.randint(0 , len(last_names)-1)
        random.shuffle(first_names)
        random.shuffle(last_names)
        name = first_names[f_ind] + " " + last_names[l_ind]
        await ctx.send(name)
    else:
        await ctx.send("Send valid arguments ya :nerd:")

@client.command()
async def mars(ctx , *args):
    if(len(args)==1):
        sol = args[0]
        gres = requests.get('https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=' + sol + '&camera=fhaz&api_key=' + API_TOKEN)
        gdata = gres.json()
        ind = random.randint(0 , len(gdata['photos'])-1)
        await ctx.send(gdata['photos'][ind]['img_src'])
    else:
        try:
            reference_args = {'o' : 'opportunity' , 'c' : 'curiosity' , 's' : 'spirit'}
            sol = args[0]
            cam = args[1].lower()
            rover = reference_args[args[2].lower()]
            #print(rover)
            gres = requests.get('https://api.nasa.gov/mars-photos/api/v1/rovers/' + rover + '/photos?sol=' + sol + '&camera=' + cam + '&api_key=' + API_TOKEN)
            gdata = gres.json()
            ind = random.randint(0 , len(gdata['photos'])-1)
            await ctx.send(gdata['photos'][ind]['img_src'])
        except: 
            await ctx.send('Image not available :pensive:')

@client.command()
async def apod(ctx):
    gres = requests.get('https://api.nasa.gov/planetary/apod?api_key=' + API_TOKEN)
    gdata = gres.json()
    embed = discord.Embed(title = 'Astronomy Picture Of the Day' , color = 0x0000ff)
    embed.add_field(name = 'Date' , value = gdata['date'])
    # embed.add_field(name = gdata['title'] , value = gdata['explanation'])
    embed.set_image(url = gdata['hdurl'])
    await ctx.send(embed = embed)

@client.command(aliases = ['nrand'])
async def randomnum(ctx , *args):
    try:
        num1 = int(args[0])
        num2 = int(args[1])
        if(num1>num2):
            await ctx.send('First argument should be less than the second one')
        elif(num1==num2):
            await ctx.send('Do you really want a random number :|')
        else:
            randnum = random.randint(num1 , num2)
            await ctx.send(randnum)
    except:
        await ctx.send('Please send valid input :pleading_face:')

@client.command(aliases = ['sg'])
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
async def shoegazeimage(ctx , *args):
    #try: 
        im = Image.open(requests.get(args[0], stream = True).raw)
        if(im.format=='GIF'):
            im.seek(0)
        im = randomizeImage(im)
        addage = ""
        if(len(args)==2 and args[1]=='-d'):
            im = distortImage(im)
            addage = " with distortion"
        buffer = BytesIO()
        im.save(buffer , "png")
        buffer.seek(0)
        fil = discord.File(filename = 'avatar.png' , fp  = buffer)
        embed = discord.Embed(title = "Here is a shoegaze version of the image" + addage)
        embed.set_image(url = 'attachment://avatar.png')  
        await ctx.send(file = fil , embed = embed) 
    #except:
    #   await ctx.send("invalid url :pensive:")

#FM COMMANDS
@client.command(aliases = ['fmh'])
async def fmhelp(ctx):
    embed = Discord.embed()
    embed = discord.Embed(title = 'Hugo FM Help' , color=0x00ffea)
    embed.add_field(name = "Command to set fm account" , value = "h.fmset" , inline = False)
    embed.add_field(name = "Command to see current track" , value = "h.fm" , inline = False)
    embed.add_field(name = "Command to see who knows an artist" , value = "h.fmw `artist` or h.fmw" , inline = False)
    await ctx.send(embed = embed)

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
        embed = discord.Embed(title = 'Now Playing/Recent Track' , color=0x00ffea)
        embed.add_field(name = "Track Name" , value = trackname  , inline = False)
        embed.add_field(name = "Artist Name" , value = trackartist , inline = False)
        embed.add_field(name = "Album Name", value = trackalbum , inline = False)
        embed.set_image(url = trackimg)
        await ctx.send(embed = embed)


@client.command(aliases = ['fmwhoknows' , 'fmwk'])
async def fmw(ctx , *, args):
    artist = ""
    if(args==None):
        userid = str(ctx.message.author.id)
        if(userid not in data):
            await ctx.send("Please set your last fm account first")
            return ;
        else:
            fmuname = data[userid]
            res = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + fmuname + '&api_key=' + LAST_FM_TOKEN + '&format=json') 
            content = json.loads(res.text)
            artist = track["artist"]["#text"]
    artist = args
    leaderBoard = dict()
    image = ""
    async for member in ctx.guild.fetch_members(limit = None):
        memberID = str(member.id)
        if(memberID in data):
            uname = data[memberID]    
            nick = str(member.nick)
            unparsedURL = {'artist' : artist , 'username' : uname , 'api_key' : LAST_FM_TOKEN , 'format' : 'json'}
            parsedURL = urllib.parse.urlencode(unparsedURL)
            res2 = requests.get('http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&' + parsedURL)
            content = json.loads(res2.text)
            playCount = content['artist']['stats']['userplaycount']
            image = content['artist']['image'][1]['#text']
            if(playCount!='0'):
                leaderBoard[nick] = int(playCount)
        
    leaderBoard =  sorted(leaderBoard.items(), key=lambda item: item[1] , reverse= True)
    embed = discord.Embed(title = 'WHO KNOWS **' + artist + '**' , color=0x00ffea)
    for key,value in leaderBoard:
        embed.add_field(name = key, value = value , inline = False)
    await ctx.send(embed = embed)

client.run(TOKEN)
