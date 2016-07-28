from django.db import models


class Stop(models.Model):
    id = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=64, default='Unnamed')
    location = models.CharField(max_length=3)
    description = models.TextField(blank=True, default='')
    geography = models.ForeignKey('Geography')
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    signage = models.CharField(max_length=20, default='Undecided')
    shelter = models.CharField(max_length=20, default='Undecided')
    operating = models.DateField(null=True, blank=True)
    speed = models.IntegerField(default=25)
    available = models.IntegerField(default=2)

    def __str__(self):
        return '({}) {}'.format(self.stop_id, self.name)

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class Geography(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    minimum = models.CharField(max_length=3)
    maximum = models.CharField(max_length=3)

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class Inventory(models.Model):
    AVAILABLE = 'A'
    DAMAGED = 'D'
    FRAME = 'F'
    GROUND = 'G'
    INSPECT = 'I'
    NOT_REVIEWED = 'N'
    POSTED = 'P'
    REPLACE = 'R'
    SWAP = 'S'
    UNAVAILABLE = 'U'
    CODE_CHOICES = (
        (AVAILABLE, 'Sign is available but not in the field.'),
        (DAMAGED, 'Sign is damaged but does not require replacement.'),
        (FRAME, 'Sign is in a temporary frame.'),
        (GROUND, 'Sign is in a temporary frame but the ground has been dug, awaiting post.'),
        (INSPECT, 'Sign post or anchor requires inspection by JBLM shop.'),
        (NOT_REVIEWED, 'Sign was not reviewed.'),
        (POSTED, 'Sign is posted and up to standard.'),
        (REPLACE, 'Sign has sustained damaged and needs to be replaced.'),
        (SWAP, 'Sign needs to be swapped due to a pilot or style upgrade.'),
        (UNAVAILABLE, 'Sign needs to be placed but is currently unavailable.'),
    )
    stop = models.ForeignKey('Stop')
    timestamp = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=1, choices=CODE_CHOICES)
    notes = models.TextField(blank=True)

