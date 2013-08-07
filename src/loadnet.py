'''
Created on Sep 10, 2012

@package  loadnet
@author   map
@version  \$Revision: 1.2 $
@date     \$Date: 2013/08/07 15:33:46 $

read network from database

$Log: loadnet.py,v $
Revision 1.2  2013/08/07 15:33:46  paegerm
add loading from pickle file, hand over options, set --> nset

add loading from pickle file, hand over options, set --> nset

Revision 1.1  2012/09/24 21:27:58  paegerm
read trained network from database

Initial revision
'''


from optparse import OptionParser

import numpy as np
import os
import pickle

import sqlitetools.dbreader as dbr

import mlp
import dbconfig
from stopwatch import *



def readvec(netuid, reader, name):
    nset = reader.fetchall('select * from vector where netuid = ? and name = ? ' +
                          'order by i', (netuid, name))
    vlen = len(nset)
    vals = np.zeros((vlen,))
    for res in nset:
        vals[res['i']] = res['val']
    
    return vals



def loadnet(options):   #options.fqnetdb, uid = None, name = None, pname = None):
    net     = None
    netuid  = None
    netname = None
    
    if ((options.netuid == None) and (options.netname == None) and 
        (options.fqpickle == None)):
        return (net, netuid, netname)
    
    if (options.fqpickle != None):
        pf = open(options.fqpickle)
        net = pickle.load(pf)
        pf.close()
        netname = options.netname
        return (net, netuid, netname)


    netreader = dbr.DbReader(options.fqnetdb)
    ndict = None
    if (options.netuid != None):
        ndict = netreader.fetchone('select * from netdict where uid = ?', 
                                   (options.netuid,))
    else:
        nset = netreader.fetchall('select * from netdict where name = ?', 
                                 (options.netname,))
        setlen = len(nset)
        if (setlen > 1):
            print "WARNING:", setlen, 'entries for ', options.netname, \
                  '! Selecting first'
        ndict = nset[0]
    
    netuid  = ndict['uid']
    netname = ndict['name']
    inputs  = np.zeros((1, ndict['nin']))
    targets = np.zeros((1, ndict['nout'])) 
    
    net = mlp.Mlp(inputs, targets, ndict['nhidden'], ndict['beta'], 
                  ndict['momentum'], ndict['outtype'], ndict['multires'], 
                  ndict['mdelta'])
    net.trainerror = ndict['trainerror']
    net.validerror = ndict['validerror']
    net.stopcount  = ndict['stopcount']
    net.allpercent = ndict['allpercent']
    net.comment    = ndict['comment']
    net.ndata      = ndict['ndata']
    
    # get weights
    nset = netreader.fetchall('select * from weights where netuid = ?', (netuid,))
    for w in nset:
        if w['layer'] == 1:
            net.weights1[w['i']][w['j']] = w['value']
        elif w['layer'] == 2:
            net.weights2[w['i']][w['j']] = w['value']
        else:
            print 'Illegal layer:', w['layer']
    
    # get classes
    nset = netreader.fetchall('select * from classes where netuid = ? order by i', 
                              (netuid,))
    for c in nset:
        if net.classes == None:
            net.classes = []
        net.classes.append(c['class'])
    nclasses = len(net.classes)
        
    # get confusion matrix
    nset = netreader.fetchall('select * from matrix where netuid = ? and ' + 
                              'name = ? order by i, j', (netuid, 'confmat'))
    net.cm = np.zeros((nclasses, nclasses), dtype = int)
    for c in nset:
        net.cm[c['i']][c['j']] = c['val']
    
    # get vectors
    net.normsubtract = readvec(netuid, netreader, 'normsubtract')
    net.normdevide   = readvec(netuid, netreader, 'normdivide')
    net.trainstats   = readvec(netuid, netreader, 'trainstats')
    net.validstats   = readvec(netuid, netreader, 'validstats')
    net.teststats    = readvec(netuid, netreader, 'teststats')
    
    return (net, netuid, netname)
    
    

if __name__ == '__main__':
    net = loadnet('/home/map/data/asas10/asasnet.sqlite', 1)
#    net = loadnet('/home/map/data/asas/asasnet.sqlite', None, 'results_max5_10')
    
    net.report('%7s ', '%7d ', '%7.2f ')
    
    print 'Done'
    
    