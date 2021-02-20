import json
import discord
from discord_slash import SlashCommand, SlashContext

bot = discord.Client(intent=discord.Intents.all())

slash_command = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print("Login successful!")


@slash_command.slash(name="potato", description="(╮╯╭)を投稿します。", guild_ids=[597378876556967936])
async def slash_command_potato(ctx: SlashContext):
    await ctx.send(content="(╮╯╭)")


if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    bot.run(config["discord_token"])
