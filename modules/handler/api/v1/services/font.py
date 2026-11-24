from django.core.files.uploadedfile import UploadedFile

from modules.handler.models import Font


class FontService:
    @staticmethod
    def create(*, user_id: int, name: str, uploaded_file: UploadedFile) -> Font:
        font = Font(user_id=user_id, name=name, file=uploaded_file)
        font.full_clean(exclude=["file"])
        font.save()
        return font
