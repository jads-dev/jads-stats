import os
import re
import sqlite3
import shelve
import shutil
import json
import logging

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone


import discord

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

con = sqlite3.connect("static/stats.db")


class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def get_channel_messages(self, channel, after, before):
        messages = []
        _after = after
        while True:
            reached_bounds = False
            fetched = False
            async for message in channel.history(after=_after, limit=100, oldest_first=True):
                fetched = True
                if message.created_at >= after and message.created_at < before:
                    messages.append(message)
                    _after = message
                else:
                    reached_bounds = True
            if not fetched or reached_bounds:
                return messages

    async def on_ready(self):
        print(f"Logged_in_as {self.user.name} id: {self.user.id}")
        print("------")

        guild = self.get_guild(308515582817468420)  # jads

        today = date.today()

        # date_start = datetime(2020, 1, 13, 0, 0, 0, 0)
        date_start = datetime(2020, 1, 13, 0, 0, 0, 0, tzinfo=timezone.utc)
        date_start = datetime(2022, 11, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        # date_limit = datetime(2021, 10, 1, 0, 0, 0, 0)
        date_limit = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)

        emote_pattern = re.compile("<a?:(.*?):([0-9]+?)>")

        cursor = con.cursor()

        dd = guild.get_channel(666328861985865749)
        archived_thread_ids = [
            888659721651904573,  # deltarune spoiler chat
            1039499797729648680, # gow ragnarok
        ]
        extra_channels = [
            974341120198844467,  # zero escape spoiler channel
            1052997665610285137, # lis spoiler channel
        ]

        974341120198844467

        channels = [channel for channel in guild.channels if channel.category_id == 360768845662781440]
        channels += [channel for channel in guild.channels if channel.id in extra_channels]
        channels += [thread for thread in guild.threads]
        channels += [thread async for thread in dd.archived_threads() if thread.id in archived_thread_ids]

        for channel in channels:
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
                    messages = await self.get_channel_messages(channel, after=cur_time, before=cur_time_end)

                    messages = [
                        {
                            "message_id": message.id,
                            "author_id": message.author.id,
                            "username": f"{message.author.name}#{message.author.discriminator}",
                            "content": message.content,
                            "reactions": [reaction.emoji if type(reaction.emoji) is str else reaction.emoji.id for reaction in message.reactions],
                            "reactions_detailed": [
                                {
                                    "reaction": reaction.emoji if type(reaction.emoji) is str else reaction.emoji.id,
                                    "count": reaction.count,
                                }
                                for reaction in message.reactions
                            ],
                            "attachments": len(message.attachments),
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
                    """INSERT OR IGNORE INTO channel_totals_breakdown (timestamp, channel, user, message_count, emote_count, reaction_count)
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
                    """INSERT OR IGNORE INTO emote_totals_breakdown (timestamp, channel, user, emote, amount)
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

        # these tables will use less data (faster) when querying from the browser
        cursor.executescript(
            """
            drop table if EXISTS channel_totals;
            create table channel_totals as
            select ct.timestamp, channel, sum(message_count) as message_count, sum(emote_count) as emote_count, sum(reaction_count) as reaction_count
            from (
            select distinct timestamp, channel_id
            from channel_totals_breakdown, channel_info
            ) as c
            left join channel_totals_breakdown as ct on ct.timestamp = c.timestamp and ct.channel = c.channel_id 
            group by ct.timestamp, channel
            order by ct.timestamp, channel;

            CREATE INDEX "ct_timestamp" ON "channel_totals" (
                "timestamp"	ASC
            );


            drop table if EXISTS channel_user_totals;
            create table channel_user_totals as
            select timestamp, user, sum(message_count) as message_count, sum(emote_count) as emote_count, sum(reaction_count) as reaction_count
            from channel_totals_breakdown as ct 
            group by timestamp, user
            order by timestamp, sum(message_count) desc;

            CREATE INDEX "cut_timestamp" ON "channel_user_totals" (
                "timestamp"	ASC
            );


            drop table if exists emote_totals;
            create table emote_totals as
            select timestamp, channel, emote, sum(amount) as amount
            from emote_totals_breakdown
            group by timestamp, channel, emote;

            CREATE INDEX "et_timestamp" ON "emote_totals" (
                "timestamp"	ASC
            );

            """
        )

        con.close()

        end_date = date_limit - timedelta(days=1)
        start_date = date_limit - timedelta(days=31)

        dir_name = f"stats-{end_date.year}{end_date.month:02}{end_date.day:02}"
        os.makedirs(f"./static/{dir_name}")
        os.system(f"bash create_db.sh static/stats.db static/{dir_name}/")
        with open("static/data.json", "w") as f:
            data = {
                "start_date": f"{start_date.year}-{start_date.month:02}-{start_date.day:02}",
                "end_date": f"{end_date.year}-{end_date.month:02}-{end_date.day:02}",
                "dir_name": f"./{dir_name}",
            }
            json.dump(data, f)

        print("Done")

        await self.close()


def run():
    client = Bot(intents=intents)
    client.run(os.environ["discord_token"], log_level=logging.INFO)


if __name__ == "__main__":
    run()
