import discord
from discord.ext import commands
from datetime import *
import pyrebase
firebaseConfig = {

  "apiKey": "AIzaSyByPyvbYI4TRLvwD6Bfw9TCmzFK46KbcOE",

  "authDomain": "hugobot-3d0d0.firebaseapp.com",

  "databaseURL": "https://hugobot-3d0d0-default-rtdb.firebaseio.com",

  "projectId": "hugobot-3d0d0",

  "storageBucket": "hugobot-3d0d0.appspot.com",

  "messagingSenderId": "205636928878",

  "appId": "1:205636928878:web:a0aafee6ab5c69b5722d7f"

};

class Study(commands.Cog):
    def __init__(self , bot):
        self.bot = bot
        self.firebase = pyrebase.initialize_app(firebaseConfig)
        self.db = self.firebase.database()

    async def add_time(self , obj1 , obj2):
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
        finaltimeobj = datetime.strptime(finaltime , "%H:%M:%S")
        return finaltimeobj

    @commands.command(aliases = ['stz'])
    async def settimezone(self , ctx , *args):
        res = self.db.child('study').child(str(ctx.message.author.id)).get()
        if(res.val()!=None):
            await ctx.reply("User already there!" , mention_author = True)
        else:
            tz = args[0]
            tmp = {"logs" : ["0"],  "pending"  : ["0"] , "timezone" : tz}
            self.db.child('study').child(str(ctx.message.author.id)).set(tmp);
            await ctx.message.add_reaction("✅")
            await ctx.reply("Successfully added" , mention_author = True)
    
    @commands.command(aliases = ['start' , 'str'])
    async def startsession(self , ctx):
        userid = str(ctx.message.author.id)
        check = self.db.child('study').child(userid).get()
        if(check.val()==None):
            await ctx.reply("Set time zone first!" , mention_author = True)
        else:
            userdata = self.db.child('study').child(userid).child('pending').get()
            if(len(userdata.val())==1):
                now = datetime.now()
                stringnow = datetime.strftime(now , "%d-%M-%Y %H:%m:%S")
                self.db.child('study').child(userid).update({"pending" : ["0", stringnow]})
            else:
                await ctx.reply("Session already going on!" , mention_author = True)
    
    @commands.command(aliases = ['stop' , 'stp'])
    async def stopsession(self , ctx):
        userid = str(ctx.message.author.id)
        check = self.db.child('study').child(userid).get()
        if(check.val()==None):
            await ctx.reply("Set time zone first!" , mention_author = True)
        else:
            userdata = self.db.child('study').child(userid).child('pending').get()
            if(len(userdata.val())!=1):
                now = datetime.now()
                date = datetime.strftime(datetime.today() , "%d-%m-%Y")
                sessiondata = self.db.child('study').child(userid).child('pending').get().val()
                logs = self.db.child('study').child(userid).child('logs').get().val()
                nowdateobj = datetime.strptime(sessiondata[1] , "%d-%M-%Y %H:%m:%S")
                timediffobj = now - nowdateobj
                hours = timediffobj.seconds//3600
                mins = timediffobj.seconds//60 % 60
                seconds = timediffobj.seconds - (3600 * hours + mins * 60)
                self.db.child('study').child(userid).update({"pending" : ["0"]})
                print(logs)
                logs.append({"hours" : hours , "mins" : mins , "secs" : seconds , "date" : date})
                self.db.child('study').child(userid).update({"logs" : logs})
                await ctx.reply("You studied for {} hours , {} minutes , {} seconds".format(hours , mins , seconds) , mention_author = True)
            else:
                await ctx.reply("No ongoing session" , mention_author = True)

    @commands.command(aliases = ['stats' , 'daily'])
    async def dailystats(self , ctx):
        userid = ctx.message.author.id
        check = self.db.child('study').child(userid).get()
        if(check.val()==None):
            await ctx.reply("Set time zone first!" , mention_author = True)
        else:
            date = datetime.strftime(datetime.today() , "%d-%m-%Y")
            logs = self.db.child('study').child(userid).child('logs').get().val()
            totalTime = time(0 , 0 , 0)
            for i in logs[1:]:
                if(date==i["date"]):
                    timeobj = time(i["hours"] , i["mins"] , i["secs"])
                    totalTime = await self.add_time(timeobj , totalTime)
            
            await ctx.reply("You studied for {} hours {} minutes {} seconds! today".format(totalTime.hour , totalTime.minute , totalTime.second) , mention_author = True)


def setup(bot):
    bot.add_cog(Study(bot))