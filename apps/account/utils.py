from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from decouple import config

from config.celery_ import app


@app.task
def send_activation_code(user_id):

    User = get_user_model()

    user = User.objects.get(id=user_id)
    user.generate_activation_code()
    user.set_activation_code()
    activation_url = f"{config('LINK')}account/activate/{user.activation_code}"
    message = f'Activate your account, following this link {activation_url}'
    send_mail("Activate account", message, "test@gmail.com", [user.email, ])

@app.task
def password_confirm(user_id):
    
    User = get_user_model()
    
    user = User.objects.get(id=user_id)
    activation_url = f"{config('LINK')}account/forgot_password/{user.activation_code}"
    message = f"""
    Do you want to change password?
    Confirm password changes: {activation_url}
    """
    send_mail(
        "Please confirm new changes", 
        message, "test@gmail.com", [user.email, ]
    )
