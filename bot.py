#actual python modules
import discord, os, json, subprocess, datetime, cv2, qrcode
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path
from qreader import QReader

#my own python files
from geminillm import gemrequest
from urlextract import URLExtract
from cfradar import urlScan
from cfsd import sdgen
from htmlify import makePage
from UploadFile import uploadFileToCloud
import localconverters, cfllm, whispercf

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.command()
async def llmreq(ctx, *, msg):
    """
    Straight request to the llm backend.
    Does not have any additional features, simply add what you'd like to send as a request.
    """
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
    """
    Dump your memory file.
    If exists, it'll try to send both your short term memory JSON file, and your long term memory text file.
    """
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
    """
    Will return whether you're in a conversation.
    Will have (stale) if your short term memory is older than an hour, in which case it'll be immediately purged (appended to long term memory) when you start a new conversation.
    """
    usr = str(ctx.message.author)
    
    if Path("stmemories/"+usr+".json").exists():
        
        toSend = ""
        
        with open("stmemories/"+usr+".json", "r", encoding="utf-8") as mem:
            shortTermMemory = json.load(mem)#read short term memory
        
        toSend += "Conversation ongoing for "+ usr +" with "+str(len(shortTermMemory)//2)+" interactions."
        
        date = shortTermMemory[-2]["parts"][0][0:10].split("-")
        time = shortTermMemory[-2]["parts"][0][11:19].split(":")

        if datetime.datetime.now() - datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2])) > datetime.timedelta(hours=1):
            toSend += " (stale)"
            

    else:
        await ctx.send("No conversation ongoing for "+usr)

@bot.command()
async def finish(ctx):
    """
    Finishes the current conversation.
    Will summarize the current conversation and append it to your long term memory.
    """
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
        return
    else:#append summary to long term memory
        with open("ltmemories/"+usr+".txt", "a", encoding="utf-8") as mem:
            mem.write(str(datetime.datetime.today) + ": "+modelReply[1])
            Path.unlink(Path("stmemories/"+usr+".json"))
        await ctx.send("Current conversation summarized and appended to long term memory: "+modelReply[1])

@bot.command()
async def stmemPurge(ctx):
    """
    Purges your short term memory file.
    This will immediately and irreversibly delete your short term memory! (long term memory not affected)
    """
    usr = str(ctx.message.author)
    if Path("stmemories/"+usr+".json").exists():
        Path.unlink(Path("stmemories/"+usr+".json"))
        await ctx.send("Purged short term memory for "+usr)
    else:
        await ctx.send("No short term memory file found for "+usr)

@bot.command()
async def deregisterAllMemory(ctx):
    """
    Deletes all short term and long term memory.
    """
    usr = str(ctx.message.author)
    if Path("ltmemories/"+usr+".txt").exists():
        Path.unlink(Path("ltmemories/"+usr+".txt"))
    if Path("stmemories/"+usr+".json").exists():
        Path.unlink(Path("stmemories/"+usr+".json"))
    await ctx.send("Deleted all memory permanantly for "+usr)

@bot.command()
async def talk(ctx, *, msg):
    """
    Converse with the bot!
    The bot will remember you to the best of its abilities.
    """
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
            date = shortTermMemory[-2]["parts"][0][0:10].split("-")
            time = shortTermMemory[-2]["parts"][0][11:19].split(":")
            time_difference = datetime.datetime.now() - datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))

            if time_difference > datetime.timedelta(hours=1):

                construct = "The following is a conversation between a chatbot and a user. Summarize the interaction briefly.\n"

                for i in shortTermMemory:
                    construct += i["parts"][0]
                    construct += "\n"
                
                modelReply = gemrequest(construct)

                if modelReply[0] == False:
                    await ctx.send("something went wrong: "+modelReply[1])
                    return
                else:#append summary to long term memory
                    with open("ltmemories/"+usr+".txt", "a", encoding="utf-8") as mem:
                        mem.write(str(datetime.datetime.today)+": "+modelReply[1])
                        
                    with open("stmemories/"+usr+".json", "w", encoding="utf-8") as mem:
                        mem.write("")
                        shortTermMemory = ""

        

    async with ctx.typing():
        construct = []
        if shortTermMemory == "":
            construct.append({'role':'user','parts': ["You are a helpful assistant, helping a user named " + usr + ". These are summaries of your previous conversations with the user for context: " + longTermMemory+"\n Do not include a timestamp in your reply."]})
        else:
            construct = shortTermMemory

        construct.append({'role':'user',
        'parts': [str(datetime.datetime.now()) + ": " + msg]})

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

