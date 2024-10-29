from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import (
    ResetPasswordForm as DefaultPasswordResetForm,
    default_token_generator,
)
from allauth.account.internal import flows
from allauth.account.adapter import DefaultAccountAdapter, get_adapter
from allauth.account.utils import (
    filter_users_by_email,
    user_pk_to_url_str,
    user_username,
)

from .functions import get_reset_password_from_params_url


class AllAuthPasswordResetForm(DefaultPasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        email = get_adapter().clean_email(email)
        self.users = filter_users_by_email(email, is_active=True, prefer_verified=True)
        return self.cleaned_data["email"]

    def save(self, request, **kwargs) -> str:
        email = self.cleaned_data["email"]
        if not self.users:
            flows.signup.send_unknown_account_mail(request, email)
            return email

        adapter: DefaultAccountAdapter = get_adapter()
        token_generator = kwargs.get("token_generator", default_token_generator)
        for user in self.users:
            temp_key = token_generator.make_token(user)

            uid = user_pk_to_url_str(user)
            url = get_reset_password_from_params_url(request, key=temp_key, uid=uid)
            context = {
                "user": user,
                "password_reset_url": url,
                "uid": uid,
                "key": temp_key,
                "request": request,
            }

            if (
                app_settings.AUTHENTICATION_METHOD
                != app_settings.AuthenticationMethod.EMAIL
            ):
                context["username"] = user_username(user)
            adapter.send_password_reset_mail(user, email, context)
        return email
