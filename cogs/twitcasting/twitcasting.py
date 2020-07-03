from aiohttp import web
from discord.ext import commands
from discord import Embed
from discord import NotFound
import logging
import os

from .database import TwitcastDatabase, Subscription
from .pytwitcast import TwitcastAPI
from . import constants


class Twitcasting(commands.Cog):
    """
    The Twitcasting cog allows users to search and follow users streaming on the Twitcasting platform (twitcasting.tv).

    TODO: Add admin-only privileges for subcommands (setup, clear)
    """
    def __init__(self, bot):
        self.logger = logging.getLogger('zhenpai.twitcasting')
        self.bot = bot
        self.twitcasting = None
        self.init_api()
        self.db = TwitcastDatabase()

    def init_api(self):
        if os.path.isfile('config.py'):
            from . import config
            client_id = config.TWITCAST_CLIENT_ID
            client_secret = config.TWITCAST_CLIENT_SECRET
            access_token = config.TWITCAST_ACCESS_TOKEN
        else:
            client_id = os.environ.get(constants.TWITCAST_CLIENT_ID)
            client_secret = os.environ.get(constants.TWITCAST_CLIENT_SECRET)
            access_token = os.environ.get(constants.TWITCAST_ACCESS_TOKEN)
        self.twitcasting = TwitcastAPI(client_id=client_id, client_secret=client_secret, access_token=access_token)

    @commands.group()
    async def tc(self, ctx):
        if ctx.invoked_subcommand is None:
            help_text = ""
            for command in self.walk_commands():
                if not isinstance(command, commands.Group) and not command.hidden:
                    help_text += f'{command}: {command.help}\n'
            await ctx.send(f'```{help_text}```')

    @tc.error
    async def tc_error_handler(self, ctx, error):
        self.logger.warning('%s - %s', ctx.message.content, error)
        await ctx.send(f"{error}\nType `z!tc help` for usage details.")

    @tc.command()
    async def search(self, ctx, *args):
        """
        Searches Twitcasting for up to three users that closely matches the provided query.
            Usage: z!tc search <arg1> <arg2> ...
        """
        if len(args) == 0:
            await ctx.send("Send at least one word in the search query.")
            return
        users = self.twitcasting.search_users(words=args, limit=3)
        for user in users:
            embed_dict = {
                'title': user.name,
                'url': f'https://twitcasting.tv/{user.screen_id}',
                'description': f'''ID: {user.id}
                                Screen ID: {user.screen_id}
                                Profile: {user.profile}\n''',
                'author': {'name': user.screen_id},
                'thumbnail': {'url': user.image}
            }
            await ctx.send(embed=Embed.from_dict(embed_dict))

    @tc.command()
    async def add(self, ctx, twitcast_user_id: str, channel_name: str = None):
        """
        Adds subscription of the Twitcasting user to the provided text channel. If #<channel-name> is left blank,
        then the channel in which the command was sent is used instead.
            Usage: z!tc add <twitcasting-user-id> #<channel-name>(optional)
        """
        if channel_name:
            channel_id = self._get_channel_id_from_name(channel_name)
            if not channel_id:
                await ctx.send(f'Cannot find {channel_name} in {ctx.guild.name}')
                return
        else:
            channel_id = ctx.channel.id

        users = self.twitcasting.search_users(words=twitcast_user_id, limit=1)
        if users[0].id != twitcast_user_id:
            await ctx.send(f'Cannot find {twitcast_user_id} on the Twitcasting platform. Enter a valid ID.')
            return
        if self.db.get_sub(channel_id, twitcast_user_id):
            await ctx.send(content=f"Already subscribed to {users[0].screen_id} ({twitcast_user_id}) in {channel_name}.")
            return

        guild_id = ctx.guild.id
        self.twitcasting.register_webhook(user_id=twitcast_user_id)
        self.db.add_sub(Subscription(channel_id, guild_id, twitcast_user_id, users[0].screen_id))
        await ctx.send(content=f"Subscribed to {users[0].screen_id} ({twitcast_user_id}) in {channel_name}.")
        self.db.commit()

    @tc.command()
    async def list(self, ctx, channel_name: str = None):
        """
        Lists all Twitcasting users that this guild or text channel has subscribed to. If #<channel-name> is left blank,
        then the command will list subscriptions for the entire guild/server instead.
            Usage: z!tc list #<channel-name>(optional)
        """
        if channel_name:
            channel_id = self._get_channel_id_from_name(channel_name)
            if not channel_id:
                await ctx.send(f'Cannot find {channel_name} in {ctx.guild.name}')
                return
            users = self.db.get_subs_by_channel(channel_id=channel_id)
        else:
            users = self.db.get_subs_by_guild(ctx.guild.id)

        user_embed = Embed(title='Registered Users')
        for user in users:
            user_embed.add_field(name='====================',
                                 value=f"""Name: [{user.twitcast_name}](https://twitcasting.tv/{user.twitcast_name})
                                        ID: {user.twitcast_user_id}
                                        Channel: <#{user.channel_id}>""",
                                 inline=False)
        await ctx.send(embed=user_embed)

    @tc.command()
    async def remove(self, ctx, twitcast_user_id: str, channel_name: str = None):
        """
        Removes subscription of the Twitcasting user from the text channel. If #<channel-name> is left blank,
        then the channel in which the command was sent is used instead.
            Usage: z!tc remove <twitcasting-user-id> #<channel-name>(optional)
        """
        if channel_name:
            channel_id = self._get_channel_id_from_name(channel_name)
            if not channel_id:
                await ctx.send(f'Cannot find {channel_name} in {ctx.guild.name}')
                return
        else:
            channel_id = ctx.channel.id

        sub = self.db.get_sub(channel_id=channel_id, twitcast_user_id=twitcast_user_id)
        if not sub:
            await ctx.send(f"Cannot find user {twitcast_user_id} in subscription list for {channel_name}.")
            return

        user_name = sub.twitcast_name
        self.db.remove_sub(sub)
        if self.db.count_subs_by_user_id(twitcast_user_id=twitcast_user_id) == 0:
            self.twitcasting.remove_webhook(user_id=twitcast_user_id)
        await ctx.send(f"Unsubscribed from {user_name} ({twitcast_user_id}) in {channel_name}.")
        self.db.commit()

    @tc.command()
    async def clear(self, ctx, channel_name: str):
        """
        Deletes any subscriptions in the text channel.
            Usage: z!tc clear #<channel-name>
        """
        channel_id = self._get_channel_id_from_name(channel_name)
        if not channel_id:
            await ctx.send(f'Cannot find {channel_name} in {ctx.guild.name}')
            return
        subs = self.db.get_subs_by_channel(channel_id=channel_id)
        if subs:
            self.db.remove_all_subs_from_channel(channel_id=channel_id)
            for sub in subs:
                if self.db.count_subs_by_user_id(twitcast_user_id=sub.twitcast_user_id) == 0:
                    self.twitcasting.remove_webhook(user_id=sub.twitcast_user_id)
            await ctx.send(f"Cleared {channel_name} of twitcasting subscriptions.")
            self.db.commit()
        else:
            await ctx.send(f"No subs had been added to {channel_name}. There is nothing to clear.")

    @tc.command(hidden=True)
    async def update(self, ctx):
        """
        Dev command used to update names of locally stored Twitcasting users
        """
        users = self.db.get_subs_by_channel(channel_id=ctx.channel.id)
        for user in users:
            if user.twitcast_user_id:
                new_user_info = self.twitcasting.search_users(words=user.twitcast_user_id, limit=1)
                self.db.update_name_of_twitcast_user(twitcast_user_id=user.twitcast_user_id,
                                                     twitcast_name=new_user_info[0].screen_id)
        self.db.commit()

    async def broadcast(self, request):
        """
        Callback function that forwards incoming Twitcasting webhooks to subscribed channels.
        """
        request = await request.json()
        movie, user = self.twitcasting.parse_incoming_webhook(request)
        res = self.db.get_subs_by_user_id(twitcast_user_id=user.id)
        message = f'{user.screen_id} has went live!' if user.is_live else f'{user.screen_id} has gone offline!'
        embed_dict = {
            'title': message,
            'description': f'**Title**: [{movie.title}]({movie.link})\n{movie.subtitle}',
            'author': {'name': user.screen_id,
                       'icon_url': user.image},
            'thumbnail': {'url': user.image}
        }
        embed = Embed.from_dict(embed_dict)
        for sub in res:
            channel = self.bot.get_channel(int(sub.channel_id))
            await channel.send(f'{message} @here', embed=embed)
        return web.Response(status=200)

    def _get_channel_id_from_name(self, channel_name: str):
        channel_id = channel_name.strip('<>#')
        try:
            if self.bot.get_channel(int(channel_id)):
                return channel_id
            else:
                return None
        except ValueError:
            return None
