import math
import os
import re

from src.scripts.transit.constants import PATH


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


def csv_writer(path, file, matrix):
    if not matrix or len(matrix) == 1:
        return False

    # Set up directories and files
    if not os.path.isdir(path):
        os.makedirs(path)
    writer = open('{}/{}.csv'.format(path, file), 'w')

    # Write header
    writer.write('{}\n'.format(','.join(str(s) for s in matrix[0])))
    # Write sorted rows
    for row in sorted(matrix[1:]):
        writer.write('{}\n'.format(','.join(str(s) for s in row)))
    writer.close()
    return True

