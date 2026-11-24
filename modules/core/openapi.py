from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CsrfExemptSessionAuthenticationScheme(OpenApiAuthenticationExtension):
    """Tells drf-spectacular how to document `CsrfExemptSessionAuthentication`
    - otherwise identical to DRF's own session auth, just without the CSRF
    requirement (see `modules/core/authentication.py` for why)."""

    target_class = "modules.core.authentication.CsrfExemptSessionAuthentication"
    name = "sessionAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "sessionid",
            "description": (
                "Session-cookie auth. Call POST /api/core/v1/auth/ first - "
                "the browser/client then sends the `sessionid` cookie "
                "automatically on every subsequent request."
            ),
        }
