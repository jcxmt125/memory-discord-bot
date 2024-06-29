#actual python modules
import discord, os, json, subprocess, datetime
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

#my own python files
from geminillm import gemrequest
from urlextract import URLExtract
from cfradar import urlScan
from cfsd import sdgen
from htmlify import makePage
from UploadFile import uploadFileToCloud
import localconverters, nltocommand, cfllm, whispercf

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.command()
async def llmreq(ctx, *, msg):
    async with ctx.typing():
        try:
            resp = gemrequest(msg)
        except:
            resp = cfllm.llmrequest("You are a helpful assistant that doesn't use emoji", msg)

        if resp[0] == True:
            await ctx.send(resp[1])
        else:
            await ctx.send("Prompt likely blocked: "+resp[1])

@bot.command()
async def dumpMemory(ctx):
    usr = str(ctx.message.author)
    if Path("ltmemories/"+usr+".txt").exists():
        await ctx.send(file=discord.File("ltmemories/"+usr+".txt"))
    else:
        await ctx.send("No long term memory file found for "+usr)
    
    if Path("stmemories/"+usr+".json").exists():
        await ctx.send(file=discord.File("stmemories/"+usr+".json"))
    else:
        await ctx.send("No short term memory file found for "+usr)

@bot.command()
async def current(ctx):
    usr = str(ctx.message.author)
    
    if Path("stmemories/"+usr+".json").exists():
        with open("stmemories/"+usr+".json", "r", encoding="utf-8") as mem:
            shortTermMemory = json.load(mem)#read short term memory
        
        await ctx.send("Conversation ongoing with "+str(len(shortTermMemory)//2)+" interactions.")
    else:
        await ctx.send("No conversation ongoing for "+usr)

@bot.command()
async def finish(ctx):
    usr = str(ctx.message.author)

    with open("stmemories/"+usr+".json", "r", encoding="utf-8") as mem:
        shortTermMemory = json.load(mem)#read short term memory
    
    construct = "The following is a conversation between a chatbot and a user. Summarize the interaction briefly.\n"

    for i in shortTermMemory:
        construct += i["parts"][0]
        construct += "\n"
    
    modelReply = gemrequest(construct)

    if modelReply[0] == False:
        await ctx.send("something went wrong: "+modelReply[1])
    else:#append summary to long term memory
        with open("ltmemories/"+usr+".txt", "a", encoding="utf-8") as mem:
            mem.write(modelReply[1])
            Path.unlink(Path("stmemories/"+usr+".json"))
        await ctx.send("Current conversation summarized and appended to long term memory: "+modelReply[1])

@bot.command()
async def talk(ctx, *, msg):
    usr = str(ctx.message.author)

    #short term memory: list (gemini API multi-turn)
    #long term memory: -> Let's just make it a text file for simplicity (not sure how well it'll work)

    if not Path("ltmemories/"+usr+".txt").exists():
        with open("ltmemories/"+usr+".txt", "w", encoding="utf-8") as mem:
            mem.write("")
            longTermMemory = ""
    else:
        with open("ltmemories/"+usr+".txt", "r", encoding="utf-8") as mem:
            longTermMemory = mem.read()

    if not Path("stmemories/"+usr+".json").exists():
        with open("stmemories/"+usr+".json", "w", encoding="utf-8") as mem:
            mem.write("")
            shortTermMemory = ""
    else:
        with open("stmemories/"+usr+".json", "r", encoding="utf-8") as mem:
            shortTermMemory = json.load(mem)#read short term memory
        

    async with ctx.typing():
        construct = []
        if shortTermMemory == "":
            construct.append({'role':'user','parts': ["You are a helpful assistant, helping a user named " + usr + ". The current date is " + str(datetime.date.today()) + ". These are summaries of your previous conversations with the user for context: " + longTermMemory]})
        else:
            construct = shortTermMemory

        construct.append({'role':'user',
        'parts': [msg]})

        try:
            modelReply = gemrequest(construct)
            if modelReply[0] == False:
                raise
            try:
                await ctx.send(modelReply[1])
            except:#too long
                with open("temp.txt", "w", encoding="utf-8") as temp:
                    temp.write(modelReply)
                await ctx.send("The response is too long to send! I'll give you a text file instead.",file = discord.File("temp.txt"))
                Path.unlink(Path("temp.txt"))
        except:
            await ctx.send("Sorry, something seems to have gone wrong. Please try again. This conversation wasn't recorded into memory.")
            return
        
        construct.append({'role':'model', 'parts': [modelReply[1]]})

        with open("stmemories/"+usr+".json", "w", encoding="utf-8") as mem:
            json.dump(construct, mem)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

bot.run(os.getenv("DISCORD_BOT_TOKEN"))