import math
import os


def stitch_dicts(a, b, lax=None):
    stitch = {}
    if len(a) != (len(b) + 1):
        return 'Sizes incongruent problem'
    for key in b:
        a_key = min(a.keys(), key=lambda k: abs(k-key))
        if a_key in stitch:
            return 'Duplicate problem'
        if lax or lax == 0:
            if abs(key - a_key) > lax:
                print(a, b)
                return 'Lax problem'
        stitch[b[key]] = a[a_key]
    return stitch


def stack(a, n, divisible='rows', structure='rows'):
        i = 0
        b = []
        c = []
        divisor = n if divisible == 'rows' else math.ceil(len(a) / n)
        for entry in a:
            if i < divisor:
                c.append(entry)
                i += 1
            elif i == divisor:
                b.append(c)
                c = [entry]
                i = 1
        while i < divisor:
            c.append('')
            i += 1
        b.append(c)
        if structure == 'rows':
            return [list(x) for x in zip(*b)]
        else:
            return b

