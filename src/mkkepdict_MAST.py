'''
Created on Jan 14, 2013

@package  mkkepdict
@author   map
@version  \$Revision: 1.1 $
@date     \$Date: 2013/06/10 22:47:07 $

Make dictionary database for Kepler EBs

$Log: mkkepdict_MAST.py,v $
Revision 1.1  2013/06/10 22:47:07  paegerm
initial revision

Revision 1.1  2013/06/03 19:31:25  paegerm
initial revision

Initial revision'''

from optparse import OptionParser

from stopwatch import *
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
    parser.add_option('--del', dest='delete', action='store_true', default=True,
                      help='per staruid: delete old entries in plc (default = True)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='kepebdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--imp', dest='impname', type='string', 
                      default='KEP_DB.dict',
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

    tmpreader = dbr.DbReader('/Users/mahmoudparvizi/fits2sql/src/KEB_DB.sqlite')
    generator  = tmpreader.traverse('select * from stars;', None, 1000)
    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, 
                              dbconfig.dictcols, dbconfig.dicttname, 
                              dbconfig.dicttypes, dbconfig.dictnulls)
    inslist = []
    for star in generator:
        kic    = star['KIC']
        stype  = star['morph']
        t0     = star['bjd0']
        period = star['period']
        kmag   = star['kmag']
        t2t1   = star['T21']
        r1r2   = star['rho12']
        q      = star['q']
        esinw  = star['e_sin_omega']
        ecosw  = star['e_cos_omega']
        ff     = star['FF']
        sini   = star['sin_i']
        teff   = star['Teff']
        ra     = star['RA']
        dec    = star['DEC']
        sc     = star['SC']
        sdir   = None
        cls    = 'EB'
        rfmin  = None
        rfmax  = None
        rfmean = None
        rfmed  = None 
        cfmin  = None
        cfmax  = None
        cfmean = None
        cfmed  = None 
        dfmin  = None
        dfmax  = None
        dfmean = None
        dfmed  = None 
        toins  = (kic, period, t0, stype, t2t1,
                   r1r2, q, esinw, ecosw, ff,
                   sini, teff, kmag, ra, dec, 
                   sc, sdir, cls, rfmin, rfmax, 
                   rfmean, rfmed, cfmin, cfmax, cfmean, 
                   cfmed, dfmin, dfmax, dfmean, dfmed)
        inslist.append(toins)

    if len(inslist) > 0:
        dictwriter.insert(inslist, True)
    tmpreader.close()
    dictwriter.close()
        
    print len(inslist), 'stars inserted in', watch.stop(), 's'
    print 'done'