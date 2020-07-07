from .user import User


class _DatabaseUsers:
    def add_user(self, user: User):
        self.session.add(user)
    
    def get_user(self, user_id: int) -> User:
        return self.session.query(User)\
                .filter(User.user_id == user_id)\
                .first()
    
    def delete_user(self, user_id: int):
        self.session.query(User) \
            .filter(User.user_id == user_id) \
            .delete()
