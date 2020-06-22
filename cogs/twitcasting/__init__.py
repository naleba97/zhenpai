import threading

from .twitcasting import *
from aiohttp import web
import asyncio



def setup(bot):
    twitcasting_cog = Twitcasting(bot)
    bot.add_cog(twitcasting_cog)

    app = web.Application()
    app.router.add_post('/', twitcasting_cog.broadcast)

    async def run_server():
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_server())
