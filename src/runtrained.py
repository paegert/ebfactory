'''
Created on Jul 6, 2012

@package  runtrained
@author   map
@version  \$Revision: 1.3 $
@date     \$Date: 2012/11/30 20:39:20 $

Sample program for running a trained network

$Log: runtrained.py,v $
Revision 1.3  2012/11/30 20:39:20  paegerm
convert del to nodel option

convert del to nodel option

Revision 1.2  2012/09/24 21:45:39  paegerm
adding dbconfig option, loading net from database

Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision
'''


from optparse import OptionParser

import numpy as np
import os

import mlp
import dbconfig
import loadnet

from stopwatch import *

import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr
from sqlitetools.dbfunctions import rowtolist

import trainnet



if __name__ == '__main__':
    usage = '%prog [options] [fitname]'
    parser = OptionParser(usage=usage)
    parser.add_option('--clscol', dest='clscol', type='string', 
                      default='varcls',
                      help='dictionary column for class (varcls)')
    parser.add_option('--clsname', dest='clsname', type='string', 
                      default='asascls.sqlite',
                      help='name for database with results (asascls.sqlite)')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
#    parser.add_option('--del', dest='delete', action='store_true', default=True,
#                      help='per starudi: delete old entries in plc (default = True)')
    parser.add_option('--nodel', dest='delete', action='store_false', default=True,
                      help='per staruid: do not delete old entries (default = delete)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--fit', dest='fitname', type='string', 
                      default='asasfit.sqlite',
                      help='database file with fitted light curves')
    parser.add_option('--fqnetdb', dest='fqnetdb', type='string', 
                      default=None,
                      help='fully qualified filename for the trained network (None)')
    parser.add_option('--netname', dest='netname', type='string', 
                      default=None,
                      help='name of the trained network to use (None)')
    parser.add_option('--netuid', dest='netuid', type='int', 
                      default=None,
                      help='UID of the trained network to use (None)')    
    parser.add_option('--repname', dest='repname', type='string', 
                      default=None,
                      help='filename for written report (default = None)')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./)')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars where chi2 is not null;',
                      help='select statement for dictionary ' +
                           '(Def: select * from stars where chi2 is not null;)')
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    if (len(args) == 1):
        options.fitname = args[0]
        
#    for line in open(options.rootdir + options.clsnames):
#        if (len(line.strip()) == 0) or (line.startswith('#')):
#            continue
#        options.classes = line.split()
        
    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")
        
    if (options.netuid == None) and (options.netname == None):
        print "either netuid or netname must be given"
        parser.print_help()

    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()
    
    watch = Stopwatch()
    watch.start()
    
    watch2 = Stopwatch()
    watch2.start()

    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    fitreader  = dbr.DbReader(options.rootdir + options.fitname)
    generator = dictreader.traverse(options.select, None, 5000)
    nrstars   = 0
    noclass   = 0
    nofit     = 0
    curidx    = 0
    dictarr   = np.zeros(0, dtype = dbc.npdicttype)
    coeffarr  = np.zeros(0, dtype = dbc.npcoefftype)
    staruids  = []
    for star in generator:
        nrstars += 1
        coeffs = fitreader.getlc(star['uid'], dbc.cfftname)
        if len(coeffs) == 0:
            nofit += 1
            print 'Warning: no fit for', star['uid'], star['id'], 'skipping'
            continue
        if (len(coeffs) > 1):
            print 'Warning: ', len(coeffs), ' fits for', star['id'], 'taking first'
        staruids.append(star['uid'])
        dictarr = np.append(dictarr, np.zeros(1, dbc.npdicttype))
        dictarr[curidx] = tuple(star)
        coeffarr = np.append(coeffarr, np.zeros(1, dbc.npcoefftype))
        coeffarr[curidx] = tuple(coeffs[0])
        curidx += 1
        
    dictreader.close()
    fitreader.close()
    
    readtime = watch2.stop()
    watch2.start()

    net = loadnet.loadnet(options.fqnetdb, options.netuid, options.netname)
    options.classes = net.classes

    # prepare the data, target and normalization values
    (alld, allt, allnames, 
     normsubtract, normdevide) = trainnet.prepdata(options, dbc, dictarr, 
                                                   coeffarr, False,
                                                   net.normsubtract, 
                                                   net.normdevide)
    preptime = watch2.stop()
    watch2.start()
    
#    print 'initial report'
#    net.report('%7s ', '%7d ', '%7.2f ', options.classes)

    print ''
    print nofit, 'stars without fit'
    res = net.evaluate(alld, False)
    cm = net.confmat(alld, allt, True)
    net.comment = options.select
    net.trainstats = None
    net.validstats = None
    net.teststats  = None
    net.report('%7s ', '%7d ', '%7.2f ', options.classes, options.repname,
               '%7s', True, len(alld))
    classtime = watch2.stop()
    watch2.start()
    
    probidx = res.argsort(axis=1)
    maxidx  = len(net.classes) - 1
#    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, dbc.dictcols)
    clswriter  = dbw.DbWriter(options.rootdir + options.clsname, dbc.clscols, 
                              dbc.clstname, dbc.clstypes, dbc.clsnulls)
    repf = None
    if (options.repname != None):
        repf = open(options.repname, 'w')
        repf.write('#ID   Cls1   Prob1  Cls2  Prob2  Cls3  Prob3\n')
        
    clss = []
    for i in xrange(len(allnames)):
#        dictwriter.update('update stars set varcls = ? where id = ?', 
#                          [(net.classes[probidx[i][maxidx]], allnames[i])], False)
        if (options.delete == True):
            clswriter.deletebystaruid(staruids[i])
        clss.append([staruids[i], allnames[i], 
                     net.classes[probidx[i][maxidx]], 
                     round(res[i][probidx[i][maxidx]], 4),
                     net.classes[probidx[i][maxidx-1]], 
                     round(res[i][probidx[i][maxidx-1]], 4),
                     net.classes[probidx[i][maxidx-2]], 
                     round(res[i][probidx[i][maxidx-2]], 4)
                     ])
        if repf != None:
            oline = '%s  %s  %6.4f  %s  %6.4f  %s  %6.4f\n' % \
                    (allnames[i], 
                     net.classes[probidx[i][maxidx]], 
                     round(res[i][probidx[i][maxidx]], 4),
                     net.classes[probidx[i][maxidx-1]], 
                     round(res[i][probidx[i][maxidx-1]], 4),
                     net.classes[probidx[i][maxidx-2]], 
                     round(res[i][probidx[i][maxidx-2]], 4)
                     )
            repf.write(oline)

    if (repf != None):
        repf.close()    
#    dictwriter.commit()
#    dictwriter.close()
    
    clswriter.insert(clss, True)
    clswriter.close()
    
    print nrstars, 'light curves prepared and classified in ', watch.stop(), 's'
    print 'reading records:', readtime
    print 'preparing data :', preptime
    print 'classification :', classtime
    print 'writing results:', watch2.stop()
    print ''
    print 'Done'
    