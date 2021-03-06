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
        #create the looping task so it acts every N seconds
        self.loop.create_task(self.clear_list())

    async def clear_list(self):
        '''Acts every N seconds (defined in settings.json), by clearing the list and, with it, sending the prompt to the browser.'''
        while True:
            #using the randint for more randomizing.
            await asyncio.sleep(self.cooldown + random.randint(0, 0.999))
            if self.prompts:
                prompt= random.choice(self.prompts)
                self.browser.send_prompt(prompt)
                self.prompts.clear()
                self.authors.clear()
                await self.send_message(f'''Selected prompt: "{prompt}", you have {self.cooldown} seconds to write the next prompt!''')

    async def event_message(self, message):
        await self.handle_commands(message)

    @commands.command(name='p')
    async def get_prompt(self, ctx):
        '''Fetches the prompt from the chat, if the author didn't sent a prompt already.'''
        if ctx.author.name not in self.authors:
            self.prompts.append(ctx.message.content[3:])
            self.authors.append(ctx.author.name)
            await ctx.send(f'Prompt accepted!')
        else:
            await ctx.send("You've submitted a prompt already!")

    @commands.command(name='reset')
    async def start_voting(self, ctx):
        '''Used to initiate the voting for reset.'''
        self.is_voting= True
        await self.send_message("Starting a vote for reset! Say !y to vote for reset, and !n to vote against! Voting goes for 2 minutes!")
        await asyncio.sleep(120)
        if self.votes['y'] > self.votes['n']:
            self.browser.reset_game()
            await self.send_message("Restarting the game...")
        else:
            await self.send_message("The vote failed. Next voting is available in 5 mins.")
        self.votes['y'], self.votes['n']= 0, 0
        self.voters.clear()
        await asyncio.sleep(300)

    @commands.command(name='y')
    async def vote_yes(self, ctx):
        '''Used for voting. Doesn't work if vote isn't initiated.'''
        if ctx.author.name not in self.voters and self.is_voting:
            self.votes['y'] += 1
            self.voters.append(ctx.author.name)
            await self.send_message("Vote accepted!")
        else:
            pass
   
    async def send_message(self, message):
        '''A shortcut for sending the message in the chat. Added for readability.'''
        await self.get_channel(name=self.data["channel"]).send(message)

    @commands.command(name='n')
    async def vote_no(self, ctx):
        '''Used for voting. Doesn't work if vote isn't initiated.'''
        if ctx.author.name not in self.voters and self.is_voting:
            self.votes['n'] += 1
            self.voters.append(ctx.author.name)
            await self.send_message("Vote accepted!")
        else:
            pass
botto= Bot(Browser())
botto.run()
