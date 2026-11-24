from django.db.models import QuerySet

from modules.handler.models import Font


class FontSelector:
    @staticmethod
    def list_for_user(user_id: int) -> QuerySet[Font]:
        return Font.objects.filter(user_id=user_id)

    @staticmethod
    def get_by_id(user_id: int, font_id: int) -> Font | None:
        return Font.objects.filter(user_id=user_id, id=font_id).first()
