import discord
from discord.ext import commands
import requests
import random
import json
import imageio
import io
import os
from PIL import Image, ImageDraw, ImageFont
import youtube_dl

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.messages = True

# Create a new bot instance with intents and the / prefix
bot = commands.Bot(command_prefix='/', intents=intents,
                   help_command=None)  # Disable default help command


# Event: When the bot is ready and connected to the server
@bot.event
async def on_ready():
  print(f'Logged in as {bot.user.name} ({bot.user.id})')


# Command: Ping
@bot.command()
async def ping(ctx):
  latency = bot.latency
  await ctx.send(f'Pong! Latency: {round(latency * 1000)}ms')


# Add more commands and events as needed




@bot.command()
async def help(ctx, command_name=None):
  creator = "Shareef Pathan"
  if command_name is None:
    # Display general help message with list of commands
    help_embed = discord.Embed(
      title="Bot ki Commands",
      description="Koi bhi command run karne kailiye uske pehle / likhen")
    for command in bot.commands:
      help_embed.add_field(name=command.name, value=command.help, inline=False)
    await ctx.send(embed=help_embed)
  else:
    # Display specific help message for a command
    command = bot.get_command(command_name)
    if command is not None:
      help_embed = discord.Embed(title=f"Help: {command.name}",
                                 description=command.help)
      await ctx.send(embed=help_embed)
    else:
      await ctx.send("Command mojood nahi.")


# Add more commands and events as needed
@bot.command()
async def joke(ctx):
  # Fetch a random joke from the JokeAPI
  response = requests.get("https://official-joke-api.appspot.com/random_joke")
  if response.status_code == 200:
    joke_data = response.json()
    await ctx.send(f"**{joke_data['setup']}**\n{joke_data['punchline']}")
  else:
    await ctx.send("Koi Error Agya Contact Shareef Pathan")


async def on_member_join(member):
  welcome_channel = discord.utils.get(
    member.guild.text_channels,
    name="welcome")  # Replace "welcome" with your desired welcome channel name

  if welcome_channel:
    welcome_message = f"Welcome {member.mention} to the server! We're glad to have you here."
    await welcome_channel.send(welcome_message)


# Command to sing a song for the mentioned user
@bot.command()
async def sing_song(ctx, user: discord.Member):
  song = f"🎵 Happy Birthday to {user.mention}! 🎉🎂🎵"
  await ctx.send(song)




@bot.command()
async def convert(ctx, amount: float):
    response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')

    if response.status_code == 200:
        data = response.json()
        exchange_rate = data['rates']['PKR']
        result = amount * exchange_rate
        await ctx.send(f'{amount} USD is equal to {result:.2f} PKR.')
    else:
        await ctx.send('Unable to retrieve the exchange rate. Please try again later.')

# Run the bot with your Discord bot token

# Command to fetch and display a random anime wallpaper
@bot.command()
async def wallpaper(ctx):
    response = requests.get('https://api.unsplash.com/photos/random', params={
        'query': 'anime wallpaper',
        'orientation': 'landscape',
        'w': '3840',
        'h': '2160',
        'client_id': '6qiJvFt3STpDFIQ2SI2YpP6gnQw-w34h2DykF0ropZE'
    })

    if response.status_code == 200:
        data = response.json()
        image_url = data['urls']['full']
        await ctx.send(image_url)
    else:
        await ctx.send('Unable to fetch the wallpaper. Please try again later.')

# Command to fetch and display a random motivational quote
@bot.command()
async def motivate(ctx):
    response = requests.get('https://api.quotable.io/random')

    if response.status_code == 200:
        data = response.json()
        quote = data['content']
        author = data['author']
        await ctx.send(f'"{quote}" - {author}')
    else:
        await ctx.send('Unable to fetch a motivational quote. Please try again later.')

# Command to play the choice game
@bot.command()
async def play(ctx):
    choices = ['Rock', 'Paper', 'Scissors']
    bot_choice = random.choice(choices)

    def check_winner(player_choice, bot_choice):
        if player_choice == bot_choice:
            return 'It\'s a tie!'
        elif (
            (player_choice == 'Rock' and bot_choice == 'Scissors') or
            (player_choice == 'Paper' and bot_choice == 'Rock') or
            (player_choice == 'Scissors' and bot_choice == 'Paper')
        ):
            return 'You win!'
        else:
            return 'I win!'

    def validate_choice(choice):
        return choice.title() in choices

    await ctx.send('Let\'s play Rock, Paper, Scissors! Please choose one: Rock, Paper, or Scissors.')

    try:
        player_choice_message = await bot.wait_for('message', timeout=10.0, check=lambda message: message.author == ctx.author and validate_choice(message.content))
        player_choice = player_choice_message.content.title()

        winner = check_winner(player_choice, bot_choice)
        await ctx.send(f'You chose: {player_choice}\nI chose: {bot_choice}\n{winner}')
    except TimeoutError:
        await ctx.send('You took too long to make a choice. The game has ended.')


# Load leaderboard data from file
def load_leaderboard():
    try:
        with open('leaderboard.json', 'r') as file:
            leaderboard = json.load(file)
    except FileNotFoundError:
        leaderboard = {}
    return leaderboard

# Save leaderboard data to file
def save_leaderboard(leaderboard):
    with open('leaderboard.json', 'w') as file:
        json.dump(leaderboard, file)

# Event to run when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('Game bot is ready!')

