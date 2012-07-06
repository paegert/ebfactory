'''
Created on Jul 5, 2012

@package  trainnet
@author   map
@version  \$Revision: 1.1 $
@date     \$Date: 2012/07/06 20:34:19 $

$Log: trainnet.py,v $
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



def maketarget(classes, varcls, target):
    if (varcls.find('/') < 0):
        try:
            index = classes.index(varcls)
            target[index] = 1
        except ValueError:
            print varcls, ' not in classlist'
    else:
        splitted = varcls.split('/')      # assign to first
        index = classes.index(splitted[0])
        target[index] = 1


def prepdata(options, arr, cff, shuffle = True, 
             normsubtract = None, normdevide = None):
    nrrows = np.shape(arr)[0]
    
    # randomize order
    if (shuffle == True):
        order = range(nrrows)
        np.random.shuffle(order)
        arr = arr[order, :]
        cff = cff[order, :]

    nrinputs = 20
    newnorm = False
    alld = np.zeros((nrrows, nrinputs))
    if (normsubtract == None) or (normdevide == None):
        normsubtract = np.zeros(nrinputs)
        normdevide   = np.ones(nrinputs)
        newnorm = True
    allt = np.zeros((nrrows, len(options.classes)))
    allnames = []
    for i in xrange(nrrows):
        allnames.append(arr[i]['id'])
        # normalize coefficients per row
        coeffs = np.asarray(tuple(cff[i]))
        coeffs[3:6]   = (coeffs[3:6] - coeffs[3:6].mean()) / \
                           coeffs[3:6].std()
        coeffs[7:10]  = (coeffs[7:10] - coeffs[7:10].mean()) / \
                           coeffs[7:10].std()
        std = coeffs[11:14].std()
        if (std > 1e-6):
            coeffs[11:14] = (coeffs[11:14] - coeffs[11:14].mean()) / std
        std = coeffs[15:18].std()
        if (std > 1e-6):
            coeffs[15:18] = (coeffs[15:18] - coeffs[15:18].mean()) / std
                           

        # copy knots and normalized coeffs to data table
        alld[i, :16] = coeffs[2:]
        
        # add period, magnitude, difference of normalized magnitudes, chi2
        alld[i, 16]  = np.log10(arr[i]['period'])
        alld[i, 17]  = arr[i]['vmag']
        alld[i, 18]  = arr[i]['fmax'] - arr[i]['fmin']
        alld[i, 19]  = arr[i]['chi2']
        
        # make the target value line
        maketarget(options.classes, arr[i]['varcls'], allt[i])

    # normalize vmag
    if (newnorm == True):
        normsubtract[17] = alld[:, 17].mean()
        normdevide[17]   = alld[:, 17].std()
    alld[:, 17] = (alld[:, 17] - normsubtract[17]) / normdevide[17] 

    # skip normalized magnitude difference (already small enough)

    # chi2 (devide by 3 * std to avoid overflows due to huge spread
    if (newnorm == True):
        normsubtract[19] = alld[:, 19].mean()
        normdevide[19]   = 3.0 * alld[:, 19].std()
    alld[:, 19] = (alld[:, 19] - normsubtract[19]) / normdevide[19] 

    return (alld, allt, allnames, normsubtract, normdevide)

        

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

    cls = getattr(dbconfig, 'Asas')
    dbconfig = cls()
    
    watch = Stopwatch()
    watch.start()
    watchprep = Stopwatch()
    watchprep.start()
    
    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")
    
    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    fitreader  = dbr.DbReader(options.rootdir + options.fitname)
    
#    options.select = "select * from stars " \
#                     "where varcls not like '%/%' and " \
#                           "varcls not like '%=%' and " \
#                           "varcls not like '%:%' and " \
#                           "chi2 is not null;"
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
    
    # prepare the data, target and normalization values
    (alld, allt, allnames, 
     normsubtract, normdevide) = prepdata(options, dictarr, coeffarr)
    
    print noclass, ' stars skipped'
    print nrstars, ' selected and prepared in ', watchprep.stop(), ' seconds'
    watchprep.start()
    
    # ratio of training to validation to testing
    nrrows   = len(allnames)
    trainmax = int(nrrows * 0.5)
    validmax = int(nrrows * 0.75)
    testmax  = nrrows
    
    # split data and target class arrays into training, validation and testing
    # set. the names are kept for bookkeeping and identifying individual results
    traind = alld[:trainmax]
    traint = allt[:trainmax]
    trainn = allnames[:trainmax]
    
    validd = alld[trainmax:validmax]
    validt = allt[trainmax:validmax]
    validn = allnames[trainmax:validmax]
    
    testd = alld[validmax:]
    testt = allt[validmax:]
    testn = allnames[validmax:]

    # testcode
    net = mlp.mlp(traind, traint, nhidden = 10, beta = 1.0, momentum = 0.9, 
                  outtype = 'softmax', multires = False, mdelta = 0.01)
    net.subdir = options.rootdir + options.resdir
    if not os.path.exists(net.subdir):
        os.mkdir(net.subdir)
    net.debug = options.debug
    net.setnormvalues(normsubtract, normdevide)
    net.earlystopping(traind, traint, validd, validt, eta = 0.95, 
                      niterations = 25, makestats = True)
    cm = net.confmat(testd, testt, True)
    net.report('%7s ', '%7d ', '%7.2f ', options.classes, 
               ofname = options.repname)

    pf = open(net.subdir + '/' + options.picklename, 'w')
    pickle.dump(net, pf)
    pf.close()

    nrprocess = int(os.environ['OMP_NUM_THREADS'])
    if (nrprocess <= 0):
        nrprocess = 2

    print 'network trained in ', watchprep.stop(), 'seconds'
    print watch.stop(), 'seconds over all'
    print ''
    print 'Done'
