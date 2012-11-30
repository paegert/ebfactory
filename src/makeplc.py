'''
Created on Jun 18, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.3 $
@date     \$Date: 2012/11/30 20:31:10 $

make phase folded light curves

$Log: makeplc.py,v $
Revision 1.3  2012/11/30 20:31:10  paegerm
convert del to nodel option

convert del to nodel option

Revision 1.2  2012/09/24 21:35:04  paegerm
adding dbconfig and selfile option, adding maxgap to dictionary

Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision

'''

import math
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
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
#    parser.add_option('--del', dest='delete', action='store_true', default=True,
#                      help='per starudi: delete old entries in plc (default = True)')
    parser.add_option('--nodel', dest='delete', action='store_false', default=True,
                      help='per staruid: do not delete old entries in plc (default = delete)')
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
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    if (len(args) == 1):
        options.plcname = args[0]
        
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
    lcreader  = dbr.DbReader(options.rootdir + options.rawlcname)
    plcwriter = dbw.DbWriter(options.rootdir + options.plcname, dbc.plccols, 
                             'stars', dbc.plctypes, dbc.plcnulls)
    gaps   = []
    failed = 0
    for star in generator:
        nrstars += 1
        lc = lcreader.getlc(star['uid'], 'stars', 'hjd')
        print 'phasing ', nrstars, star['id']
        period = dbc.getperiod(star)    
        shift  = dbc.getshift(star)        
        if period <= 0.0:
            failed += 1
            continue
        if options.delete == True:
            plcwriter.deletebystaruid(star['uid'])
        (plc, gap) = makephasedlc(lc, star['t0'], star[dbc.t['mag']], 
                                  period, 0.0)
        gaps.append ([period, gap, star['uid']])
        plcwriter.insert(plc)
    
    plcwriter.commit()
    plcwriter.close()
    dictreader.close()
    
    print 'updating dictionary'
    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, dbc.dictcols)
    dictwriter.update('update stars set period = ?, plcmaxgap = ? where uid = ?;', 
                      gaps, True)
    dictwriter.close()
    
    print nrstars, 'light curves read in ', watch.stop(), ' seconds'
    print failed, 'light curves failed to phase (period <= 0)' 
    print ''       
    print 'done'
