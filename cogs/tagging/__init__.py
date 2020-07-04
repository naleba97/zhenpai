from .tagging import Tagging


def setup(bot):
    bot.add_cog(Tagging(bot))
