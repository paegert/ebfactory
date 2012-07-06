'''
Created on Jun 18, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.1 $
@date     \$Date: 2012/07/06 20:34:19 $

make phase folded light curves

$Log: makeplc.py,v $
Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision

'''

from optparse import OptionParser

import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr

import dbconfig
from functions import *
from stopwatch import *



if __name__ == '__main__':
    usage = '%prog [options] plcdbfile'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--del', dest='delete', action='store_true', default=True,
                      help='per starudi: delete old entries in plc (default = True)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--rawlc', dest='rawlcname', type='string', 
                      default='asaslc.sqlite',
                      help='database file with raw light curves')
    parser.add_option('--plc', dest='plcname', type='string', 
                      default='asasplc.sqlite',
                      help='database file with phased light curves')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./)')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars;',
                      help='select statement for dictionary (Default: select * from stars;)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    if (len(args) == 1):
        options.plcname = args[0]
        
    watch = Stopwatch()
    watch.start()

    cls = getattr(dbconfig, 'Asas')
    dbconfig = cls()

    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    
    generator = dictreader.traverse(options.select, None, 1000)
    nrstars   = 0
    lcreader  = dbr.DbReader(options.rootdir + options.rawlcname)
    plcwriter = dbw.DbWriter(options.rootdir + options.plcname, dbconfig.plccols)
    for star in generator:
        nrstars += 1
        lc = lcreader.getlc(star['uid'], 'stars', 'hjd')
        print 'phasing ', star['id']
        if options.delete == True:
            plcwriter.deletebystaruid(star['uid'])            
        plc = makephasedlc(lc, star['t0'], star['vmag'], star['period'])
        plcwriter.insert(plc)
    
    plcwriter.commit()
    plcwriter.close()
    dictreader.close()
    
    print nrstars, 'light curves phased in ', watch.stop(), ' seconds' 
    print ''       
    print 'done'
