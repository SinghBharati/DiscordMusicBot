import discord
from discord.ext import commands,tasks
import youtube_dl   #  it is a commandline ptogram use to download videos from youtube
from random import choice

youtube_dl.utils.bug_reports_message = lambda: 'I think something is wrong. '   # this gives a message if there is a bug

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {          #  This convert video to audio
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=10):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')


    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        import asyncio
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

client=commands.Bot(command_prefix='?')

status=["Jamming out to music!","Eating!","Sleeping!"]

@client.event
async  def on_ready():
    change_status.start()
    print("Bot is online!")

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Welcome {member.mention}!  Ready to jam out? See `?help` command for details!')

@client.command(name="ping",help="This command returns the latency")
async def ping(ctx):
    await ctx.send(f"**pong!**  Latenct: {round(client.latency*100)}ms")

@client.command(name="hello",help="This command returns a random welcome message")
async def hello(ctx):
    response=["***How was your day?☺*** ","Hey buddy!!!","Hello, how are you?","Hi","**Whats up!**"]
    await ctx.send(choice(response))

@client.command(name='play', help='This command plays songs')
async def play(ctx,url):
    await ctx.send(f"**Playing....** ")
    if not ctx.message.author.voice:
        await  ctx.send("You are not connected to a voice channel!")
        return
    else:
        channel=ctx.message.author.voice.channel
    await channel.connect()

    server=ctx.message.guild
    voice_channel = server.voice_client
    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))


@client.command(name='stop', help='This command stops the song!')
async def stop(ctx):
    await ctx.send("**Stoped...Hope you enjoyed ☺** ")
    voice_client=ctx.message.guild.voice_client
    await  voice_client.disconnect()


@tasks.loop(seconds=20)
async def change_status():
    await  client.change_presence(activity=discord.Game(choice(status)))

client.run("bottoken")




