from django.core.exceptions import ValidationError
from django.db import transaction

from modules.drive.models import File
from modules.handler.models import CertificateTemplate, TemplateField


class TemplateService:
    @staticmethod
    @transaction.atomic
    def create(
        *, user_id: int, name: str, file: File, fields: list[dict]
    ) -> CertificateTemplate:
        if file.user_id != user_id:
            raise ValidationError("Template file does not belong to this user.")

        template = CertificateTemplate(user_id=user_id, name=name, file=file)
        template.full_clean()
        template.save()

        for field_data in fields:
            field = TemplateField(template=template, **field_data)
            field.full_clean()
            field.save()

        return template
