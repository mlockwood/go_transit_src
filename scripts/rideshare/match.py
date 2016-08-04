import datetime
import hashlib


class Rider:

    objects = {}

    def __init__(self, first, last, dod, home_gps, home_county, work_gps, work_county, work_geo, employer, workdays,
                 start, end, van):
        if any(k in vars(self) for k in vars()):
            raise NameError('Preventing method overwrite for a Rider object')
        vars(self).update((k,v) for k,v in vars().items() if k != 'self')

        self.id = hashlib.sha512('{}_{}_{}'.format(first, last, ''.join(home_gps)))
        self.start = False # ?????
        Rider.objects[self.id] = self

    def match(self):
        for van in Van.objects.values():
            # If the rider is eligible for the vanpool by home or work county and the van is not full
            if (self.home_county == van.agency or self.work_county == van.agency) and len(van.riders) < van.occupancy:
                # Check times
                pass


class Van:

    objects = {}

    def __init__(self, id, agency, occupancy, origin=None, worksite=None, arrive=None, depart=None):
        self.id = id
        self.agency = agency
        self.occupancy = occupancy
        self.origin = origin
        self.worksite = worksite
        self.arrive = arrive
        self.depart = depart
        self.riders = {}
        Van.objects[id] = self


class Agency:

    objects = {}

    def __init__(self, name):
        self.name = name
        self.vans = {}
        Agency.objects[name] = self

