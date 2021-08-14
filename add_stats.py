import os
import re
import sqlite3


from collections import defaultdict
from datetime import datetime, timezone, timedelta


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

            print(channel)
            cur_time = date_start
            while cur_time < date_limit:
                cur_time_end = cur_time + timedelta(days=1)

                print(f"Searching between {cur_time} and {cur_time_end}")
                messages = 0
                emotes = 0
                reactions = 0
                async for message in channel.history(after=cur_time, before=cur_time_end, limit=None):
                    messages += 1
                    if emote_pattern.search(message.content):
                        emotes += 1
                    if len(message.reactions):
                        reactions += 1

                time_str = cur_time.isoformat()
                cursor.execute(
                    """INSERT INTO channel_totals (timestamp, channel, message_count, emote_count, reaction_count)
                                VALUES (?,?,?,?,?)
                            """,
                    (time_str, channel.id, messages, emotes, reactions),
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
