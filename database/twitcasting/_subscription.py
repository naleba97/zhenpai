from .subscription import Subscription
from .twitcast_user import TwitcastUser
from ..core.user import User
from ..core.channel import Channel
from ..core.guild import Guild
from typing import List


class _DatabaseSubscriptions:
    def get_sub(self, channel_id: str, twitcast_user_id: str) -> Subscription:
        """
        Retrieves a subscription associated with a Discord text channel and Twitcast user ID.
        :param channel_id: the id of the text channel.
        :param guild_id: the ID of the guild.
        :param twitcast_user_id: the ID of the Twitcast user.
        :return: a Subscription record associated with the Twitcast user and channel_id.
        """
        return self.session.query(Subscription) \
            .filter(Subscription.channel_id == channel_id) \
            .filter(Subscription.twitcast_user_id == twitcast_user_id) \
            .first()

    def get_subs_by_guild(self, guild_id: str) -> List[Subscription]:
        """
        Retrieves all subscriptions associated with a Discord guild/server.
        :param guild_id: the ID of the Discord guild/server
        :return: list of Subscription records associated with a Discord guild/server.
        """
        return self.session.query(Subscription) \
            .filter(Subscription.guild_id == guild_id) \
            .all()

    def get_subs_by_channel(self, channel_id: str) -> List[Subscription]:
        """
        Retrieves all subscriptions associated with a Discord text channel.
        :param channel_id: the ID of the Discord text channel.
        :return: list of Subscription records associated with a Discord text channel.
        """
        return self.session.query(Subscription)\
            .filter(Subscription.channel_id == channel_id)\
            .all()

    def get_subs_by_user_id(self, twitcast_user_id: str) -> List[Subscription]:
        """
        Retrieves all subscriptions to a particular Twitcasting user.
        :param twitcast_user_id: the ID of the Twitcasting user.
        :return: list of Subscriptions records associated with a Twitcasting user.
        """
        return self.session.query(Subscription)\
            .filter(Subscription.twitcast_user_id == twitcast_user_id)\
            .all()

    def count_subs_by_user_id(self, twitcast_user_id: str) -> int:
        """
        Counts the number of text channels that have subscribed to a Twitcasting user.
        :param twitcast_user_id: the ID of the Twitcasting user.
        :return: the number of subscribed text channels.
        """
        return self.session.query(Subscription) \
            .filter(Subscription.twitcast_user_id == twitcast_user_id) \
            .count()

    def remove_sub(self, sub: Subscription):
        """
        Adds a subscription from a text channel.
        :param sub: the subscription to add to the database.
        :return:
        """
        self.session.delete(sub)

    def remove_sub_from_channel_by_user_id(self, channel_id: str, twitcast_user_id: str):
        """
        Removes a subscription to the provided Twitcast user from a Discord text channel.
        :param channel_id: the ID of the Discord text channel
        :param twitcast_user_id: the ID of the Twitcasting user.
        :return:
        """
        self.session.query(Subscription)\
            .filter(Subscription.channel_id == channel_id)\
            .filter(Subscription.twitcast_user_id == twitcast_user_id)\
            .delete()

    def remove_all_subs_from_channel(self, channel_id: str):
        """
        Removes all subscriptions from a Discord text channel.
        :param channel_id: the ID of the text channel.
        :return:
        """
        self.session.query(Subscription)\
            .filter(Subscription.channel_id == channel_id)\
            .delete()

    def add_sub(self, sub: Subscription):
        """
        Adds a subscription to a text channel.
        :param sub: the subscription to add to the database.
        :return:
        """
        self.session.add(sub)

    def update_name_of_twitcast_user(self, twitcast_user_id: str, twitcast_name: str):
        """
        Updates the name of a Twitcasting user in the database.
        :param twitcast_user_id: the ID of the user whose names will be updated.
        :param twitcast_name: the name of the Twitcasting user.
        :return:
        """
        for sub in self.get_subs_by_user_id(twitcast_user_id):
            sub.twitcast_name = twitcast_name
