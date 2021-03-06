'''
Created on Jul 5, 2012

@package  trainnet
@author   map
@version  \$Revision: 1.9 $
@date     \$Date: 2013/12/05 17:35:19 $

Routines for retrieving, preparing and handing data over to a neural network 
for training. Note: the main part is just for testing purposes, use trainnetmp
for all real training


$Log: trainnet.py,v $
Revision 1.9  2013/12/05 17:35:19  paegerm
adding prb option (take probability from target database (currently asas11 only)
store str(options) as net.comment
adding resname option
adding chi2 option
adding asas11target function for storing probabilities to result vectors
setting default stopval to 0.01

adding prb option (take probability from target database (currently asas11 only)
store str(options) as net.comment
adding resname option
adding chi2 option
adding asas11target function for storing probabilities to result vectors
setting default stopval to 0.01

Revision 1.8  2013/11/05 20:44:54  paegerm
shuffling in prepdata needs 1 dimension (was arr = arr[order, :]

Revision 1.7  2013/09/05 19:07:55  paegerm
switching to npviewtype (variable view of database) adding readfulldata,
adding vmagamp to training for asas, adding fullfit option, reassigning net
after training

Revision 1.6  2013/08/13 19:17:12  paegerm
maketarget: allow varcls to be None and return if so (needed for runtrained), 
take fmin, fmax from dbc.t

Revision 1.5  2013/07/26 20:32:44  paegerm
adding fittype, passing logfile to net

Revision 1.4  2012/11/30 20:40:07  paegerm
convert print statements to logfile output
write unknown classes, stars without fit or with multiple fits to logfile

Revision 1.3  2012/09/24 21:46:22  paegerm
store select statement as comment in net object, class mlp --> Mlp,
add database model to prepdata

Revision 1.2  2012/07/20 20:24:34  paegerm
adding readdata(), reshuffle(), parseoptions() and options for the network

Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision
'''

from optparse import OptionParser

import numpy as np
import os
import pickle

import mlp
import dbconfig
from stopwatch import *
from logfile import *

import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr
from sqlitetools.dbfunctions import rowtolist



def maketarget(classes, varcls, target):
    '''
    Set the target vector for a single object
    '''
    if (varcls == None):
        return
    
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



def asas11target(prbr, staruid, classes, varcls, target):
    '''
    Set the target vector for a single object using probabilites from
    database
    '''
    if (varcls == None):
        return
    
    if varcls not in classes:
        options.lf.write('ERROR: unknown class ' + varcls)
    
    prb = prbr.fetchall('select * from classification where staruid = ?', (staruid,))
    sprb = 0.0
    for i, cls in enumerate(classes):
        target[i] = prb[0][cls]
        sprb += prb[0][cls]
    target /= sprb



def prepdata(options, dbc, arr, cff, 
             normsubtract = None, normdivide = None):
    '''
    Prepare data for neural network (assemble and normalize). Note: the polyfit
    coefficients are normalized row-wise, NOT column-wise as usual. Within a 
    row each block of 3 coefficients is normalized individually
    
    Used: 4 blocks of 3 coefficients cff1, cff2, cff3 (second order fit)
          log10(Period)
          Vmag
          Max - Min for normalized magnitudes
          chi2 from polyfit
    '''
    nrrows = np.shape(arr)[0]
    
    # randomize order
    if (options.shuffle == True):
        order = range(nrrows)
        np.random.shuffle(order)
        arr = arr[order]
        cff = cff[order]

    nrinputs = 19
    if options.chi2 == True:
        nrinputs += 1
    newnorm = False
    alld = np.zeros((nrrows, nrinputs))
    if (normsubtract == None) or (normdivide == None):
        normsubtract = np.zeros(nrinputs)
        normdivide   = np.ones(nrinputs)
        newnorm = True
    allt = np.zeros((nrrows, len(options.classes)))
    allnames = []
    for i in xrange(nrrows):
        staruid = int(arr[i][0])
        allnames.append(arr[i][dbc.t['id']])
        # normalize coefficients per row
        coeffs = np.asarray(tuple(cff[i]))
        if options.fittype == 'coeffs':    # only coeffs need normalization
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
                           

        # copy knots and normalized coeffs/fluxes to data table
        alld[i, :16] = coeffs[2:]
        
        # add period, magnitude, difference of normalized magnitudes, chi2
        alld[i, 16]  = np.log10(arr[i]['period'])
        alld[i, 17]  = arr[i][dbc.t['magamp']]
        alld[i, 18]  = arr[i][dbc.t['fmax']] - arr[i][dbc.t['fmin']]
        if options.chi2 == True:
            alld[i, 19]  = arr[i]['chi2']
        
        # make the target value line
        varcls = None
        if options.clscol != None:
            varcls = arr[i][options.clscol]
        if options.prb == None:
            maketarget(options.classes, varcls, allt[i])
        else:
            asas11target(options.prb, staruid, options.classes, varcls, allt[i])
            

    # normalize vmag
    if (newnorm == True):
        normsubtract[17] = alld[:, 17].mean()
        normdivide[17]   = alld[:, 17].std()
    alld[:, 17] = (alld[:, 17] - normsubtract[17]) / normdivide[17] 

    # skip normalized magnitude difference (already small enough)

    # chi2 (divide by 5 * std to avoid overflows due to huge spread
    if options.chi2 == True:
        if (newnorm == True):
            normsubtract[19] = alld[:, 19].mean()
            normdivide[19]   = 5.0 * alld[:, 19].std()
        alld[:, 19] = (alld[:, 19] - normsubtract[19]) / normdivide[19] 

    return (alld, allt, allnames, normsubtract, normdivide)



