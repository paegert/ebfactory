'''
Created on Sep 18, 2012

@package  rephase
@author   map
@version  \$Revision: 1.1 $
@date     \$Date: 2013/08/13 19:36:22 $

rephase lightcurves

$Log: rephase.py,v $
Revision 1.1  2013/08/13 19:36:22  paegerm
Initial revision

Initial revision
'''

from optparse import OptionParser

import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr

import dbconfig
from functions import *
from stopwatch import *



if __name__ == '__main__':
    usage = '%prog [options] plcdbfile'
    parser = OptionParser(usage=usage)
    parser.add_option('--blc', dest='blcname', type='string', 
                      default='asasblc.sqlite',
                      help='database file with binned light curves')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--method', dest='method', type='string', 
                      default='split',
                      help='min, max, split (default)')    
    parser.add_option('--plc', dest='plcname', type='string', 
                      default='asasplc.sqlite',
                      help='database file with phased light curves')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./)')
    parser.add_option('--select', dest='select', type='string', 
                      default=None,
                      help='select statement for dictionary (Default: None)')
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')
    parser.add_option('--starid', dest='starid', type='string', 
                      default=None,
                      help='name or id of star to rephase (default: None)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    if (len(args) == 1):
        options.plcname = args[0]
        
    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")
        
    if (options.select == None) and (options.starid == None):
        print 'Neither select statement nor starid are given'
        parser.print_help()
        exit(1)
        
    if (options.starid != None):
        options.select = "select * from stars where id = '" + options.starid + "'"                         

    watch = Stopwatch()
    watch.start()

    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()

    print options.select
    
    dictreader = dbr.DbReader(options.rootdir + options.dictname)   
    stars = dictreader.fetchall(options.select)
    dictreader.close()
    

    nrstars = 0    
    for star in stars:
        nrstars += 1
        plcreader = dbr.DbReader(options.rootdir + options.plcname)
        blcreader = dbr.DbReader(options.rootdir + options.blcname)
        plc = plcreader.getlc(star['uid'])
        blc = blcreader.getlc(star['uid'])
        mmin = 99
        mmax = 0
        pmin = None
        pmax = None
        for entry in blc:
            if (entry['normmag'] < mmin):
                mmin = entry['normmag']
                pmin = entry['phase']
            if (entry['normmag'] > mmax):
                mmax = entry['normmag']
                pmax = entry['phase']
        plcreader.close()
        blcreader.close()
        shift = 0.0
        if options.method == 'max':
            shift = pmax
        if options.method == 'min':
            shift = pmin
        if options.method == 'split':
            if (star[dbc.t['mean']] < star[dbc.t['median']]):
                shift = pmax
            else:
                shift = pmin
        
        blcs = []
        for entry in blc:
            uid = entry['uid']
            phase = entry['phase'] - shift
            while phase < -0.5:
                phase += 1.0
            while phase > 0.5:
                phase -= 1.0
            blcs.append([phase, uid])
        blcwriter = dbw.DbWriter(options.rootdir + options.blcname, dbc.blccols)
        cmd = 'update stars set phase = ? where uid = ?'
        blcwriter.update(cmd, blcs, True)
        blcwriter.close()

        plcs = []
        for entry in plc:
            uid = entry['uid']
            phase = entry['phase'] - shift
            while phase < -0.5:
                phase += 1.0
            while phase > 0.5:
                phase -= 1.0
            plcs.append([phase, uid])
        plcwriter = dbw.DbWriter(options.rootdir + options.plcname, dbc.plccols)
        cmd = 'update stars set phase = ? where uid = ?'
        plcwriter.update(cmd, plcs, True)
        plcwriter.close()

    print nrstars, 'rephased in', watch.stop(), 's'
    print ''
    print 'Done'