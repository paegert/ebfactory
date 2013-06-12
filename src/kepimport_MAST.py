'''
Created on Jan 16, 2013

@package  kepimport
@author   map
@version  \$Revision: 1.1 $
@date     \$Date: 2013/06/12 22:20:26 $

Import Kepler EBs

$Log: kepimport_MAST.py,v $
Revision 1.1  2013/06/12 22:20:26  paegerm
Mast added for new version of Kepler EBs

Revision 1.1  2013/06/03 19:30:44  paegerm
initial revision

Initial revision
'''

from optparse import OptionParser

import os
import numpy as np

import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr

import dbconfig
from stopwatch import *



if __name__ == '__main__':
    usage = '%prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Mast',
                      help='name of database configuration (default = Kepler')
    parser.add_option('--nodel', dest='delete', action='store_false', default=True,
                      help='per staruid: delete old entries in plc (default = True)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='kepebdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--impdir', dest='impdir', type='string', 
                      default='rplc_files',
                      help='directory in rootdir with data files')
    parser.add_option('--plc', dest='plcname', type='string', 
                      default='keplerrplc.sqlite',
                      help='database file with phased light curves')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='/Users/mahmoudparvizi/ebf/src',
                      help='directory for database files (default = /Users/mahmoudparvizi/ebf/src)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'
    if (options.impdir[-1] != '/'):
        options.impdir += '/'

    if (len(args) == 1):
        options.plcname = args[0]
        
    watch = Stopwatch()
    watch.start()
    
    cls = getattr(dbconfig, options.dbconfig)
    dbconfig = cls()
    
    lcdtype = [('bjd', 'f8'), ('phase', 'f8'), ('raw_flux', 'f8'), ('raw_err', 'f8'),
               ('corr_flux', 'f8'), ('corr_err', 'f8'),('dtr_flux', 'f8'), ('dtr_err', 'f8')]

    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    generator  = dictreader.traverse('select * from stars;', None, 1000)
    plcwriter = dbw.DbWriter(options.rootdir + options.plcname, dbconfig.rplccols, 
                            'stars', dbconfig.rplctypes, dbconfig.rplcnulls)

    updlist  = []
    nrstars  = 0
    nrimport = 0
    for star in generator:
        nrstars += 1
        print nrstars
        staruid  = star['uid']
        
        if len(star['KIC']) == 7:
            pad = '0'
            pad2 = '.00'
        elif len(star['KIC']) == 8:
             pad = ''
             pad2 = '.00'
        elif len(star['KIC']) == 10:
             pad = '0'
             pad2 = ''
        elif len(star['KIC']) == 11:
             pad = ''
             pad2 = ''
             
        fname = options.rootdir + options.impdir + pad + star['KIC'] + pad2 + '.lc.data'
        print fname
        
        if os.path.exists(fname):
            nrimport += 1
            lcarr = np.loadtxt(fname, dtype = lcdtype)
            rfmin  = lcarr['raw_flux'].min()
            rfmax  = lcarr['raw_flux'].max()
            rfmean = round(lcarr['raw_flux'].mean(), 6)
            rfmedian = round(np.median(lcarr['raw_flux']), 6)
            cfmin  = lcarr['corr_flux'].min()
            cfmax  = lcarr['corr_flux'].max()
            cfmean = round(lcarr['corr_flux'].mean(), 6)
            cfmedian = round(np.median(lcarr['corr_flux']), 6)
            dfmin  = lcarr['dtr_flux'].min()
            dfmax  = lcarr['dtr_flux'].max()
            dfmean = round(lcarr['dtr_flux'].mean(), 6)
            dfmedian = round(np.median(lcarr['dtr_flux']), 6)
            updlist.append((float(rfmin), float(rfmax), rfmean, rfmedian, 
                            float(cfmin), float(cfmax), cfmean, cfmedian, 
                            float(dfmin), float(dfmax), dfmean, dfmedian,staruid))
            inslc = []
            for row in lcarr:
                inslc.append((staruid, round(row['bjd'],6), round(row['phase'], 6), 
                              round(row['raw_flux'], 6), round(row['raw_err'], 6), 
                              round(row['corr_flux'], 6), round(row['corr_err'], 6), 
                              round(row['dtr_flux'], 6), round(row['dtr_err'], 6)))
            if options.delete == True:
                plcwriter.deletebystaruid(staruid)
            if len(inslc) > 0:
                plcwriter.insert(inslc, True)

    dictreader.close()
    plcwriter.close()
    if (len(updlist) > 0):
        cmd = 'update stars set rf_min = ?, rf_max = ?, rf_mean = ?, rf_median = ?, ' + \
              'cf_min = ?, cf_max = ?, cf_mean = ?, cf_median = ?, ' + \
              'df_min = ?, df_max = ?, df_mean = ?, df_median = ? where uid = ?;'
        dictwriter = dbw.DbWriter(options.rootdir + options.dictname, 
                                  dbconfig.dictcols)
        dictwriter.update(cmd, updlist, True)
        dictwriter.close()

    
    print nrstars, 'stars found,', nrstars - nrimport, 'without light curve'
    print nrimport, 'light curves imported in', watch.stop(), 's'
    print ''
    print 'Done'
    