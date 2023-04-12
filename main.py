import discord
from discord.ext import commands
from datetime import datetime, timedelta

# Put your bot token here:
TOKEN = "MTA5NTc5NDE4MDA0NDg4MjA4Mg.GCZRfu.x7OhE1qkstqgitYMNh3IDKGRSWZopY2PZ34O_s"

print("Starting bot...")
# Set up the bot client
bot = commands.Bot(command_prefix='!')

# Example command
@bot.command()
async def ping(ctx):
    print("Pong!")
    await ctx.send('Pong!')

# Another example command
@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.mention}!')

# Command to send message to specified channel
@bot.command()
async def send(ctx, channel_id: int, *, message):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(message)
    else:
        await ctx.send(f"Channel with ID {channel_id} not found.")

# Run the bot
bot.run(TOKEN)
