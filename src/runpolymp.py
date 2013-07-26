'''
Created on Jul 2, 2012

@package  runpolymp
@author   map
@version  \$Revision: 1.4 $
@date     \$Date: 2013/07/26 20:06:19 $

Multi-process version of runpoly. Set $OMP_NUM_THREADS to desired number of 
threads

$Log: runpolymp.py,v $
Revision 1.4  2013/07/26 20:06:19  paegerm
adding midpoints and fullfit options, switching to mastpolyfit

adding midpoints and fullfit options, switching to mastpolyfit

Revision 1.3  2012/11/30 20:38:21  paegerm
passing options to fitlc, catching OSError in case another process created
the dictionary before the actual one could
converting prints to writing to logfile
passing options object to fitlc

Revision 1.2  2012/09/24 21:43:43  paegerm
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



def runpolyproc(options, dbc, lmax, stars):
    nrstars   = 0
    failed    = 0
    olddir    = options.rootdir
    os.chdir(olddir)
    options.lf.write(str(lmax) + ' started')
    plcreader  = dbr.DbReader(options.rootdir + options.plcname)
    blcreader  = dbr.DbReader(options.rootdir + options.blcname)
    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, 
                              dbc.dictcols, tout = 60.0)
    cffwriter  = dbw.DbWriter(options.rootdir + options.fitname, 
                              dbc.cffcols, dbc.cfftname, tout = 60.0)
    fitwriter  = dbw.DbWriter(options.rootdir + options.fitname, 
                              dbc.fitcols, dbc.fittname, tout = 60.0)
    midwriter  = dbw.DbWriter(options.rootdir + options.fitname,
                              dbc.kmncols, dbc.kmntname, tout = 60.0)
    for star in stars:
        nrstars += 1
        staruid = star[0]    
        sdir = star[dbc.sdirindex]
        plc = plcreader.getlc(staruid, 'stars', 'phase')
        blc = blcreader.getlc(staruid, 'stars', 'phase')
        try:
            cffwriter.deletebystaruid(staruid)
            fitwriter.deletebystaruid(staruid)
            midwriter.deletebystaruid(staruid)
        except sqlite3.OperationalError as err:
            options.lf.write(str(lmax) + ' ' + str(staruid) + 
                             ' fit database is locked while deleting')
            options.lf.write(str(err))
            options.lf.write()
        if (options.rootdir + sdir != olddir):
            olddir = options.rootdir + sdir
            os.chdir(olddir)
            if not os.path.exists('plots'):
                try:
                    os.mkdir('plots')
                except OSError:       # in case its created by another process
                    pass
            if not os.path.exists('failed'):
                try:
                    os.mkdir('failed')
                except OSError:
                    pass
        varclsidx = 1 + dbc.dictcols.index(options.clscol)
        # fake the database star by a dictionary. Necessary because the
        # sqlite type of star will not be handled correctly over process
        # borders
        dstar = {'uid': staruid, 'id': star[1] , 'varcls' : star[varclsidx], 
                 'Period' : dbc.getperiod(star)}
        (ok, chi2, coeffs, fit, midpoints) = fitlc(dstar, plc, blc, options)
        try:
            dictwriter.update('update stars set chi2 = ? where uid = ?;', 
                              [(chi2, staruid)], True)
        except sqlite3.OperationalError as err:
            options.lf.write(str(lmax) + ' ' + str(staruid) + 
                             ' dict database is locked')
            options.lf.write(str(err))
            options.lf.write()

        if ok == False:
            failed += 1
            continue
        
        if (len(coeffs) == 9):
            for i in range(0, 8):
                coeffs.append(0.0)
        try:
            cffwriter.insert((coeffs,), True)
            if options.fullfit == True:
                fitwriter.insert(fit, True)
            if options.fittype == 'midpoints':
                midwriter.insert([midpoints], True)
        except sqlite3.OperationalError as err:
            print staruid, midpoints
            options.lf.write(str(lmax) + ' ' + str(staruid) + 
                             ' fit database is locked while inserting')
            options.lf.write(str(err))
            options.lf.write()
        
    plcreader.close()
    blcreader.close()
    
    dictwriter.commit()
    
    dictwriter.close()
    cffwriter.close()
    fitwriter.close()  
    midwriter.close()  
    
    options.lf.write(str(lmax) + ' done')

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
    tmpwriter = dbw.DbWriter(options.rootdir + options.fitname, 
                             dbc.kmncols, dbc.kmntname, 
                             dbc.kmntypes, dbc.kmnnulls)
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
#        runpolyproc(options, dbc, lmax, stars[lmin:lmax])
        results.append(pool.apply_async(runpolyproc, 
                                        (options, dbc, lmax, stars[lmin:lmax])))
        
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
        
    options.lf.write(str(nrstars) + ' processed, ' + 
                     str(failed) + ' lightcurves failed')
    options.lf.write(str(watch.stop()) + ' seconds')
    options.lf.write('')
    options.lf.write('Done')
    