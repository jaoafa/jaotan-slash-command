import json
import discord
from discord_slash import SlashCommand, SlashContext, SlashCommandOptionType
from mysql.connector import DatabaseError

from src import get_twitter_id, is_page_exists, set_social_account, get_uuid_from_discordId
from src.database import get_connection

bot = discord.Client(intent=discord.Intents.all())

slash_command = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print("Login successful!")


@slash_command.slash(name="potato", description="(╮╯╭)を投稿します。", guild_ids=[597378876556967936])
async def slash_command_potato(ctx: SlashContext):
    await ctx.send(content="(╮╯╭)")


@slash_command.slash(name="socials", description="ソーシャルアカウントを登録します。", guild_ids=[597378876556967936], options=[
    {
        "type": SlashCommandOptionType.STRING,
        "name": "service",
        "description": "登録するソーシャルアカウントのサービス名",
        "required": True,
        "choices": [
            {
                "name": "Twitter",
                "value": "twitter"
            },
            {
                "name": "GitHub",
                "value": "github"
            },
            {
                "name": "Webサイト",
                "value": "home"
            }
        ]
    },
    {
        "type": SlashCommandOptionType.STRING,
        "name": "value",
        "description": "ソーシャルアカウントのユーザーID・サイトURL",
        "required": True,
    }
])
async def slash_command_socials(ctx: SlashContext, service: str, value: str):
    uuid = await get_uuid_from_discordId(ctx, ctx.author_id)
    if uuid is None:
        embed = discord.Embed(
            title="Socials",
            description="あなたはまだMinecraftアカウントとの連携がされていません。`/link`を実行して連携してください。",
            color=0xfbff00)
        await ctx.send(embed=embed)

    if service == "twitter":
        user_id = get_twitter_id(value)
        if user_id is None:
            embed = discord.Embed(
                title="Socials",
                description="残念ながら、指定されたTwitterアカウントの情報を取得できませんでした。\n"
                            "ユーザーが存在しないか、処理に失敗している恐れがあります。\n"
                            "時間をおいてもう一度お試しください。",
                color=0xfbff00)
            await ctx.send(embed=embed)
            return
        await set_social_account(ctx, uuid, "twitterId", user_id)
        embed = discord.Embed(
            title="Socials",
            description="Twitterアカウントとの連携を完了しました。",
            color=0x00ff00)
        await ctx.send(embed=embed)
        return

    elif service == "github":
        if "/" in value:
            embed = discord.Embed(
                title="Socials",
                description="指定されたユーザーIDが不適切です。",
                color=0xff0000)
            await ctx.send(embed=embed)

        exists = is_page_exists("https://github.com/" + value)
        if not exists:
            embed = discord.Embed(
                title="Socials",
                description="残念ながら、指定されたGitHubアカウントの存在を確認できませんでした。\n"
                            "ユーザーが存在しないか、処理に失敗している恐れがあります。\n"
                            "時間をおいてもう一度お試しください。",
                color=0xfbff00)
            await ctx.send(embed=embed)

        await set_social_account(ctx, uuid, "githubId", value)
        embed = discord.Embed(
            title="Socials",
            description="GitHubアカウントとの連携を完了しました。",
            color=0x00ff00)
        await ctx.send(embed=embed)
        return

    elif service == "home":
        if not value.startswith("http://") and not value.startswith("https://"):
            embed = discord.Embed(
                title="Socials",
                description="指定されたサイトアドレスが不適切です。",
                color=0xff0000)
            await ctx.send(embed=embed)

        exists = is_page_exists(value)
        if not exists:
            embed = discord.Embed(
                title="Socials",
                description="残念ながら、指定されたサイトアドレスの存在を確認できませんでした。\n"
                            "時間をおいてもう一度お試しください。",
                color=0xfbff00)
            await ctx.send(embed=embed)

        await set_social_account(ctx, uuid, "homeUrl", value)
        embed = discord.Embed(
            title="Socials",
            description="Webサイトとの連携を完了しました。",
            color=0x00ff00)
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title="Socials",
        description="何らかの問題が発生しています。",
        color=0xff0000)
    await ctx.send(embed=embed)


if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    bot.run(config["discord_token"])
