'''
Created on Sep 20, 2012

@package  plotcls
@author   map
@version  \$Revision: 1.1 $
@date     \$Date: 2012/09/24 21:40:50 $

$Log: plotcls.py,v $
Revision 1.1  2012/09/24 21:40:50  paegerm
plot classified lightcurves

Initial revision
'''

import os
import matplotlib.pyplot as pl
from multiprocessing import Pool

from optparse import OptionParser

import numpy as np

import dbconfig

from stopwatch import *

import sqlitetools.dbreader as dbr


def plotclslcs(options, lmax, stars):
    print 'max = ', lmax
    nrstars   = 0
    failed    = 0
    olddir    = options.rootdir
    os.chdir(olddir)
    plcreader  = dbr.DbReader(options.rootdir + options.plcname)
    blcreader  = dbr.DbReader(options.rootdir + options.blcname)
    fitreader  = dbr.DbReader(options.rootdir + options.fitname)
    clsreader  = dbr.DbReader(options.rootdir + options.clsname)
    for star in stars:
        nrstars += 1
        staruid = star[0]
        plc = plcreader.getlc(staruid)
        blc = blcreader.getlc(staruid)
        fit = fitreader.getlc(staruid, 'fit')
        cls = clsreader.getlc(staruid, 'classification')
        cls = cls[0]
        plcphases = [x[3] for x in plc]
        plcmags   = [x[4] for x in plc]
        blcphases = [x[2] for x in blc]
        blcmags   = [x[3] for x in blc]
        fitphases = [x[2] for x in fit]
        fitvalues = [x[3] for x in fit]
        plotname  = options.plotdir + star[1] + '.png'
        pl.plot(plcphases, plcmags, 'k.', 
                blcphases, blcmags, 'r.', 
                fitphases, fitvalues, 'b-')
        pl.xticks(fontsize = options.fsize)
        pl.yticks(fontsize = options.fsize)
        pl.xlim(-0.5, 0.5)
        tmp = 'Phase (Period = ' + str(dbc.getperiod(star)) + ' d)'
        pl.xlabel(tmp, fontsize=options.fsize)
        pl.ylabel('normalized mag', fontsize=options.fsize)
        pl.title(star[dbc.t['id']] + ', ' +
                 cls['cls1'] + ' = ' + str(cls['prob1']) + ', ' +
                 cls['cls2'] + ' = ' + str(cls['prob2']),
                 fontsize=options.fsize)
        pl.savefig(plotname)
#        pl.show()
        pl.clf()




if __name__ == '__main__':
    usage = '%prog [options] [fitname]'
    parser = OptionParser(usage=usage)
    parser.add_option('--blc', dest='blcname', type='string', 
                      default='asasblc.sqlite',
                      help='database file with binned light curves')
    parser.add_option('--clsname', dest='clsname', type='string', 
                      default='asascls.sqlite',
                      help='name for database with results (asascls.sqlite)')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--fit', dest='fitname', type='string', 
                      default='asasfit.sqlite',
                      help='database file with fitted light curves')
    parser.add_option('--fsize', dest='fsize', type='int', 
                      default=18,
                      help='font size for plots (default: 18')
    parser.add_option('--plc', dest='plcname', type='string', 
                       default='asasplc.sqlite',
                       help='database file with phased light curves')
    parser.add_option('--plotdir', dest='plotdir', type='string', 
                      default='plots',
                      help='database file with phased light curves')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./)')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars where chi2 is not null;',
                      help='select statement for dictionary ' +
                           '(Def: select * from stars where chi2 is not null;)')
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'
    if (options.plotdir[-1] != '/'):
        options.plotdir += '/'

    if (len(args) == 1):
        options.fitname = args[0]
        
#    for line in open(options.rootdir + options.clsnames):
#        if (len(line.strip()) == 0) or (line.startswith('#')):
#            continue
#        options.classes = line.split()
        
    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")
        
    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()
    
    watch = Stopwatch()
    watch.start()

    dictreader = dbr.DbReader(options.rootdir + options.dictname, False)
    stars   = dictreader.fetchall(options.select)
    dictreader.close()
    
    chunksize = 100
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
#        plotclslcs(options, lmax, stars[lmin:lmax])
        results.append(pool.apply_async(plotclslcs, 
                                        (options, lmax, stars[lmin:lmax])))
        
    pool.close()
    pool.join()
    
    print 'Done'
    