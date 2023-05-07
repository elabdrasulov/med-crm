from .models import Appointment
from rest_framework.response import Response

def booked_up(book_date, book_time, doctor):
    """
    Если такое время уже занято, 
    то выводит респонс о том, что время забронировано
    """

    entries = Appointment.objects.filter(doctor=doctor)
    if entries:
        for e in entries:
            if str(e.date) == str(book_date):
                if str(e.time) == str(e.TIME[int(book_time)][-1]):
                    return True
    else:
        return False
