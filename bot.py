import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

ROLE_ADD_IDS = [
    int(os.getenv("ROLE_ADD_1")),
    int(os.getenv("ROLE_ADD_2")),
    int(os.getenv("ROLE_ADD_3")),
]
ROLE_REMOVE_ID = int(os.getenv("ROLE_REMOVE"))
ALLOWED_ROLE_ID = int(os.getenv("ROLE_ONBOARD_ALLOWED"))

intents = discord.Intents.default()
intents.message_content = True  # REQUIRED for prefix commands
intents.members = True          # Needed for member edits

bot = commands.Bot(command_prefix="!", intents=intents)


def get_role(guild, role_id):
    role = guild.get_role(role_id)
    if role is None:
        raise ValueError(f"Role ID {role_id} not found.")
    return role


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
@commands.has_role(ALLOWED_ROLE_ID)
#!onboard @member [optional nickname]
async def onboard(ctx, member: discord.Member, *, nickname: str = None):
    """Adds 3 roles, removes 1 role, changes nickname"""

    try:
        roles_to_add = [get_role(ctx.guild, rid) for rid in ROLE_ADD_IDS]
        role_to_remove = get_role(ctx.guild, ROLE_REMOVE_ID)

        # Add roles
        await member.add_roles(*roles_to_add, reason=f"Onboarded by {ctx.author}")

        # Remove role
        await member.remove_roles(role_to_remove, reason=f"Onboarded by {ctx.author}")

        # Changes nickname to have [Pvt] before new name
        base_name = nickname if nickname else member.name
        new_nick = f"[Pvt] {base_name}"
        await member.edit(nick=new_nick, reason=f"Onboarded by {ctx.author}")

        await ctx.send(f"✅ {member.mention} has been onboarded!")

    except discord.Forbidden:
        await ctx.send("❌ I don't have permission. Check role hierarchy & permissions.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@onboard.error
async def onboard_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(" You don't have the required role to use this command.")
    else:
        await ctx.send(f" Error: {error}")


bot.run(TOKEN)
