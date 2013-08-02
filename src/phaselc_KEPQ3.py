
from optparse import OptionParser
import os
import subprocess
import tempfile
import matplotlib.pyplot as pl
import numpy as np

import random
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
                      default='log_phaselc_78.txt',
                      help='name of logfile (default = log_pd.txt')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Kepq3',
                      help='name of database configuration (default = Kepq3flat)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='kepq3dict_var.sqlite',
                      help='dictionary database file')
    parser.add_option('--keplc', dest='keplcname', type='string', 
                      default='kepq3rplc_78.sqlite',
                      help='database file to read raw_flux & write dtr_flux')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='/home/parvizm/workspace/ebf/src/',
                      help='directory for .py scripts (default = ./)')
    parser.add_option('--dbdir', dest='dbdir', type='string', 
                      default='/home/parvizm/REU/kepq3files/',
                      help='directory for database files (default = ./)')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars order by uid;',
                      help='select statement for dictionary ' +
                           '(Default: select * from stars order by uid;)')
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')
    parser.add_option('--fsize', dest='fsize', type='int', 
                      default=18,
                      help='font size for plots (default: 18')
   
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'
         
    if (options.dbdir[-1] != '/'):
        options.dbdir += '/'
        
    if (len(args) == 2):
        options.dictname    = args[0]
        options.keplcname   = args[1]
       
        
    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")

    cls = getattr(dbconfig, options.dbconfig)
    dbconfig = cls()
         
    dictreader  = dbr.DbReader(options.dbdir + options.dictname)
    keplcreader = dbr.DbReader(options.dbdir + options.keplcname)
    keplcwriter = dbw.DbWriter(options.dbdir + options.keplcname, 
                               dbconfig.rplccols, dbconfig.rplctname, 
                               dbconfig.rplctypes, dbconfig.rplcnulls, isolevel = None)
    start = datetime.datetime.today()  
    dstart = str(start)
    watch = Stopwatch()
    
    log = lf.Logfile(options.logfile, True, False)
    log.write('Q3 LC PHASING REPORT: 0.1 < period < 30d')
    log.write()
    keplcname = str(options.keplcname)
    log.write(dstart +' Begin phasing Q3 lcs in ' + keplcname + '.')
    log.write()

    nrstars = 0
    generator = dictreader.fetchall('select * from stars;')
    for star in generator:
        staruid = star['staruid']
        ustar = str(staruid)
        starkic = star['KIC']
        kstar = str(starkic)
        period = star['PERIOD']
        
        keplc = keplcreader.fetchall('select * from stars where staruid = ' + ustar + ' and SLC_FLAG = 0;')
        if keplc == None or len(keplc)==0:
            if options.debug != 0:
                print 'DEBUG: skipping', ustar
            continue
        log.write()
        log.write('processing staruid: ' + ustar)
        watch.start()
        uids   = [x[0]  for x in keplc]
        bjd    = [x[2]  for x in keplc]
        dflux  = [x[10] for x in keplc]
        maxf = max(dflux)
        medf = np.median(dflux)
        minf = min(dflux)
        
        fr = (maxf-medf)/(maxf-minf)
         
        if fr >= 0.5:
            tzero = maxf      
        else:
            tzero = minf

        phase =[0.0]*len(uids)        
        for j in range(0,len(uids)):
            if bjd[j] == None: 
                continue # this happens if values are missing 
            if dflux[j] == tzero:
                pzero = (bjd[j]/period) - int(bjd[j]/period)
                phase[j] = pzero
            else:
                phase[j] = (bjd[j]/period) - int(bjd[j]/period)
                   
        for k in range(0,len(uids)):
            phase[k] = phase[k]-pzero
            if phase[k] < -0.5:
                phase[k] = phase[k]+1.0
            if phase[k] > 0.5:
                phase[k] = phase[k]-1.0
                
        updates = []
        for i in range(0, len(uids)):
            updates.append([round(float(phase[i]),6), uids[i]])
    
        keplcwriter.update('update stars set PHASE = ? where uid = ?;', updates, True)
                    
#         plotname = options.rootdir + 'q3phase_plots/' + starkic + '_Q3phased.png'
#         pl.plot(phase, dflux, 'k.')
#         pl.xticks(fontsize = options.fsize)
#         pl.yticks(fontsize = options.fsize)
#         pl.xlim(-0.5, 0.5)
#         pl.xlabel('Phase (Period = ' + str(period) + 'd)', fontsize=options.fsize)
#         pl.ylabel('normalized flux', fontsize=options.fsize)
#         pl.title('phased lc of_' + starkic + ' _Q3', fontsize=options.fsize)
#         pl.savefig(plotname)
#         pl.clf()
             
        stop = watch.stop()
        stop = str(stop)   
        log.write('\t' + '- phased lc plotted in ' + stop +  's')    
        nrstars+=1
    
    keplcwriter.close()            
    keplcreader.close()
    dictreader.close()   
     
    dstop = datetime.datetime.today()
    final = dstop-start
    final = str(final) 
    dstop = str(dstop)
    nrstars = str(nrstars)
    log.write()
    log.write(dstop + ' Finished with phasing of ' + nrstars + ' stars in ' + final)
    log.write('done')   

    
    
    
    
    
    
