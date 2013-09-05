'''
@package: normalize
@author   : map
@version  : \$Revision: 1.2 $
@Date      : \$Date: 2013/09/05 18:57:40 $

Normalize lightcurves given in magnitudes

$Log: normalize.py,v $
Revision 1.2  2013/09/05 18:57:40  paegerm
keep uid of raw-lc entry in normalized and phased db

keep uid of raw-lc entry in normalized and phased db

Revision 1.1  2013/08/13 19:32:28  paegerm
Initial revision
'''

from optparse import OptionParser

import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr

import dbconfig
from functions import *
from stopwatch import *


if __name__ == '__main__':
    usage = '%prog [options] nplcdbfile'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
    parser.add_option('--nodel', dest='delete', action='store_false', default=True,
                      help='per staruid: do not delete old entries (default = delete)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--rawlc', dest='rawlcname', type='string', 
                      default='asaslc.sqlite',
                      help='database file with raw light curves')
    parser.add_option('--nplc', dest='nplcname', type='string', 
                      default='asasnplc.sqlite',
                      help='database file for phased light curves')
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
        options.nplcname = args[0]
        
    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")

    watch = Stopwatch()
    watch.start()

    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()

    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    
    generator = dictreader.traverse(options.select, None, 1000)
    nrstars   = 0
    rlcreader  = dbr.DbReader(options.rootdir + options.rawlcname)
    nplcwriter = dbw.DbWriter(options.rootdir + options.nplcname, dbc.nplccols, 
                             'stars', dbc.nplctypes, dbc.nplcnulls)
    rlccmd = "select * from stars " \
             "where staruid = ? and " \
             "(quality is NULL or quality = 'A' or quality = 'B') " \
             "order by hjd asc;"
    nrtotal = 0
    for star in generator:
        nrstars += 1
        vmag = star['vmag']
        nplcrows = []
        rlc = rlcreader.fetchall(rlccmd, (star['uid'],))
        for entry in rlc:
            nmag = round(2.0 - entry['vmag'] / vmag, 6)
            nerr = round(entry['vmag_err'] / vmag, 6)
            nplcrows.append([star['uid'], entry['uid'], entry['hjd'], 
                             None, nmag, nerr])
        if options.delete == True:
            nplcwriter.deletebystaruid(star['uid'])
        nrentries = len(nplcrows)
        if (len(nplcrows) > 0):
            nplcwriter.insert(nplcrows, True)
            nrentries = len(nplcrows)
            nrtotal += nrentries
 
    dictreader.close()
    rlcreader.close()
    nplcwriter.close()

    print nrtotal, 'lines written in', watch.stop(), 's'    
    print 'Done'
    