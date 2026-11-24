from django.db.models import QuerySet

from modules.handler.models import CertificateTemplate


class TemplateSelector:
    @staticmethod
    def list_for_user(user_id: int) -> QuerySet[CertificateTemplate]:
        return CertificateTemplate.objects.filter(user_id=user_id)

    @staticmethod
    def get_by_id(user_id: int, template_id: int) -> CertificateTemplate | None:
        return CertificateTemplate.objects.filter(
            user_id=user_id, id=template_id
        ).first()
