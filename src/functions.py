'''
Created on Jun 18, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.1 $
@date     \$Date: 2012/07/06 20:34:19 $

$Log: functions.py,v $
Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision

Initial revision
'''

import numpy as np

     

def makephasedlc(lc, t0, dictvmag, period):
    plc = []
    for entry in lc:
        obstime = entry['hjd']
        diff = obstime - t0
        nmag  = 2.0 - entry['vmag'] / dictvmag
        err   = entry['vmag_err'] / dictvmag
        phase = diff / period - diff // period
        phase -= 0.5
        if (phase < 0):
            phase += 1.0
        phase -= 0.5
        plc.append((entry['staruid'], round(phase, 5), 
                    round(nmag, 5), round(err, 5)))
        
    return plc



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
        actbin = int((0.5 + entry['phase']) / binsize)
        if (actbin != oldbin):
            if (oldbin != -1):
                mean  = binfluxes.mean()
                sigma = binfluxes.std()
                phase = oldbin * binsize - 0.5
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
        mean  = binfluxes.mean()
        sigma = binfluxes.std()
        phase = oldbin * binsize - 0.5
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
        std  = deriv2(phases, fluxes) / (fluxes.max() - fluxes.min())
    
    return (blc, fmin, fmax, std)


        
if __name__ == '__main__':
    pass