from modules.core.models import User


class UserSelector:
    @staticmethod
    def get_by_email(email: str) -> User | None:
        return User.objects.filter(email__iexact=email).first()
