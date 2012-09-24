'''
Created on Jun 18, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.1 $
@date     \$Date: 2012/09/24 21:36:16 $

multi-process version of makeplc and makeblc, phases the lightcurve if T0 <= 0.0

$Log: makeplcmp.py,v $
Revision 1.1  2012/09/24 21:36:16  paegerm
multi-process version of makeplc and makeblc, phases the lightcurve if T0 <= 0.0

Initial revision

'''

import math
import os

from multiprocessing import Pool
from optparse import OptionParser

import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr

import dbconfig
from functions import *
from stopwatch import *


def binlc(plc, staruid, nrbins = 100):
    binsize = 1.0 / nrbins
    oldbin = -1
    blc = []
    phases = np.ndarray((0,))
    fluxes = np.ndarray((0,))
    sigmas = np.ndarray((0,))
    binfluxes = np.ndarray((0,))
    for entry in plc:
        actbin = int((0.5 + entry[2]) / binsize)
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
            binfluxes = np.append(binfluxes, entry[3])
        else:
            binfluxes = np.append(binfluxes, entry[3])

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

    fmin    = None
    fmax    = None
    fminidx = None
    fmaxidx = None
    if (len(fluxes) > 0):
        fmin    = fluxes.min()
        fmax    = fluxes.max()
        fminidx = fluxes.argmin()
        fmaxidx = fluxes.argmax()
    
    return (blc, fminidx, fmaxidx, fmin, fmax)



def runmakeplc(options, lmax, stars):
    print 'max = ', lmax
    nrstars   = 0
    failed    = 0
    gaps = []
    plcs = []
    blcs = []
    
    lcreader  = dbr.DbReader(options.rootdir + options.rawlcname)
    for star in stars:
        nrstars += 1
        staruid = star[0]
        lc = lcreader.getlc(staruid, 'stars', 'hjd')
#        print 'phasing ', lmax + nrstars, star[0]
        period = dbc.getperiod(star)    
        shift  = dbc.getshift(star)
        t0     = dbc.gett0(star)        
        magmin = 999.9
        magmax = 0.0
        hjdmin = 0.0
        hjdmax = 0.0
#        if (t0 <= 0.0):
#            for entry in lc:
#                if entry['vmag'] < magmin:
#                    magmin = entry['vmag']
#                    hjdmin = entry['hjd']
#                if entry['vmag'] > magmax:
#                    magmax = entry['vmag']
#                    hjdmax = entry['hjd']
#            if (star[dbc.t['mean']] > star[dbc.t['median']]):
#                t0 = hjdmax
#            else:
#                t0 = hjdmin
        if period <= 0.0:
            failed += 1
            continue
        if options.delete == True:
            plcwriter = dbw.DbWriter(options.rootdir + options.plcname, dbc.plccols, 
                             'stars', dbc.plctypes, dbc.plcnulls)
            plcwriter.deletebystaruid(staruid)
            plcwriter.close()
            blcwriter = dbw.DbWriter(options.rootdir + options.blcname, dbc.blccols, 
                             'stars', dbc.blctypes, dbc.blcnulls)
            blcwriter.deletebystaruid(staruid)
            blcwriter.close()
        (plc, gap) = makephasedlc(lc, t0, star[dbc.t['mag']], 
                                  period, 0.0)
        (blc, mmin, mmax, fmin, fmax) = binlc(plc, staruid, options.nrbins)
        if (t0 <= 0.0):
            shift = 0.0
            if (star[dbc.t['mean']] < star[dbc.t['median']]):
                shift = -blc[mmax][1]
                t0 = hjdmax
            else:
                shift = -blc[mmin][1]
                t0 = hjdmin
            if (shift != 0.0):
                for i in xrange(len(plc)):
                    plc[i][2] += shift
                    while plc[i][2] < -0.5:
                        plc[i][2] += 1
                    while plc[i][2] > 0.5:
                        plc[i][2] -= 1                        
                for i in xrange(len(blc)):
                    blc[i][1] += shift
                    while blc[i][1] < -0.5:
                        blc[i][1] += 1
                    while blc[i][1] > 0.5:
                        blc[i][1] -= 1                        
                
        plcs += plc
        blcs += blc
        gaps.append ([period, gap, fmin, fmax, staruid])
    
    lcreader.close()    
    plcwriter = dbw.DbWriter(options.rootdir + options.plcname, dbc.plccols, 
                             'stars', dbc.plctypes, dbc.plcnulls, tout = 30.0)
    plcwriter.insert(plcs, True)
    plcwriter.close()
    blcwriter = dbw.DbWriter(options.rootdir + options.blcname, dbc.blccols, 
                             'stars', dbc.blctypes, dbc.blcnulls, tout = 30.0)
    blcwriter.insert(blcs, True)
    blcwriter.close()
    
    print 'done', lmax
    return gaps
    


if __name__ == '__main__':
    usage = '%prog [options] plcdbfile'
    parser = OptionParser(usage=usage)
    parser.add_option('--blc', dest='blcname', type='string', 
                      default='asasblc.sqlite',
                      help='database file with binned light curves')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
    parser.add_option('--del', dest='delete', action='store_true', default=True,
                      help='per starudi: delete old entries in plc (default = True)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--nrbins', dest='nrbins', type='int', 
                      default=100,
                      help='number of bins (100)')
    parser.add_option('--plc', dest='plcname', type='string', 
                      default='asasplc.sqlite',
                      help='database file with phased light curves')
    parser.add_option('--rawlc', dest='rawlcname', type='string', 
                      default='asaslc.sqlite',
                      help='database file with raw light curves')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./)')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars;',
                      help='select statement for dictionary (Default: select * from stars;)')
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    if (len(args) == 1):
        options.plcname = args[0]
        
    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")

    watch = Stopwatch()
    watch.start()

    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()

    print options.select
    dictreader = dbr.DbReader(options.rootdir + options.dictname, False)   
    stars = dictreader.fetchall(options.select)
    dictreader.close()
    
    nrstars   = 0
    chunksize = 100
    tmax    = 1 + len(stars) / chunksize
    nrprocess = int(os.environ['OMP_NUM_THREADS'])
    results   = []
    failed = 0    
    pool = Pool(processes = nrprocess)
    for i in xrange(tmax):
        lmin = i * chunksize
        lmax = (i + 1) * chunksize
        if (lmax > len(stars)):
            lmax = len(stars)
#        runmakeplc(options, lmax, stars[lmin:lmax])
        results.append(pool.apply_async(runmakeplc, 
                                        (options, lmax, stars[lmin:lmax])))

    pool.close()
    pool.join()
    
    # collect results
    print 'updating dictionary'
    nrstars = 0
    failed  = 0
    nr = 0
    nf = 0
    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, dbc.dictcols)
    for i in range(len(results)):
        gaps = results[i].get(timeout=1)
        nrstars += len(gaps)
        failed  += nf
        dictwriter.update('update stars set period = ?, plcmaxgap = ?, ' +
                          'fmin = ?, fmax = ? where uid = ?;', 
                          gaps, True)
    dictwriter.close()
    
    print nrstars, 'light curves read in ', watch.stop(), ' seconds'
    print failed, 'light curves failed to phase (period <= 0)' 
    print ''       
    print 'done'
