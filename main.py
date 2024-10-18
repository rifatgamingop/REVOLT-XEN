import discord
import socket
import requests
import asyncio
from discord.ext import commands, tasks

client = commands.Bot(command_prefix="=", self_bot=True)

@client.event
async def on_ready():
    print("SelfBot Is Online")
    print("------------------------")
    print("Prefix is =")

@client.command()
async def spam(ctx, amount: int, *, message):
    await ctx.message.delete()
    for _i in range(amount):
        await ctx.send(f'{message}\n')

@client.command()
async def ping(ctx):
    latency = round(client.latency * 1000)
    await ctx.send(f"Ping: {latency}ms")

@client.command()
async def stream(ctx, *, message):
    await ctx.message.delete()
    stream = discord.Streaming(name=message, url='https://discord.gg/QQS4payKap')
    await client.change_presence(activity=stream)

@client.command()
async def play(ctx, *, message):
    await ctx.message.delete()
    game = discord.Game(name=message)
    await client.change_presence(activity=game)

@client.command()
async def watch(ctx, *, message):
    await ctx.message.delete()  # Delete the command message
    watching = discord.Activity(type=discord.ActivityType.watching, name=message)  # Set the activity to "Watching"
    await client.change_presence(activity=watching)  # Update the bot's presence

auto_react = False
reaction_emoji = None

@client.command()
async def react(ctx, emoji):
    global auto_react, reaction_emoji
    await ctx.message.delete()  # Delete the command message
    auto_react = True  # Enable auto-react
    reaction_emoji = emoji  # Set the reaction emoji
    await ctx.send(f"Auto-react is now ON with {emoji}!", delete_after=5)  # Optional: delete message after 5 seconds

@client.command()
async def stopreact(ctx):
    global auto_react
    await ctx.message.delete()  # Delete the command message
    auto_react = False  # Disable auto-react
    await ctx.send("Auto-react is now OFF!", delete_after=5)  # Optional: delete message after 5 seconds

# Event listener to react to all messages when auto-reaction is enabled
@client.event
async def on_message(message):
    global auto_react, reaction_emoji
    if auto_react and reaction_emoji and message.author == client.user:  # Check if auto-react is enabled and emoji is set
        try:
            await message.add_reaction(reaction_emoji)  # Add the emoji as a reaction
        except discord.errors.InvalidArgument:
            print(f"Invalid emoji: {reaction_emoji}")
    await client.process_commands(message)  # Process other commands

auto_reply = False
opponent = None

@client.command()
async def autoreply(ctx, user: discord.User):
    global auto_reply, opponent
    await ctx.message.delete()  # Delete the command message
    auto_reply = True  # Enable auto-reply
    opponent = user  # Set the opponent
    await ctx.send(f"Auto-reply is now ON for {user.mention}!", delete_after=5)

@client.command()
async def stopreply(ctx):
    global auto_reply, opponent
    await ctx.message.delete()  # Delete the command message
    auto_reply = False  # Disable auto-reply
    opponent = None  # Clear the opponent
    await ctx.send("Auto-reply is now OFF!", delete_after=5)

# Event listener to auto-reply to messages from the opponent
@client.event
async def on_message(message):
    global auto_reply, opponent
    if auto_reply and opponent and message.author == opponent and not message.author.bot:
        # Example auto-replies
        replies = [
            "hey yo u ugly grangky dork ass nigga",
            "ur looking so shit",
            "ong ur lifeless ur a discord crusader alfronzo",
            "alexander fucked ur momma with japanese katana"
        ]
        
        # Send a random auto-reply from the list
        import random
        reply = random.choice(replies)
        await message.channel.send(reply)
    
    await client.process_commands(message)  # Process other commands

# Global variables to manage the loop and group ID
gc_loop_running = False
gc_group = None

@client.command()
async def gc(ctx, group_id: int):
    global gc_loop_running, gc_group
    await ctx.message.delete()  # Delete the command message
    
    # Find the group by ID (group DMs are found in private channels)
    group = client.get_channel(group_id)
    if not isinstance(group, discord.GroupChannel):
        await ctx.send(f"Invalid Group ID: {group_id}. Please provide a valid group DM ID.", delete_after=5)
        return
    
    gc_group = group
    gc_loop_running = True  # Set the loop to start

    await ctx.send(f"Started changing the group name for Group ID: {group_id}", delete_after=5)
    
    # Start the loop task to change the group name
    change_group_name.start()

@tasks.loop(seconds=1)  # Change the group name every 10 seconds (adjust as needed)
async def change_group_name():
    global gc_loop_running, gc_group
    if gc_group and gc_loop_running:
        # List of sample group names to loop through
        names = [
            "Nigga",
            "Get",
            "Fucked",
            "Up",
            "RX",
            "Rule",
            "You"
        ]
        for name in names:
            if not gc_loop_running:
                break  # Exit loop if stop command is issued
            try:
                await gc_group.edit(name=name)  # Change the group name
                print(f"Changed group name to: {name}")
                await asyncio.sleep(1)  # Wait for 10 seconds before changing again
            except discord.Forbidden:
                print(f"Permission denied to change group name for {gc_group.name}")
                break

@client.command()
async def stopgc(ctx):
    global gc_loop_running
    await ctx.message.delete()  # Delete the command message
    gc_loop_running = False  # Stop the loop
    change_group_name.stop()  # Stop the loop task
    await ctx.send("Stopped changing the group name.", delete_after=5)


client.remove_command("help")

@client.command()
async def help(ctx):
    help_message = '''
```xml
╔══════════════════════════════════╗
║             𝗥𝗘𝗩𝗢𝗟𝗧 𝗫𝗘𝗡           ║
╚══════════════════════════════════╝

➤ =autoreply                  
➤ =gc <groupid>                       
➤ =help                      
➤ =ping                      
➤ =play <game>               
➤ =react <emoji>             
➤ =spam <message>            
➤ =stopgc                    
➤ =stopreact                 
➤ =stopreply                 
➤ =stream <message>          
➤ =watch <content>
➤ =ipinfo <ipaddress>
➤ =portscan           

╚══════════════════════════════════╝
```'''
    await ctx.send(help_message)

@client.command()
async def ipinfo(ctx, ip_address: str):
    try:
        response = requests.get(f'https://ipinfo.io/{ip_address}/json')
        data = response.json()
        
        if response.status_code == 200:
            ip_info = (
                f"**IP Address:** {data.get('ip')}\n"
                f"**Hostname:** {data.get('hostname')}\n"
                f"**City:** {data.get('city')}\n"
                f"**Region:** {data.get('region')}\n"
                f"**Country:** {data.get('country')}\n"
                f"**Location:** {data.get('loc')}\n"
                f"**Organization:** {data.get('org')}\n"
            )
            await ctx.send(ip_info)
        else:
            await ctx.send("Could not fetch IP information. Please check the IP address and try again.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")




@client.command()
async def portscan(ctx, ip_address: str, start: int, end: int):
    open_ports = []
    for port in range(start, end + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip_address, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    await ctx.send(f"Open ports on {ip_address}: {', '.join(map(str, open_ports)) if open_ports else 'None'}")


client.run("MTI5NjQ2MTI4ODk1MTY0ODI2Ng==.cNXcwHs.hUgbGsoF4tv5Jivirib1vs4tkCo", bot=False)
