import discord
import requests
import os
import json
import urllib.parse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np 
from firebase import firebase
from discord.ext import commands
from io import BytesIO


LAST_FM_TOKEN = os.getenv('LAST_FM_TOKEN')
FIREBASE_URL = os.getenv('FIREBASE_URL')

class Lastfm(commands.Cog):
    def __init__(self , bot):
        self.bot = bot 
        self.firebaseObj = firebase.FirebaseApplication(FIREBASE_URL)
        tmpdata = self.firebaseObj.get('/lastfm' , None)
        self.data = dict()
        for key,value in tmpdata.items(): 
            for subKey, subVal in value.items():
                self.data[subKey] = subVal
    
    @commands.command()
    async def fmset(self , ctx , *args):
        userid = str(ctx.message.author.id)
        fmuname = args[0]


        for key, value in self.data.items(): 
            if(key==userid or value==fmuname):
                await ctx.send("User is already there")
                return 0
            else:
                res = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user=' + fmuname + '&api_key=' + LAST_FM_TOKEN + '&format=json')
                content = json.loads(res.text)
                if("message" in content and content["message"]=="User not found"):
                    await ctx.send("User not found :(")
                    return 0

        self.data[userid] = fmuname
        tmp = {userid : fmuname}
        self.firebaseObj.post('/lastfm' , tmp)
        await ctx.send("User successfully added :vampire:")

    @commands.command()
    async def fm(self , ctx):
        userid = str(ctx.message.author.id)
        if(userid not in self.data):
            await ctx.send("Please set your last fm account first")
        else:
            fmuname = self.data[userid]
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


    @commands.command(aliases = ['fmwhoknows' , 'fmwk'])
    async def fmw(self , ctx , *, args):
        artist = args
        leaderBoard = dict()
        image = ""
        async for member in ctx.guild.fetch_members(limit = None):
            memberID = str(member.id)
            if(memberID in self.data):
                uname = self.data[memberID]
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
            artist = ""
            userid = str(ctx.message.author.id)
            if(userid not in self.data):
                await ctx.send("Please set your last fm account first")
                return ;
            else:
                fmuname = self.data[userid]
                res = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + fmuname + '&api_key=' + LAST_FM_TOKEN + '&format=json') 
                content = json.loads(res.text)
                track = content["recenttracks"]["track"][0]
                artist = track["artist"]["#text"]

            leaderBoard = dict()
            image = ""
            async for member in ctx.guild.fetch_members(limit = None):
                memberID = str(member.id)
                if(memberID in self.data):
                    uname = self.data[memberID]
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
        artistAlbum = args.split("-")
        artistAlbum = [i.strip() for i in artistAlbum]
        album = artistAlbum[1]
        artist = artistAlbum[0]
        leaderBoard = dict()
        image = ""
        async for member in ctx.guild.fetch_members(limit = None):
            memberID = str(member.id)
            if(memberID in self.data):
                uname = self.data[memberID]
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
            description = key + '  -  ' + '**' + str(value) + '** plays \n'

        embed = discord.Embed(title = 'Who knows **' + artist + '** - ' + '**' + album + '**' , description = description , color=0x00ffea)
        embed.set_image(url = image)
        await ctx.send(embed = embed) 

    @fmwhoknowsalbum.error
    async def fmwhoknowsalbumerr(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            artist = ""
            album = ""
            userid = str(ctx.message.author.id)
            if(userid not in self.data):
                await ctx.send("Please set your last fm account first")
                return ;
            else:
                fmuname = self.data[userid]
                res = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + fmuname + '&api_key=' + LAST_FM_TOKEN + '&format=json') 
                content = json.loads(res.text)
                track = content["recenttracks"]["track"][0]
                artist = track["artist"]["#text"]
                album = track["album"]["#text"]
        
                leaderBoard = dict()
                image = ""
                async for member in ctx.guild.fetch_members(limit = None):
                    memberID = str(member.id)
                    if(memberID in self.data):
                        uname = self.data[memberID]
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
                    description = key + '  -  ' + '**' + str(value) + '** plays \n'

                embed = discord.Embed(title = 'Who knows **' + artist + '** - ' + '**' + album + '**' , description = description , color=0x00ffea)
                embed.set_image(url = image)
                await ctx.send(embed = embed) 

    @commands.command(aliases = ['fmwt' , 'fmwkt'])
    async def fmwhoknowstrack(self , ctx , * , args):
        artistTrack = args.split("-")
        artistTrack = [i.strip() for i in artistTrack]
        track = artistTrack[1]
        artist = artistTrack[0]
        leaderBoard = dict()
        image = ""
        async for member in ctx.guild.fetch_members(limit = None):
            memberID = str(member.id)
            if(memberID in self.data):
                uname = self.data[memberID]
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
            description = key + '  -  ' + '**' + str(value) + '** plays \n'

        embed = discord.Embed(title = 'Who knows **' + artist + '** - ' + '**' + track + '**' , description = description , color=0x00ffea)
        embed.set_image(url = image)
        await ctx.send(embed = embed) 

    @fmwhoknowstrack.error
    async def fmwhoknowstrackerr(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            artist = ""
            track= ""
            userid = str(ctx.message.author.id)
            if(userid not in self.data):
                await ctx.send("Please set your last fm account first")
                return ;
            else:
                fmuname = self.data[userid]
                res = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + fmuname + '&api_key=' + LAST_FM_TOKEN + '&format=json') 
                content = json.loads(res.text)
                trackitem = content["recenttracks"]["track"][0]
                artist = trackitem["artist"]["#text"]
                track = trackitem["name"]
        
                leaderBoard = dict()
                image = ""
                async for member in ctx.guild.fetch_members(limit = None):
                    memberID = str(member.id)
                    if(memberID in self.data):
                        uname = self.data[memberID]
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
                    description = key + '  -  ' + '**' + str(value) + '** plays \n'

                embed = discord.Embed(title = 'Who knows **' + artist + '** - ' + '**' + track + '**' , description = description , color=0x00ffea)
                embed.set_image(url = image)
                await ctx.send(embed = embed)    


def setup(bot):
    bot.add_cog(Lastfm(bot))