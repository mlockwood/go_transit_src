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


class Holiday(models.Model):
    id = models.IntegerField(primary_key=True)
    holiday = models.DateField()

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
    origin = models.ForeignKey('stop.Stop', related_name='direction_origin')
    destination = models.ForeignKey('stop.Stop', related_name='direction_destination')

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
    id = models.CharField(max_length=255, primary_key=True)
    joint = models.ForeignKey('Joint')
    schedule = models.ForeignKey('Schedule')
    segment = models.ForeignKey('Segment')
    direction = models.ForeignKey('Direction')
    start_loc = models.IntegerField()
    end_loc = models.IntegerField()
    base_time = models.DateTimeField()
    start_time = models.DateTimeField
    end_time = models.DateTimeField
    driver = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class StopTime(models.Model):
    trip = models.ForeignKey('Trip')
    stop = models.ForeignKey('stop.Stop')
    arrive = models.DateTimeField()
    depart = models.DateTimeField()
    gtfs_depart = models.DateTimeField()
    arrive_24p = models.DateTimeField()
    depart_24p = models.DateTimeField()
    gtfs_depart_24p = models.DateTimeField()
    order = models.IntegerField()
    timepoint = models.IntegerField()
    pickup = models.IntegerField()
    dropoff = models.IntegerField()
    display = models.IntegerField()