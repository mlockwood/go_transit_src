from django.db import models

from stop.models import Stop


class Service(models.Model):
    id = models.IntegerField(primary_key=True)
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField()
    text = models.TextField()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class Joint(models.Model):
    id = models.IntegerField(primary_key=True)
    routes = models.CharField(max_length=12)
    description = models.TextField()
    service = models.ForeignKey('Service')
    headway = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class Schedule(models.Model):
    id = models.IntegerField(primary_key=True)
    joint = models.ForeignKey('Joint')
    start = models.TimeField()
    end = models.TimeField()
    offset = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class Direction(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    description = models.TextField()
    origin = models.ForeignKey('stop.Stop')
    destination = models.ForeignKey('stop.Stop')

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class Segment(models.Model):
    joint = models.ForeignKey('Joint')
    schedule = models.ForeignKey('Schedule')
    dir_order = models.IntegerField()
    route = models.IntegerField()
    name = models.CharField(max_length=12)
    direction = models.ForeignKey('Direction')


class StopSeq(models.Model):
    segment = models.CharField(max_length=12)
    stop = models.ForeignKey('stop.Stop')
    arrive = models.IntegerField()
    depart = models.IntegerField
    timed = models.IntegerField()
    display = models.IntegerField()
    load_seq = models.IntegerField()
    destination = models.BooleanField()


class Trip(models.Model):
    pass


class StopTime(models.Model):
    pass