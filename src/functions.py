'''
Created on Jun 18, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.5 $
@date     \$Date: 2013/09/05 18:46:04 $

$Log: functions.py,v $
Revision 1.5  2013/09/05 18:46:04  paegerm
makephasedlc --> phaselc. Keeping normalized and phased values in one table
adding fluxratio, gett0, stetson



Revision 1.4  2013/06/25 17:03:12  parvizm
adding makebinnedlc_MAST

Revision 1.3  2013/06/20 18:24:06  paegerm
skip None entries, add rounding and correct actbin in makebinnedlc

Revision 1.2  2012/09/24 21:26:30  paegerm
adding uid of raw light curve entry to phased light curve, adding phase shift

Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision
'''

import numpy as np

from math import *



def stetson(lc, idxname = 'vmag', errname = 'vmag_err'):
    # compute Stetson indices 
    lcdtype = [('hjd', 'f4'), ('mag', 'f4'), ('err', 'f4')]
    lcarr   = np.zeros(len(lc), dtype = lcdtype)
    for i in xrange(len(lc)):
        lcarr[i]['hjd'] = lc[i]['hjd']
        lcarr[i]['mag'] = lc[i][idxname]
        lcarr[i]['err'] = lc[i][errname]
    
    wk = 1.0  #Weighting Factor
    n = len(lcarr)
    meanmag = lcarr['mag'].mean()
    jt = np.zeros(n, float)
    jb = np.zeros(n, float)
    kt = np.zeros(n, float)
    kb = np.zeros(n, float)
    
    for i in xrange(0, n -2, 2):
        sigi = (lcarr['mag'][i] - meanmag) / (lcarr['err'][i]) * \
               (sqrt(n / (n - 1)))
        sigj = (lcarr['mag'][i + 1] - meanmag) / (lcarr['err'][i + 1]) * \
               (sqrt(n / (n - 1)))
        pk = sigi * sigj
        sgnpk = 0.0
        if pk > 0.0:
            sgnpk = 1.0
        if pk < 0.0:
            sgnpk = -1.0
        jt[i] = wk * sgnpk * (sqrt(abs(pk))) # Kinemuchi eq.1 (Numerator)
        jb[i] = wk                           # Kinemuchi eq.1 (Denominator)
        kt[i] = abs(sigi)                    # Kinemuchi eq.5 (Numerator)
        kb[i] = abs(sigi * sigi)             # Kinemuchi eq.5 (Denominator)
            
    j_stet = np.sum(jt) / sum(jb)                                   # Eq 1
    k_stet = 1.0 / n * np.sum(kt) / (sqrt((1.0 / n) * np.sum(kb)))  # Eq 5
    l_stet = j_stet * k_stet / (0.7908)                             # Eq 7
    
    return (round(j_stet, 4), round(k_stet, 4), round(l_stet, 4))




def fluxratio(npmags):
    maxf = max(npmags)
    medf = np.median(npmags)
    minf = min(npmags)
    
    fr = (maxf - medf) / (maxf - minf)

    return round(fr, 4)



def gett0fr(lc, idxname = 'vmag', hjdname = 'hjd'):
    dflux = np.zeros((len(lc),))
    for i, row in enumerate(lc):
        dflux[i] = row[idxname]

    fr = fluxratio(dflux)     
    if fr <= 0.5:
        tzero = dflux.argmin()
    else:
        tzero = dflux.argmax()
    
    return (lc[tzero][hjdname], fr)
     
     

def phaselc(lc, t0, period, shift = 0.0):
    plc = []
    if (t0 <= 0.0):
        (t0, fr) = gett0fr(lc)
    for entry in lc:
        obstime = entry['hjd']
        lcuid   = entry['uid']
        diff = obstime - t0
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
        plc.append([round(phase, 5), lcuid]) 
        
    plc = sorted(plc, key = lambda plc: plc[0])
    maxgap = 1.0 + plc[0][0] - plc[-1][0] 
    for i in xrange(1, len(plc)):
        if plc[i][0] - plc[i - 1][0] > maxgap:
            maxgap = plc[i][0] - plc[i - 1][0]
    return (plc, maxgap, t0)



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



def makebinnedlc_MAST(rplc, staruid, nrbins = 200):
    binsize = 1.0 / nrbins
    oldbin = -1
    blc = []
    phases = np.ndarray((0,))
    fluxes = np.ndarray((0,))
    sigmas = np.ndarray((0,))
    binfluxes = np.ndarray((0,))
#    binfluxuids = np.ndarray((0,))
    for entry in rplc:
        actbin = int((0.5 + entry['phase']) * nrbins + 0.5)
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
            binfluxes = np.append(binfluxes, entry['dtr_flux'])
        else:
            binfluxes = np.append(binfluxes, entry['dtr_flux'])
            
        # Test of rplc UIDs in bin encapsulating phase 0.0   
#         if (staruid == 2 and actbin == 99): 
#             binfluxuids = np.append(binfluxuids, entry['UID'])
#             binfluxuids = np.sort(binfluxuids)
#             binfluxuids.tofile('/Users/mahmoudparvizi/vphome/kepler/buid_2_99.txt', sep='\n', format="%s")

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
     
    blc_min = None
    blc_max = None
    blc_std  = None
    if (len(fluxes) > 0):
        blc_min = fluxes.min()
        blc_max = fluxes.max()
        blc_std  = deriv2(phases, fluxes) / (fluxes.max() - fluxes.min())
    
    return (blc, blc_min, blc_max, blc_std)


        
if __name__ == '__main__':
    pass