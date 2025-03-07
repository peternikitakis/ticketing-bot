import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
import sys

load_dotenv()
TOKEN = os.getenv("discordTokenID")
print(f"Python version: {sys.version}")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load tickets from JSON file (if it exists)
TICKET_FILE = "tickets.json"
if os.path.exists(TICKET_FILE):
    with open(TICKET_FILE, "r") as f:
        tickets = json.load(f)
else:
    tickets = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

def save_tickets():
    with open(TICKET_FILE, "w") as f:
        json.dump(tickets, f, indent=4)

@bot.command()
async def ticket(ctx, *, description):
    ticket_id = str(len(tickets) + 1)
    # Create a new channel for the ticket
    guild = ctx.guild
    ticket_channel = await guild.create_text_channel(f"ticket-{ticket_id}")
    # Save ticket data
    tickets[ticket_id] = {
        "author": str(ctx.author),
        "description": description,
        "status": "open",
        "created_at": str(ctx.message.created_at),
        "channel_id": str(ticket_channel.id)
    }
    save_tickets()
    await ctx.send(f"Ticket #{ticket_id} created: {description}. See {ticket_channel.mention} for details.")
    await ticket_channel.send(f"Ticket #{ticket_id} by {ctx.author.mention}: {description}")

@bot.command()
async def close(ctx, ticket_id):
    if ticket_id in tickets:
        tickets[ticket_id]["status"] = "closed"
        # Delete the ticket channel if it exists
        channel_id = tickets[ticket_id].get("channel_id")
        if channel_id:
            channel = ctx.guild.get_channel(int(channel_id))
            if channel:
                await channel.delete()
        save_tickets()
        await ctx.send(f"Ticket #{ticket_id} has been closed and channel deleted.")
    else:
        await ctx.send(f"Ticket #{ticket_id} not found.")

@bot.command()
async def list(ctx):
    open_tickets = {k: v for k, v in tickets.items() if v["status"] == "open"}
    if not open_tickets:
        await ctx.send("No open tickets.")
        return
    embed = discord.Embed(title="Open Tickets", color=0x00ff00)
    for ticket_id, data in open_tickets.items():
        embed.add_field(
            name=f"Ticket #{ticket_id}",
            value=f"**Description**: {data['description']}\n**Author**: {data['author']}\n**Created**: {data['created_at']}",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def history(ctx):
    closed_tickets = {k: v for k, v in tickets.items() if v["status"] == "closed"}
    if not closed_tickets:
        await ctx.send("No closed tickets.")
        return
    embed = discord.Embed(title="Closed Tickets", color=0xFF4500)  # Orange-red color for closed tickets
    for ticket_id, data in closed_tickets.items():
        embed.add_field(
            name=f"Ticket #{ticket_id}",
            value=f"**Description**: {data['description']}\n**Author**: {data['author']}\n**Created**: {data['created_at']}\n**Status**: Closed",
            inline=False
        )
    await ctx.send(embed=embed)

bot.run(TOKEN)