from twitchio.ext import commands
import asyncio
import random
from web_bot import Browser
import json


class Bot(commands.Bot):
    def __init__(self, browser):
        with open("settings.json") as data:
            self.data = json.load(data)
        super().__init__(irc_token=self.data["oauth"], client_id=self.data["client_id"], nick="AIDungeonBot", prefix='!', initial_channels=[self.data["channel"]])
        self.prompts= []
        self.authors= []
        self.voters= []
        self.is_voting= False
        self.browser= browser
        self.cooldown= self.data["cooldown"]
        self.votes= {'y': 0,
                 'n': 0}
        self.loop.create_task(self.clear_list())

    async def clear_list(self):
        while True:
            await asyncio.sleep(self.cooldown)
            if self.prompts:
                prompt= random.choice(self.prompts)
                self.browser.send_prompt(prompt)
                self.prompts.clear()
                self.authors.clear()
                await self.get_channel(name=self.data["channel"]).send(f'''Prompt: "{prompt}", You have {self.cooldown} seconds to write the next prompt!''')

    async def event_message(self, message):
        await self.handle_commands(message)

    @commands.command(name='p')
    async def get_prompt(self, ctx):
        if ctx.author.name not in self.authors:
            self.prompts.append(ctx.message.content.lstrip("!p "))
            self.authors.append(ctx.author.name)
            await ctx.send(f'Prompt accepted!')
        else:
            await ctx.send("You've submitted a prompt already!")

    @commands.command(name='reset')
    async def start_voting(self, ctx):
        self.is_voting= True
        await self.get_channel(name=self.data["channel"]).send("Starting a vote for reset! Say !y to vote for reset, and !n to vote against! Voting goes for 2 minutes!")
        await asyncio.sleep(120)
        if self.votes['y'] > self.votes['n']:
            self.browser.reset_game()
            await self.get_channel(name=self.data["channel"]).send("Restarting the game...")
        else:
            await self.get_channel(name=self.data["channel"]).send("The vote failed. Next voting is available in 5 mins.")
        self.votes['y'], self.votes['n']= 0, 0
        self.voters.clear()
        await asyncio.sleep(300)

    @commands.command(name='y')
    async def vote_yes(self, ctx):
        if ctx.author.name not in self.voters and self.is_voting:
            self.votes['y'] += 1
            self.voters.append(ctx.author.name)
            await self.get_channel(name=self.data["channel"]).send("Vote accepted!")
        else:
            pass

    @commands.command(name='n')
    async def vote_no(self, ctx):
        if ctx.author.name not in self.voters and self.is_voting:
            self.votes['n'] += 1
            self.voters.append(ctx.author.name)
            await self.get_channel(name=self.data["channel"]).send("Vote accepted!")
        else:
            pass
botto= Bot(Browser())
botto.run()
