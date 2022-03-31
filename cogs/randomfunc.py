import discord
import random
from discord.ext import commands
from listofnames import first_names, last_names
from dotenv import load_dotenv
load_dotenv()
class RandomFunc(commands.Cog):
    def __init__(self , bot):
        self.bot = bot

    @commands.command(aliases = ['rand'])
    async def randomname(self , ctx , *args):
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
            await ctx.send("Send valid arguments :nerd:")
    
    @commands.command(aliases = ['nrand'])
    async def randomnum(self , ctx , *args):
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

def setup(bot):
    bot.add_cog(RandomFunc(bot))