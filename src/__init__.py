import json

import discord
import requests
from discord_slash import SlashContext
from mysql.connector import DatabaseError

from src.database import get_connection


def get_twitter_id(screen_name: str):
    with open("config.json") as f:
        config = json.load(f)
        bearer_token = config["bearer_token"]

        headers = {
            "Authorization": "Bearer {token}".format(token=config["bearer_token"])
        }
        params = {
            "screen_name": screen_name
        }
        response = requests.get("https://api.twitter.com/1.1/users/show.json",
                                headers=headers, params=params)
        if response.status_code != 200:
            print("[Error] " + str(response.status_code))
            return None

        data = response.json()
        return data["id_str"]


def is_page_exists(url):
    response = requests.get(url)
    return response.status_code == 200


async def get_uuid_from_discordId(ctx: SlashContext, discord_id):
    connection = get_connection()
    try:
        cur = connection.cursor(dictionary=True, buffered=True)
        if not connection.is_connected():
            embed = discord.Embed(
                title="Socials",
                description="データベースへの接続に失敗しました。時間をおいてもう一度お試しください。",
                color=0xff0000)
            await ctx.send(embed=embed)
            return

        cur.execute(
            "SELECT * FROM discordlink WHERE disid = %s AND disabled = 0",
            (discord_id,)
        )
        row = cur.fetchone()

        if row is None:
            return None

        return row["uuid"]
    except DatabaseError as e:
        print(e)
        connection.close()
        embed = discord.Embed(
            title="Socials",
            description="データベースの操作に失敗しました。時間をおいてもう一度お試しください。",
            color=0xff0000)
        await ctx.send(embed=embed)


async def get_social_accounts(cur, ctx: SlashContext, uuid: str):
    try:
        cur.execute(
            "SELECT * FROM socials WHERE uuid = %s",
            (uuid,)
        )
        return cur.fetchone()
    except DatabaseError as e:
        print(e)
        embed = discord.Embed(
            title="Socials",
            description="データベースの操作に失敗しました。時間をおいてもう一度お試しください。",
            color=0xff0000)
        await ctx.send(embed=embed)
        return None


async def set_social_account(ctx: SlashContext, uuid: str, key: str, value: str):
    connection = get_connection()
    try:
        cur = connection.cursor(dictionary=True, buffered=True)
        if not connection.is_connected():
            embed = discord.Embed(
                title="Socials",
                description="データベースへの接続に失敗しました。時間をおいてもう一度お試しください。",
                color=0xff0000)
            await ctx.send(embed=embed)
            return

        row = await get_social_accounts(cur, ctx, uuid)

        if row is None:
            cur.execute(
                "INSERT INTO socials (uuid, created_at) VALUES (%s, CURRENT_TIMESTAMP)",
                (uuid,)
            )

        cur.execute(
            "UPDATE socials SET %s = %s WHERE uuid = %s",
            (key, value, uuid)
        )
    except DatabaseError as e:
        print(e)
        connection.close()
        embed = discord.Embed(
            title="Socials",
            description="データベースの操作に失敗しました。時間をおいてもう一度お試しください。",
            color=0xff0000)
        await ctx.send(embed=embed)
