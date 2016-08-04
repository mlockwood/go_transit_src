from django.db import models

from stop.models import Stop


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


class Holiday(models.Model):
    id = models.IntegerField(primary_key=True)
    holiday = models.DateField()

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


class Segment(models.Model):
    joint = models.ForeignKey('Joint')
    schedule = models.ForeignKey('Schedule')
    dir_order = models.IntegerField()
    route = models.IntegerField()
    name = models.CharField(max_length=12)
    direction = models.ForeignKey('Direction')

    class Meta:
        unique_together = ('joint', 'schedule', 'name')


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


class StopSeq(models.Model):
    segment = models.CharField(max_length=12)
    stop = models.ForeignKey('stop.Stop')
    arrive = models.IntegerField(default=0)
    depart = models.IntegerField(default=0)
    timed = models.IntegerField()
    display = models.IntegerField()
    load_seq = models.IntegerField()
    destination = models.BooleanField()

    class Meta:
        unique_together = ('segment', 'load_seq')


class StopTime(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    trip = models.ForeignKey('Trip')
    stop = models.ForeignKey('stop.Stop')
    arrive = models.CharField(max_length=8)
    depart = models.CharField(max_length=8)
    gtfs_depart = models.CharField(max_length=8)
    arrive_24p = models.CharField(max_length=8)
    depart_24p = models.CharField(max_length=8)
    gtfs_depart_24p = models.CharField(max_length=8)
    order = models.IntegerField()
    timepoint = models.IntegerField()
    pickup = models.IntegerField()
    dropoff = models.IntegerField()
    display = models.IntegerField()


class Transfer(models.Model):
    joint = models.ForeignKey('Joint')
    from_stop = models.ForeignKey('stop.Stop', related_name='from_stop')
    to_stop = models.ForeignKey('stop.Stop', related_name='to_stop')
    transfer_type = models.IntegerField()


class Trip(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    schedule = models.ForeignKey('Schedule')
    direction = models.ForeignKey('Direction')
    start_loc = models.IntegerField()
    end_loc = models.IntegerField()
    start_time = models.DateTimeField()
    driver = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        super(self.__class__, self).save(*args, **kwargs)