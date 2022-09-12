milatcm = 10
mingridstep_h = 4
mingridstep_v = 3


def minmilstep(click, mingridstep):
    pixatclick = milatcm / click
    minmilstep = mingridstep / pixatclick
    return minmilstep


def roundmilstep(milstep):
    rlist = [0.1, 0.2, 0.25, 0.3, 0.5, 1]
    if milstep > max(rlist):
        return roundmilstep(milstep / 10) * 10
    elif milstep < min(rlist):
        return roundmilstep(milstep * 10) / 10
    for v in rlist:
        if v >= milstep:
            return v
    return None
