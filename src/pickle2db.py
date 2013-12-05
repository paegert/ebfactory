'''
Created on Sep 6, 2012

@package  pickle2db
@author   map
@version  \$Revision: 1.3 $
@date     \$Date: 2013/12/05 17:20:06 $

convert pickeled net to database, devide --> divide

$Log: pickle2db.py,v $
Revision 1.3  2013/12/05 17:20:06  paegerm
deleting classes option (obsolete, we store the classes in the network)

deleting classes option (obsolete, we store the classes in the network)

Revision 1.2  2013/08/07 15:43:10  paegerm
adding select and remark to network dictionary data,
renaming dict to ndict where the dictionary of the trained network is meant

Revision 1.1  2012/09/24 21:39:34  paegerm
convert pickeled network into database

Initial revision
'''


from optparse import OptionParser

import numpy as np
import os
import pickle

import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr

import mlp
import dbconfig
from stopwatch import *



def writevec(netuid, writer, vector, name):
    vals = []
    for i in xrange(len(vector)):
        vals.append([netuid, name, i, vector[i]])
    writer.insert(vals, True)
    


if __name__ == '__main__':
    usage = '%prog [options] [dbname]'
    parser = OptionParser(usage=usage)
#     parser.add_option('--classes', dest='clsnames', type='string', 
#                       default='classes.txt',
#                       help='file with space separated classnames (classes.txt)')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
    parser.add_option('--dbname', dest='dbname', type='string', 
                      default='asasnet.sqlite',
                      help='name of database file')
    parser.add_option('--name', dest='name', type='string', 
                      default=None,
                      help='name for the trained network (None)')
    parser.add_option('--pname', dest='picklename', type='string', 
                      default='mlp.pickle',
                      help='filename for the trained, pickled network (mlp.pickle)')
    parser.add_option('--remark', dest='remark', type='string', 
                      default=None,
                      help='remark for this run')
    parser.add_option('--resdir', dest='resdir', type='string', 
                      default='results',
                      help='subdirectory for results (default = results)')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    if (len(args) == 1):
        options.fitname = args[0]
        
#     for line in open(options.rootdir + options.clsnames):
#         if (len(line.strip()) == 0) or (line.startswith('#')):
#             continue
#         options.classes = line.split()
        
    if (options.name == None):
        pos = options.picklename.rfind('.')
        options.name = options.resdir + '_' + options.picklename[:pos]
        
    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()
    
    watch = Stopwatch()
    watch.start()

    pf = open(options.rootdir + options.resdir + '/' + options.picklename)
    net = pickle.load(pf)
    pf.close()
    
    ndictwriter = dbw.DbWriter(options.rootdir + options.dbname, dbc.netdictcols, 
                               dbc.netdicttname, dbc.netdicttypes, 
                               dbc.netdictnulls)
    (w1rows, w1cols) = np.shape(net.weights1)
    (w2rows, w2cols) = np.shape(net.weights2)
    mres = 0
    if net.multires == True:
        mres = 1
    ndictdata = [options.name, net.nin, net.nout, net.ndata, net.nhidden, 
                 net.beta, net.momentum, net.eta, net.outtype, mres,
                 net.mdelta, w1rows, w1cols, w2rows, w2cols, len(net.classes),
                 net.trainerror, net.validerror, net.stopcount, net.allpercent, 
                 net.comment, net.select, options.remark]
#                 None, None, None]
    ndictwriter.insert((ndictdata,), True)
    # netuid = ndictwriter.dbcurs.lastrowid
    res = ndictwriter.dbcurs.execute('SELECT uid from ' + dbc.netdicttname + 
                                     " where name = '" + options.name + "';")
    (netuid,) =  res.fetchone()
    ndictwriter.close()
    
    # write weights
    vals = []
    for i in xrange(w1rows):
        for j in xrange(w1cols):
            vals.append([netuid, 1, i, j, net.weights1[i][j]])
    writer = dbw.DbWriter(options.rootdir + options.dbname, dbc.netwcols,
                          dbc.netwtname, dbc.netwtypes, dbc.netwnulls)
    writer.insert(vals, True)
    vals = []
    for i in xrange(w2rows):
        for j in xrange(w2cols):
            vals.append([netuid, 2, i, j, net.weights2[i][j]])
    writer.insert(vals, True)
    writer.close()
    
    # write classes
    vals = []
    for i in xrange(len(net.classes)):
        vals.append([netuid, i, net.classes[i]])
    writer = dbw.DbWriter(options.rootdir + options.dbname, dbc.netclasscols,
                          dbc.netclasstname, dbc.netclasstypes, dbc.netclassnulls)
    writer.insert(vals, True)
    writer.close()
    
    # write confusion matrix
    if (net.cm != None):
        vals = []
        (rows, cols) = np.shape(net.cm)
        for i in xrange(rows):
            for j in xrange(cols):
                vals.append([netuid, dbc.confmatname, i, j, int(net.cm[i][j])])
        writer = dbw.DbWriter(options.rootdir + options.dbname, dbc.netmatcols,
                              dbc.netmattname, dbc.netmattypes, dbc.netmatnulls)
        writer.insert(vals, True)
        writer.close()
    
    writer = dbw.DbWriter(options.rootdir + options.dbname, dbc.netveccols,
                          dbc.netvectname, dbc.netvectypes, dbc.netvecnulls)
    writevec(netuid, writer, net.normdivide, 'normdivide')
    writevec(netuid, writer, net.normsubtract, 'normsubtract')

    writevec(netuid, writer, net.trainstats, 'trainstats')
    writevec(netuid, writer, net.validstats, 'validstats')
    writevec(netuid, writer, net.teststats, 'teststats')
    
    writer.close()

    print 'Network written in', watch.stop(), 's'
    print "Done"
    
