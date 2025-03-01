from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Hairstylist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  
    name = models.CharField(max_length=100)
    description = models.TextField()
    requires_password_reset = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Slot(models.Model):
    hairstylist = models.ForeignKey(Hairstylist, on_delete=models.CASCADE, null=True, blank=True)  
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.start_time} - {self.end_time} with {self.hairstylist.name if self.hairstylist else 'No Hairstylist'}"



class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Booking for {self.user.username} on {self.slot.start_time}"

    def send_confirmation_email(self):
        from django.core.mail import send_mail
        from django.conf import settings

        subject = "Booking Confirmation"
        message = f"Dear {self.user.username},\n\nYour booking for {self.slot.hairstylist.name} at {self.slot.start_time} has been confirmed.\n\nThank you for booking with us!"
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [self.user.email],
            fail_silently=False,
        )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Booking for {self.user.username} on {self.slot.start_time}"

    def send_confirmation_email(self):
        from django.core.mail import send_mail
        from django.conf import settings

        subject = "Booking Confirmation"
        message = f"Dear {self.user.username},\n\nYour booking for {self.slot.hairstylist.name} at {self.slot.start_time} has been confirmed.\n\nThank you for booking with us!"
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [self.user.email],
            fail_silently=False,
        )
