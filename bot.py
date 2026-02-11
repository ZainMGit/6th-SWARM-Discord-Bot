import json
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

def read_role_id(var_name):
    value = os.getenv(var_name)
    return int(value) if value else None

ALLOWED_ROLE_IDS = [
    rid
    for rid in [
        read_role_id("ROLE_ONBOARD_ALLOWED"),
        read_role_id("ROLE_ONBOARD_ALLOWED_2"),
    ]
    if rid
]
if not ALLOWED_ROLE_IDS:
    raise ValueError("At least one onboarding role must be set in environment variables.")

intents = discord.Intents.default()
intents.message_content = True  # REQUIRED for prefix commands
intents.members = True          # Needed for member edits

bot = commands.Bot(command_prefix="!", intents=intents)

LEADERBOARD_FILE = "leaderboard.json"


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return {}
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_leaderboard(data):
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def increment_onboard_usage(user_id):
    data = load_leaderboard()
    key = str(user_id)
    data[key] = int(data.get(key, 0)) + 1
    save_leaderboard(data)


def get_role(guild, role_id):
    role = guild.get_role(role_id)
    if role is None:
        raise ValueError(f"Role ID {role_id} not found.")
    return role


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Foxhole"))
    print(f"Logged in as {bot.user}")


@bot.command()
@commands.has_any_role(*ALLOWED_ROLE_IDS)
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

        increment_onboard_usage(ctx.author.id)

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


@bot.command()
async def leaderboard(ctx):
    """Shows total onboard command usages per user."""
    data = load_leaderboard()
    if not data:
        await ctx.send("No onboard usage recorded yet.")
        return

    entries = sorted(data.items(), key=lambda kv: kv[1], reverse=True)
    lines = []
    for user_id, count in entries[:10]:
        user = ctx.guild.get_member(int(user_id))
        name = user.display_name if user else f"User {user_id}"
        lines.append(f"{name}: {count}")

    total = sum(data.values())
    header = f"Onboard Leaderboard (total uses: {total})"
    await ctx.send(header + "\n" + "\n".join(lines))


bot.run(TOKEN)