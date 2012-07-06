'''
Created on Jul 6, 2012

@package  runtrained
@author   map
@version  \$Revision: 1.1 $
@date     \$Date: 2012/07/06 20:34:19 $

$Log: runtrained.py,v $
Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision

Initial revision
'''


from optparse import OptionParser

import numpy as np
import os
import pickle

import mlp
import dbconfig
from stopwatch import *


import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr
from sqlitetools.dbfunctions import rowtolist

import trainnet



if __name__ == '__main__':
    usage = '%prog [options] [fitname]'
    parser = OptionParser(usage=usage)
    parser.add_option('--classes', dest='clsnames', type='string', 
                      default='classes.txt',
                      help='file with space separated classnames (classes.txt)')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--fit', dest='fitname', type='string', 
                      default='asasfit.sqlite',
                      help='database file with fitted light curves')
    parser.add_option('--pname', dest='picklename', type='string', 
                      default='mlp.pickle',
                      help='filename for the trained, pickled network (mlp.pickle)')
    parser.add_option('--repname', dest='repname', type='string', 
                      default='report.txt',
                      help='filename for written report (default = report.txt)')
    parser.add_option('--resdir', dest='resdir', type='string', 
                      default='results',
                      help='subdirectory for results (default = results)')
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
        
    for line in open(options.rootdir + options.clsnames):
        if (len(line.strip()) == 0) or (line.startswith('#')):
            continue
        options.classes = line.split()
        
    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")

    cls = getattr(dbconfig, 'Asas')
    dbconfig = cls()
    
    watch = Stopwatch()
    watch.start()

    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    fitreader  = dbr.DbReader(options.rootdir + options.fitname)
    generator = dictreader.traverse(options.select, None, 5000)
    nrstars   = 0
    noclass   = 0
    curidx    = 0
    dictarr   = np.zeros(0, dtype = dbconfig.npdicttype)
    coeffarr  = np.zeros(0, dtype = dbconfig.npcoefftype)
    for star in generator:
        nrstars += 1
        if not (star['varcls'] in options.classes):
            noclass += 1
            print 'star', star['id'], 'with class', star['varcls'], 'skipped'
            continue
        coeffs = fitreader.getlc(star['uid'], dbconfig.cfftname)
        if len(coeffs) == 0:
            print 'Warning: no fit for', star['id'], 'skipping'
            continue
        if (len(coeffs) > 1):
            print 'Warning: ', len(coeffs), ' fits for', star['id'], 'taking first'
        dictarr = np.append(dictarr, np.zeros(1, dbconfig.npdicttype))
        dictarr[curidx] = tuple(star)
        coeffarr = np.append(coeffarr, np.zeros(1, dbconfig.npcoefftype))
        coeffarr[curidx] = tuple(coeffs[0])
        curidx += 1
        
    dictreader.close()
    fitreader.close()
    

    pf = open(options.rootdir + options.resdir + '/' + options.picklename)
    net = pickle.load(pf)
    pf.close()

    # prepare the data, target and normalization values
    (alld, allt, allnames, 
     normsubtract, normdevide) = trainnet.prepdata(options, dictarr, 
                                                   coeffarr, False,
                                                   net.normsubtract, 
                                                   net.normdevide)
    
    print 'initial report'
    net.report('%7s ', '%7d ', '%7.2f ', options.classes)

    print ''
    print 'new report'
    cm = net.confmat(alld, allt, True)
    net.report('%7s ', '%7d ', '%7.2f ', options.classes)

    print len(allnames), 'lightcurves classified in ', watch.stop(), ' seconds'
    print ''
    print 'Done'
    