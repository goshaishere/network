from django.utils.encoding import force_str
from rest_framework.exceptions import APIException, ErrorDetail


class CaptchaRequired(APIException):
    """400 с полями detail и code (строковый detail у APIException в JSON без code)."""

    status_code = 400
    default_detail = "Требуется пройти капчу."
    default_code = "captcha_required"

    def __init__(self, detail=None, code=None):
        if detail is None:
            msg = force_str(self.default_detail)
            c = code or self.default_code
            detail = {
                "detail": ErrorDetail(msg, code=c),
                "code": ErrorDetail(c, code=c),
            }
        super().__init__(detail=detail, code=code)
