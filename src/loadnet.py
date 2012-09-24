'''
Created on Sep 10, 2012

@package  loadnet
@author   map
@version  \$Revision: 1.1 $
@date     \$Date: 2012/09/24 21:27:58 $

read network from database

$Log: loadnet.py,v $
Revision 1.1  2012/09/24 21:27:58  paegerm
read trained network from database

Initial revision
'''


from optparse import OptionParser

import numpy as np
import os

import sqlitetools.dbreader as dbr

import mlp
import dbconfig
from stopwatch import *



def readvec(netuid, reader, name):
    set = reader.fetchall('select * from vector where netuid = ? and name = ? ' +
                          'order by i', (netuid, name))
    vlen = len(set)
    vals = np.zeros((vlen,))
    for res in set:
        vals[res['i']] = res['val']
    
    return vals



def loadnet(fname, uid = None, name = None):
    if (uid == None) and (name == None):
        return None

    netreader = dbr.DbReader(fname)
    ndict = None
    if (uid != None):
        ndict = netreader.fetchone('select * from netdict where uid = ?', (uid,))
    else:
        set = netreader.fetchall('select * from netdict where name = ?', (name,))
        setlen = len(set)
        if (setlen > 1):
            print "WARNING:", setlen, 'entries for ', name, '! Selecting first'
        ndict = set[0]
    
    netuid  = ndict['uid']    
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
    set = netreader.fetchall('select * from weights where netuid = ?', (netuid,))
    for w in set:
        if w['layer'] == 1:
            net.weights1[w['i']][w['j']] = w['value']
        elif w['layer'] == 2:
            net.weights2[w['i']][w['j']] = w['value']
        else:
            print 'Illegal layer:', w['layer']
    
    # get classes
    set = netreader.fetchall('select * from classes where netuid = ? order by i', 
                             (netuid,))
    for c in set:
        if net.classes == None:
            net.classes = []
        net.classes.append(c['class'])
    nclasses = len(net.classes)
        
    # get confusion matrix
    set = netreader.fetchall('select * from matrix where netuid = ? and ' + 
                             'name = ? order by i, j', (netuid, 'confmat'))
    net.cm = np.zeros((nclasses, nclasses), dtype = int)
    for c in set:
        net.cm[c['i']][c['j']] = c['val']
    
    # get vectors
    net.normsubtract = readvec(netuid, netreader, 'normsubtract')
    net.normdevide   = readvec(netuid, netreader, 'normdivide')
    net.trainstats   = readvec(netuid, netreader, 'trainstats')
    net.validstats   = readvec(netuid, netreader, 'validstats')
    net.teststats    = readvec(netuid, netreader, 'teststats')
    
    return net
    
    

if __name__ == '__main__':
    net = loadnet('/home/map/data/asas/asasnet.sqlite', 1)
#    net = loadnet('/home/map/data/asas/asasnet.sqlite', None, 'results_max5_10')
    
    net.report('%7s ', '%7d ', '%7.2f ')
    
    print 'Done'
    
    