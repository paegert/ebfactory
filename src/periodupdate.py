
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
                      default='log_per_upd.txt',
                      help='name of logfile (default = log_pd.txt')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Kepq3',
                      help='name of database configuration (default = Kepq3)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='kepq3dict.sqlite',
                      help='dictionary database file')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='/home/parvizm/kepler/',
                      help='directory for period script (default = ./)')
#     parser.add_option('--dbdir', dest='dbdir', type='string', 
#                       default='/Users/mahmoudparvizi/kepler/',
#                       help='directory for database files (default = ./)')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars order by uid;',
                      help='select statement for dictionary ' +
                           '(Default: select * from stars order by uid;)')
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
         
    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, 
                              dbconfig.dictcols, dbconfig.dicttname, 
                              dbconfig.dicttypes, dbconfig.dictnulls, isolevel=None)

    dictreader = dbr.DbReader(options.rootdir + options.dictname)

    start = datetime.datetime.today()  
    dstart = str(start)
    watch = Stopwatch()
    
    log = lf.Logfile(options.logfile, True, False)
    log.write('PERIOD UPDATE REPORT AoV1 and AoV2:')
    log.write()
    log.write(dstart +' Begin updating period in stars')
    log.write()
    
    nrstars = 0
    generator = dictreader.fetchall('select * from stars order by uid;')
    for star in generator:
        watch.start()
        log.write('updating period in staruid ' + str(staruid))
        staruid = star['UID']
        av1per = star['AoV1_PER']
        av2per = star['AoV2_PER']
        av1aov = star['AoV1_AOV']
        av2aov = star['AoV2_AOV']
        av1snr = star['AoV1_SNR']
        av2snr = star['AoV2_SNR']
        av1neg = star['AoV1_NEG']
        av2neg = star['AoV2_NEG']
        
        if av2neg > av1neg:
            PERIOD = av2per
            AOV    = av2aov
            SNR    = av2snr
        else:
            PERIOD = av1per
            AOV    = av1aov
            SNR    = av1snr
            
        updates = []         
        updates.append([PERIOD, SNR, AOV, staruid])
        dictwriter.update('update stars set PERIOD = ?, SNR = ?, AOV = ? where UID = ?;', updates, True)
        stop = watch.stop()
        log.write('\t' + '- period updated in ' + str(stop))
        nrstars+=1   
       
    dictreader.close()    
    dictwriter.close()
     
    dstop = datetime.datetime.today()
    final = dstop-start
    final = str(final) 
    dstop = str(dstop)
    nrstars = str(nrstars)
    log.write()
    log.write(dstop + ' Finished with period update for ' + nrstars + ' stars in ' + final)
    log.write('done')   

    
    
    
    
    
    
