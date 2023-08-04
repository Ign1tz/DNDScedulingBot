import os
import re
import discord
from dotenv import load_dotenv
import datetime

WEEKDAYS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "So"]
COMMANDS = ["-n", "-m", "-a"]

YEAR = int(datetime.datetime.now().strftime("%Y"))

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

CLIENT = discord.Client(intents=discord.Intents.all())


@CLIENT.event
async def on_ready():
    for guild in CLIENT.guilds:
        if guild.name == GUILD:
            break

        print(
            f'{CLIENT.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})\n'
        )


def clarify_dates(dates):
    for date in dates:
        if "-" in date:
            temp_dates = date.split("-")

            start_date = string_to_date(temp_dates[0])
            end_date = string_to_date(temp_dates[1])

            delta = get_timedelta(start_date, end_date)

            dates.remove(date)
            for day in range(delta.days + 1):
                day = start_date + datetime.timedelta(days=day)
                dates.append(str(day.day) + "." + str(day.month))
    return dates


def string_to_date(date_str):
    date_arr = date_str.split(".")
    return datetime.date(YEAR, int(date_arr[1]), int(date_arr[0]))


def get_timedelta(start_date, end_date):
    if end_date < start_date:
        end_date = datetime.date(YEAR + 1, int(end_date.month), int(end_date.day))

    return end_date - start_date


@CLIENT.event
async def on_message(message):
    if message.author == CLIENT.user:
        return

    if message.content.startswith("!Dates "):
        content = re.sub(" +", " ", message.content.removeprefix("!Dates "))
        dates = re.sub(" .*", "", content).split("-")

        special_dates = {"-n": [],
                         "-m": [],
                         "-a": []}
        for command in COMMANDS:
            if command in content:
                com_dates = clarify_dates(re.sub(r'}.*', "", re.sub(r".*?" + command + " \{", "", content)).split(" "))
                special_dates[command] = com_dates

        start_date = string_to_date(dates[0])
        end_date = string_to_date(dates[1])

        delta = get_timedelta(start_date, end_date)

        for date in range(delta.days + 1):
            day = start_date + datetime.timedelta(days=date)
            str_day = str(day.day) + "." + str(day.month)
            if str_day not in special_dates["-n"]:
                message_str = str(day.day) + "." + str(day.month)
                if "-wd" in message.content:
                    message_str += " (" + WEEKDAYS[day.weekday()] + ")"
                if str_day in special_dates["-m"]:
                    message_str += " (Morning)"
                if str_day in special_dates["-a"]:
                    message_str += " (Afternoon)"
                await message.channel.send(message_str)

        await message.channel.send("@everyone")


CLIENT.run(TOKEN)
