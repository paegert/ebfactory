'''
Created on Aug 28, 2012

@package  makestats
@author   map
@version  \$Revision: 1.2 $
@date     \$Date: 2012/11/30 20:32:48 $

Make missing or all statistics from raw light curve data

$Log: makestats.py,v $
Revision 1.2  2012/11/30 20:32:48  paegerm
deleting unused --del and --ext option

deleting unused --del and --ext option

Revision 1.1  2012/09/24 21:37:00  paegerm
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
    rlcreader  = dbr.DbReader(options.rootdir + options.rlcname)
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
            rlc = rlcreader.getlc(star['uid'])
            nprlc = np.ndarray(shape = (len(rlc),), 
                               dtype = dbc.rlnptype)
            i = -1
            for entry in rlc:
                i += 1
                for j in range(len(rlc[0])):
                    nprlc[i][j] = entry[j]
            stats = None
            if options.allstats == True:
                stats = dbc.makeallstats(star['uid'], nprlc)
            else:
                stats = dbc.makemissingstats(star['uid'], nprlc)
            if stats != None:
                updates.append(stats)
        if (len(updates) > 0):
            dictwriter.update(dbc.missingstats, updates, False)
        stars = dictreader.fetchmany()

    dictreader.close()
    rlcreader.close()
    
    dictwriter.commit()
    dictwriter.close()
        
    print nrstars, 'updated in', watch.stop(), 's'
    print 'Done'
    