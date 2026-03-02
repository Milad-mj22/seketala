from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class WhatsAppMessage(models.Model):
    # account = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    message_text = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    # is_from_me = models.BooleanField()  # True if sent from our account
    chat_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} @ {self.timestamp}"
    
    class Meta:
        unique_together = ('receiver', 'timestamp', 'message_text', 'sender')