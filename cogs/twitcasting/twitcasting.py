from discord.ext import commands
from discord import Embed
from discord import Webhook, AsyncWebhookAdapter

from aiohttp import web
from .pytwitcast import API
from .config import *
from .sqlite import SqliteConnection


class Twitcasting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.twitcasting = API(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, access_token=ACCESS_TOKEN)
        self.connection = SqliteConnection(DB_PATH)

    @commands.group()
    async def tc(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Valid subcommands are \'setup\', \'add\', \'list\', and \'delete\'.')

    @tc.command()
    async def setup(self, ctx, webhook_name: str):
        id = f'{ctx.guild.id}:{ctx.channel.id}'
        res = self.connection.select_records_by_id(id=id)
        if not res:
            webhook = await ctx.channel.create_webhook(name=webhook_name)
            self.connection.insert_record(id, webhook.id, None, None)
            await ctx.send(f"""Created webhook with name {webhook_name}.""")
        else:
            await ctx.send(f"""Text channel has already been setup with id, {res[0]['webhook_id']}
                            Please run z!rename <name-of-new-webhook> to point subscriptions to new webhook.""")

    @tc.command()
    async def search(self, ctx, query: str):
        id = f'{ctx.guild.id}:{ctx.channel.id}'
        res = self.connection.select_records_by_id(id=id)
        if not res:
            await ctx.send("""You have not setup this channel for creating webhooks! 
                            Run ```z!tc setup <name of webhook>``` to create a webhook for this channel.""")
            return
        webhook_id = res[0]['webhook_id']
        webhook = await self.bot.fetch_webhook(webhook_id)
        users = self.twitcasting.search_users(words=query, limit=3)
        embeds = []
        for user in users:
            embed_dict = {
                'title': user.name,
                'url': f'https://twitcasting.tv/{user.screen_id}',
                'description': f'''ID: {user.id}
                                Screen ID: {user.screen_id}
                                Profile: {user.profile}\n''',
                'author': {'name': user.screen_id,
                           'icon_url': user.image},
                'thumbnail': {'url': user.image}
            }
            embeds.append(Embed.from_dict(embed_dict))
        await webhook.send(embeds=embeds)

    @tc.command()
    async def add(self, ctx, user_id: str):
        id = f'{ctx.guild.id}:{ctx.channel.id}'
        res = self.connection.select_records_by_id(id=id)
        if not res:
            await ctx.send("""You have not setup this channel for creating webhooks! 
                    Run ```z!tc setup <name of webhook>``` to create a webhook for this channel.""")
            return
        webhook_id = res[0]['webhook_id']
        users = self.twitcasting.search_users(words=user_id, limit=1)
        assert(users[0].id == user_id)
        self.twitcasting.register_webhook(user_id=user_id)
        self.connection.insert_record(id=id, webhook_id=webhook_id, user_id=user_id, name=users[0].screen_id)
        await ctx.send(content=f"Added {users[0].screen_id} ({user_id}) to list of webhooks!")

    @tc.command()
    async def list(self, ctx):
        id = f'{ctx.guild.id}:{ctx.channel.id}'
        users = self.connection.select_records_by_id(id=id)
        user_embed = Embed(title='Registered Users')
        for user in users:
            if user['user_id']:
                user_embed.add_field(name=user['name'],
                                     value=f'ID: {user["user_id"]}',
                                     inline=False)
        await ctx.send(embed=user_embed)

    @tc.command()
    async def remove(self, ctx, user_id: str):
        id = f'{ctx.guild.id}:{ctx.channel.id}'
        self.connection.delete_record(id=id, user_id=user_id)
        self.twitcasting.remove_webhook(user_id=user_id)
        await ctx.send(f"Deleted user {user_id} from list of webhooks.")

    @tc.command(hidden=True)
    async def update(self, ctx):
        id = f'{ctx.guild.id}:{ctx.channel.id}'
        users = self.connection.select_records_by_id(id=id)
        for user in users:
            if user['user_id']:
                new_user_info = self.twitcasting.search_users(words=user['user_id'], limit=1)
                self.connection.update_name_of_record(user_id=user['user_id'], name=new_user_info[0].screen_id)

    @tc.command()
    async def rename(self, ctx):
        id = f'{ctx.guild.id}:{ctx.channel.id}'

    async def broadcast(self, request):
        request = await request.json()
        movie, user = self.twitcasting.parse_incoming_webhook(request)
        res = self.connection.select_records_by_user_id(user_id=user.id)
        message = f'{user.screen_id} has went live!' if user.is_live else f'{user.screen_id} has gone offline!'
        embed_dict = {
            'title': message,
            'description': f'**Title**: [{movie.title}]({movie.link})\n{movie.subtitle}',
            'author': {'name': user.screen_id,
                       'icon_url': user.image},
            'thumbnail': {'url': user.image}
        }
        embed = Embed.from_dict(embed_dict)
        for row in res:
            webhook_id = row['webhook_id']
            webhook = await self.bot.fetch_webhook(webhook_id=webhook_id)
            await webhook.send(embed=embed, avatar_url=user.image)
        return web.Response(status=200)
