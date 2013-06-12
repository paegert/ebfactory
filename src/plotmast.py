
'''
Created on Jun 06, 2013

@package  ebf
@author   mparvizi
@version  \$ 1.0 $
@date     \$Date: 2013/06/12 22:25:38 $
'''


import os
import numpy as np
import matplotlib.pyplot as pl

from optparse import OptionParser
from stopwatch import *

import dbconfig
import sqlitetools.dbreader as dbr

if __name__ == '__main__':
    usage = '%prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Mast',
                      help='name of database configuration (default = Mast')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='kepebdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--rplc', dest='rplcname', type='string', 
                       default='keplerrplc.sqlite',
                       help='database file with phased light curves')
    parser.add_option('--blc', dest='blcname', type='string', 
                      default='mastblc.sqlite',
                      help='database file with binned light curves')
    parser.add_option('--fsize', dest='fsize', type='int', 
                      default=8,
                      help='font size for plots (default: 8')
    parser.add_option('--plotdir', dest='plotdir', type='string', 
                  default='mast_plots',
                  help='directory for plotted light curves')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='/Users/mahmoudparvizi/vphome/kepler',
                      help='directory for database files')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars limit 3;',
                      help='select statement for dictionary ' +
                           '(Def: select * from stars)')
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'
    if (options.plotdir[-1] != '/'):
        options.plotdir += '/'
    if (len(args) == 1):
        options.rplcnames = args[0]
        
    watch = Stopwatch()
    watch.start()
    
    
    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()

    rplcreader  = dbr.DbReader(options.rootdir + options.rplcname)
    blcreader  = dbr.DbReader(options.rootdir + options.blcname) 
    
    dictreader = dbr.DbReader(options.rootdir + options.dictname, False)
    stars = dictreader.fetchall(options.select)
    dictreader.close()
    
    nrstars = 0
    for star in stars: 
        nrstars += 1
        print 'staruid to plot: '
        print nrstars
        staruid = star[0]
        starkic = star[1]
        rplc = rplcreader.getlc(staruid)
        blc = blcreader.getlc(staruid)
        rplc_phases   = [x[3] for x in rplc]
        rplc_dfluxes  = [x[8] for x in rplc]
        blc_phases    = [x[2] for x in blc]
        blc_normmags  = [x[3] for x in blc]
       
        # UNBINNED rplc plots
        plotname  = options.rootdir + options.plotdir + starkic + '.png'
        pl.plot(rplc_phases, rplc_dfluxes,'k.', blc_phases, blc_normmags,'r.')
        pl.xlim(-0.5, 0.5)
        pl.xticks(fontsize = options.fsize)
        pl.yticks(fontsize = options.fsize)
        pl.xlabel('phase', fontsize=options.fsize)
        pl.ylabel('normalized_mag', fontsize=options.fsize)
        pl.title('Kepler EB Light Curve: ' + 'phased_dtr_' + starkic, 
                 fontsize=options.fsize)
        pl.savefig(plotname)
    #   pl.show()
        pl.clf()
        print 'saved file: ' + plotname
        
       