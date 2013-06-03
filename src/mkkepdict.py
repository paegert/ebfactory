'''
Created on Jan 14, 2013

@package  mkkepdict
@author   map
@version  \$Revision: 1.1 $
@date     \$Date: 2013/06/03 19:31:25 $

Make dictionary database for Kepler EBs

$Log: mkkepdict.py,v $
Revision 1.1  2013/06/03 19:31:25  paegerm
initial revision

Initial revision'''

from optparse import OptionParser

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
    parser.add_option('--del', dest='delete', action='store_true', default=True,
                      help='per staruid: delete old entries in plc (default = True)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='keplerdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--imp', dest='impname', type='string', 
                      default='keplerebs.dict',
                      help='dictionary database file')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    if (len(args) == 1):
        options.plcname = args[0]
        
    watch = Stopwatch()
    watch.start()
    
    cls = getattr(dbconfig, options.dbconfig)
    dbconfig = cls()

    tmpreader = dbr.DbReader('/home/map/data/kepler/keptmp.sqlite')
    generator  = tmpreader.traverse('select * from stars;', None, 1000)
    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, 
                              dbconfig.dictcols, dbconfig.dicttname, 
                              dbconfig.dicttypes, dbconfig.dictnulls)
    inslist = []
    for star in generator:
        kic    = star['kic']
        stype  = star['type']
        t0     = star['bjd0']
        period = star['p0']
        kmag   = star['Kmag']
        t2t1   = star['T2_T1']
        r1r2   = star['r1pr2']
        q      = star['q']
        esinw  = star['esinw']
        ecosw  = star['ecosw']
        ff     = star['FF']
        sini   = star['sini']
        toins  = (kic, None, None, period, t0, kmag, stype, t2t1, r1r2, q,
                  esinw, ecosw, ff, sini, None, None, None, None, 'kdata', 
                  None, None, None)
        inslist.append(toins)

    if len(inslist) > 0:
        dictwriter.insert(inslist, True)
    tmpreader.close()
    dictwriter.close()
        
    print len(inslist), 'stars inserted in', watch.stop(), 's'
    print 'done'