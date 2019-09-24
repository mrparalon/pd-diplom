from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from backend.models import ConfirmEmailToken, User
from backend.tasks import send_email

new_user_registered = Signal(
    providing_args=['user_id'],
)

new_order = Signal(
    providing_args=['user_id'],
)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param kwargs:
    :return:
    """
    title = f'Password Reset Token for {reset_password_token.user}'
    message = reset_password_token.key
    email = [reset_password_token.user.email]

    # send an e-mail to the user
    send_email.delay(title, message, email)


@receiver(new_user_registered)
def new_user_registered_signal(user_id, **kwargs):
    """
    отправляем письмо с подтрердждением почты
    """
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)
    title = f'Password Reset Token for {token.user.email}'
    message = token.key
    email = [token.user.email]

    # send an e-mail to the user
    send_email.delay(title, message, email)


@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """
    отправяем письмо при изменении статуса заказа
    """
    # send an e-mail to the user
    user = User.objects.get(id=user_id)
    title = f"Обновление статуса заказа"
    message = 'Заказ сформирован',
    email = [user.email]

    send_email.delay(title, message, email)