@bot.command()
async def transcribe(ctx):
    """
    Transcribes audio files with Whisper.
    Cannot transcribe long files! (A few seconds ~ tens of seconds is fine)
    """

    async with ctx.typing():

        attachments = ctx.message.attachments

        if len(attachments) == 0:
            await ctx.send("I'll try to parse through a few previous messages to find what file you want transcribed...")
            channel = ctx.channel
            try:
                messages = [message async for message in channel.history(limit=3)]
            except discord.HTTPException as e:
                await ctx.send(f"An error occurred: {e}")
                return

            for message in messages:
                if len(message.attachments) != 0:
                    attachments += message.attachments
            
            if len(attachments) == 0:
                await ctx.send("I was unable to find an audio file to transcribe. Please try again.")
                return
                
        sendText = ""

        for i in attachments:
            try:
                if not (str(i.content_type).split("/")[0] == "audio" ):
                    continue
                sendText += i.filename + "\n"
                sendText += "> " + whispercf.cfwhisper(i.url)["result"]["text"] + "\n"
            except:
                await ctx.send("Sorry, something went wrong while trying to transcribe file: " + i.filename)
        
        await ctx.send(sendText)

@bot.command()
async def ytdlAudio(ctx, msg):
    """
    Uses yt-dlp to download audio.
    """

    async with ctx.typing():
        url = URLExtract().find_urls(msg)[0]
        
        subprocess.run(["yt-dlp","-x","-o","video",url])

        localconverters.ffmpeg("video.opus","mp3")

        await ctx.channel.send(file=discord.File("video.mp3"))

        Path.unlink(Path("video.opus"))
        Path.unlink(Path("video.mp3"))

@bot.command()
async def convert(ctx, msg):
    """
    Converts media files with ffmpeg or imagemagick.
    Will look for the first file's type and choose a converter.
    """

    async with ctx.typing():
        attachments = ctx.message.attachments

        if len(attachments) == 0:
            await ctx.send("You need to send me a file to convert!")
            return
        
        typ = attachments[0].content_type.split("/")[0]

        if typ == "image":
            conv = localconverters.imagemagick
        elif typ == "video":
            conv = localconverters.ffmpeg
        elif typ == "audio":
            conv = localconverters.ffmpeg
        else:
            await ctx.send("I can only convert things supported by ffmpeg or imagemagick!")
            return

        listnewfiles = []
        listoldfiles = []
        listnewfilenames = []

        for i in attachments:
            filename = i.filename
            await i.save(fp=filename)
            listoldfiles.append(filename)
            conv(filename,msg)
            splitname = filename.split(".")

            noext = ""

            for i in range(len(splitname)-1):
                noext += splitname[i]

            newfilename = noext+"."+msg

            print(newfilename)

            listnewfiles.append(discord.File(newfilename))
            listnewfilenames.append(newfilename)
        
        await ctx.channel.send(files=listnewfiles)

        #Clean up the downloaded and converted files
        for i in listoldfiles:
            Path.unlink(Path(i))
        for j in listnewfilenames:
            Path.unlink(Path(j))

@bot.command()
async def ffmpeg(ctx, msg):
    """
    Converts media files with ffmpeg.
    """

    async with ctx.typing():
        attachments = ctx.message.attachments

        if len(attachments) == 0:
            await ctx.send("I'll try to parse through a few previous messages to find what file you want to convert...")
            channel = ctx.channel
            try:
                messages = [message async for message in channel.history(limit=3)]
            except discord.HTTPException as e:
                await ctx.send(f"An error occurred: {e}")
                return

            for message in messages:
                if len(message.attachments) != 0:
                    attachments += message.attachments
            
            if len(attachments) == 0:
                await ctx.send("I was unable to find a file to convert. Please try again.")
                return
        
        filesToSend = []
        filesToUnlink = []

        for i in attachments:
            filename = i.filename
            await i.save(fp=filename)
            localconverters.ffmpeg(filename,msg)
            filesToUnlink.append(Path(filename))
            splitname = filename.split(".")

            noext = ""

            for i in range(len(splitname)-1):
                noext += splitname[i]

            newfilename = noext+"."+msg
            filesToSend.append(discord.File(newfilename))
            filesToUnlink.append(Path(newfilename))
        
        await ctx.send(files=filesToSend)

        for i in filesToUnlink:
            Path.unlink(i)

