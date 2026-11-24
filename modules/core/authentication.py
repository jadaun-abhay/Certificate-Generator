from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """`SessionAuthentication` without CSRF enforcement.

    `CsrfViewMiddleware` is deliberately disabled for this project, but DRF's
    default `SessionAuthentication` enforces CSRF on its own regardless of
    that middleware's on/off state - without this override, every
    session-authenticated write would be permanently rejected with no way to
    ever pass the check, since nothing issues a CSRF token in the first
    place. This is a deliberate, explicit tradeoff: it reopens the
    cross-site request forgery exposure CSRF protection exists to close for
    cookie-authenticated requests.
    """

    def enforce_csrf(self, request) -> None:
        return None
