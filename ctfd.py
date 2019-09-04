import asyncio
import sys

from discord.ext import commands

import bot.display.embed as display
from bot import log
from bot.constants import TOKEN, DB_URI
from db import Database


class CTFdBot:

    def __init__(self) -> None:
        """ Discord Bot to catch CTFd events made by zTeeed """
        self.bot = commands.Bot(command_prefix='>>')
        self.bot.db = Database(DB_URI)
        self.bot.channel = None

    async def cron(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if self.bot.channel is not None:
                await display.cron(self.bot)
            await asyncio.sleep(1)

    def catch(self):
        @self.bot.event
        async def on_ready():
            await display.ready(self.bot)

        @self.bot.command(description='Show ranking of CTFd (20 first players)')
        async def scoreboard(context: commands.context.Context):
            """ """
            log.info("Command executed", name=str(context.command), author=str(context.message.author))
            await display.scoreboard(context)

        @self.bot.command(description='Show ranking of CTFd.')
        async def scoreboard_complete(context: commands.context.Context):
            """ """
            log.info("Command executed", name=str(context.command), author=str(context.message.author))
            await display.scoreboard(context, all_players=True)

        @self.bot.command(description='Show list of categories.')
        async def categories(context: commands.context.Context):
            """ """
            log.info("Command executed", name=str(context.command), author=str(context.message.author))
            await display.categories(context)

        @self.bot.command(description='Show list of challenges from a category.')
        async def category(context: commands.context.Context):
            """ <category> """
            log.info("Command executed", name=str(context.command), author=str(context.message.author))
            await display.category(context)

        @self.bot.command(description='Mention discord users if their discord id is in challenge description.')
        async def problem(context: commands.context.Context):
            """ <challenge> """
            log.info("Command executed", name=str(context.command), author=str(context.message.author))
            await display.problem(context)

        @self.bot.command(description='Return who solved a specific challenge.')
        async def who_solved(context: commands.context.Context):
            """ <challenge> """
            log.info("Command executed", name=str(context.command), author=str(context.message.author))
            await display.who_solved(context)

        @self.bot.command(description='Return challenges solved grouped by users for last day.')
        async def solved_last_days(context: commands.context.Context):
            """ <number_of_days> (<username>) """
            log.info("Command executed", name=str(context.command), author=str(context.message.author))
            await display.last_days(context)

        @self.bot.command(description='Return difference of solved challenges between two users.')
        async def diff(context: commands.context.Context):
            """ <username1> <username2> """
            log.info("Command executed", name=str(context.command), author=str(context.message.author))
            await display.diff(context)

        @self.bot.command(description='Flush all data from bot channel excepted events')
        async def flush(context: commands.context.Context):
            """ """
            log.info("Command executed", name=str(context.command), author=str(context.message.author))
            await display.flush(context)

    def start(self):
        if TOKEN == 'token':
            log.warn('Unexpected token', TOKEN=TOKEN)
            log.warn('Please update configuration in ./bot/constants.py')
            sys.exit(0)
        self.catch()
        self.bot.loop.create_task(self.cron())
        self.bot.run(TOKEN)
