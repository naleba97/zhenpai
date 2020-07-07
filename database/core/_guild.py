from .guild import Guild


class _DatabaseGuilds:
    def add_guild(self, guild: Guild):
        self.session.add(guild)

    def get_guild(self, guild_id: int) -> Guild:
        return self.session.query(Guild) \
            .filter(Guild.guild_id == guild_id) \
            .first()

    def delete_guild(self, guild_id: int):
        self.session.query(Guild) \
            .filter(Guild.guild_id == guild_id) \
            .delete()
