
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
                      default='log_pd_.txt',
                      help='name of logfile (default = log_pd.txt')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Kepq3',
                      help='name of database configuration (default = Kepq3)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='kepq3dict.sqlite',
                      help='dictionary database file')
    parser.add_option('--keplc', dest='keplcname', type='string', 
                      default='kepq3rplc.sqlite',
                      help='database file to read raw_flux & write dtr_flux')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for period script (default = ./)')
    parser.add_option('--dbdir', dest='dbdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./)')
#     parser.add_option('--vtdir', dest='vtdir', type='string', 
#                       default='./VARTOOLS1.202/',
#                       help='directory for deterend files (default = ./VARTOOLS1.202)')
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
    parser.add_option('--dtropt', dest='dtropt', type='string', 
                      default=None,
                      help='options for detrend function inputs; example: --dtropt order=10;  (default: None) ')
   
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'
        
#     if (options.vtdir[-1] != '/'):
#         options.vtdir += '/'

    if (options.dbdir[-1] != '/'):
        options.dbdir += '/'
        
    if (len(args) == 2):
        options.dictname  = args[0]
        options.keplcname = args[1]


    cls = getattr(dbconfig, options.dbconfig)
    dbconfig = cls()
         
    dictreader = dbr.DbReader(options.rootdir + options.dbdir + options.dictname)
    dictwriter = dbw.DbWriter(options.rootdir + options.dbdir + options.dictname, 
                              dbconfig.dictcols, dbconfig.dicttname, 
                              dbconfig.dicttypes, dbconfig.dictnulls, isolevel = None)
    keplcreader = dbr.DbReader(options.rootdir + options.dbdir + options.keplcname)
    
    start = datetime.datetime.today()  
    dstart = str(start)
    watch = Stopwatch()
    
    log = lf.Logfile(options.logfile, True, False)
    log.write('PERIOD FINDING REPORT:')
    log.write()
    keplcname = str(options.keplcname)
    log.write(dstart +' Begin period finding on stars in ' + keplcname + '.')
    log.write()

    nrstars = 0
    generator = dictreader.fetchall(options.select)
    for star in generator:
        staruid = star['UID']
        ustar = str(staruid)
        nrstars += 1
        
        keplc = keplcreader.fetchall('select * from stars where staruid = ' + ustar + ' and SLC_FLAG = 0;')
        if keplc == None or len(keplc)==0:
            if options.debug != 0:
                print 'DEBUG: skipping', ustar
            continue
        log.write()
        log.write('processing staruid: ' + ustar) 
        watch.start()
        uids   = [x[0] for x in keplc]
        bjd    = [x[2] for x in keplc]
        dflux  = [x[10] for x in keplc]
        dsig   = [x[11] for x in keplc]
        
        if options.debug != 0:
            print 'DEBUG: # of rows in long-cadence lc =', len(uids)
            print 'DEBUG: input data (1st row) from lc db', 'UID =', uids[0], 'BJD =', bjd[0], 'FLUX =', dflux[0], 'ERR =', dsig[0]
        
#         os.chdir(options.vtdir)
        fd, fout = tempfile.mkstemp()
        for i in range(0,len(uids)):
            if bjd[i] == None or dflux[i] == None or dsig[i] == None: 
                continue # this happens if values are missing
            os.write(fd, "%f %f %f\n" % (bjd[i], dflux[i], dsig[i]))
        os.close(fd)
   
        if options.debug != 0:
            print 'DEBUG: long-cadence lc input file written'
        
        sd, sout = tempfile.mkstemp()
        os.close(sd)
        
        os.system( "vartools -i %s -oneline -ascii -aov Nbin 200 0.1 1000 0.1 0.01 1 0 > %s" % (fout,sout))        
        
        aovfile = open(sout, 'r')
        lines = aovfile.readlines()
        
        if options.debug != 0:
            print 'DEBUG: sout =', lines
        
        for line in lines:
            if line.startswith("Period_1_0 "):
                splitted = line.split('Period_1_0         =')
                
                if options.debug != 0:  
                    print 'DEBUG: [1] =', splitted[1]
                
                period = round(float(splitted[1]),6)
            else: continue
        aovfile.close()
#         os.chdir(options.rootdir)
        
        if options.debug != 0:
            print 'DEBUG: Period =', period 
            
        updates = []         
        updates.append([period, staruid])
        dictwriter.update('update stars set PERIOD = ? where uid = ?;', updates, True)
                    
        stop = watch.stop()
        stop = str(stop)   
        log.write('\t' + 'staruid ' + ustar + ' period found and updated in ' + stop +  's')    
        
        if nrstars == 100:
            dstop = datetime.datetime.today()
            final = dstop-start
            final = str(final) 
            dstop = str(dstop)
            nrs = str(nrstars)
            log.write()
            log.write(dstop + ' Found period and updated ' + nrs + ' stars detrended in ' + final)
    
    keplcreader.close()
    dictreader.close()   
    dictwriter.close()
     
    dstop = datetime.datetime.today()
    final = dstop-start
    final = str(final) 
    dstop = str(dstop)
    nrstars = str(nrstars)
    log.write()
    log.write(dstop + ' Finished with period finding for ' + nrstars + ' stars in ' + final)
    log.write('done')   

    
    
    
    
    
    