def readdata(options, dbconfig):
    '''
    read data from database
    '''
    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    fitreader  = dbr.DbReader(options.rootdir + options.fitname)    
    generator  = dictreader.traverse(options.select, None, 5000)
    nrstars    = 0
    noclass    = 0
    nofit      = 0
    curidx     = 0
    fitdtype   = dbconfig.npcoefftype
    tablename  = dbconfig.cfftname
    dictarr    = np.zeros(0, dtype = dbconfig.npviewtype)
    if options.fittype == 'midpoints':
        fitdtype   = dbconfig.npkmntype
        tablename  = dbconfig.kmntname
    fitarr = np.zeros(0, dtype = fitdtype)

    for star in generator:
        nrstars += 1
        if not (star[options.clscol] in options.classes):
            noclass += 1
            options.lf.write('star '+ star['id'] + ' with class ' + 
                             star[options.clscol] + ' skipped')
            continue
#        coeffs = fitreader.getlc(star['uid'], dbconfig.cfftname)
        fits = fitreader.getlc(star['uid'], tablename)            
        if len(fits) == 0:
            nofit += 1
            options.lf.write('Warning: no fit for ' + str(star['uid']) + ', ' + 
                             star['id'] + ', ' + star['sdir'] + ' skipping')
            continue
        if (len(fits) > 1):
            options.lf.write('Warning: ' + str(len(fits)) + ' fits for ' +
                             star['id'] + ', taking first')
        dictarr = np.append(dictarr, np.zeros(1, dbconfig.npviewtype))
        try:
            dictarr[curidx] = tuple(star)
        except ValueError as err:
            print curidx
            print star
            print err
            exit(1)
        fitarr = np.append(fitarr, np.zeros(1, fitdtype))
        fitarr[curidx] = tuple(fits[0])
        curidx += 1
        
    dictreader.close()
    fitreader.close()
    
    return (dictarr, fitarr, nrstars, noclass, nofit)



def readfulldata(options, dbc):
    '''
    read data from database
    '''
    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    fitreader  = dbr.DbReader(options.rootdir + options.fitname)    
    generator  = dictreader.traverse(options.select, None, 5000)
    nrstars    = 0
    noclass    = 0
    nofit      = 0
    curidx     = 0
    dictarr    = np.zeros(0, dtype = dbc.npviewtype)
    fitdtype   = dbc.npkmntype
    fitarr = np.zeros(0, dtype = fitdtype)

    for star in generator:
        nrstars += 1
        if not (star[options.clscol] in options.classes):
            noclass += 1
            options.lf.write('star '+ star['id'] + ' with class ' + 
                             star[options.clscol] + ' skipped')
            continue
        fitlc = fitreader.getlc(star['uid'], 'fit', 'phase')            
        if len(fitlc) == 0:
            nofit += 1
            options.lf.write('Warning: no fit for ' + str(star['uid']) + ', ' + 
                             star['id'] + ', ' + star['sdir'] + ' skipping')
            continue
        dictarr = np.append(dictarr, np.zeros(1, dbc.npviewtype))
        try:
            dictarr[curidx] = tuple(star)
        except ValueError as err:
            print curidx
            print star
            print err
            exit(1)
        fitarr = np.append(fitarr, np.zeros(1, fitdtype))
        fitarr[curidx]['uid'] = fitlc[0]['uid']
        fitarr[curidx]['staruid'] = fitlc[0]['staruid']
        fitarr[curidx][2] = fitlc[2]['value']
        fitarr[curidx][3] = fitlc[5]['value']
        fitarr[curidx][4] = fitlc[8]['value']
        fitarr[curidx][5] = fitlc[12]['value']
        fitarr[curidx][6] = fitlc[15]['value']
        fitarr[curidx][7] = fitlc[18]['value']
        fitarr[curidx][8] = fitlc[22]['value']
        fitarr[curidx][9] = fitlc[25]['value']    # phase 0.0        
        fitarr[curidx][10] = fitlc[28]['value']
        fitarr[curidx][11] = fitlc[32]['value']
        fitarr[curidx][12] = fitlc[35]['value']
        fitarr[curidx][13] = fitlc[38]['value']
        fitarr[curidx][14] = fitlc[42]['value']
        fitarr[curidx][15] = fitlc[45]['value']
        fitarr[curidx][16] = fitlc[49]['value']
        curidx += 1
        
    dictreader.close()
    fitreader.close()
    
    return (dictarr, fitarr, nrstars, noclass, nofit)
    
    
    
