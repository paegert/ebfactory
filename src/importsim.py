'''
@package: importsim
@author   : map
@version  : \$Revision: 1.1 $
@Date      : \$Date: 2013/08/13 19:24:07 $

Import Nathans simulated lightcurves

$Log: importsim.py,v $
Revision 1.1  2013/08/13 19:24:07  paegerm
initial revision

Initial revision
'''

from optparse import OptionParser

import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr

import dbconfig
from functions import *
from stopwatch import *


tmpdicttname = 'stars'
tmpdictcols  = ['file', 'period', 'amp', 'offset']
tmpdicttype  = ['TEXT', 'REAL', 'REAL', 'REAL']
tmpdictnull  = [' NOT NULL ', ' NOT NULL ', ' NOT NULL ', ' NOT NULL ']
tmpdictnptype = [('file', 'a20'), ('period', 'f4'), 
                 ('amp', 'f4'), ('offset', 'f4')]

lcdtype = [('hjd', 'f4'), ('nmag', 'f4'), ('nerr', 'f4'), ('phase', 'f4')]


if __name__ == '__main__':
    usage = '%prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
    parser.add_option('--create', dest='create', action='store_true', 
                      default=False,
                      help='create dict for info file')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--ext', dest='ext', type='string', default='',
                      help='filename extension (default = empty string)')
    parser.add_option('--nplc', dest='nplcname', type='string', 
                      default='asasnplc.sqlite',
                      help='database file for phased light curves')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='/home/map/data/asas10',
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
    
    keepers = None
    with open(options.rootdir + 'sim/tmp/skeep.txt') as infile:
        keepers = infile.readlines()
    keepers = [int(x[:-1]) for x in keepers]
 
    goers   = None
    with open(options.rootdir + 'sim/tmp/signore.txt') as infile:
        goers = infile.readlines()
    goers = [int(x[:-1]) for x in goers]

    arr = np.loadtxt(options.rootdir + 'sim/tmp/info.txt', 
                     dtype = tmpdictnptype)
    
    if options.create == True:
        inserts = []
        for i in xrange(len(arr)):
            period = round(float(arr[i][1]), 4)
            amp    = round(float(arr[i][2]), 4)
            offset = round(float(arr[i][3]), 4)
            inserts.append([arr[i][0], period, amp, offset])
        
        tmpwriter = dbw.DbWriter(options.rootdir + 'sim/tmp/tmpdict.sqlite',
                                 tmpdictcols, 'stars', tmpdicttype, 
                                 tmpdictnull)
        tmpwriter.insert(inserts, True)
        tmpwriter.close()
    
    dictwriter = dbw.DbWriter(options.rootdir + options.dictname,
                              dbc.dictcols, 'stars', 
                              dbc.dicttypes, dbc.dictnulls)    
    dictreader = dbr.DbReader(options.rootdir + options.dictname)

    tmpreader = dbr.DbReader(options.rootdir + 'sim/tmp/tmpdict.sqlite')
    cmd = 'select * from stars where offset = 0.5;'
    stars = tmpreader.fetchall(cmd)
    newstars = []
    prefix   = '2305_0825.'
    vmag = 11.19
    varcls = 'ED'
    nrstars = 0
    nrkeep  = 0
    nrgoers = 0
    cmd = 'select * from stars where id = ?;'
    for star in stars:
        dstar = dictreader.fetchall(cmd, (prefix + star['file'],))
        if dstar != []:
            continue
        nrstars += 1
        mnr = int(star['file'][5:10])
        if (mnr <= 1350) and ((mnr in keepers) == False):
            nrgoers += 1
            continue
        if (mnr > 1350) and ((mnr in goers) == True):
            nrgoers += 1
            continue
        nrkeep += 1
        nstar = [prefix + star['file'], 0.0, 0.0, star['period'], 0.0,
                 vmag, star['amp'], varcls, None, None, None, None,
                 None, None, 'sim2', None, None, None, None, 
                 None, None, None, None, None, None, None, None, None]
        newstars.append(nstar)
    if len(newstars) > 0:
        dictwriter.insert(newstars, True)
        print len(newstars), 'new stars inserted'
    dictwriter.close()
    
    print nrstars, 'read,', nrkeep, 'kept,', nrgoers, 'filtered out'
    
#    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    nplcwriter = dbw.DbWriter(options.rootdir + options.nplcname,
                              dbc.nplccols, dbc.nplctname,
                              dbc.nplctypes, dbc.nplccols)
    nrstars = 0
    for star in stars:
        dstar = dictreader.fetchone(cmd, (prefix + star['file'],))
        if dstar == [] or dstar == None:
            continue
        staruid = dstar['uid']
        nrstars += 1
        arr = np.loadtxt(options.rootdir + 'sim/tmp/' + star['file'],
                         dtype = lcdtype)
        lc = []
        for i in xrange(len(arr)):
            hjd = round(float(arr[i][0]), 6)
            mag = round(float(arr[i][1]), 4)
            err = round(float(arr[i][2]), 4)
            phs = round(float(arr[i][3]), 4) - 0.5
            lc.append([staruid, hjd, phs, mag, err])
        nplcwriter.insert(lc, True)

    print ''
    print nrstars, 'lightcurves inserted'
    
    print 'done'