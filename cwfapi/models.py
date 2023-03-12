from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=32, null=False, unique=False)
    location = models.CharField(max_length=32, null=False, unique=False)
    description = models.CharField(max_length=256, null=False, unique=False)

    class Meta:
        unique_together = (('name', 'location'))

class Event(models.Model):
    crypto = models.CharField(max_length=32, blank=False)
    time = models.DateTimeField(null=False, blank=False)
    end_time = models.DateTimeField(null=False, blank=False)
    price_start = models.IntegerField(null=False, blank=False)
    price_end = models.IntegerField(null=True, blank=True)
    group = models.ForeignKey(Group, related_name="events", on_delete=models.CASCADE)