# Command to start the game
@bot.command()
async def start_game(ctx):
    number = random.randint(1, 100)
    await ctx.send('Guess a number between 1 and 100!')

    def check(message):
        return message.author == ctx.author and message.content.isdigit()

    try:
        guess_message = await bot.wait_for('message', timeout=10.0, check=check)
        guess = int(guess_message.content)

        if guess == number:
            leaderboard = load_leaderboard()
            author_id = str(ctx.author.id)
            if author_id not in leaderboard:
                leaderboard[author_id] = 0
            leaderboard[author_id] += 1
            save_leaderboard(leaderboard)

            await ctx.send(f'Congratulations, {ctx.author.name}! You guessed the correct number.')
        else:
            await ctx.send(f'Sorry, {ctx.author.name}. The correct number was {number}. Better luck next time!')
    except TimeoutError:
        await ctx.send('You took too long to make a guess. The game has ended.')

# Command to show the leaderboard
@bot.command()
async def leaderboard(ctx):
    leaderboard = load_leaderboard()
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

    if sorted_leaderboard:
        leaderboard_text = 'Leaderboard:\n'
        for index, (author_id, score) in enumerate(sorted_leaderboard, start=1):
            user = bot.get_user(int(author_id))
            if user:
                leaderboard_text += f'{index}. {user.name} - {score} points\n'
        await ctx.send(leaderboard_text)
    else:
        await ctx.send('No leaderboard data available.')

# Command to delete all messages of a user from the server (admin only)
@bot.command()
@commands.has_permissions(administrator=True)
async def delete_messages(ctx, user: discord.Member):
    await ctx.message.delete()

    def is_user_message(message):
        return message.author == user

    deleted_count = 0
    for channel in ctx.guild.text_channels:
        deleted_messages = await channel.purge(limit=None, check=is_user_message)
        deleted_count += len(deleted_messages)

    await ctx.send(f'Deleted {deleted_count} messages of {user.name} from the entire server.', delete_after=5)

# Error handling for missing permissions
@delete_messages.error
async def delete_messages_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the necessary permissions to use this command.")

# Leaderboard dictionary to store player scores
leaderboard = {}

# Event to run when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('Attack and Defend bot is ready!')

# Command to attack another player
@bot.command()
async def attack(ctx, target: discord.Member):
    if target.id == ctx.author.id:
        await ctx.send("You can't attack yourself!")
        return

    attacker_health = random.randint(50, 100)
    target_health = random.randint(50, 100)

    while attacker_health > 0 and target_health > 0:
        attacker_damage = random.randint(1, 20)
        target_damage = random.randint(1, 20)

        attacker_health -= target_damage
        target_health -= attacker_damage

        await ctx.send(f'{ctx.author.mention} attacked {target.mention} for {attacker_damage} damage. '
                       f'{target.mention} counterattacked for {target_damage} damage.')

    if attacker_health <= 0 and target_health <= 0:
        await ctx.send("It's a draw! Both players have been defeated!")
        update_leaderboard(ctx.author, target, 'draw')
    elif attacker_health <= 0:
        await ctx.send(f'{ctx.author.mention} has been defeated! {target.mention} wins!')
        update_leaderboard(target, ctx.author, 'win')
    else:
        await ctx.send(f'{target.mention} has been defeated! {ctx.author.mention} wins!')
        update_leaderboard(ctx.author, target, 'win')

# Command to defend against an attack
@bot.command()
async def defend(ctx):
    await ctx.send(f'{ctx.author.mention} is defending against an attack!')

# Command to show the leaderboard
@bot.command()
async def leaderboardfight(ctx):
    embed = discord.Embed(title='Game Leaderboard', color=discord.Color.gold())

    if not leaderboard:
        embed.description = 'No data available.'
    else:
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

        for index, (player, score) in enumerate(sorted_leaderboard, start=1):
            embed.add_field(name=f'#{index}: {player}', value=f'Score: {score}', inline=False)

    await ctx.send(embed=embed)

# Function to update the leaderboard
def update_leaderboard(winner, loser, result):
    if winner.id not in leaderboard:
        leaderboard[winner.id] = 0
    if loser.id not in leaderboard:
        leaderboard[loser.id] = 0

    if result == 'win':
        leaderboard[winner.id] += 1
    elif result == 'draw':
        leaderboard[winner.id] += 0.5
        leaderboard[loser.id] += 0.5

# Game variables
count = 0
last_user = None

# Event to run when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('Counting game bot is ready!')

# Command to start the counting game
@bot.command()
async def start_counting(ctx):
    global count, last_user
    count = 0
    last_user = None
    await ctx.send('The counting game has started! The count is at 0. The next number should be 1.')

# Command to submit the next number in the counting game
@bot.command()
async def submit_number(ctx, number: int):
    global count, last_user

    if ctx.author == last_user:
        await ctx.send(f'Sorry, {ctx.author.mention}, you already submitted a number last time!')
        return

    if number != count + 1:
        await ctx.send(f'Sorry, {ctx.author.mention}, the number should be {count + 1}!')
        return

    count = number
    last_user = ctx.author
    await ctx.send(f'{ctx.author.mention} submitted the correct number! The count is now at {count}. The next number should be {count + 1}.')




# Keep alive
from flask import Flask
from threading import Thread

app = Flask(__name__)


# Define a basic route
@app.route('/')
def home():
  return "Bot is online!"


# Run the Flask app
def run():
  app.run(host='0.0.0.0', port=8080)


# Create a function to start the server in a separate thread
def keep_alive():
  server = Thread(target=run)
  server.start()


# Call the keep_alive function in your bot's main code
keep_alive()

bot.run('')
