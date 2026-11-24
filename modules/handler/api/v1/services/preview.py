import io

from django.conf import settings
from PIL import Image

from modules.handler.api.v1.services.rendering import render_fields
from modules.handler.models import CertificateTemplate


class PreviewService:
    @staticmethod
    def render(*, template: CertificateTemplate, sample_row: dict[str, str]) -> bytes:
        """Render one sample row onto the template and return PNG bytes.
        Nothing is persisted - this is purely for the user to eyeball before
        committing to a full (job-based) run."""
        template.file.file.open("rb")
        try:
            image = Image.open(template.file.file).convert("RGB")
        finally:
            template.file.file.close()

        rendered = render_fields(
            image,
            list(template.fields.all()),
            sample_row,
            settings.HANDLER_DEFAULT_FONT_PATH,
        )

        buffer = io.BytesIO()
        rendered.save(buffer, format="PNG")
        return buffer.getvalue()