@bot.command()
async def magick(ctx, msg):
    """
    Converts media files with imagemagick.
    """

    async with ctx.typing():
        attachments = ctx.message.attachments

        if len(attachments) == 0:
            await ctx.send("I'll try to parse through a few previous messages to find what file you want to convert...")
            channel = ctx.channel
            try:
                messages = [message async for message in channel.history(limit=3)]
            except discord.HTTPException as e:
                await ctx.send(f"An error occurred: {e}")
                return

            for message in messages:
                if len(message.attachments) != 0:
                    attachments += message.attachments
            
            if len(attachments) == 0:
                await ctx.send("I was unable to find a file to convert. Please try again.")
                return
        
        filesToSend = []
        filesToUnlink = []

        for i in attachments:
            filename = i.filename
            await i.save(fp=filename)
            localconverters.imagemagick(filename,msg)
            filesToUnlink.append(Path(filename))
            splitname = filename.split(".")

            noext = ""

            for i in range(len(splitname)-1):
                noext += splitname[i]

            newfilename = noext+"."+msg
            filesToSend.append(discord.File(newfilename))
            filesToUnlink.append(Path(newfilename))
        
        await ctx.send(files=filesToSend)

        for i in filesToUnlink:
            Path.unlink(i)

@bot.command()
async def urlscan(ctx, msg):
    """
    Scan a URL with Cloudflare Radar.
    """
    async with ctx.typing():

        url = URLExtract.find_urls(msg)[0]

        if url[-1] == "/":
                    url = url[0:-1]
        print(url)
        scanResults = urlScan(url)
        try:
            verdict, timeMade = scanResults
            if verdict["malicious"]:
                await ctx.channel.send("The URL is likely malicious, catergorized as "+str(verdict["categories"])+". The report was made on "+timeMade+". Do NOT access the webpage for your own safety.")
            else:
                await ctx.channel.send("The URL is likely safe. The report was made on "+timeMade+".")
        except:
            await ctx.channel.send("I've sent a request to scan the URL. The report should be available at https://radar.cloudflare.com/scan/"+scanResults+" in a few minutes. Check here, or run this command again!")

@bot.command()
async def qrscan(ctx):
    """
    Scan a QR code embedded within an image.
    """
    async with ctx.typing():

        attachments = ctx.message.attachments

        if len(attachments) == 0:
            await ctx.send("I'll try to parse through a few previous messages to find what file you want to scan...")
            channel = ctx.channel
            try:
                messages = [message async for message in channel.history(limit=5)]
            except discord.HTTPException as e:
                await ctx.send(f"An error occurred: {e}")
                return

            for message in messages:
                if len(message.attachments) != 0:
                    attachments += message.attachments
            
            if len(attachments) == 0:
                await ctx.send("I was unable to find a file to scan. Please try again.")
                return
        
        qreader = QReader()

        sendText = ""

        for i in attachments:
            try:
                filename = i.filename
                await i.save(fp=filename)
                image = cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2RGB)
                decoded_text = qreader.detect_and_decode(image=image)

                if len(decoded_text) == 0:
                    sendText += "QR code not found for file: "+filename+"\n"
                
                else:
                    
                    sendText += "> "+filename+"\n"

                    for j in decoded_text:
                        sendText += j + "\n"
                
                Path.unlink(Path(filename))

            except:
                sendText += "Error occured while processing file: "+filename+"\n"

        await ctx.send(sendText)



@bot.command()
async def publish(ctx):
    """
    Publish a txt file as a webpage for easier viewing on mobile.
    (Warn: the file will be public. Share URLs at your own risk.)
    """
    async with ctx.typing():
        if len(attachments) == 0:
            await ctx.send("I'll try to parse through a few previous messages to find what file you want to use...")
            channel = ctx.channel
            try:
                messages = [message async for message in channel.history(limit=5)]
            except discord.HTTPException as e:
                await ctx.send(f"An error occurred: {e}")
                return

            for message in messages:
                if len(message.attachments) != 0:
                    attachments = message.attachments
                    break
            
            if len(attachments) == 0:
                await ctx.send("I was unable to find a text file to publish. Please try again.")
                return

        for i in attachments:

            filename = i.filename

            await i.save(fp=filename)
            
            with open(filename, "r", encoding="UTF-8") as txtfile:
                htmlLoc = makePage(txtfile.readlines(), description="Automatically generated page from "+filename)
            
            link = uploadFileToCloud(htmlLoc, "webpage/")

            Path.unlink(Path(filename))
            Path.unlink(Path(htmlLoc))
            
            await ctx.send(link)

@bot.command()
async def makeqr(ctx, *, msg):
    """
    Make a QR code from provided text.
    """
    async with ctx.typing():
        img = qrcode.make(msg)
        img.save("qrcode.png")

        localconverters.imagemagick("qrcode.png", "webp")

        await ctx.send(file=discord.File("qrcode.webp"))

        Path.unlink(Path("qrcode.png"))
        Path.unlink(Path("qrcode.webp"))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

bot.run(os.getenv("DISCORD_BOT_TOKEN"))