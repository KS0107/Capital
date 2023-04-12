from asyncio import tasks
import random
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import matplotlib.pyplot as plt
import io, time

# Put your bot token here:
TOKEN = "MTA5NTc5NDE4MDA0NDg4MjA4Mg.GCZRfu.x7OhE1qkstqgitYMNh3IDKGRSWZopY2PZ34O_s"

print("Starting bot...")
# Set up the bot client
bot = commands.Bot(command_prefix='@')

# Example command
@bot.command()
async def ping(ctx):
    start_time = time.monotonic()
    message = await ctx.send("Pinging...")
    end_time = time.monotonic()
    response_time = (end_time - start_time) * 1000  # Convert to milliseconds

    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latency: {response_time:.2f}ms",
        color=discord.Color.blurple()
    )
    print(f"Ping, Latency: {response_time:.2f}ms")

    await message.edit(content=None, embed=embed)


# Another example command
@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.mention}!')

# Command to send message to specified channel
@bot.command()
async def announce(ctx, channel_id: int, title: str, *, message: str):
    channel = bot.get_channel(channel_id)
    embed = discord.Embed(title=title, description=message, color=discord.Color.blurple())
    await channel.send(embed=embed)



@bot.command()
async def numusers(ctx):
    num_users = len(ctx.guild.members)
    await ctx.send(f'The server has {num_users} members.')
        

@bot.command()
async def activeusers(ctx):
    num_active_users = 0
    for member in ctx.guild.members:
        if member.activity is not None and member.activity.type is discord.ActivityType.playing:
            last_played = member.activity.timestamps.get("start")
            if last_played is not None and datetime.utcnow() - last_played < timedelta(days=30):
                num_active_users += 1
    await ctx.send(f'There are {num_active_users} active users in the last 30 days.')
    
@bot.command()
async def stats(ctx):
    # Get server member count
    member_count = len(ctx.guild.members)
    # Get active member count
    active_members = [m for m in ctx.guild.members if m.activity and m.activity.type != discord.ActivityType.custom and (discord.utils.utcnow() - m.activity.created_at).days < 30]
    active_member_count = len(active_members)
    # Get message statistics
    total_messages = 0
    unique_authors = set()
    for channel in ctx.guild.text_channels:
        async for message in channel.history(limit=None):
            total_messages += 1
            unique_authors.add(message.author.id)
    unique_author_count = len(unique_authors)
    avg_messages_per_author = total_messages / unique_author_count
    # Send the statistics as a message
    await ctx.send(f"Server Statistics:\n"
                   f"Total members: {member_count}\n"
                   f"Active members (in last 30 days): {active_member_count}\n"
                   f"Total messages: {total_messages}\n"
                   f"Unique authors: {unique_author_count}\n"
                   f"Avg. messages per author: {avg_messages_per_author:.2f}")
        
@bot.command()
async def messagestats(ctx):
    total_messages = 0
    message_authors = {}
    message_channels = {}

    async for message in ctx.channel.history(limit=None):
        total_messages += 1
        author = message.author.name
        channel = message.channel.name

        if author not in message_authors:
            message_authors[author] = 1
        else:
            message_authors[author] += 1

        if channel not in message_channels:
            message_channels[channel] = 1
        else:
            message_channels[channel] += 1

    top_authors = sorted(message_authors.items(), key=lambda x: x[1], reverse=True)[:5]
    top_channels = sorted(message_channels.items(), key=lambda x: x[1], reverse=True)[:5]

    # Create a new embedded message
    embed = discord.Embed(title="Message Statistics", color=0x33CAFF)
    embed.add_field(name="Total messages sent", value=total_messages, inline=False)

    # Add a field for each of the top authors
    author_field = ""
    for author, num_messages in top_authors:
        author_field += f"{author}: {num_messages} messages\n"
    embed.add_field(name="Top Authors", value=author_field, inline=False)

    # Add a field for each of the top channels
    channel_field = ""
    for channel, num_messages in top_channels:
        channel_field += f"#{channel}: {num_messages} messages\n"
    embed.add_field(name="Top Channels", value=channel_field, inline=False)

    await ctx.send(embed=embed)
@bot.command()
async def ucg(ctx):
    print("Generating user count graph...")
    await ctx.send("Generating user count graph...")
    user_counts = []

    for i in range(30):
        date = datetime.utcnow() - timedelta(days=i)
        count = sum(1 for member in ctx.guild.members if not member.bot and member.joined_at.date() == date.date())
        user_counts.append(count)

    fig, ax = plt.subplots()
    ax.plot(range(1, 31), user_counts, color='turquoise')
    ax.set(xlabel='Days', ylabel='User Count', title='User Count Over Last 30 Days')
    ax.set_facecolor('#424549')
    ax.grid(color='white')
    ax.tick_params(colors='white')

    # Save the figure to a buffer
    buf = io.BytesIO()
    fig.savefig(buf, format='png', facecolor='#424549')
    buf.seek(0)

    # Create the discord embed
    embed = discord.Embed(title='User Count Over Last 30 Days', color=discord.Color.green())
    file = discord.File(buf, filename='user_count.png')
    embed.set_image(url=f'attachment://user_count.png')

    await ctx.send(file=file, embed=embed)


