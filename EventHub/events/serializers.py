from rest_framework import serializers
from .models import Event, Reservation
# Add a computed field reservations_count using SerializerMethodField, and validate that available_seats does not exceed total_seats.

class EventSerializer(serializers.ModelSerializer):
      reservations_count = serializers.SerializerMethodField()

      class Meta:
            model = Event
            fields = '__all__'

      def get_reservations_count(self, obj):
            return Reservation.objects.filter(event=obj).count()

      def validate(self, data):
            total_seats = data.get(
                  'total_seats',
                  self.instance.total_seats if self.instance else 0
            )

            available_seats = data.get(
                  'available_seats',
                  self.instance.available_seats if self.instance else 0
            )

            if available_seats > total_seats:
                  raise serializers.ValidationError({
                  'available_seats':
                        'available_seats cannot exceed total_seats.'
                  })

            if total_seats < 0:
                  raise serializers.ValidationError({
                        'total_seats': 'total_seats cannot be negative.'
                  })

            return data

class ReservationSerializer(serializers.ModelSerializer):
      class Meta:
            model = Reservation
            fields = '__all__'

            read_only_fields = ('status','created_at')

      def validate(self, data):
            if data.get('number_of_seats', 0) <= 0:
                  raise serializers.ValidationError({
                        'number_of_seats': 'number_of_seats must be greater than zero.'
                  })
            return data

      def validate_number_of_seats(self, value):
            if value <= 0:
                  raise serializers.ValidationError(
                        'number_of_seats must be greater than zero.'
                  )
            return value

      def validate_event(self, data):
            event = data.get(
                  'event', 
                  self.instance.event if self.instance else None
            )

            if not event:
                  raise serializers.ValidationError({
                        'event': 'Event must be specified.'
                  })

            if event.status not in ('upcoming', 'ongoing'):
                  raise serializers.ValidationError({
                        'event': f'Cannot reserve seats for a {event.status} event.'
                  })

            seats = data.get(
                  'seats_reserved',
                  self.instance.seats_reserved if self.instance else 0
            )

            if not self.instance and seats > event.available_seats:
                  raise serializers.ValidationError({
                        'seats_reserved': (
                        f'Only {event.available_seats} seat(s) available.'
                  )
            })

            return data

      def create(self, validated_data):
            event = validated_data['event']
            seats_reserved = validated_data['seats_reserved']

            if seats_reserved > event.available_seats:
                  raise serializers.ValidationError({
                        'seats_reserved': (
                        f'Only {event.available_seats} seat(s) available.'
                  )
            })

            event.available_seats -= seats_reserved
            event.save()

            reservation = Reservation.objects.create(**validated_data)
            return reservation
