

def booked_up(book_date, book_time, doctor):
    """
    Если такое время уже занято, 
    то выводит респонс о том, что время забронировано
    """

    entries = Appointment.objects.filter(doctor=doctor)
    if entries:
        for e in entries:
            if str(e.date) == str(book_date) and str(e.book_time) == str(book_time):
                return Response(
                    """
                    This time slot is already booked for this doctor. 
                    Please choose another time or day
                    """
                )