@bot.command()
async def mcg(ctx):
    print('Generating message count graph...')
    await ctx.send('Generating message count graph...')
    message_counts = []

    for i in range(30):
        date = datetime.utcnow() - timedelta(days=i)
        count = 0

        async for message in ctx.channel.history(limit=None):
            if message.created_at.date() == date.date():
                count += 1

        message_counts.append(count)

    fig, ax = plt.subplots()
    ax.plot(range(1, 31), message_counts, color='turquoise')
    ax.set(xlabel='Days', ylabel='Message Count', title='Message Count Over Last 30 Days')
    ax.set_facecolor('#424549')
    ax.grid(color='white')
    ax.tick_params(colors='white')

    # Save the figure to a buffer
    buf = io.BytesIO()
    fig.savefig(buf, format='png', facecolor='#424549')
    buf.seek(0)

    # Create the discord embed
    embed = discord.Embed(title='Message Count Over Last 30 Days', color=discord.Color.blue())
    file = discord.File(buf, filename='message_count.png')
    embed.set_image(url=f'attachment://message_count.png')

    await ctx.send(file=file, embed=embed)


@bot.command()
async def commandhelp(ctx):
    embed = discord.Embed(
        title="Bot Commands Help",
        description="A brief explanation of every command and its usage.",
        color=discord.Color.blurple()
    )
    embed.add_field(name="ping", value="Tests the bot's latency.", inline=False)
    embed.add_field(name="hello", value="Greets the user.", inline=False)
    embed.add_field(name="announce [channel_id] [title] [message]", value="Sends an announcement to the specified channel with the given title and message.", inline=False)
    embed.add_field(name="numusers", value="Displays the total number of members in the server.", inline=False)
    embed.add_field(name="activeusers", value="Displays the number of active users in the last 30 days.", inline=False)
    embed.add_field(name="stats", value="Displays server statistics, including total members, active members in the last 30 days, total messages, unique authors, and average messages per author.", inline=False)
    embed.add_field(name="messagestats", value="Displays message statistics, including total messages sent, top authors by message count, and top channels by message count.", inline=False)
    embed.add_field(name="ucg", value="Displays a graph of the number of new users who joined the server over the last 30 days.", inline=False)
    embed.add_field(name="mcg", value="Displays a graph of the number of messages sent in the current channel over the last 30 days.", inline=False)

    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    while True:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="video games"))
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="time fly"))
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="commands"))
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the chat closely"))
        await asyncio.sleep(10)



# List of blocked words
blocked_words = ["spam", "scam", "hack"]

# Event listener for message creation
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if message contains blocked words
    for word in blocked_words:
        if word in message.content.lower():
            # Delete message and send warning
            await message.delete()
            await message.channel.send(f"{message.author.mention}, your message was deleted for containing inappropriate language.")

    # Allow other commands to be processed
    await bot.process_commands(message)

# SPAM CHECKER
SPAM_THRESHOLD = 5  # number of messages allowed in the time window
SPAM_TIME = 5      # time window in seconds

user_messages = {}

@bot.event
async def on_message(message):
    # Check if message author is a bot
    if message.author.bot:
        return

    # Check if the user has sent too many messages in a short time span
    author_id = message.author.id
    if author_id in user_messages:
        user_messages[author_id].append(time.time())
        if len(user_messages[author_id]) > SPAM_THRESHOLD:
            if user_messages[author_id][-1] - user_messages[author_id][0] < SPAM_TIME:
                await message.channel.send(f"{message.author.mention} please don't spam!")
                user_messages[author_id] = []
                return
            else:
                user_messages[author_id] = user_messages[author_id][-SPAM_THRESHOLD:]
    else:
        user_messages[author_id] = [time.time()]

    # Process the message normally if it's not spam
    await bot.process_commands(message)
    
    
@bot.command()
@commands.has_role("Mod")
async def manage(ctx, action, user_id:int, *, reason):
    guild = ctx.guild
    user = await bot.fetch_user(user_id)
    if action == 'kick':
        embed = discord.Embed(title=f"You have been kicked from {guild.name}!", description=f"Reason: {reason}", color=0xff5733)
        await user.send(embed=embed)
        await guild.kick(user, reason=reason)
        
    elif action == 'ban':
        embed = discord.Embed(title=f"You have been banned from {guild.name}!", description=f"Reason: {reason}", color=0xff5733)
        await user.send(embed=embed)
        await guild.ban(user, reason=reason)
    else:
        await ctx.send("Invalid action. Please enter either 'kick' or 'ban' as the first argument.")
        return
    
# Run the bot
bot.run(TOKEN)
