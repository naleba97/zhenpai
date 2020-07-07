from .channel import Channel


class _DatabaseChannels:
    def add_channel(self, channel: Channel):
        self.session.add(channel)

    def get_channel(self, channel_id: int) -> Channel:
        return self.session.query(Channel) \
            .filter(Channel.channel_id == channel_id) \
            .first()

    def delete_channel(self, channel_id: int):
        self.session.query(Channel) \
            .filter(Channel.channel_id == channel_id) \
            .delete()
