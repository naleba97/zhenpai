from .twitcast_user import TwitcastUser


class _DatabaseTwitcastUsers:
    def add_user(self, twitcast_user: TwitcastUser):
        self.session.add(twitcast_user)

    def get_user(self, twitcast_user_id: int) -> TwitcastUser:
        return self.session.query(TwitcastUser) \
            .filter(TwitcastUser.twitcast_user_id == twitcast_user_id) \
            .first()

    def delete_user(self, twitcast_user_id: int):
        self.session.query(TwitcastUser) \
            .filter(TwitcastUser.twitcast_user_id == twitcast_user_id) \
            .delete()
