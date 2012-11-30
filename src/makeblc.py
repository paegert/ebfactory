'''
Created on Jun 28, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.3 $
@date     \$Date: 2012/11/30 20:30:27 $

make phase folded light curves

$Log: makeblc.py,v $
Revision 1.3  2012/11/30 20:30:27  paegerm
convert del to nodel option

convert del to nodel option

Revision 1.2  2012/09/24 21:34:11  paegerm
adding dbconfig and selfile option, trigger creation if database does not exist
adding nrbins option

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
    usage = '%prog [options] blcname'
    parser = OptionParser(usage=usage)
    parser.add_option('--blc', dest='blcname', type='string', 
                      default='asasblc.sqlite',
                      help='database file with phased light curves')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
#    parser.add_option('--del', dest='delete', action='store_true', default=False,
#                      help='per staruid: delete old entries in plc (default = False)')
    parser.add_option('--nodel', dest='delete', action='store_false', default=True,
                      help='per staruid: do not delete old entries in plc (default = delete)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--nrbins', dest='nrbins', type='int', 
                      default=100,
                      help='number of bins per lightcurve (100)')
    parser.add_option('--plc', dest='plcname', type='string', 
                      default='asasplc.sqlite',
                      help='database file with phased light curves')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./)')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars;',
                      help='select statement for dictionary (Default: select * from stars;)')
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    if (len(args) == 1):
        options.blcname = args[0]

    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")

    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()

    watch = Stopwatch()
    watch.start()
    
    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    
    generator = dictreader.traverse(options.select, None, 1000)
    nrstars   = 0
    dictupd = []
    plcreader = dbr.DbReader(options.rootdir + options.plcname)
    blcwriter = dbw.DbWriter(options.rootdir + options.blcname, dbc.blccols,
                             'stars', dbc.blctypes, dbc.blcnulls)
    for star in generator:
        nrstars += 1
        plc = plcreader.getlc(star['uid'], order = 'phase')
        print 'binning ', nrstars, star['id']
        if options.delete == True:
            blcwriter.deletebystaruid(star['uid'])            
        (blc, mmin, mmax, std) = makebinnedlc(plc, star['uid'], options.nrbins)
        blcwriter.insert(blc)
        dictupd.append([mmin, mmax, std, star['uid']])
    
    blcwriter.dbconn.commit()
    dictreader.dbconn.close()
    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, dbc.dictcols)
    updcmd = 'update stars set fmin = ?, fmax = ?, stddev = ? where uid = ?;'
    dictwriter.update(updcmd, dictupd)
    
    print nrstars, ' light curves binned in ', watch.stop(), ' seconds'        
    print 'done'
