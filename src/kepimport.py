'''
Created on Jan 16, 2013

@package  kepimport
@author   map
@version  \$Revision: 1.1 $
@date     \$Date: 2013/06/03 19:30:44 $

Import Kepler EBs

$Log: kepimport.py,v $
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
                      default='Kepler',
                      help='name of database configuration (default = Kepler')
    parser.add_option('--nodel', dest='delete', action='store_false', default=True,
                      help='per staruid: delete old entries in plc (default = True)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='keplerdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--impdir', dest='impdir', type='string', 
                      default='kdata',
                      help='directory in rootdir with data files')
    parser.add_option('--plc', dest='plcname', type='string', 
                      default='keplerplc.sqlite',
                      help='database file with phased light curves')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./)')
    
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
    
    lcdtype = [('hjd', 'f8'), ('phase', 'f4'), ('flux', 'f4'), ('ferr', 'f4')]

    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    generator  = dictreader.traverse('select * from stars;', None, 1000)
    plcwriter = dbw.DbWriter(options.rootdir + options.plcname, dbconfig.plccols, 
                            'stars', dbconfig.plctypes, dbconfig.plcnulls)

    updlist  = []
    nrstars  = 0
    nrimport = 0
    for star in generator:
        nrstars += 1
        print nrstars
        staruid  = star['uid']
        fname = options.rootdir + options.impdir + star['id'] + '.dtr.data'
        if os.path.exists(fname):
            nrimport += 1
            lcarr = np.loadtxt(fname, dtype = lcdtype)
            fmin  = lcarr['flux'].min()
            fmax  = lcarr['flux'].max()
            fmean = round(lcarr['flux'].mean(), 6)
            fmedian = round(np.median(lcarr['flux']), 6)
            updlist.append((float(fmin), float(fmax), fmean, fmedian, staruid))
            inslc = []
            for row in lcarr:
                inslc.append((staruid, staruid, round(row['phase'], 6), 
                              round(row['flux'], 6), round(row['ferr'], 6)))
            if options.delete == True:
                plcwriter.deletebystaruid(staruid)
            if len(inslc) > 0:
                plcwriter.insert(inslc, True)

    dictreader.close()
    plcwriter.close()
    if (len(updlist) > 0):
        cmd = 'update stars set fmin = ?, fmax = ?, fmean = ?, fmedian = ? ' + \
              'where uid = ?;'
        dictwriter = dbw.DbWriter(options.rootdir + options.dictname, 
                                  dbconfig.dictcols)
        dictwriter.update(cmd, updlist, True)
        dictwriter.close()

    
    print nrstars, 'stars found,', nrstars - nrimport, 'without light curve'
    print nrimport, 'light curves imported in', watch.stop(), 's'
    print ''
    print 'Done'
    