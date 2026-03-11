from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class SpecialCharacterValidator:
    def validate(self, password, user=None):
        special_chars = r'!@#$%^&*(),.?":{}|<>'
        if not any(char in special_chars for char in password):
            raise ValidationError(
                _("Your password must contain at least one special character."),
                code="password_no_special_char",
            )

    def get_help_text(self):
        return _("Your password must contain at least one special character.")
