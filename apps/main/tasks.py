from config.celery_ import app
from django.core.mail import send_mail
from .models import Appointment


@app.task
def create_an_appointment(a_id):
    """
    Задача для отправки уведомления по электронной почте при успешном создании записи. 
    """
    entry = Appointment.objects.get(id=a_id)
    subject = f'Appointment #{a_id}'

    message = f"""
    Dear {entry.user.email},
    You have successfully made an appointment 
    with Dr.{entry.doctor.last_name} by {entry.time} on {entry.date}.
    """

    mail_sent = send_mail(subject, message, 'test@gmail.com', [entry.user.email])

    return mail_sent
