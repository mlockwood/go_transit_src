from django.db import models


class Stop(models.Model):
    STOP = 0
    STATION = 1
    LOCATION_TYPE_CHOICES = (
        (STOP, 'Stop location where passengers board or disembark from a transit vehicle.'),
        (STATION, 'Station, physical structure, or area that contains more than one stop.')
    )
    PREVIOUS = 0
    CURRENT = 1
    IMMINENT = 2
    POTENTIAL = 3
    FUTURE = 4
    AVAILABLE_CHOICES = (
        (PREVIOUS, 'Stop was previously available and is no longer operating.'),
        (CURRENT, 'Stop is currently available.'),
        (IMMINENT, 'Stop is not currently available but will be soon.'),
        (POTENTIAL, 'Stop has been scoped and there is a current effort to plan for it.'),
        (FUTURE, 'Stop has been identified but there is no current plan to implement it.')
    )
    id = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=64, default='Unnamed')
    location = models.CharField(max_length=3)
    location_type = models.IntegerField(choices=LOCATION_TYPE_CHOICES, default=STOP)
    description = models.TextField(blank=True, null=True, default='')
    geography = models.ForeignKey('Geography')
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    operating = models.DateField(null=True, blank=True)
    speed = models.IntegerField(default=25)
    available = models.IntegerField(choices=AVAILABLE_CHOICES, default=IMMINENT)

    def __str__(self):
        return '{} ({})'.format(self.name, self.id)


class Geography(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    minimum = models.CharField(max_length=3)
    maximum = models.CharField(max_length=3)

    def __str__(self):
        return '{} ({})'.format(self.name, self.id)

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class Shelter(models.Model):
    CANTILEVER = 'C'
    GABLE = 'G'
    NIAGARA = 'N'
    SHELTER_CHOICES = (
        (CANTILEVER, 'Cantilever model.'),
        (NIAGARA, 'Niagara model.'),
        (GABLE, 'Gable model.')
    )
    stop = models.OneToOneField('Stop')
    design = models.CharField(max_length=1, choices=SHELTER_CHOICES)
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=80)
    solar_lighting = models.BooleanField(default=False)
    ad_panel = models.BooleanField(default=False)


class Sign(models.Model):
    GROUND = 'G'
    PLATE = 'P'
    ANCHOR_CHOICES = (
        (GROUND, 'Sign is attached to a ground anchor.'),
        (PLATE, 'Sign is attached to a plate anchor.')
    )
    DESIGN_A = 'A'
    DESIGN_B = 'B'
    SIGN_DESIGN_CHOICES = (
        (DESIGN_A, '2015 Sign Design - Large Route Circles.'),
        (DESIGN_B, '2016 Sign Design - Top Green Stripe, Modular Routes.')
    )
    stop = models.OneToOneField('Stop')
    anchor = models.CharField(max_length=1, choices=ANCHOR_CHOICES, default=GROUND)
    design = models.CharField(max_length=1, choices=SIGN_DESIGN_CHOICES, default=DESIGN_B)
    midi_guide = models.BooleanField(default=False)