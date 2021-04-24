import discord
import os
import random
import requests
import datetime as dt
from firebase import firebase 
from math import *

from dotenv import load_dotenv
from discord.ext import commands
from PIL import Image
from listofnames import first_names,last_names
from io import BytesIO
import urllib.parse
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
API_TOKEN = os.getenv('API_TOKEN')
LAST_FM_TOKEN = os.getenv('LAST_FM_TOKEN')
FIREBASE_URL = os.getenv('FIREBASE_URL')
client = commands.Bot(command_prefix = 'h.')
client.remove_command('help')
modes = [100 , 200 , 127 , 265 , 246 , 110 , 1 , 34 , 124 , 245]
firebaseObj = firebase.FirebaseApplication(FIREBASE_URL)
tmpdata = firebaseObj.get('/lastfm' , None)
data = {}

for key,value in tmpdata.items(): 
     for subKey, subVal in value.items():
         data[subKey] = subVal


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
    #except:
    #   await ctx.send("invalid url :pensive:")

@client.command()
async def fmset(ctx , *args):
    userid = str(ctx.message.author.id)
    fmuname = args[0]


    for key, value in data.items(): 
          if(value["user_id"]==userid or value["fmuname"]==fmuname):
              await ctx.send("User is already there")
              return 0
          else:
              res = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user=' + fmuname + '&api_key=' + LAST_FM_TOKEN + '&format=json')
              content = json.loads(res.text)
              if("message" in content and content["message"]=="User not found"):
                  await ctx.send("User not found :(")
                  return 0

    lkeys = list(data.keys())
    length = len(lkeys)
    tmp = {userid : fmuname}
    result = firebaseObj.post('/lastfm' , tmp)
    print(result)
    await ctx.send("User successfully added")

@client.command()
async def fmw(ctx , *, args):
    artist = args
    leaderBoard = dict()
    image = ""
    async for member in ctx.guild.fetch_members(limit = None):
        memberID = str(member.id)
        if(memberID in data):
            uname = data[memberID]    
            nick = str(member.name)
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

@client.command(aliases = ['sol'])
async def standardofliving(ctx , * , args):
    queryCity = urllib.parse.urlencode({'search' : args})
    res1 = requests.get('https://api.teleport.org/api/cities/?' + queryCity)
    content1 = json.loads(res1.text)
    nextUrl = content1['_embedded']['city:search-results'][0]['_links']['city:item']['href']

    if(nextUrl):
        res2 = requests.get(nextUrl)
        content2 = json.loads(res2.text)
        nextnextUrl = content2['_links']['city:urban_area']['href'] + 'scores'
        res3 = requests.get(nextnextUrl)
        content3 = json.loads(res3.text)
        city_score = content3['teleport_city_score']
        embed = discord.Embed(name = 'Teleport City Summary' , description = "**Teleport City Score  : " + str(city_score) + "**" , color = 0x00ffea)
        categories = content3['categories']
        flip = False
        ctr = 1
        for i in content3['categories']:
            if(ctr%4==0):
                flip = False
            else:
                flip = True

            ctr+=1
            embed.add_field(name = i['name'] , value = i['score_out_of_10'] , inline = flip)

        embed.set_footer(text = 'data provided by Teleport api')
        embed.set_thumbnail(url = 'https://www.plantemoran.com/-/media/images/insights-images/2018/04/thinking-about-becoming-a-smart-city.jpg?h=704&w=1100&la=en&hash=0F4F54BBECD3E501765A064202A24F8851D74E04')
        await ctx.send(embed = embed)
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
    country = args[0]
    param = ""
    try:
        countrydata = content[country]
        if(len(args)<2):
            await ctx.send("Missin Arguments :nerd:")
            return ;

        if(args[1]=='-d'):
            param = "deaths"
        elif(args[1]=='-r'):
            param = "recovered"
        elif(args[1]=='-c'):
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
        for i in range(10):
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
        await ctx.send(file = fil)
    except:
        await ctx.send("Invalid Country name :rage:")

@client.command(aliases = ['codefrand' , 'cfrand'])
async def codeforcesrandomprob(ctx):
    res = requests.get('http://codeforces.com/api/problemset.problems')
    content = json.loads(res.text)
    probNum = random.randint(0 , len(content["result"]["problems"]))
    prob = content["result"]["problems"][probNum]
    embed = discord.Embed(title = prob["name"] , url = "http://codeforces.com/problemset/problem/" + str(prob["contestId"]) + "/" + prob["index"] , description = 'Type : *' + prob["type"] + '*')
    embed.add_field(name = "points" , value = prob["points"], inline = False , color = 0xffffff)
    embed.add_field(name = "rating" , value = prob["rating"], inline = False)
    tmpstr = ""
    for i in prob["tags"]:
        tmpstr = tmpstr + i + "\n"
    embed.add_field(name = "tags" , value = tmpstr)
    embed.set_footer(text = "Random codeforces problem requested by a nerd")
    embed.set_thumbnail(url = 'https://codeforces.com/predownloaded/3b/86/3b8616d876e29762202e93e184d4373eb62e7274.png')
    await ctx.send(embed = embed)

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
    
client.run(TOKEN)
