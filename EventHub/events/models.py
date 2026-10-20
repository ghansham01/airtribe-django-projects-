from django.db import models

# Create your models here.
class Event(models.Model):
      STATUS_CHOICES = [
            ('upcoming', 'Upcoming'),
            ('ongoing', 'Ongoing'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
      ]

      title = models.CharField(max_length=200)
      venue = models.CharField(max_length=200)
      date = models.DateField()

      total_seats = models.PositiveIntegerField()
      available_seats = models.PositiveIntegerField()

      status = models.CharField(
            max_length=10,
            choices=STATUS_CHOICES,
            default='upcoming',
      )

      created_at = models.DateTimeField(auto_now_add=True)  

      def __str__(self):
            return f"{self.title} at {self.venue} on {self.date}"

      class Meta:
            ordering = ['-date']


class Reservation(models.Model):
      STATUS_CHOICES = [
            ('CONFIRMED', 'Confirmed'),
            ('CANCELLED', 'Cancelled'),
      ]

      event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reservations')
      attendee_name = models.CharField(max_length=200)
      attendee_email = models.EmailField()
      seats_reserved = models.PositiveIntegerField()

      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
            
            return f"{self.attendee_name} - {self.event.title} ({self.seats_reserved} seats)"


      class Meta:
            ordering = ['-created_at']


'''
            Event -> Reservation
            
the event is linked to its reservations through a foreign key.
'''