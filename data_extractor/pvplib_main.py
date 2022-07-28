import math
import scipy.interpolate as sint
import scipy.signal as ssig
import math
import random
import scipy.optimize as opti
import numpy

norm = lambda x: numpy.divide(x, numpy.max(x))

def interp_filt(t,x, _filter = {"filtername" : "kaiser", 'fc' : 10, 'rdb': 10, 'width': 5}, deriv = 2, zero_time = True):
    #### Accounts for unequal sampling times, by reinterpolating x and y at multiples of the average sampling timeself. Filters the data using the filter: _filter. By default a kaiser window is used with parameters that should work for most movement data, but you can provide any filter by using a dictionnary specifying taps 'b' and 'a', see scipy.signal filtfilt documentation. Also computes naïve derivatives of y up to arbitrary order. This might work only for low derivative orders; stronger low-pass filtering might improve this behavior.

    ## Verify if arrays have been provided
    if type(x) is not numpy.ndarray or type(t) is not numpy.ndarray:
        print("Please Input numpy arrays")
        return -1

    ## For zero time_shift
    t0 = t[0]
    t = t-t0

    _diff = numpy.diff(t)[numpy.diff(t) < .1]
    TS = numpy.mean(_diff)
    interp = sint.interp1d(t,x, fill_value = 'extrapolate')
    _time = numpy.array([TS*i for i in range(0,int(t[-1]/TS +1))])

    x_interp = interp(_time)
    if _filter['filtername'] == "kaiser":
        N, beta = ssig.kaiserord(_filter['rdb'], _filter['width']*2*TS)
        taps = ssig.firwin(N, _filter['fc']*2*TS, window=('kaiser', beta))
        filtered_x = ssig.filtfilt(taps, 1, x_interp)
    else:
        b,a = _filter['b'], _filter['a']
        filtered_x = ssig.filtfilt(b,a, x_interp)
    sig = filtered_x
    if not zero_time:
        _time = _time + t0


    _time = _time.reshape(1,-1)
    sig = sig.reshape(1,-1)
    container = numpy.concatenate((_time, sig), axis=0 )

    ## Compute derivatives
    _time = numpy.concatenate((_time, numpy.array([_time[0,-1]+ TS]).reshape(1,-1)), axis = 1)

    for i in range(1,deriv+1):
        sig = numpy.concatenate((numpy.array([0]).reshape(1,-1), sig), axis = 1)
        sig = numpy.divide(numpy.diff(sig), numpy.diff(_time))
        container = numpy.concatenate((container, sig), axis = 0)
    return container, TS



def find_movs(_time, x, midpoint, single = True, discrete = True, trim = None, index = False):
    ### Try to find one point located inside each movement, to be used later. midpoint is the amplitude point that will be looked for, single is when the given trajectory is of a single movement, discrete is whether the trajectory is discrete or reciprocal, trim[n:-m] is whether you want to eliminate the first n and last m movements, index = True will output only the index of the time series, index = False will output also t and x.

    def single_find_midpoint(x, midpoint):
        _k = 0
        for k,v in enumerate(x):
            if v < midpoint:
                _k = k
            else:
                return k
        return _k

    def find_mid_discrete(x, midpoint, trim):
        _k = []
        status = False
        for k,_test in enumerate(x > midpoint):
            if  _test == True and status == False:
                # Start of movement
                _k.append(k)
                status = True
            elif _test == True and status == True:
                # During Movement
                pass
            elif _test == False and status == False:
                # idle
                pass
            elif _test == False and status == True:
                # End of Movement
                status = False
        if trim is not None:
            if trim[1] is not None:
                k = _k[trim[0]:trim[1]]
            else:
                k = _k[trim[0]:]
        else:
            k = _k
        return k


    if single:
        k = single_find_midpoint(x, midpoint)
    else:
        if discrete:
            k = find_mid_discrete(x, midpoint, trim )
        else:
            k = find_mid_discrete(x, midpoint, trim)
    if index == True:
        return k
    else:
        return [x[k], y[k], k]



def find_start(_time, x, v, midpoints, thresh = 1e-2, index = True):
    ### Start points
    startpt = []
    for k in midpoints:
        indx = k
        while abs(v[indx]) >= thresh:
            indx += -1
        startpt.append(indx)
    if index == True:
        return startpt
    else:
        return [_time[startpt],x[startpt], startpt]






def extract_single_mov_discrete(_time, x, v, starts, MIDPOINT, thresh = 1e-2, index = True):
    movs = []
    for k in range(len(starts)-1):
        _start = starts[k]
        _stop = starts[k+1]
        while x[_stop] < MIDPOINT:
            _stop += -1
        while abs(v[_stop]) > thresh:
            _stop += -1
        if index:
            movs.append([_start, _stop])
        else:
            movs.append([[_time[_start], x[_start], _start], [_time[_stop], x[_stop], _stop]])
    return movs

