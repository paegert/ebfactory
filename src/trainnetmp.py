'''
Created on Jul 18, 2012

@package  trainnetmp
@author   map
@version  \$Revision: 1.7 $
@date     \$Date: 2013/12/05 17:38:14 $

Multi-processing training of multiple networks at once. Be sue to have the 
environment variable OMP_NUM_THREADS set to a reasonable value (number of CPUs
for example). The default is working with just 2 processes.

$Log: trainnetmp.py,v $
Revision 1.7  2013/12/05 17:38:14  paegerm
add prb option for database with probabilities for training (currently only
Asas 1.1)
adding resname option
adding chi2 option
store str(options) as net.comment
change name of report files from nrhidden to fittype
add stopval to args if not shuffling

add prb option for database with probabilities for training (currently only
Asas 1.1)
adding resname option
adding chi2 option
store str(options) as net.comment
change name of report files from nrhidden to fittype
add stopval to args if not shuffling

Revision 1.6  2013/09/05 19:10:33  paegerm
reassigning net after training, adding fullfit option

Revision 1.5  2013/08/13 19:15:29  paegerm
add net.select, write network options to logfile

Revision 1.4  2013/07/26 20:33:59  paegerm
passing logfile to net

Revision 1.3  2012/11/30 20:40:59  paegerm
adding clscol option, adding logfile and converting print statements

Revision 1.2  2012/09/24 21:46:52  paegerm
store select statement as comment in net object, class mlp --> Mlp

Revision 1.1  2012/07/20 20:24:34  paegerm
Initial revision

'''


from optparse import OptionParser
from multiprocessing import Pool

import numpy as np
import os
import pickle

import mlp
from stopwatch import *
from trainnet import *
from logfile import *



def callnet(*args, **kwargs):
    '''
    Wrapper function for calling the neural network
    '''
    net = kwargs['net']
    lf = kwargs['logfile']
    lf.write('start training ' + str(kwargs['nrhidden']) + ' ' + 
             str(kwargs['iteration']))
    net = net.earlystopping(*args)
    lf.write('finished ' + str(kwargs['nrhidden']) + ' ' + 
             str(kwargs['iteration']))
    return (net, kwargs['nrhidden'], kwargs['iteration'])



if __name__ == '__main__':
    (options, args) = parseoptions()
    resdir = options.rootdir + options.resdir
    if not os.path.exists(resdir):
        os.mkdir(resdir)
    
    cls = getattr(dbconfig, 'Asas')
    dbc = cls()
    
    watch = Stopwatch()
    watch.start()
    watchprep = Stopwatch()
    watchprep.start()
    
    # read from database
    
    options.lf.write(options.select)
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
     normsubtract, normdevide) = prepdata(options, dbc, dictarr, coeffarr)
    if options.prb != None:
        options.prb.close()
        options.prb = None
    
    options.lf.write(str(nrstars) + ' selected')
    options.lf.write(str(noclass) + ' stars with unknown class')
    options.lf.write(str(nofit) + ' stars without fit')
    options.lf.write(str(nrstars - noclass) + ' prepared in ' + 
                     str(watchprep.stop()) + ' seconds')
    options.lf.write('')
    options.lf.write('fittype  = ' + options.fittype)
    options.lf.write('neurons  = ' + str(options.minhidden))
    options.lf.write('eta      = ' + str(options.eta))
    options.lf.write('momentum = ' + str(options.momentum))
    options.lf.write('')

    watchprep.start()

    # split into training, validation and testing set
    (traind, traint, trainn, 
     validd, validt, validn, 
     testd, testt, testn)    = splitdata(alld, allt, allnames, 0.5, 0.25)

    nrprocess = int(os.environ['OMP_NUM_THREADS'])
    if (nrprocess <= 0):
        nrprocess = 2

    args = (traind, traint, validd, validt, options.eta, options.nriter, 
            options.stopval, True)
    maxpercent = 0.0
    results = []
    pool = Pool(processes = nrprocess)
    for i in xrange(options.minhidden, options.maxhidden + 1):
        for j in range(options.nrnets):
            if (options.shuffle == True):
                (alld, allt, allnames) = reshuffle(alld, allt, allnames)
                (traind, traint, trainn, 
                 validd, validt, validn, 
                 testd, testt, testn) = splitdata(alld, allt, allnames, 
                                                  0.5, 0.25)
                args = (traind, traint, validd, validt, 
                        options.eta, options.nriter, options.stopval, True)

            net = mlp.Mlp(traind, traint, nhidden = i,
                          beta = options.beta, momentum = options.momentum, 
                          outtype = options.outtype, 
                          multires = options.multi, mdelta = options.mdelta)
            net.subdir  = resdir
            net.select  = options.select
            net.comment = str(options)
            if not os.path.exists(net.subdir):
                os.mkdir(net.subdir)
            net.lf    = Logfile(options.rootdir + options.resdir + '/' + 
                         options.logfile + str(i) + '_' + str(j), True, True)
            net.debug = options.debug
            net.setnormvalues(normsubtract, normdevide)

            kwargs = {'net': net, 'nrhidden': i, 'iteration': j, 
                      'logfile': net.lf}
