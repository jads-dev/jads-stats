import os
import re
import sqlite3


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

        emote_pattern = re.compile("<a?:.*?:([0-9]*?)>")

        cursor = con.cursor()

        for channel in guild.channels:
            if channel.category_id != 360768845662781440:  # main category
                continue

            print(channel.id, channel)

            cursor.execute("select max(timestamp) from channel_totals where channel = ?", (channel.id,))
            result = cursor.fetchone()[0]
            if result:
                cur_time = datetime.fromisoformat(result)
                cur_time = cur_time + timedelta(days=1)
            else:
                cur_time = date_start
            while cur_time < date_limit:
                cur_time_end = cur_time + timedelta(days=1)

                print(f"Searching between {cur_time} and {cur_time_end}")

                user_data = defaultdict(
                    lambda: {
                        "messages": 0,
                        "emotes": 0,
                        "reactions": 0,
                    }
                )

                usernames = {}

                async for message in channel.history(after=cur_time, before=cur_time_end, limit=None):
                    aid = message.author.id
                    user_data[aid]["messages"] += 1
                    if emote_pattern.search(message.content):
                        user_data[aid]["emotes"] += 1
                    if len(message.reactions):
                        user_data[aid]["reactions"] += 1

                    usernames[aid] = f"{message.author.name}#{message.author.discriminator}"

                time_str = cur_time.date().isoformat()

                user_data_flat = [
                    (time_str, channel.id, key, user_data[key]["messages"], user_data[key]["emotes"], user_data[key]["reactions"]) for key in user_data
                ]
                cursor.executemany(
                    """INSERT INTO channel_totals (timestamp, channel, user, message_count, emote_count, reaction_count)
                       VALUES (?,?,?,?,?,?)
                            """,
                    user_data_flat,
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
