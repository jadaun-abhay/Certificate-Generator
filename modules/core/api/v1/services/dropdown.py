from modules.core.models import Dropdown


class DropdownService:
    @staticmethod
    def create(*, label: str, parent: Dropdown | None = None, **fields) -> Dropdown:
        return Dropdown.objects.create(label=label, parent=parent, **fields)

    @staticmethod
    def update(*, dropdown: Dropdown, **fields) -> Dropdown:
        for field, value in fields.items():
            setattr(dropdown, field, value)
        dropdown.save(update_fields=[*fields.keys(), "updated_at"])
        return dropdown
