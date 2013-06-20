'''
Created on Jun 18, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.3 $
@date     \$Date: 2013/06/20 18:24:06 $

$Log: functions.py,v $
Revision 1.3  2013/06/20 18:24:06  paegerm
skip None entries, add rounding and correct actbin in makebinnedlc

skip None entries, add rounding and correct actbin in makebinnedlc

Revision 1.2  2012/09/24 21:26:30  paegerm
adding uid of raw light curve entry to phased light curve, adding phase shift

Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision
'''

import numpy as np

     

def makephasedlc(lc, t0, dictvmag, period, shift = 0.0):
    plc = []
    for entry in lc:
        obstime = entry['hjd']
        rlcuid  = entry['uid']
        diff = obstime - t0
        nmag  = 2.0 - entry['vmag'] / dictvmag
        err   = entry['vmag_err'] / dictvmag
        phase = diff / period - diff // period
        phase -= 0.5
        if (phase < 0):
            phase += 1.0
        phase -= 0.5
        phase -= shift
        if phase < -0.5:
            phase += 1.0
        elif phase > 0.5:
            phase -= 1.0
        plc.append([entry['staruid'], rlcuid, round(phase, 5), 
                    round(nmag, 5), round(err, 5)])
        
    plc = sorted(plc, key = lambda plc: plc[2])
    maxgap = 1.0 + plc[0][2] - plc[-1][2] 
    for i in xrange(1, len(plc)):
        if plc[i][2] - plc[i - 1][2] > maxgap:
            maxgap = plc[i][2] - plc[i - 1][2]
    return (plc, maxgap)



def deriv2(x, y):
    if (len(x) == 0) or (len(x) != len(y)):
        return None
    sabs = 0.0
    for i in xrange(1, len(x) - 1):
        f1 = (y[i] - y[i - 1]) / (x[i] - x[i - 1])
        f2 = (y[i + 1] - y[i]) / (x[i + 1] - x[i])
        d2 = (f2 - f1) / (x[i + 1] - x[i - 1])
        sabs += abs(d2)
    return sabs / len(x)



def makebinnedlc(plc, staruid, nrbins = 100):
    binsize = 1.0 / nrbins
    oldbin = -1
    blc = []
    phases = np.ndarray((0,))
    fluxes = np.ndarray((0,))
    sigmas = np.ndarray((0,))
    binfluxes = np.ndarray((0,))
    for entry in plc:
        if entry['phase'] == None:
            continue
        # actbin = int((0.5 + entry['phase']) / binsize)
        actbin = int((0.5 + entry['phase']) * nrbins + 0.5)
        if (actbin != oldbin):
            if (oldbin != -1):
                mean  = round(binfluxes.mean(), 6)
                sigma = round(binfluxes.std(), 6)
                phase = round(oldbin * binsize - 0.5, 6)
                if (sigma < 0.001):
                    sigma = 0.001
                blc.append([staruid, phase, mean, sigma])
                phases = np.append(phases, phase)
                fluxes = np.append(fluxes, mean)
                sigmas = np.append(sigmas, sigma)
            oldbin = actbin
            binfluxes = np.ndarray((0,))
            binfluxes = np.append(binfluxes, entry['normmag'])
        else:
            binfluxes = np.append(binfluxes, entry['normmag'])

    if (len(binfluxes) > 0):
        mean  = round(binfluxes.mean(), 6)
        sigma = round(binfluxes.std(), 6)
        phase = round(oldbin * binsize - 0.5, 6)
        if (sigma < 0.001):
            sigma = 0.001
        blc.append([staruid, phase, mean, sigma])
        phases = np.append(phases, phase)
        fluxes = np.append(fluxes, mean)
        sigmas = np.append(sigmas, sigma)

    fmin = None
    fmax = None
    std  = None
    if (len(fluxes) > 0):
        fmin = fluxes.min()
        fmax = fluxes.max()
        std  = round(deriv2(phases, fluxes) / (fluxes.max() - fluxes.min()), 6)
    
    return (blc, fmin, fmax, std)


        
if __name__ == '__main__':
    pass