#            callnet(*args, **kwargs)
            results.append(pool.apply_async(callnet, args, kwargs))
            
    # collect results and write a summary report, pickle the network with the 
    # best result
    pool.close()
    pool.join()
    nrres = len(results)
    oldj = options.minhidden - 1
    mean = 0.0
    maxpercent = 0.0
    minvalerr  = 1.0e6
    oline = '%2d:  ' % options.minhidden
    rname = resdir + '/'  + options.fittype + str(options.minhidden) + '_'
    # resarr = (maxhidden - minhidden + 1) * [[[] for j in xrange(0, nrtests)]]
    of = open(resdir + '/' + options.repname, 'w')
    of.write('Summary report\n')
    jmax = -1
    kmax = -1
    jvmin = -1
    kvmin = -1
    for i in xrange(nrres):
        (net, j, k) = results[i].get(1)
        #print i, ': ', j, ', ', k 
        # resarr[j - minhidden][k] = net
        if (j != oldj):
            if (oldj != options.minhidden - 1):
                oline += '%5.2f\n' % (mean / options.nrnets)
                of.write(oline)
                mean = 0.0
                oline = '%2d:  ' % (j)
            oldj = j
        rname = '/' + options.resname + str(j) + '_' + str(k) + '.txt'
        cm = net.confmat(testd, testt, True)
        net.report('%7s ', '%7d ', '%7.2f ', options.classes, rname)
        val = net.allpercent
        mean += val
        if val > maxpercent:
            jmax = j
            kmax = k
            maxpercent = val
            pf = open(resdir + '/' + options.picklename + 'maxp' + 
                      str(options.minhidden) + '_' + 
                      str(options.maxhidden) + '.pickle', 'w')
            pickle.dump(net, pf)
            pf.close()
            print j, ', ', k, ': maxpercent = ', maxpercent
        val = 100.0 * net.validerror / len(validd)
        if val < minvalerr:
            jvmin = j
            kvmin = k
            minvalerr = val
            pf = open(resdir + '/' + options.picklename + 'minv' + 
                      str(options.minhidden) + '_' + 
                      str(options.maxhidden) + '.pickle', 'w')
            pickle.dump(net, pf)
            pf.close()
            print j, ', ', k, ': minvalerr = ', minvalerr

        oline += "%5.2f / %5.2f   " % (net.allpercent, 
                                       100.0 * net.validerror / len(validd))
    oline += '%5.2f\n' % (mean / options.nrnets)
    of.write(oline)
    of.write('\n')
    oline = 'max = %5.2f at %d, %d\n' % (maxpercent, jmax, kmax)
    of.write(oline)
    oline = 'min = %5.2f at %d, %d\n' % (minvalerr, jvmin, kvmin)
    of.write(oline)
    oline = '%f minutes over all\n' % (watch.stop() / 60.0)
    of.write(oline)
    of.close()

    options.lf.write(oline)
            
    print ''
    print oline
    print 'done'