def extract_single_mov_reciprocal(_time, x, v, starts_up, starts_down, thresh = 1e-2, index = True):
    movs_up = []
    movs_down = []
    if starts_up[0] > starts_down[0]:
        if starts_up[0] > starts_down[1]:
            print("error, missing starting points somewhere")
            return -1
        else:
            if len(starts_up) < len(starts_down):
                starts_down = starts_down[:-1]
            for i, (u,v) in enumerate(zip(starts_down, starts_up)):
                if index:
                    movs_down.append([u,v])
                    try:
                        movs_up.append([v,starts_down[i+1]])
                    except IndexError:
                        pass
                else:
                    movs_down.append([[_time[u], x[u], u], [_time[v], x[v], v]])
                    try:
                        movs_up.append([[_time[v], x[v], v], [_time[starts_down[i+1]], x[starts_down[i+1]], starts_down[i+1]]])
                    except IndexError:
                        pass
    elif starts_up[0] < starts_down[0]:
        if starts_up[0] < starts_down[1]:
            print("error, missing starting points somewhere")
            return -1
        else:
            if len(starts_up) > len(starts_down):
                starts_up = starts_up[:-1]
            for u,v in zip(starts_up, starts_down):
                if index:
                    movs_down.append([u,v])
                    try:
                        movs_up.append([v,starts_up[i+1]])
                    except IndexError:
                        pass
                else:
                    movs_down.append([[_time[u], x[u], u], [_time[v], x[v], v]])
                    try:
                        movs_up.append([[_time[v], x[v], v], [_time[starts_up[i+1]], x[starts_up[i+1]], starts_up[i+1]]])
                    except IndexError:
                        pass
    else:
        print("error, same starting point for up and down")
        return -1
    return movs_up, movs_down




def find_stop_from_mov(_time, x, v, delim, _thresh = 1e-2, index = True, plateau = False):
    ### Give stopping points based on different rules for a given trajectory representing one single movement

    ### Delim is the starting and ending index for one movement

    threshold = lambda signal: [x if abs(x) > _thresh else 0 for x in signal]
    vthresh = threshold(v)

    first_zero = []
    best_zero = []
    first_dwell = []
    longest_dwell = []
    last_dwell_start = []
    last_dwell_mid = []
    last_dwell_end = []
    plateaux = []

    k = delim[0]
    try:
        while v[k]*v[k+1] > 0 and k < delim[1]:
            k+=1
    except IndexError:
        k = delim[1]

    if index == True:
        first_zero.append(k)
    else:
        first_zero.append([_time[k],x[k], k])
    ##############
    plateau = vthresh[tmp_start:tmp_stop]
    Dwell = False
    First = True
    plateaux = []
    for nu,u in enumerate(plateau[:-1]):
        if u == 0 and plateau[nu+1] == 0 and plateau[nu-1] == 0 and Dwell == False:
            a = nu + tmp_start
            Dwell = True
            indx = a
        elif u != 0 and Dwell == True:
            b = nu + tmp_start
            Dwell = False
            if (_time[b] - _time[a]) > 30e-3:
                plateaux.append([a,b])
                plat.append([a,b])
            else:
                pass
        else:
            pass

    try:
        if index == True:
            last_dwelling.append(plateaux[-1][0])
        else:
            last_dwelling.append([_time[plateaux[-1][0]], x[plateaux[-1][0]], plateaux[-1][0]])
        _mid = int((plateaux[0][1] + plateaux[0][0])/2)
        if index == True:
            first_dwell_mid.append(_mid)
        else:
            first_dwell_mid.append([_time[_mid], x[_mid], _mid])

        if index == True:
            final.append(plateaux[-1][1])
        else:
            final.append([_time[plateaux[-1][1]], x[plateaux[-1][1]], plateaux[-1][1]])

        _mid = int((plateaux[-1][1] + plateaux[-1][0])/2)
        if index == True:
            mid.append(_mid)
        else:
            mid.append([_time[_mid], x[_mid], _mid])

        tmp = 0
        for a,b in plateaux:
            _dist = b-a
            if _dist > tmp:
                tmp = _dist
                out = int(a + _dist/2)
        if index == True:
            score_based.append(out)
        else:
            score_based.append([_time[out], x[out], out])
    except IndexError:
        if index == True:
            last_dwelling.append(fzindex)
        else:
            last_dwelling.append([_time[fzindex], x[fzindex], fzindex])
        if index == True:
            first_dwell_mid.append(fzindex)
        else:
            first_dwell_mid.append([_time[fzindex], x[fzindex], fzindex])


        if index == True:
            final.append(fzindex)
        else:
            final.append([_time[fzindex], x[fzindex], fzindex])

        if index == True:
            mid.append(fzindex)
        else:
            mid.append([_time[fzindex], x[fzindex], fzindex])
        if index == True:
            score_based.append(fzindex)
        else:
            score_based.append([_time[fzindex], x[fzindex], fzindex])


    return numpy.array(first_zero), numpy.array(last_dwelling), numpy.array(score_based), numpy.array(final), numpy.array(mid), numpy.array(first_dwell_mid), plat
