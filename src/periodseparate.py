
from optparse import OptionParser
import os
import subprocess
import tempfile
import matplotlib.pyplot as pl
import numpy as np

import dbconfig
import dbwriter as dbw
import dbreader as dbr
import logfile as lf
import datetime
from stopwatch import *

        

if __name__ == '__main__':

    usage = '%prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='debug', type='int', default=0,
                      help='debug setting (default: 0)')
    parser.add_option('--log', dest='logfile', type='string', 
                      default='log_per_sep.txt',
                      help='name of logfile (default = log_pd.txt')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Kepq3var',
                      help='name of database configuration (default = Kepq3)')
    parser.add_option('--rdict', dest='rdictname', type='string', 
                      default='kepq3dict.sqlite',
                      help='dictionary database file')
    parser.add_option('--wdict', dest='wdictname', type='string', 
                      default='kepq3dict_var.sqlite',
                      help='dictionary database file')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='/home/parvizm/kepler/',
                      help='directory for period script (default = ./)')
#     parser.add_option('--dbdir', dest='dbdir', type='string', 
#                       default='/Users/mahmoudparvizi/kepler/',
#                       help='directory for database files (default = ./)')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars where AoV1_AOV < 100 ' + 
                      'and AoV2_AOV < 100 and AoV1_SNR < 100 and AoV2_SNR < 100 ' + 
                      'and AoV1_NEG < 500 and AoV2_NEG < 500;',
                      help='(Default: select * from stars order by uid;)')
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')

   
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

#     if (options.dbdir[-1] != '/'):
#         options.dbdir += '/'
        
#     if (len(args) == 1):
#         options.dictname  = args[0]

    cls = getattr(dbconfig, options.dbconfig)
    dbconfig = cls()
         
    dictwriter = dbw.DbWriter(options.rootdir + options.wdictname, 
                              dbconfig.dictcols, dbconfig.dicttname, 
                              dbconfig.dicttypes, dbconfig.dictnulls, isolevel=None)
    dictwriter.create_dict_idx()
    dictreader = dbr.DbReader(options.rootdir + options.rdictname)

    start = datetime.datetime.today()  
    dstart = str(start)
    watch = Stopwatch()
    
    log = lf.Logfile(options.logfile, True, True)
    log.write('PERIOD SEPARATE REPORT:')
    log.write()
    log.write(dstart +' Begin period separate in stars')
    log.write()
    
    nrstars = 0
    allstars = dictreader.fetchall('select UID, KIC, PERIOD from stars;')
    nonvars  = dictreader.fetchall(options.select)
    nvu = [x[0] for x in nonvars]
    nonuids = [0]*len(nonvars)
    for i in range (0,len(nonvars)):
        nonuids[i] = nvu[i]
    for star in allstars:
        staruid = star['UID']
        if staruid in nonuids:
            continue
        else:
            starkic = star['KIC']
            period  = star['PERIOD']
            log.write('star - ' + str(nrstars) + ': processing staruid ' + str(staruid))
            watch.start()
            dinslist = (staruid, starkic, period)
            dictwriter.insert((dinslist,), True)
            stop = watch.stop()
            log.write('\t' + 'inserted in ' + str(stop) + 's')
            nrstars+=1  
       
    dictreader.close()    
    dictwriter.close()
     
    dstop = datetime.datetime.today()
    final = dstop-start
    final = str(final) 
    dstop = str(dstop)
    nrstars = str(nrstars)
    log.write()
    log.write(dstop + ' Finished with period separate for ' + nrstars + ' stars in ' + final)
    log.write('done')   

    
    
    
    
    
    
