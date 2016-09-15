from django.db import models


class Stop(models.Model):
    id = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=64, default='Unnamed')
    location = models.CharField(max_length=3)
    description = models.TextField(blank=True, default='')
    geography = models.ForeignKey('Geography')
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    operating = models.DateField(null=True, blank=True)
    speed = models.IntegerField(default=25)
    available = models.IntegerField(default=2)

    def __str__(self):
        return '({}) {}'.format(self.id, self.name)


class Geography(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    minimum = models.CharField(max_length=3)
    maximum = models.CharField(max_length=3)

    def __str__(self):
        return '({}) {}'.format(self.id, self.name)

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
    DESIGN_A = 'A'
    DESIGN_B = 'B'
    SIGN_DESIGN_CHOICES = (
        (DESIGN_A, '2015 Sign Design - Large Route Circles.'),
        (DESIGN_B, '2016 Sign Design - Top Green Stripe, Modular Routes.')
    )
    stop = models.OneToOneField('Stop')
    design = models.CharField(max_length=1, choices=SIGN_DESIGN_CHOICES)
    midi_guide = models.BooleanField(default=False)