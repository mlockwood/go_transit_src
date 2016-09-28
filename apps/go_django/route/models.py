from django.db import models

from stop.models import Stop


class Holiday(models.Model):
    id = models.IntegerField(primary_key=True)
    holiday = models.DateField()

    def __str__(self):
        return self.holiday.strftime('%Y-%m-%d')

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class Joint(models.Model):
    id = models.IntegerField(primary_key=True)
    routes = models.CharField(max_length=12)
    description = models.TextField()
    service = models.ForeignKey('Service')
    headway = models.IntegerField(default=1200)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class Route(models.Model):
    id = models.IntegerField(primary_key=True)
    short_name = models.CharField(max_length=12)
    long_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7)
    text_color = models.CharField(max_length=7)

    def __str__(self):
        return 'Route {}'.format(self.id)

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class Schedule(models.Model):
    id = models.IntegerField(primary_key=True)
    joint = models.ForeignKey('Joint')
    start = models.TimeField(default='07:00:00')
    end = models.TimeField(default='18:00:00')
    offset = models.IntegerField(default=0)

    def __str__(self):
        return 'Schedule {} for Joint {}'.format(str(self.id), str(self.joint))

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class Segment(models.Model):
    id = models.IntegerField(primary_key=True)
    route = models.ForeignKey('Route')
    direction = models.CharField(max_length=80)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return 'Segment {} | Route {} to {}'.format(self.id, self.route.id, self.direction)

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class SegmentOrder(models.Model):
    INBOUND = 'I'
    LOOP = 'L'
    OUTBOUND = 'O'
    DIR_TYPE_CHOICES = (
        (INBOUND, 'Inbound (return) trip'),
        (LOOP, 'Loop (one-direction) trip that returns to trip origin'),
        (OUTBOUND, 'Outbound (originating) trip')
    )
    schedule = models.ForeignKey('Schedule')
    order = models.IntegerField(default=0)
    segment = models.ForeignKey('Segment')
    dir_type = models.CharField(max_length=1, choices=DIR_TYPE_CHOICES, default=OUTBOUND)

    class Meta:
        unique_together = ('schedule', 'order')


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

    def __str__(self):
        return '{} to {}; {}'.format(self.start_date, self.end_date, self.text)

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class StopSeq(models.Model):
    NON_TIMED = 0
    TIMED = 1
    TIMEPOINT_CHOICES = (
        (NON_TIMED, 'Times are considered approximate.'),
        (TIMED, 'Times are considered exact.')
    )
    segment = models.ForeignKey('Segment')
    stop = models.ForeignKey('stop.Stop')
    arrive = models.IntegerField(default=0)
    depart = models.IntegerField(default=0)
    timed = models.IntegerField(choices=TIMEPOINT_CHOICES, default=NON_TIMED)

    class Meta:
        unique_together = ('segment', 'arrive')

    def __str__(self):
        return '{} -- {} @ {}'.format(self.segment.id, self.stop, self.arrive)


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


class Trip(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    schedule = models.ForeignKey('Schedule')
    start_loc = models.IntegerField()
    end_loc = models.IntegerField()
    start_time = models.DateTimeField()
    driver = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        super(self.__class__, self).save(*args, **kwargs)