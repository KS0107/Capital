import asyncio
import random, math
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import matplotlib.pyplot as plt
import io, time, sqlite3
from collections import defaultdict
from discord import Emoji

# Put your bot token here:
TOKEN = "MTA5NTc5NDE4MDA0NDg4MjA4Mg.GUIGRk.ypvplVYNUc5XEmzytozgrNOKrX0kNhRCwXqDgI"
print("Starting bot...")
print("Passing token", TOKEN)
# Set up the bot client
intents = discord.Intents.all()  # Include all the intents
bot = commands.Bot(command_prefix='^', intents=intents)


@bot.command()
async def ping(ctx):
  start_time = time.monotonic()
  message = await ctx.send("Pinging...")
  end_time = time.monotonic()
  response_time = (end_time - start_time) * 1000  # Convert to milliseconds

  embed = discord.Embed(title="🏓 Pong!",
                        description=f"Latency: {response_time:.2f}ms",
                        color=discord.Color.blurple())
  print(f"Ping, Latency: {response_time:.2f}ms")

  await message.edit(content=None, embed=embed)
  
# Connect to the database
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create a table to store user information
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, name TEXT, points INTEGER)''')
conn.commit()


@bot.command()
async def addpoints(ctx, user: discord.Member, points: int):
    # Check if user already exists in the database
    c.execute('SELECT * FROM users WHERE id=?', (user.id,))
    row = c.fetchone()
    if row:
        # Update user's points
        c.execute('UPDATE users SET points=? WHERE id=?', (row[2] + points, user.id))
    else:
        # Add new user to the database
        c.execute('INSERT INTO users VALUES (?, ?, ?)', (user.id, user.name, points))
    conn.commit()
    await ctx.send(f'{points} points added to {user.name}!')


@bot.command()
async def showpoints(ctx):
    c.execute('SELECT * FROM users WHERE id=?', (ctx.author.id,))
    row = c.fetchone()
    if row:
        await ctx.send(f'You have {row[2]} points.')
    else:
        await ctx.send('You have 0 points.')
        


@bot.command()
async def topusers(ctx):
    c.execute('SELECT * FROM users ORDER BY points DESC LIMIT 10')
    rows = c.fetchall()
    if rows:
        embed = discord.Embed(title='Top Users', color=0xffd700)
        for i, row in enumerate(rows):
            embed.add_field(name=f'{i+1}. {row[1]}', value=f'{row[2]} points', inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send('No users found.')
        
@bot.command()
async def helpdice(ctx):
    embed = discord.Embed(title="🎲 Dice Rolling Game",
                          description="Welcome to the dice rolling game! Here's how it works:\n\n\
                          • You can roll a six-sided die and win points based on the outcome.\n\
                          • The higher the number you roll, the more points you can win.\n\
                          • However, the higher the multiplier you choose, the lower the chance of winning.\n\n\
                          To play, type `^roll_dice <wager> <multiplier>`.\n\
                          For example, if you want to wager 10 points and set the multiplier to 5, type `^roll_dice 10 5`.\n\n\
                          Good luck and have fun!",
                          color=discord.Color.blurple())
    await ctx.send(embed=embed)

@bot.command()
async def roll(ctx, wager: int, multiplier: int):
    # Check if multiplier is between 1 and 10
    if not 1 <= multiplier <= 10:
        await ctx.send('Multiplier should be between 1 and 10.')
        return

    # Check if user has enough points to place the wager
    c.execute('SELECT * FROM users WHERE id=?', (ctx.author.id,))
    row = c.fetchone()
    if not row or row[2] < wager:
        await ctx.send(f'You do not have enough points to place a wager of {wager} points.')
        return

    # Calculate the odds of winning based on the multiplier
    win_odds = 1 / multiplier

    # Roll the dice and determine the outcome based on the roll and the win odds
    roll = random.random()
    if roll < win_odds:
        outcome = f'You won {multiplier * wager} points!'
        winnings = multiplier * wager
    else:
        outcome = 'You lost the wager.'
        winnings = -wager

    # Update the user's points and send the outcome message
    c.execute('UPDATE users SET points=? WHERE id=?', (row[2] + winnings, ctx.author.id))
    conn.commit()

    # Create an embed to display the outcome
    embed = discord.Embed(title='Roll Result', color=0xffd500)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url='https://www.freepnglogos.com/uploads/dice-png/dice-transparent-png-pictures-icons-and-png-backgrounds-0.png')

    # Add fields to the embed to show the outcome, the roll result and the winning odds
    embed.add_field(name='Outcome', value=outcome, inline=False)
    embed.add_field(name='Roll Result', value=f'{round(roll*6)+1}/6', inline=False)
    embed.add_field(name='Winning Odds', value=f'1 in {multiplier:.0f}', inline=False)
    embed.add_field(name='Previous Balance', value=f'{row[2]:,}', inline=True)
    embed.add_field(name='Current Balance', value=f'{row[2] + winnings:,}', inline=True)

    await ctx.send(embed=embed)
# Close the database connection when the bot is stopped
@bot.event
async def on_bot_disconnect():
    conn.close()
    
@bot.command()
async def pick(ctx):
    """Pick up any dropped coins in chat."""
    c.execute('SELECT * FROM users WHERE id=?', (ctx.author.id,))
    row = c.fetchone()
    if not row:
        await ctx.send('You do not have any points yet.')
        return

    # Check if there are any dropped coins available to pick up
    if not dropped_coins:
        await ctx.send('There are no dropped coins at the moment.')
        return

    # Pick up a random dropped coin
    dropped_coin = random.choice(dropped_coins)
    c.execute('UPDATE users SET points=? WHERE id=?', (row[2] + dropped_coin, ctx.author.id))
    conn.commit()

    # Remove the picked up coin from the list of dropped coins
    dropped_coins.remove(dropped_coin)

    # Send the success message
    await ctx.send(f"You picked up {dropped_coin} points! You now have {row[2] + dropped_coin} points.")

async def drop_coins():
    """Drop coins in chat at random times of the day."""
    while True:
        # Wait for a random amount of time between 1 and 3 hours
        await asyncio.sleep(random.randint(3600, 10800))

        # Drop a random amount of coins between 300 and 1000
        dropped_coin = random.randint(300, 1000)
        dropped_coins.append(dropped_coin)

        # Loop through every guild the bot is a member of
        for guild in bot.guilds:
            # Loop through every text channel in the guild
            for channel in guild.text_channels:
                # Send the dropped coin message in chat
                await channel.send(f'A coin worth {dropped_coin} points has been dropped in chat in {guild.name}! Type "^pick" to claim it.')


# Initialize the list of dropped coins
dropped_coins = []

# Start the drop coins loop as a background task
bot.loop.create_task(drop_coins())
    
############################################################################################################


@bot.command()
async def hello(ctx):
  await ctx.send(f'Hello, {ctx.author.mention}!')


# Command to send message to specified channel
@bot.command()
async def announce(ctx, channel_id: int, title: str, *, message: str):
  channel = bot.get_channel(channel_id)
  embed = discord.Embed(title=title,
                        description=message,
                        color=discord.Color.blurple())
  await channel.send(embed=embed)


@bot.command()
async def send(ctx, channel_id: int, *, message: str):
  channel = bot.get_channel(channel_id)
  await channel.send(message)


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
      if last_played is not None and datetime.utcnow(
      ) - last_played < timedelta(days=30):
        num_active_users += 1
  await ctx.send(
    f'There are {num_active_users} active users in the last 30 days.')


@bot.command()
async def stats(ctx):
  # Get server member count
  member_count = len(ctx.guild.members)
  # Get active member count
  active_members = [
    m for m in ctx.guild.members
    if m.activity and m.activity.type != discord.ActivityType.custom and
    (discord.utils.utcnow() - m.activity.created_at).days < 30
  ]
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

  top_authors = sorted(message_authors.items(),
                       key=lambda x: x[1],
                       reverse=True)[:5]
  top_channels = sorted(message_channels.items(),
                        key=lambda x: x[1],
                        reverse=True)[:5]

  # Create a new embedded message
  embed = discord.Embed(title="Message Statistics", color=0x33CAFF)
  embed.add_field(name="Total messages sent",
                  value=total_messages,
                  inline=False)

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

  for i in reversed(range(30)):
    date = datetime.utcnow() - timedelta(days=i)
    count = sum(1 for member in ctx.guild.members if not member.bot and member.joined_at.date() <= date.date())
    user_counts.append(count)

  fig, ax = plt.subplots()
  ax.plot(range(30, 0, -1), user_counts[::-1], color='turquoise')
  ax.set(xlabel='Days',
         ylabel='User Count',
         title='User Count Over Last 30 Days')
  ax.set_facecolor('#424549')
  ax.grid(color='white')
  ax.tick_params(colors='white')
  ax.invert_xaxis()

  # Save the figure to a buffer
  buf = io.BytesIO()
  fig.savefig(buf, format='png', facecolor='#424549')
  buf.seek(0)

  # Create the discord embed
  embed = discord.Embed(title='User Count Over Last 30 Days',
                        color=discord.Color.blurple())
  file = discord.File(buf, filename='user_count.png')
  embed.set_image(url=f'attachment://user_count.png')

  await ctx.send(file=file, embed=embed)


@bot.command()
async def mcg(ctx):
    print('Generating message count graph...')
    await ctx.send('Generating message count graph...')
    message_counts = []

    for i in reversed(range(30)):
        date = datetime.utcnow() - timedelta(days=i)
        count = 0

        for channel in ctx.guild.text_channels:
            print(f'Counting messages in {channel.name}...')
            async for message in channel.history(limit=None):
                if message.created_at.date() == date.date():
                    count += 1

        message_counts.append(count)

    fig, ax = plt.subplots()
    ax.plot(range(30, 0, -1), message_counts[::-1], color='turquoise')
    ax.set(xlabel='Days',
            ylabel='Message Count',
            title='Message Count Over Last 30 Days')
    ax.set_facecolor('#424549')
    ax.grid(color='white')
    ax.tick_params(colors='white')
    ax.invert_xaxis()

    # Save the figure to a buffer
    buf = io.BytesIO()
    fig.savefig(buf, format='png', facecolor='#424549')
    buf.seek(0)

    # Create the discord embed
    embed = discord.Embed(title='Message Count Over Last 30 Days',
                        color=discord.Color.blue())
    file = discord.File(buf, filename='message_count.png')
    embed.set_image(url=f'attachment://message_count.png')

    await ctx.send(file=file, embed=embed)



@bot.command()
async def commandhelp(ctx, cmd: str = None):
    if cmd is None:
        embed = discord.Embed(title="Bot Commands", color=discord.Color.blurple())
        embed.add_field(name="^hello", value="Greets the user who sent the command", inline=False)
        embed.add_field(name="^announce <channel_id> <title> <message>", value="Sends an announcement message to the specified channel with the given title and message", inline=False)
        embed.add_field(name="^numusers", value="Shows the total number of members in the server", inline=False)
        embed.add_field(name="^activeusers", value="Shows the number of active users in the last 30 days", inline=False)
        embed.add_field(name="^stats", value="Shows statistics about the server, such as total members, active members, total messages, unique authors, and average messages per author", inline=False)
        embed.add_field(name="^messagestats", value="Shows statistics about the messages in the current channel, such as total messages sent, top authors, and top channels", inline=False)
        embed.add_field(name="^ucg", value="Generates a graph of the user count over the last 30 days", inline=False)
        await ctx.send(embed=embed)
    else:
        if cmd == "hello":
            await ctx.send("Greets the user who sent the command")
        elif cmd == "announce":
            await ctx.send("Sends an announcement message to the specified channel with the given title and message. Usage: ^announce <channel_id> <title> <message>")
        elif cmd == "send":
            await ctx.send("Sends a message to the specified channel. Usage: ^send <channel_id> <message>")
        elif cmd == "numusers":
            await ctx.send("Shows the total number of members in the server")
        elif cmd == "activeusers":
            await ctx.send("Shows the number of active users in the last 30 days")
        elif cmd == "stats":
            await ctx.send("Shows statistics about the server, such as total members, active members, total messages, unique authors, and average messages per author")
        elif cmd == "messagestats":
            await ctx.send("Shows statistics about the messages in the current channel, such as total messages sent, top authors, and top channels")
        elif cmd == "ucg":
            await ctx.send("Generates a graph of the user count over the last 30 days")
        else:
            await ctx.send(f"Invalid command '{cmd}'")



@bot.event
async def on_ready():
  while True:
    await bot.change_presence(activity=discord.Activity(
      type=discord.ActivityType.playing, name="video games"))
    await asyncio.sleep(10)
    await bot.change_presence(activity=discord.Activity(
      type=discord.ActivityType.watching, name="time fly"))
    await asyncio.sleep(10)
    await bot.change_presence(activity=discord.Activity(
      type=discord.ActivityType.listening, name="commands"))
    await asyncio.sleep(10)
    await bot.change_presence(activity=discord.Activity(
      type=discord.ActivityType.watching, name="the chat closely"))
    await asyncio.sleep(10)


# List of blocked words
blocked_words = ["retard", "shit", "fuck","cunt"]


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
      await message.channel.send(
        f"{message.author.mention}, your message was deleted for containing inappropriate language."
      )

  # Allow other commands to be processed
  await bot.process_commands(message)


# SPAM CHECKER
SPAM_THRESHOLD = 5  # number of messages allowed in the time window
SPAM_TIME = 5  # time window in seconds

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
        await message.channel.send(
          f"{message.author.mention} please don't spam!")
        user_messages[author_id] = []
        return
      else:
        user_messages[author_id] = user_messages[author_id][-SPAM_THRESHOLD:]
  else:
    user_messages[author_id] = [time.time()]

  # Process the message normally if it's not spam
  await bot.process_commands(message)


# Moderation commands

@bot.command()
@commands.has_role("Mod")
async def manage(ctx, action, user_id: int, *, reason):
  guild = ctx.guild
  user = await bot.fetch_user(user_id)
  if action == 'kick':
    embed = discord.Embed(title=f"You have been kicked from {guild.name}!",
                          description=f"Reason: {reason}",
                          color=0xff5733)
    await user.send(embed=embed)
    await guild.kick(user, reason=reason)

  elif action == 'ban':
    embed = discord.Embed(title=f"You have been banned from {guild.name}!",
                          description=f"Reason: {reason}",
                          color=0xff5733)
    await user.send(embed=embed)
    await guild.ban(user, reason=reason)
  else:
    await ctx.send(
      "Invalid action. Please enter either 'kick' or 'ban' as the first argument."
    )
    return

@bot.command()
@commands.has_role("Mod")
async def timeout(ctx, member: discord.Member, time: int):
    await member.edit(mute=True)
    await ctx.send(f"{member.display_name} has been muted for {time} minutes.")
    await asyncio.sleep(time * 60)
    await member.edit(mute=False)
    await ctx.send(f"{member.display_name} has been unmuted.")

@bot.command()
async def purge(ctx, num_messages: int):
    if num_messages <= 0:
        await ctx.send('Please provide a positive integer for the number of messages to delete.')
        return

    await ctx.channel.purge(limit=num_messages+2)
    await ctx.send(f'Deleted the last {num_messages} messages.')


@bot.command()
async def poll(ctx, channel_id: int, title: str, *, options: str):
    channel = bot.get_channel(channel_id)
    embed = discord.Embed(title=title,
                          description=options,
                          color=discord.Color.blurple())
    message = await channel.send(embed=embed)

    reactions = ['✅', '❌']
    for reaction in reactions:
        await message.add_reaction(reaction)

    votes = {'✅': 0, '❌': 0}

    def check(reaction, user):
        return user != bot.user and str(reaction.emoji) in reactions and reaction.message.id == message.id

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', check=check)
        except:
            break
        else:
            votes[str(reaction.emoji)] += 1
            await message.edit(embed=discord.Embed(title=title, 
                                                   description=options + '\n\n' + f"✅: {votes['✅']} ❌: {votes['❌']}",
                                                   color=discord.Color.blurple()))


@bot.command()
async def teams(ctx, *, members: str):
    members = members.replace(" ", "")  # remove spaces
    members = members.split(';')  # split into list
    random.shuffle(members)  # shuffle list
    num_members = len(members)
    team_size = (num_members + 1) // 2  # calculate team size
    teams = [members[i:i+team_size] for i in range(0, num_members, team_size)]
    
    for i, team in enumerate(teams):
        team_embed = discord.Embed(title=f"Team {i+1}", description=", ".join(team), color=discord.Color.blue() if i == 0 else discord.Color.red())
        await ctx.send(embed=team_embed)


@bot.command()
async def playaudio(ctx, channel_id: int):
    # check if user is in a voice channel
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to use this command!")
        return

    # get the voice channel by ID
    voice_channel = bot.get_channel(channel_id)
    if not voice_channel:
        await ctx.send("Invalid voice channel ID!")
        return

    # join the voice channel
    vc = await voice_channel.connect()

    # play the mp3 file
    vc.play(discord.FFmpegPCMAudio('fart-tiktok.mp3'))
    print("Playing audio...")
    # wait for the audio to finish playing
    while vc.is_playing():
        print("Audio is playing...")
        await asyncio.sleep(1)

    # disconnect from the voice channel
    await vc.disconnect()
    
@bot.command()
async def giveaway(ctx, time: int, *, prize: str):
    embed = discord.Embed(title="🎉 GIVEAWAY 🎉",
                          description=f"React with 🎉 to enter the giveaway for {prize}!",
                          color=discord.Color.blurple())
    if ctx.message.attachments:
        image_url = ctx.message.attachments[0].url
        embed.set_image(url=image_url)
    embed.set_footer(text=f"Giveaway ends in {time} seconds. React with 🎉 to enter!")
    message = await ctx.send(embed=embed)
    await message.add_reaction("🎉")

    await asyncio.sleep(time)

    message = await ctx.channel.fetch_message(message.id)
    reaction = discord.utils.get(message.reactions, emoji="🎉")
    if reaction and reaction.count > 1:
        users = await reaction.users().flatten()
        users.remove(bot.user)
        winner = random.choice(users)
        await ctx.send(f"Congratulations {winner.mention}! You won the {prize}!")
    else:
        await ctx.send("Sorry, there are not enough participants for the giveaway.") 

@bot.command()
async def drink(ctx, amount):
    try:
        total_amount = float(amount)
        if total_amount <= 0:
            await ctx.send("Please enter a valid amount of water to drink.")
            return
    except ValueError:
        await ctx.send("Please enter a valid amount of water to drink.")
        return

    water_per_hour = total_amount / 12
    reminder_interval = 3600 // 12 # interval is constant
    reminders = []

    for i in range(1, 13):
        reminder_time = reminder_interval * i
        reminder_amount = round(water_per_hour, 2)
        reminders.append((reminder_time, reminder_amount))
        total_amount -= reminder_amount
    print(reminders)
    await ctx.send(f"You need to drink {amount} liters of water in the next 12 hours.")
    await asyncio.sleep(reminder_interval)

    for reminder in reminders:
        await ctx.send(f"**Reminder:** Drink {reminder[1]}L of water.")
        await asyncio.sleep(reminder_interval)

    await ctx.send("You've reached your goal for the day! Good job!")

@bot.command()
async def assign_roles(ctx, *, title):
    embed = discord.Embed(title=title, color=0x00ff00)
    embed.add_field(name="React with 🔵 for CSGO role.", value="React with 🔴 for Fortnite role.")

    msg = await ctx.send(embed=embed)
    await msg.add_reaction('🔵')
    await msg.add_reaction('🔴')

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if str(reaction.emoji) == '🔵':
        role = discord.utils.get(reaction.message.guild.roles, name="CSGO")
        await user.add_roles(role)
    elif str(reaction.emoji) == '🔴':
        role = discord.utils.get(reaction.message.guild.roles, name="Fortnite")
        await user.add_roles(role)



# Run the bot
bot.run(TOKEN)
