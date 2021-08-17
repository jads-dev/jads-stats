import os
import re
import sqlite3
import shelve
import json

from collections import defaultdict
from datetime import datetime, timedelta


import discord

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

con = sqlite3.connect("static/stats.db")


class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f"Logged_in_as {self.user.name} id: {self.user.id}")
        print("------")

        guild = self.get_guild(308515582817468420)  # jads

        date_start = datetime(2020, 1, 13, 0, 0, 0, 0)
        date_limit = datetime(2021, 8, 1, 0, 0, 0, 0)

        emote_pattern = re.compile("<a?:(.*?):([0-9]*?)>")

        cursor = con.cursor()

        for channel in guild.channels:
            if channel.category_id != 360768845662781440:  # main category
                continue

            print(channel.id, channel)

            cur_time = date_start
            while cur_time < date_limit:
                cur_time_end = cur_time + timedelta(days=1)

                print(f"Searching between {cur_time} and {cur_time_end}")

                user_data = defaultdict(
                    lambda: {
                        "message_count": 0,
                        "emote_count": 0,
                        "reaction_count": 0,
                        "emotes": defaultdict(int),
                    }
                )

                usernames = {}
                emote_names = {}

                cache_folder = f"./cache/{channel.id}"
                os.makedirs(cache_folder, exist_ok=True)
                cache_path = f"{cache_folder}/{cur_time.strftime('%Y%m%d-%H%M%S')}.json"

                if os.path.exists(cache_path):
                    with open(cache_path, "r") as f:
                        messages = json.load(f)
                else:
                    messages = []
                    async for message in channel.history(after=cur_time, before=cur_time_end, limit=None):
                        messages.append(message)
                    messages = [
                        {
                            "author_id": message.author.id,
                            "username": f"{message.author.name}#{message.author.discriminator}",
                            "content": message.content,
                            "reactions": [reaction.emoji.id if reaction.custom_emoji else reaction.emoji for reaction in message.reactions],
                        }
                        for message in messages
                    ]

                    with open(cache_path, "w") as f:
                        json.dump(messages, f)

                for message in messages:
                    aid = message["author_id"]
                    user_data[aid]["message_count"] += 1

                    emotes = emote_pattern.findall(message["content"])

                    if len(emotes):
                        user_data[aid]["emote_count"] += 1
                        for emote_name, emote_id in emotes:
                            user_data[aid]["emotes"][emote_id] += 1
                            emote_names[emote_id] = emote_name
                    if message["reactions"]:
                        user_data[aid]["reaction_count"] += 1
                    usernames[aid] = message["username"]

                time_str = cur_time.date().isoformat()

                user_data_flat = [
                    (time_str, channel.id, key, user_data[key]["message_count"], user_data[key]["emote_count"], user_data[key]["reaction_count"])
                    for key in user_data
                ]

                cursor.executemany(
                    """INSERT OR IGNORE INTO channel_totals (timestamp, channel, user, message_count, emote_count, reaction_count)
                       VALUES (?,?,?,?,?,?)
                            """,
                    user_data_flat,
                )

                emote_data_flat = [
                    (time_str, channel.id, user_id, emote, user_data[user_id]["emotes"][emote])
                    for user_id in user_data
                    for emote in user_data[user_id]["emotes"]
                ]

                cursor.executemany(
                    """INSERT OR IGNORE INTO emote_totals (timestamp, channel, user, emote, amount)
                       VALUES (?,?,?,?,?)
                            """,
                    emote_data_flat,
                )

                usernames_flat = [(key, usernames[key]) for key in usernames]
                cursor.executemany(
                    """insert into user_info (user_id, username)
                       VALUES (?,?)
                       ON CONFLICT(user_id) 
                       DO UPDATE SET username=excluded.username;
                            """,
                    usernames_flat,
                )
                emote_names_flat = [(key, emote_names[key]) for key in emote_names]
                cursor.executemany(
                    """insert into emote_info (emote_id, emote_name)
                       VALUES (?,?)
                       ON CONFLICT(emote_id) 
                       DO UPDATE SET emote_name=excluded.emote_name;
                    """,
                    emote_names_flat,
                )

                con.commit()

                cur_time = cur_time_end

        con.close()
        print("Done")

        await self.close()


def run():
    client = Bot(intents=intents)
    client.run(os.environ["discord_token"], bot=True)


if __name__ == "__main__":
    run()
