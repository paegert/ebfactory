'''
Created on Aug 28, 2012

@package  makestats
@author   map
@version  \$Revision: 1.1 $
@date     \$Date: 2013/08/07 15:37:33 $

Make missing or all statistics from binned light curve data

$Log: makestatsblc.py,v $
Revision 1.1  2013/08/07 15:37:33  paegerm
Initial revision


'''

from optparse import OptionParser

import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr

import dbconfig
from functions import *
from stopwatch import *



if __name__ == '__main__':
    usage = '%prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('--all', dest='allstats', action='store_true', default=False,
                      help='make all stats (default = False)')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--rawlc', dest='rlcname', type='string', 
                      default='asaslc.sqlite',
                      help='database file with raw light curves')
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

    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()

    dictreader = dbr.DbReader(options.rootdir + options.dictname)
#    rlcreader  = dbr.DbReader(options.rootdir + options.rlcname)
    blcreader  = dbr.DbReader(options.rootdir + options.rlcname)
    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, 
                              dbc.dictcols)
    
    nrstars = 0
    stars = dictreader.fetchmany(options.select)
    while (stars != None) and (len(stars) > 0):
        updates = []
        for star in stars:
            nrstars += 1
            if nrstars % 1000 == 0:
                print nrstars
#            rlc = rlcreader.getlc(star['uid'])
            blc = blcreader.getlc(star['uid'])
#            nprlc = np.ndarray(shape = (len(rlc),), dtype = dbc.rlnptype)
            npblc = np.ndarray(shape = (len(blc),), dtype = dbc.blcnptype)
            i = -1
#             for entry in rlc:
#                 i += 1
#                 for j in range(len(rlc[0])):
#                     nprlc[i][j] = entry[j]
            for entry in blc:
                i += 1
                for j in range(len(blc[0])):
                    npblc[i][j] = entry[j]
            stats = None
#             if options.allstats == True:
#                 stats = dbc.makeallstats(star['uid'], nprlc)
#             else:
#                 stats = dbc.makemissingstats(star['uid'], nprlc)
            if (len(npblc) > 0):
                if options.allstats == True:
                    stats = dbc.makeallstats(star['uid'], npblc)
                else:
                    stats = dbc.makemissingstats(star['uid'], npblc)
                if stats != None:
                    updates.append(stats)
                
        if (len(updates) > 0):
            dictwriter.update(dbc.missingstats, updates, False)
        stars = dictreader.fetchmany()

    dictreader.close()
#    rlcreader.close()
    blcreader.close()
    
    dictwriter.commit()
    dictwriter.close()
        
    print nrstars, 'updated in', watch.stop(), 's'
    print 'Done'
    