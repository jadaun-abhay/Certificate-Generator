from django.db.models import QuerySet

from modules.core.models import Dropdown


class DropdownSelector:
    @staticmethod
    def all() -> QuerySet[Dropdown]:
        return Dropdown.objects.all()

    @staticmethod
    def get_by_id(dropdown_id: int) -> Dropdown | None:
        return Dropdown.objects.filter(id=dropdown_id).first()
