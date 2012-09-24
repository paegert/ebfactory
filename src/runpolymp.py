'''
Created on Jul 2, 2012

@package  runpolymp
@author   map
@version  \$Revision: 1.2 $
@date     \$Date: 2012/09/24 21:43:43 $

Multi-process version of runpoly. Set $OMP_NUM_THREADS to desired number of 
threads

$Log: runpolymp.py,v $
Revision 1.2  2012/09/24 21:43:43  paegerm
passing font size to fitlc, setting title to 'not classified' if varcls is
missing, catching sqlite database lock

passing font size to fitlc, setting title to 'not classified' if varcls is 
missing, catching sqlite database lock

Revision 1.1  2012/08/23 16:36:28  paegerm
initial revision

'''


from optparse import OptionParser
import os
import subprocess
import matplotlib.pyplot as pl

import sqlite3
import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr

import dbconfig
from multiprocessing import Pool
from functions import *
from stopwatch import *
from runpoly import *



def runpolyproc(options, lmax, stars):
    print 'max = ', lmax
    nrstars   = 0
    failed    = 0
    olddir    = options.rootdir
    os.chdir(olddir)
    plcreader  = dbr.DbReader(options.rootdir + options.plcname)
    blcreader  = dbr.DbReader(options.rootdir + options.blcname)
    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, 
                              dbc.dictcols, tout = 30.0)
    cffwriter  = dbw.DbWriter(options.rootdir + options.fitname, 
                              dbc.cffcols, dbc.cfftname, tout = 30.0)
    fitwriter  = dbw.DbWriter(options.rootdir + options.fitname, 
                              dbc.fitcols, dbc.fittname, tout = 30.0)
    for star in stars:
        nrstars += 1
        staruid = star[0]    
        sdir = star[dbc.sdirindex]
        plc = plcreader.getlc(staruid, 'stars', 'phase')
        blc = blcreader.getlc(staruid, 'stars', 'phase')
        try:
            cffwriter.deletebystaruid(staruid)
            fitwriter.deletebystaruid(staruid)
        except sqlite3.OperationalError as err:
            print max, 'fit database is locked'
            print err
        if (options.rootdir + sdir != olddir):
            olddir = options.rootdir + sdir
            os.chdir(olddir)
            if not os.path.exists('plots'):
                os.mkdir('plots')
            if not os.path.exists('failed'):
                os.mkdir('failed')
        dstar = {'uid': staruid, 'id': star[1] , 'varcls' : star[dbc.varclsindex]}
        (ok, chi2, coeffs, fit) = fitlc(dstar, plc, blc, 
                                        options.debug, options.fsize)
        try:
            dictwriter.update('update stars set chi2 = ? where uid = ?;', 
                              [(chi2, staruid)], True)
        except sqlite3.OperationalError as err:
            print max, 'dict database is locked'
            print err

        if ok == False:
            failed += 1
            continue
        
        if (len(coeffs) == 8):
            for i in range(0, 8):
                coeffs.append(0.0)
        coeffs.insert(0, staruid)
        try:
            fitwriter.insert(fit, True)
            cffwriter.insert((coeffs,), True)
        except sqlite3.OperationalError as err:
            print max, 'fit database is locked while inserting'
            print err
        
    plcreader.close()
    blcreader.close()
    
    dictwriter.commit()
    
    dictwriter.close()
    cffwriter.close()
    fitwriter.close()    

    return(nrstars, failed)



if __name__ == '__main__':

    options = get_polyopts()
    chunksize = 100
    
    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()
    
    # enforce creation if database or table does not exist
    tmpwriter = dbw.DbWriter(options.rootdir + options.fitname, 
                             dbc.cffcols, dbc.cfftname, 
                             dbc.cfftypes, dbc.cffnulls)
    tmpwriter.close()
    tmpwriter = dbw.DbWriter(options.rootdir + options.fitname, 
                             dbc.fitcols, dbc.fittname, 
                             dbc.fittypes, dbc.fitnulls)
    tmpwriter.close()

    watch = Stopwatch()
    watch.start()
    
    dictreader = dbr.DbReader(options.rootdir + options.dictname, False)
    
    
    # generator = dictreader.traverse(options.select, None, 1000)
    stars   = dictreader.fetchall(options.select)
    dictreader.close()
    tmax    = 1 + len(stars) / chunksize
    results = []
    nrprocess = int(os.environ['OMP_NUM_THREADS'])
    if (nrprocess <= 0):
        nrprocess = 2
    pool = Pool(processes = nrprocess)
    for i in xrange(tmax):
        lmin = i * chunksize
        lmax = (i + 1) * chunksize
        if (lmax > len(stars)):
            lmax = len(stars)
#        runpolyproc(options, lmax, stars[lmin:lmax])
        results.append(pool.apply_async(runpolyproc, 
                                        (options, lmax, stars[lmin:lmax])))
        
    pool.close()
    pool.join()
    
    # collect results
    nrstars = 0
    failed  = 0
    nr = 0
    nf = 0
    for i in range(len(results)):
        (nr, nf)= results[i].get(timeout=1)
        nrstars += nr
        failed  += nf
        
    print nrstars, ' processed, ', failed, ' lightcurves failed'
    print watch.stop(), ' seconds'
    print ''
    print 'Done'
    