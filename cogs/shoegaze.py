import discord
import cv2 as cv
import numpy as np
import urllib
import requests
import random
from PIL import Image
from math import *
from discord.ext import commands

class Shoegaze(commands.Cog):
    def __init__(self , bot):
        self.bot = bot

    async def distortImage(self , im):
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

    async def getShoegazedImage(self , imgurl , color):
        if(color!='p' and color!='g' and color!='b'):
            return None
        colorefs = {'b' : (255 , 0 , 0) , 'p' : (255 , 18 , 255) , 'g' : (0 , 255 , 0)}
        embedrefs = {'b' : 0x0000ff , 'p' : 0xc912de , 'g' : 0x00ff00}
        im = Image.open(requests.get(imgurl , stream = True).raw)
        im.save('inter.png')
        image = 'inter.png'
        initimg = cv.imread(image , 1)

        rows , cols , res = initimg.shape
        refimg = np.full((rows , cols , res) , colorefs[color] , np.uint8)
        finalimg = cv.addWeighted(initimg , 1 , refimg , 0.6 , 0)
        cv.imwrite('res.jpg', finalimg)
        embed = discord.Embed(title = "Shoegazed image" , color = embedrefs[color])
        fil = discord.File('res.jpg')
        embed.set_image(url = 'attachment://res.jpg')
        return (fil , embed)

    @commands.command(aliases = ['sg' , 'sgc'])
    async def shoegazecolor(self , ctx , color):
        output = await self.getShoegazedImage(ctx.message.author.avatar_url , color)
        if(output!=None):
            await ctx.send(file = output[0] , embed = output[1])
        else:
            await ctx.send("invalid color input")
    
    @shoegazecolor.error
    async def shoegazecolorerr(self , ctx , err):
        if isinstance(err , commands.MissingRequiredArgument):
            output = await self.getShoegazedImage(ctx.message.author.avatar_url , "p")
            if(output!=None):
                await ctx.send(file = output[0] , embed = output[1])
            else:
                await ctx.send("Invalid color input")

    @commands.command(aliases = ['sgd'])
    async def shoegazecolordistort(self , ctx , color):
        output = await self.getShoegazedImage(ctx.message.author.avatar_url , color)
        if(output!=None):
            im = Image.open("res.jpg")
            res = await self.distortImage(im)
            res.save('res.jpg')
            fil = discord.File('res.jpg')
            await ctx.send(embed = output[1] , file = fil)
        else:
            await ctx.send("Invalid color input")
    
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(aliases = ['sgi'])
    async def shoegazeimage(self , ctx , url , color):
        output = await self.getShoegazedImage(url , color)
        if(output!=None):
            await ctx.send(file = output[0] , embed = output[1])
        else:
            await ctx.send("Invalid color input")

    @shoegazeimage.error
    async def errorsgi(self  , ctx , err):
        if isinstance(err , commands.CommandOnCooldown):
            await ctx.send("Cooldown for a while send in {:.2f}s".format(err.retry_after))

    
    @commands.command(aliases = ['sgid'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def shoegazeimagedistort(self , ctx , url , color):
        output = await self.getShoegazedImage(url , color)
        if(output!=None):
            im = Image.open("res.jpg")
            res = await self.distortImage(im)
            res.save('res.jpg')
            fil = discord.File('res.jpg')
            await ctx.send(embed = output[1] , file = fil)
        else:
            await ctx.send("Invalid color input")

    @shoegazeimagedistort.error
    async def errorsgid(self  , ctx , err):
        if isinstance(err , commands.CommandOnCooldown):
            await ctx.send("Cooldown for a while send in {:.2f}s".format(err.retry_after))


def setup(bot):
    bot.add_cog(Shoegaze(bot))