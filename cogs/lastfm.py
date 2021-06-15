import discord
import requests
import os
import json
import urllib.parse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np 
import cv2 as cv
from firebase import firebase
from discord.ext import commands
import lyricsgenius as lg
from io import BytesIO
from pygicord import Paginator
from PIL import Image

LAST_FM_TOKEN = os.getenv('LAST_FM_TOKEN')
FIREBASE_URL = os.getenv('FIREBASE_URL')
GENIUS_TOKEN = os.getenv('GENIUS_TOKEN')

class Lastfm(commands.Cog):
    def __init__(self , bot):
        self.bot = bot 
        self.firebaseObj = firebase.FirebaseApplication(FIREBASE_URL)
        self.genius = lg.Genius(GENIUS_TOKEN)
 
    async def mergeImages(self , url1 , url2):
        im1 = Image.open(requests.get(url1 , stream = True).raw)
        im2 = Image.open(requests.get(url2 , stream = True).raw)
        im1 = im1.resize((220 , 220))
        im2 = im2.resize((220 , 220))
        im1.save('1.png')
        im2.save('2.png')
        im1arr = cv.imread('1.png')
        im2arr = cv.imread('2.png')
        res = cv.addWeighted(im2arr , 1 , im1arr , 0.6 , 0)
        cv.imwrite('out.png' , res)

    async def getArtistInfo(self , artist):
        MAX_VAL = 5900000
    
        
        queryString = urllib.parse.urlencode({'artist' : artist})
        print(queryString)
        res = requests.get('http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&' + queryString+  '&api_key=' + LAST_FM_TOKEN + '&format=json')
        content = res.json()
        if("error" in content):
            return None
        else:
            listeners = float(content["artist"]["stats"]["listeners"])
            bio = content["artist"]["bio"]["summary"]
            bio = bio.rpartition('<a href')[0]
            tagList = content["artist"]["tags"]["tag"]
            similarList = content["artist"]["similar"]["artist"]
            
            #for tag description
            tagdescr = ""
            for i in tagList:
                tagdescr = tagdescr + "[{}]({}) \n".format(i["name"] , i["url"])
            tagdescr.strip()

            #for similar artist description
            similardescr = ""
            for i in similarList:
                similardescr = similardescr + "[{}]({}) \n".format(i["name"] , i["url"])
            similardescr.strip()


            embed = discord.Embed(title = "Artist info for {}".format(artist) , url = content["artist"]["url"], color = 0xff0000)
            embed.add_field(name = "Description" , value = bio if bio!="" else "-" , inline = False)
            embed.add_field(name = "Tags" , value = tagdescr if tagdescr!="" else "-", inline = False)
            embed.add_field(name = "Similar Artists" , value = similardescr if similardescr!="" else "-" , inline = False)
            based_meter = 100 - ((listeners/float(MAX_VAL)) * 100)
            embed.add_field(name = "Based Meter" , value = "**Artist is {:.2f} percent based**".format(based_meter) , inline = False)
            embed.set_footer(text = "info provided through Last Fm api")
            return embed
        
    async def getLyricsObject(self , trackartist , trackname):
        track = self.genius.search_song(trackname , trackartist)
        return track

    async def getCurrentTrack(self , discordUser , messageSender):
        print(discordUser , messageSender)
        tmpdata = self.firebaseObj.get('/lastfm' , None)
        data = dict()
        for key,value in tmpdata.items(): 
            for subKey, subVal in value.items():
                data[subKey] = subVal
                
        userid = str(discordUser.id)
        if(userid not in data):
            return None
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
            dicttrack = {'trackname' : trackname , 'trackartist' : trackartist , 'trackalbum' : trackalbum , 'trackimg' : trackimg }
            return dicttrack

    async def getTopArtists(self , discordUser , messageSender):
        tmpdata = self.firebaseObj.get('/lastfm' , None)
        data = dict()
        for key,value in tmpdata.items(): 
            for subKey, subVal in value.items():
                data[subKey] = subVal
        
        userid = str(discordUser.id)
        if(userid not in data):
            return None
        
        lastfmuname = data[userid]
        queryUname = urllib.parse.urlencode({'user' : lastfmuname})
        print(queryUname)
        res = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&' + queryUname + '&period=7day&api_key=' + LAST_FM_TOKEN + '&format=json')
        content = res.json()
        
        description = ""
        ctr = 1
        for i in content["topartists"]["artist"][:10]:
            description+=("{}. [{}]({}) - **{}** plays \n ".format(ctr , i["name"] , i["url"] , i["playcount"]))
            ctr+=1
        
        embed = discord.Embed(title = "Top Artists for {}".format(discordUser.name) , description = description ,color = 0x27f37b,url = "https://last.fm/user/" + lastfmuname)
        embed.set_thumbnail(url = discordUser.avatar_url)
        embed.set_footer(text = "requested by {}, info provided by Last Fm api".format(messageSender.name))
        return embed

    async def getTopAlbumsTracks(self , discordUser , messageSender , flag):
        tag = "track"
        if(flag==1):
            tag = "album"
        tmpdata = self.firebaseObj.get('/lastfm' , None)
        data = dict()
        for key,value in tmpdata.items(): 
            for subKey, subVal in value.items():
                data[subKey] = subVal
        
        userid = str(discordUser.id)
        if(userid not in data):
            return None
        
        lastfmuname = data[userid]
        queryUname = urllib.parse.urlencode({'user' : lastfmuname})
        print(queryUname)
        res = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.gettop' + tag + 's&' + queryUname + '&period=7day&api_key=' + LAST_FM_TOKEN + '&format=json')
        content = res.json()
        
        description = ""
        ctr = 1
        for i in content["top" + tag + "s"][tag][:10]:
            description+=("{}. [{} : {}]({}) - **{}** plays \n ".format(ctr ,i["artist"]["name"] ,  i["name"] , i["url"] ,  i["playcount"]))
            ctr+=1
        
        embed = discord.Embed(title = "Top {}s for {}".format(tag , discordUser.name) , description = description ,color = 0x27f37b,url = "https://last.fm/user/" + lastfmuname)
        embed.set_thumbnail(url = discordUser.avatar_url)
        embed.set_footer(text = "requested by {}, info provided by Last fm api".format(messageSender.name))
        return embed

    @commands.command(aliases = ['fmh'])
    async def fmhelp(self , ctx):
        embed = discord.Embed(title = 'Hugo FM Help' , color=0x00ffea)
        embed.add_field(name = "Command to set Last fm account" , value = "h.fmset" , inline = False)
        embed.add_field(name = "Command to see current track" , value = "h.fm" , inline = False)
        embed.add_field(name = "Command to see who knows an artist" , value = "h.fmw `artist` or h.fmw aliases = h.fmwhoknows" , inline = False)
        embed.add_field(name = "Command to see who knows an album" , value = "h.fmwka `<artist> - <albumname>`(aliases = h.fmwa , h.fmwhoknowsalbum) " , inline = False)
        embed.add_field(name = "Command to see who knows a track" , value = "h.fmwkt `<artist> - <trackname>` (aliases = h.fmwt , h.fmwhoknowstrack)" , inline = False)
        embed.set_thumbnail(url = 'https://lh3.googleusercontent.com/proxy/BzW7U-yNC8RjUf2SWOEzDcRxlCjXZBx7RGjiGu7QdDm7g4aKHC3tE815KW-cyut1yBF-qOKhR0r5i919Fa2nPnYqITbp-bg4Rqs_dxE8b976G3bi9SMUIC88Qkw8RIOphMD7rrIsggvBzwtcZdwTSvqVVM-vzhdeQtc')
        embed.set_footer(text = 'requested by ' + ctx.message.author.name)
        await ctx.send(embed = embed)

    @commands.command()
    async def fmset(self , ctx , *args):
        tmpdata = self.firebaseObj.get('/lastfm' , None)
        data = dict()
        for key,value in tmpdata.items(): 
            for subKey, subVal in value.items():
                data[subKey] = subVal

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
        self.firebaseObj.post('/lastfm' , tmp)
        await ctx.send("User successfully added :vampire:")

    @commands.command()
    async def fm(self , ctx , member : discord.Member):
        res = await self.getCurrentTrack(member , ctx.message.author)
        if(res["trackartist"]==None):
            res["trackartist"] = "-"
        if(res["trackname"]==None):
            res["trackname"] = "-"
        if(res["trackalbum"]==None):
            res["trackalbum"] = "-"
        if(res["trackimg"]==None):
            res["trackimg"] = "https://www.brandwatch.com/wp-content/themes/brandwatch/src/core/endpoints/resize.php?image=uploads/brandwatch/troll.jpg&width=469"

        print(res)
        if(res!=None):
            embed = discord.Embed(title = 'Now Playing/Recent Track' , color=0x00ffea)
            embed.add_field(name = "Track Name" , value = res['trackname'], inline = False)
            embed.add_field(name = "Artist Name" , value = res['trackartist'] , inline = False)
            embed.add_field(name = "Album Name", value = res['trackalbum'], inline = False)
            embed.set_image(url = res['trackimg'])
            await ctx.send(embed = embed)
        else:
            await ctx.send("no last fm set")
    
    @fm.error
    async def fmerror(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            res = await self.getCurrentTrack(ctx.message.author , ctx.message.author)
            if(res!=None):
                embed = discord.Embed(title = 'Now Playing/Recent Track' , color=0x00ffea)
                embed.add_field(name = "Track Name" , value = res['trackname']  , inline = False)
                embed.add_field(name = "Artist Name" , value = res['trackartist'] , inline = False)
                embed.add_field(name = "Album Name", value = res['trackalbum'] if(res['trackalbum']!=None) else "-" , inline = False)
                embed.set_image(url = res['trackimg'])
                await ctx.send(embed = embed)
            else:
                await ctx.send("no last fm set")            

        if isinstance(err , commands.BadArgument):
            await ctx.reply("Wrong argument" , mention_author = True)  

    @commands.command(aliases = ['fmwhoknows' , 'fmwk'])
    async def fmw(self , ctx , *, args):
        tmpdata = self.firebaseObj.get('/lastfm' , None)
        data = dict()
        for key,value in tmpdata.items(): 
            for subKey, subVal in value.items():
                data[subKey] = subVal
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
        for x,y in leaderBoard[:5]:
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
    async def fmwerror(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            tmpdata = self.firebaseObj.get('/lastfm' , None)
            data = dict()
            for key,value in tmpdata.items(): 
                for subKey, subVal in value.items():
                    data[subKey] = subVal
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
            for x,y in leaderBoard[:5]:
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

    @commands.command(aliases = ['fmwka' , 'fmwa'])
    async def fmwhoknowsalbum(self , ctx , * , args):
        tmpdata = self.firebaseObj.get('/lastfm' , None)
        data = dict()
        for key,value in tmpdata.items(): 
            for subKey, subVal in value.items():
                data[subKey] = subVal
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
        description = ""
        ctr = 0
        for key,value in leaderBoard:
            ctr+=1
            description = description + str(ctr) + ". " + key + '  -  ' + '**' + str(value) + '** plays \n'

        embed = discord.Embed(title = 'Who knows **' + artist + '** - ' + '**' + album + '**' , description = description , color=0x00ffea)
        embed.set_thumbnail(url = image)
        embed.set_footer(text = "requested by " + ctx.message.author.name)
        await ctx.send(embed = embed) 

    @fmwhoknowsalbum.error
    async def fmwhoknowsalbumerr(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            tmpdata = self.firebaseObj.get('/lastfm' , None)
            data = dict()
            for key,value in tmpdata.items(): 
                for subKey, subVal in value.items():
                    data[subKey] = subVal
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
                description = ""
                ctr = 0
                for key,value in leaderBoard:
                    ctr+=1
                    description += str(ctr) + ". " + key + '  -  ' + '**' + str(value) + '** plays \n'

                embed = discord.Embed(title = 'Who knows **' + artist + '** - ' + '**' + album + '**' , description = description , color=0x00ffea)
                embed.set_thumbnail(url = image)
                embed.set_footer(text = "requested by " + ctx.message.author.name)
                await ctx.send(embed = embed) 

    @commands.command(aliases = ['fmwt' , 'fmwkt'])
    async def fmwhoknowstrack(self , ctx , * , args):
        tmpdata = self.firebaseObj.get('/lastfm' , None)
        data = dict()
        for key,value in tmpdata.items(): 
            for subKey, subVal in value.items():
                data[subKey] = subVal
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
        description = ""
        ctr = 0
        for key,value in leaderBoard:
            ctr+=1
            description += str(ctr) + ". " + key + '  -  ' + '**' + str(value) + '** plays \n'

        embed = discord.Embed(title = 'Who knows **' + artist + '** - ' + '**' + track + '**' , description = description , color=0x00ffea)
        embed.set_thumbnail(url = image)
        embed.set_footer(text = "requested by " + ctx.message.author.name)
        await ctx.send(embed = embed) 

    @fmwhoknowstrack.error
    async def fmwhoknowstrackerr(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            tmpdata = self.firebaseObj.get('/lastfm' , None)
            data = dict()
            for key,value in tmpdata.items(): 
                for subKey, subVal in value.items():
                    data[subKey] = subVal
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
                description = ""
                ctr = 0
                for key,value in leaderBoard:
                    ctr+=1
                    description += str(ctr) + ". " + key + '  -  ' + '**' + str(value) + '** plays \n'

                embed = discord.Embed(title = 'Who knows **' + artist + '** - ' + '**' + track + '**' , description = description , color=0x00ffea)
                embed.set_thumbnail(url = image)
                embed.set_footer(text = "requested by " + ctx.message.author.name)
                await ctx.send(embed = embed)    
    
    @commands.command(aliases = ['fmta' , 'fmtopa' , 'fmtoparts'])
    async def fmtopartists(self , ctx , member:discord.Member):
        discordUser = member
        sender = ctx.message.author
        embed = await self.getTopArtists(discordUser , sender)
        if(embed != None):
            await ctx.send(embed = embed)
        else:
            await ctx.reply("Invalid user" , mention_author = True)

    @fmtopartists.error
    async def fmtaerr(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            member = ctx.message.author
            embed = await self.getTopArtists(member , member)
            if(embed !=None):
                await ctx.send(embed = embed)
            else:
                await ctx.reply("Invalid user" , mention_author = True)
        
        if isinstance(err , commands.BadArgument):
            await ctx.reply("Invalid arguments" , mention_author = True)

    @commands.command(aliases = ['fmtt' , 'fmtoptr' , 'fmttracks'])
    async def fmtoptracks(self , ctx , member:discord.Member):
        discordUser = member
        sender = ctx.message.author
        embed = await self.getTopAlbumsTracks(discordUser , sender , 0)
        if(embed != None):
            await ctx.send(embed = embed)
        else:
            await ctx.reply("Invalid user" , mention_author = True)

    @fmtoptracks.error
    async def fmtterr(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            member = ctx.message.author
            embed = await self.getTopAlbumsTracks(member , member , 0)
            if(embed !=None):
                await ctx.send(embed = embed)
            else:
                await ctx.reply("Invalid user" , mention_author = True)
        
        if isinstance(err , commands.BadArgument):
            await ctx.reply("Invalid arguments" , mention_author = True)
    
    @commands.command(aliases = ['fmtal' , 'fmtopal' , 'fmtalbums'])
    async def fmtopalbums(self , ctx , member:discord.Member):
        discordUser = member
        sender = ctx.message.author
        embed = await self.getTopAlbumsTracks(discordUser , sender , 1)
        if(embed != None):
            await ctx.send(embed = embed)
        else:
            await ctx.reply("Invalid user" , mention_author = True)

    @fmtopalbums.error
    async def fmtterr(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            member = ctx.message.author
            embed = await self.getTopAlbumsTracks(member , member , 1)
            if(embed !=None):
                await ctx.send(embed = embed)
            else:
                await ctx.reply("Invalid user" , mention_author = True)
        
        if isinstance(err , commands.BadArgument):
            await ctx.reply("Invalid arguments" , mention_author = True)

    @commands.command(aliases = ['fma' , 'fmainfo'])
    async def fmartistinfo(self , ctx , *args):
        if(args==()):
            member = ctx.message.author
            trackoutput = await self.getCurrentTrack(member , member)
            if(trackoutput==None):
                await ctx.send("Set your last fm account first")
                return ;
            artist = trackoutput["trackartist"]
            output = await self.getArtistInfo(artist)
            if(output==None):
                await ctx.send("Invalid artist")
            else:
                await ctx.send(embed = output)
        else:
            artist = args
            artistname = ""
            for i in artist:
                artistname = artistname + " " + i

            output = await self.getArtistInfo(artistname.strip())
            if(output==None):
                await ctx.send("Invalid artist")
            else:
                await ctx.send(embed = output)
          
    @commands.command(aliases = ['l' , 'fmlyr' , 'lyr'])
    async def fmlyrics(self , ctx , * , args):
        track = args.split('-')
        if(len(track)!=2):
            await ctx.send("Send trackname in valid format which is `<Artist> - <trackname>`")
        else:
            lyrics = await self.getLyricsObject(track[0].strip() , track[1].strip())
            result = list(filter(lambda x : x != '', lyrics.lyrics.split('\n\n')))
            pages = []
            for i in range(1 , len(result) + 1):
                embed = discord.Embed(title = "Lyrics for **{}** - page {}".format(args , i) , description = result[i-1] , color = 0xffff64)
                embed.set_footer(text = "requested by {} and provided by Genius API".format(ctx.message.author.name))
                pages.append(embed)
            
            paginator = Paginator(pages = pages)
            await paginator.start(ctx)
        
    @fmlyrics.error
    async def fmlerr(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            track = await self.getCurrentTrack(ctx.message.author , ctx.message.author)
            lyricsobj = await self.getLyricsObject(track["trackartist"] , track["trackname"])
            result = list(filter(lambda x : x != '', lyricsobj.lyrics.split('\n\n')))
            pages = []
            for i in range(1 , len(result) + 1):
                embed = discord.Embed(title = "Lyrics for **{} - {}** - page {}".format(track["trackartist"] , track["trackname"] , i) , description = result[i-1] , color = 0xffff64)
                embed.set_footer(text = "requested by {} and provided by Genius API".format(ctx.message.author.name))
                embed.set_thumbnail(url = track["trackimg"])
                pages.append(embed)
            
            paginator = Paginator(pages = pages)
            await paginator.start(ctx)

    @commands.command(aliases = ['fmcomerge' , 'fmm' , 'fmcm' , ])
    async def fmcovermerge(self , ctx):
        member = ctx.message.author
        output = await self.getCurrentTrack(member , member)
        if(output["trackimg"]==""):
            await ctx.reply('No cover url on last fm :pensive:' , mention_author = True)
        else:
            await self.mergeImages(member.avatar_url , output["trackimg"])
            fil = discord.File('out.png')
            embed = discord.Embed(title = "Merged pictures")
            embed.set_image(url = "attachment://out.png")
            await ctx.send(embed = embed , file = fil)
        
def setup(bot):
    bot.add_cog(Lastfm(bot))