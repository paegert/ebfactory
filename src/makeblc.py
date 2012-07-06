'''
Created on Jun 28, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.1 $
@date     \$Date: 2012/07/06 20:34:19 $

make phase folded light curves

$Log: makeblc.py,v $
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
    parser.add_option('--blc', dest='blcname', type='string', 
                      default='asasblc.sqlite',
                      help='database file with phased light curves')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--del', dest='delete', action='store_true', default=False,
                      help='per staruid: delete old entries in plc (default = False)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
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

    cls = getattr(dbconfig, 'Asas')
    dbconfig = cls()

    watch = Stopwatch()
    watch.start()
    
    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    
    generator = dictreader.traverse(options.select, None, 1000)
    nrstars   = 0
    dictupd = []
    plcreader = dbr.DbReader(options.rootdir + options.plcname)
    blcwriter = dbw.DbWriter(options.rootdir + options.blcname, dbconfig.blccols)
    for star in generator:
        nrstars += 1
        plc = plcreader.getlc(star['uid'], 'phase')
        print 'binning ', star['id']
        if options.delete == True:
            blcwriter.deletebystaruid(star['uid'])            
        (blc, mmin, mmax, std) = makebinnedlc(plc, star['uid'], 100)
        blcwriter.insert(blc)
        dictupd.append([mmin, mmax, std, star['uid']])
    
    blcwriter.dbconn.commit()
    dictreader.dbconn.close()
    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, dbconfig.dictcols)
    updcmd = 'update stars set fmin = ?, fmax = ?, stddev = ? where uid = ?;'
    dictwriter.update(updcmd, dictupd)
    
    print nrstars, ' light curves binned in ', watch.stop(), ' seconds'        
    print 'done'