def reshuffle(alld, allt, allnames):
    '''
    re-shuffling the data
    '''
    nrrows = np.shape(alld)[0]
    # randomize order
    order = range(nrrows)
    np.random.shuffle(order)
    alld = alld[order,:]
    allt = allt[order,:]
    allnames = [allnames[i] for i in order]
    
    return (alld, allt, allnames)



def parseoptions():
    '''
    Parse command line options
    
    Note: trainnet and trainnetmp use the same options although not all of them
    make sense for trainnet. For example only minhidden is used in trainnet
    '''
    usage = '%prog [options] [fitname]'
    parser = OptionParser(usage=usage)
    parser.add_option('--beta', dest='beta', type='float', 
                      default=1.0,
                      help='scale factor for activation function (1.0)')
    parser.add_option('--chi2', dest='chi2', action='store_true', 
                      default=False,
                      help='add chi2 from polyfit as input')
    parser.add_option('--classes', dest='clsnames', type='string', 
                      default='classes.txt',
                      help='file with space separated classnames (classes.txt)')
    parser.add_option('--clscol', dest='clscol', type='string', 
                      default='varcls',
                      help='dictionary column for class (varcls)')
    parser.add_option('-d', dest='debug', type='int', default=0,
                      help='debug setting (default: 0)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--eta', dest='eta', type='float', 
                      default=0.25,
                      help='learning rate (0.25)')
    parser.add_option('--fit', dest='fitname', type='string', 
                      default='asasfit.sqlite',
                      help='database file with fitted light curves')
    parser.add_option('--fittype', dest='fittype', type='string', 
                      default='coeffs',
                      help='coeffs (default) / midpoints / fullfit')
    parser.add_option('--logfile', dest='logfile', type='string', 
                      default='trainlog.txt',
                      help='name of logfile (trainlog.txt)')
    parser.add_option('--maxhidden', dest='maxhidden', type='int', 
                      default=0,
                      help='Maximum number of hidden neurons (nr of outputs)')
    parser.add_option('--minhidden', dest='minhidden', type='int', 
                      default=1,
                      help='Minimum number of hidden neurons (1)')
    parser.add_option('--momentum', dest='momentum', type='float', 
                      default=0.9,
                      help='Momentum for driving over local minima (0.9)')
    parser.add_option('--multi', dest='multi', action='store_true', 
                      default=False,
                      help='allow multiple class-results')
    parser.add_option('--mdelta', dest='mdelta', type='float', 
                      default=0.1,
                      help='allowed deviation for multiple classes (0.1)')
    parser.add_option('--nriter', dest='nriter', type='int', 
                      default=100,
                      help='iterations per learning cycle (100)')
    parser.add_option('--noshuffle', dest='shuffle', action='store_false', 
                      default=True,
                      help='disable shuffling of data')
    parser.add_option('--nrnets', dest='nrnets', type='int', 
                      default=1,
                      help='train this many nets (1)')
    parser.add_option('--outtype', dest='outtype', type='string', 
                      default='softmax',
                      help='type of output neurons (softmax, linear or logistic)')
    parser.add_option('--pname', dest='picklename', type='string', 
                      default='mlp.pickle',
                      help='filename for the trained, pickled network (mlp.pickle)')
    parser.add_option('--prb', dest='prb', type='string', 
                      default=None,
                      help='filename with probability database for target vector')
    parser.add_option('--repname', dest='repname', type='string', 
                      default='report.txt',
                      help='filename for written report (default = report.txt)')
    parser.add_option('--resdir', dest='resdir', type='string', 
                      default='results',
                      help='subdirectory for results (default = results)')
    parser.add_option('--resname', dest='resname', type='string', 
                      default='nrresults',
                      help='name for individual result reports)')
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
    parser.add_option('--stopval', dest='stopval', type='float', 
                      default=0.01,
                      help='allowed deviation for multiple classes (0.01)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    if (len(args) == 1):
        options.fitname = args[0]
       
    try: 
        for line in open(options.rootdir + options.clsnames):
            if (len(line.strip()) == 0) or (line.startswith('#')):
                continue
            options.classes = line.split()
    except IOError:
        parser.print_help()
        print 'File ', options.rootdir + options.clsnames, 'not found'
        exit(1)
    
    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")

    if not os.path.exists(options.rootdir + options.resdir):
        os.mkdir(options.rootdir + options.resdir)
    options.lf = Logfile(options.rootdir + options.resdir + '/' + 
                         options.logfile, True, True)
    
    return (options, args)



def splitdata(alld, allt, allnames, trainfrac = 0.5, validfrac = 0.25):
    '''
    Split data into training, validation and testing set according to given
    fractions
    '''
    # ratio of training to validation to testing
    nrrows   = len(allnames)
    trainmax = int(nrrows * trainfrac)
    validmax = int(nrrows * (trainfrac + validfrac))
    
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

    return (traind, traint, trainn, validd, validt, validn, testd, testt, testn)



if __name__ == '__main__':
    (options, args) = parseoptions()
    
    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()
    
    watch = Stopwatch()
    watch.start()
    watchprep = Stopwatch()
    watchprep.start()
    
    options.lf.write('Select statement:')
    options.lf.write(options.select)    
    
    # read from database
    dictarr = None
    coeffarr = None
    nrstars = 0
    noclass = 0
    nofit = 0
    if options.fittype == 'fullfit':
        (dictarr, coeffarr, nrstars, noclass, nofit) = readfulldata(options, 
                                                                    dbc)
    else:
        (dictarr, coeffarr, nrstars, noclass, nofit) = readdata(options, dbc)
    
    # prepare the data, target and normalization values
    if options.prb != None:
        options.prb = dbr.DbReader(options.rootdir + options.prb)
    (alld, allt, allnames, 
     normsubtract, normdivide) = prepdata(options, dbc, dictarr, 
                                                          coeffarr)
    if options.prb != None:
        options.prb.close()
        options.prb = None
    
    options.lf.write(str(nrstars) + ' selected')
    options.lf.write(str(noclass) + ' stars skipped because of unknown class')
    options.lf.write(str(nofit) + ' stars have no fit')
    options.lf.write(str(nrstars - noclass) + ' prepared in ' +
                     str(watchprep.stop()) + ' seconds')
    options.lf.write('')
    watchprep.start()
    
    (traind, traint, trainn, 
     validd, validt, validn, 
     testd, testt, testn)    = splitdata(alld, allt, allnames, 0.5, 0.25)

    # testcode
    options.lf.write('fittype  = ' + options.fittype)
    options.lf.write('neurons  = ' + str(options.minhidden))
    options.lf.write('eta      = ' + str(options.eta))
    options.lf.write('momentum = ' + str(options.momentum))
    options.lf.write('')
    net = mlp.Mlp(traind, traint, nhidden = options.minhidden, 
                  beta = options.beta, momentum = options.momentum, 
                  outtype = options.outtype, 
                  multires = options.multi, mdelta = options.mdelta)
    net.subdir = options.rootdir + options.resdir
    if not os.path.exists(net.subdir):
        os.mkdir(net.subdir)
    net.lf      = options.lf
    net.debug   = options.debug
    net.select  = options.select
    net.comment = str(options)
    net.setnormvalues(normsubtract, normdivide)
    try:
        net = net.earlystopping(traind, traint, validd, validt, 
                                eta = options.eta, 
                                niterations = options.nriter, 
                                stopval = options.stopval, makestats = True)
    except mlp.MlpError as err:
        print 'star name in line ', err.value, ' = ', trainn[err.value]
        
    cm = net.confmat(testd, testt, True)
    net.report('%7s ', '%7d ', '%7.2f ', options.classes, 
               ofname = options.repname)

    pf = open(net.subdir + '/' + options.picklename, 'w')
    pickle.dump(net, pf)
    pf.close()

    options.lf.write(str(watchprep.stop()) + ' seconds for training')
    options.lf.write(str(watch.stop()) + ' seconds over all')
    options.lf.write('')
    options.lf.write('Done')
