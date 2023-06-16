milatcm = 10
# mingridstep_h = 4
# mingridstep_v = 3
mingridstep_h = 4
mingridstep_v = 2
rlist = [0.1, 0.2, 0.25, 0.5, 1]


def minmilstep(click, mingridstep):
    pixatclick = milatcm / click
    minmilstep = mingridstep / pixatclick
    return minmilstep


def roundmilstep(milstep):
    step = abs(milstep)
    # rlist = [0.1, 0.2, 0.25, 0.5, 1]
    # rlist = [0.1, 0.2, 0.25, 0.3, 0.5, 1]
    # rlist = [0.1, 0.25, 0.5, 1]
    if step == 0:
        return 0
    if step > max(rlist):
        return roundmilstep(step / 10) * 10
    elif step < min(rlist):
        return roundmilstep(step * 10) / 10
    for v in rlist:
        if v >= step:
            return v
    return None
