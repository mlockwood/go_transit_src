

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



