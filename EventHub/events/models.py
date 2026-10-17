from django.db import models

# Create your models here.
class Event(models.Model):
      STATUS_CHOICES = [
            ('UPCOMING', 'Upcoming'),
            ('ONGOING', 'Ongoing'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled'),
      ]

      title = models.CharField(max_length=200)
      venue = models.CharField(max_length=200)
      date = models.DateField()

      total_seats = models.PositiveIntegerField()
      available_seats = models.PositiveIntegerField()

      status = models.CharField(
            max_length=10,
            choices=STATUS_CHOICES,
            default='UPCOMING',
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

      event = models.ForeignKey(Event, on_delete=models.CASCADE)
      user = models.CharField(max_length=200)
      status = models.CharField(
            max_length=10,
            choices=STATUS_CHOICES,
            default='CONFIRMED',
      )

      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
            return (
                  f"{self.user} - {self.event.title} "
                  f"({self.status})"
            )

      class Meta:
            ordering = ['-created_at']


'''
            Event -> Reservation
            
the event is linked to its reservations through a foreign key.
'''