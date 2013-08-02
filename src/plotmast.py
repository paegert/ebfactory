
'''
Created on Jun 06, 2013

@package  ebf
@author   mparvizi
@version  \$ 1.0 $
@date     \$Date: 2013/08/02 20:05:17 $
'''


import os
import numpy as np
import matplotlib.pyplot as pl

from optparse import OptionParser
from stopwatch import *

import dbconfig
import dbreader as dbr

if __name__ == '__main__':
    usage = '%prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Mast',
                      help='name of database configuration (default = Mast')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='kepq3dict_var.sqlite',
                      help='dictionary database file')
    parser.add_option('--rplc', dest='rplcname', type='string', 
                       default='kepq3rplc_12.sqlite',
                       help='database file with phased light curves')
    parser.add_option('--blc', dest='blcname', type='string', 
                      default='kepq3blc_12.sqlite',
                      help='database file with binned light curves')
    parser.add_option('--fit', dest='fitname', type='string', 
                      default='kepq3fit_12.sqlite',
                      help='database file with fitted light curves')
    parser.add_option('--fsize', dest='fsize', type='int', 
                      default=18,
                      help='font size for plots (default: 18')
    parser.add_option('--dbdir', dest='dbdir', type='string', 
                  default='/home/parvizm/REU/kepq3files/',
                  help='directory for raw light curves db')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='/home/parvizm/workspace/ebf/src/',
                      help='directory for database files')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars limit 100;',
                      help='select statement for dictionary ' +
                           '(Def: select * from stars)')
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'
#     if (options.plotdir[-1] != '/'):
#         options.plotdir += '/'
    if (len(args) == 1):
        options.rplcnames = args[0]
        
    watch = Stopwatch()
    watch.start()
    
    
    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()

    rplcreader = dbr.DbReader(options.dbdir + options.rplcname)
    blcreader  = dbr.DbReader(options.dbdir + options.blcname)
    fitreader  = dbr.DbReader(options.dbdir + options.fitname)
    dictreader = dbr.DbReader(options.dbdir + options.dictname)
    
    stars = dictreader.fetchall('select * from stars where KIC = 1026032;')
    
    nrstars = 0
    for star in stars: 
        staruid = star['staruid']
        ustar   = str(staruid)
        starkic = star['KIC']
        kstar   = str(starkic)
        period  = star['PERIOD']
        sper    = str(period)
        rplc = rplcreader.fetchall('select * from stars where staruid = ' + ustar + ' and SLC_FLAG = 0;')
        if rplc == None or len(rplc)==0:
            continue
        blc  = blcreader.fetchall('select * from stars where staruid = ' + ustar + ';')
        if blc == None or len(blc)==0:
            continue
        nrstars += 1
        print 'star #', nrstars, 'staruid to plot: ', staruid
        fit  = fitreader.fetchall('select * from midpoints where staruid = ' + ustar + ';')
        bjd_times     = [x[2] for x in rplc]
        rplc_phases   = [x[3] for x in rplc]
        rplc_rfluxes  = [x[4] for x in rplc] 
        rplc_dfluxes  = [x[10] for x in rplc]
        blc_phases    = [x[2] for x in blc]
        blc_normmags  = [x[3] for x in blc]
        fit_phases    = [[x[2], x[4], x[6], x[8], x[10], x[12], x[14], x[16]] for x in fit]
        fit_normmags  = [[x[3], x[5], x[7], x[9], x[11], x[13], x[15], x[17]] for x in fit]
        print len(rplc_fluxes)
        print rplc_fluxes
        
        # UNBINNED rplc plots
        plotname = options.rootdir + 'pres_plots/' + kstar + '_Q3pres_fit.png'
#         pl.plot(bjd_times, rplc_rfluxes, 'k.')
        pl.plot(rplc_phases, rplc_dfluxes, 'k.',
                blc_phases, blc_normmags, 'r.',
                fit_phases, fit_normmags, 'bo')
        pl.xticks(fontsize = options.fsize)
        pl.yticks(fontsize = options.fsize)
        pl.xlim(-0.5, 0.5)
#         pl.xlabel('mjd', fontsize=options.fsize)
#         pl.ylabel('flux', fontsize=options.fsize)
        pl.xlabel('Phase (Period = ' + sper + 'd)', fontsize=options.fsize)
        pl.ylabel('normalized flux', fontsize=options.fsize)
        pl.legend(('dtr_flux', 'bin_flux', 'fit_flux'), loc=0)
        pl.title('Phased, Fitted Light Curve of_' + starkic + ' _Q3', fontsize=options.fsize)
        pl.savefig(plotname)
        pl.clf()
        print 'saved file: ' + plotname
        
    dictreader.close()  
    rplcreader.close()
    blcreader.close()  