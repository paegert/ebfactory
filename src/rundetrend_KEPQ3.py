
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

        
    
def detrend (hjd, flux, sig, order=10, breaks=None, br_orders=None, br_lo=None, br_hi=None, sc_unif=True, lo=1., hi=3., config=None, debug=False, verbose=False):
    '''
    runs sigclip and returns the detrended lightcurve and the baseline
    ex: sc_hjd, sc_flux, sc_sig, sc_baseline = detrend(hjd, flux, sig, order, breaks)
    '''
#     breaks = breaks if breaks is not None else [54953.5, 54964.0, 55000.5, 55016.0, 55033.30934, 55063.8, 55079.181605, 55092.7, 55114.0, 55124.0, 55155.5, 55184.0, 55217.0, 55232.0, 55276.0, 55308.5, 55337.5, 55372.0, 55400.0, 55432.0, 55462.5, 55493.5, 55523.5, 55544.0, 55561.0, 55595.5, 55638.0, 55678.5, 55707.5, 55739.5, 55770.5, 55802.5, 55833.5, 55866.0, 55896.5, 55904.5, 55932.0, 55951.0, 55959.5, 55965.0, 55987.0, 55996.0, 56015.5, 56048.5, 56078.5, 56106.5, 56126.5, 56138.5, 56170.5, 56204.5]
    breaks = breaks if breaks is not None else [120.5, 131.0, 167.5, 183.0, 200.30934, 230.8, 246.181605, 259.7, 281.0, 291.0, 322.5, 351.0, 384.0, 399.0, 443.0, 475.5, 504.5, 539.0, 567.0, 599.0, 629.5, 660.5, 690.5, 711.0, 728.0, 762.5, 805.0, 845.5,    874.5,    906.5,    937.5,    969.5,    1000.5,    1033.0,    1063.5,    1071.5,    1099.0,    1118.0,    1126.5,   1132.0,    1154.0,    1163.0,    1182.5,    1215.5,   1245.5,    1273.5,   1293.5,    1305.5, 1337.5, 1371.5]

   
    if config is not None:
        order = config['sc_order']
        breaks = config['breaks']
        br_orders = config['br_orders']
        br_lo = config['br_lo']
        br_hi = config['br_hi']
        sc_unif = config['sc_unif']
        lo = config['sc_lo']
        hi = config['sc_hi']
    orders=br_orders
    if orders is None:
        orders = [-1]*len(breaks)
    if br_lo is None:
        br_lo = [-1]*len(breaks)
    if br_hi is None:
        br_hi = [-1]*len(breaks)
    if breaks!=None:
        if sc_unif:
            for i in range(len(orders)):
                if orders[i]==-1:
                    orders[i]=int(order)
        for i in range(len(br_lo)):
            if br_lo[i]==-1:
                br_lo[i]=lo
            if br_hi[i]==-1:
                br_hi[i]=hi
                
        if breaks != None and orders != None and len(breaks) != len(orders):
            print "ERROR: len(breaks) must be len(orders)!"
            print "breaks: ", breaks
            print "orders: ", orders
            return

        # Break indices:
        br = [0]*len(breaks)

        # The following loop relies on breaks[] being sorted. It loops through all
        # hjd values and populates br[] with break indices.
        breaks.sort()
        for i in range(0,len(hjd)):
            for j in range(0,len(breaks)):
                if hjd[i] < breaks[j]:
                    for k in range (j,len(breaks)):
                        br[k] = i+1
                    break

        if debug:
            debug_print ("break indices: %s" % br)
            debug_print ("total array length: %d" % (len(hjd)))

        # Split arrays at breaks into sub-arrays:
        hjd = np.split(hjd,br)
        flux = np.split(flux,br)
        sig = np.split(sig,br)

    else:
        hjd = [hjd]
        flux = [flux]
        sig = [sig]

        orders=[order]

    if debug:
        for i in range(0,len(hjd)):
            debug_print ("part %d length: %d" % (i+1, len(hjd[i])))

    # Initialize return arrays:
    sc_hjd, sc_flux, sc_sig, sc_baseline = np.array([]), np.array([]), np.array([]), np.array([])

    Q1len = len(hjd[0]) if len(hjd[0]) != 0 else 1626
    if not sc_unif:
        #~ orders = [0.0]*(len(breaks)+1)
        orders.append(-1) #sc_unif requires one extra entry
        for i in range(0,len(hjd)):
            if orders[i]==-1:
                orders[i] = max(min(int(float(order)/Q1len*len(hjd[i])),500),1)

    for i in range(0,len(hjd)):
        if len(hjd[i]) == 0: continue # this happens if data are missing in some Qs
        fd, fout = tempfile.mkstemp()
        for j in range(0,len(hjd[i])):
            os.write(fd, "%f %e %e\n" % (hjd[i][j], flux[i][j], sig[i][j]))
        os.close(fd)

        sd, sout = tempfile.mkstemp()
        os.close(sd)

        if verbose:
            os.system("sigclip -o %d --autoiter -s %f %f --pd %s > %s" % (orders[i], lo, hi, fout, sout))
        else:
            os.system("sigclip -o %d --autoiter -s %f %f --pd %s > %s 2> /dev/null" % (orders[i], br_lo[i], br_hi[i], fout, sout))

        #~ try:
        if True:
            scb, scx, scy, scz = np.loadtxt(sout, usecols=(3,4,5,6), unpack=True)
        #~ except:
            #~ scb, scx, scy, scz = [], [], [], []
        
        sc_hjd  = np.append(sc_hjd, scx)
        sc_flux = np.append(sc_flux, scy)
        sc_sig = np.append(sc_sig,scz)
        sc_baseline = np.append(sc_baseline, scb)

        os.remove (fout)
        os.remove (sout)

    return sc_hjd, sc_flux, sc_sig, sc_baseline


if __name__ == '__main__':

    usage = '%prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 0)')
    parser.add_option('--log', dest='logfile', type='string', 
                      default='log_rd.txt',
                      help='name of logfile (default = log_rd.txt')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Kepq3',
                      help='name of database configuration (default = Kepq3)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='_dict.sqlite',
                      help='dictionary database file')
    parser.add_option('--keplc', dest='keplcname', type='string', 
                      default='_rplc.sqlite',
                      help='database file to read raw_flux & write dtr_flux')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for detrend files (default = ./)')
    parser.add_option('--dbdir', dest='dbdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./)')
#     parser.add_option('--plotdir', dest='plotdir', type='string', 
#                       default='/kepq3_dtr_plots/',
#                       help='directory for dtr_plot files (default = /kepq3_dtr_plots/)')
#     parser.add_option('--dtrdir', dest='dtrdir', type='string', 
#                       default='/dev/shm/kepler/',
#                       help='directory for deterend files (default = ./)')
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
        
#     if (options.dtrdir[-1] != '/'):
#         options.dtrdir += '/'

    if (len(args) == 2):
        options.dictname  = args[0]
        options.keplcname = args[1]
    
#     if options.selfile != None:
#         fsel = open(options.rootdir + options.selfile)
#         options.select = fsel.read()
#         fsel.close()
#         options.select = options.select.replace("\n", "")
    
#     options.lf = Logfile(options.logfile, True, True)

    cls = getattr(dbconfig, options.dbconfig)
    dbconfig = cls()
         
    dictreader = dbr.DbReader(options.rootdir + options.dbdir + options.dictname)
    keplcreader = dbr.DbReader(options.rootdir + options.dbdir + options.keplcname)
    keplcwriter = dbw.DbWriter(options.rootdir + options.dbdir + options.keplcname, 
                               dbconfig.keplccols, dbconfig.keplctname, 
                               dbconfig.keplctypes, dbconfig.keplcnulls)
    
    start = datetime.datetime.today()  
    dstart = str(start)
    watch = Stopwatch()
    
    log = lf.Logfile(options.logfile, True, True)
    log.write('DETRENDING REPORT:')
    log.write()
    keplcname = str(options.keplcname)
    log.write(dstart +' Begin detrending SAP_FLUX from ' + keplcname + ' order=10.')
    log.write()

    nrstars = 0
    generator = dictreader.traverse(options.select, None, 1000)
    for star in generator:
        staruid = star['UID']
        ustar = str(staruid)
#         starkic = star['KIC']
        
        
      
        watch.start()
        keplc = keplcreader.fetchall('select * from stars where staruid = ' + ustar + ' order by SLC_FLAG asc;')
        if keplc == None or len(keplc)==0:
            continue
        nrstars += 1
        log.write()
        log.write('processing staruid: ' + ustar)
        slc    = [x[12] for x in keplc] 
        uids   = [x[0] for x in keplc]
        bjd    = [x[2] for x in keplc]
        rflux  = [x[4] for x in keplc]
        rsig   = [x[5] for x in keplc]
        
 
        print slc[0], uids[0], bjd[0], rflux[0], rsig[0]
        
        k=0
        for j in range(0,len(slc)):
            if slc[j] == 0:
                k+=1
#         logS = lf.Logfile(None, True, True)
#         K = str(k)
#         logS.write(K)
        if k < len(slc):
            uidsl   = uids[0:k]
            bjdl    = bjd[0:k]
            rfluxl  = rflux[0:k]
            rsigl   = rsig[0:k]
            
            (sc_hjd, sc_flux, sc_sig, sc_baseline) = detrend(bjdl, rfluxl, rsigl)
            
            i=0
            updates = []
            for i in xrange(len(sc_hjd)):
                updates.append([round(float(sc_flux[i]),6), round(float(sc_sig[i]),6), uidsl[i]])
    
            keplcwriter.update('update stars set DTR_FLUX = ?, DTR_ERR = ? where uid = ?;',
                                updates, True)
            
            stop = watch.stop()
            stop = str(stop)   
            log.write('\t' + 'staruid ' + ustar + '_LC detrended and updated in ' + stop +  's') 
            
            watch.start()            
            uidss   = uids[k+1:]
            bjds    = bjd[k+1:]
            rfluxs  = rflux[k+1:]
            rsigs   = rsig[k+1:]
            
            blocks = int(len(uidss)/10)
            b_uids   = [0]*10
            b_bjds   = [0]*10
            b_rfluxs = [0]*10
            b_rsigs  = [0]*10
#             print 'length =', len(uidss)
#             print 'blocks =', blocks
            
            b=0
            while b < 10:
#                 print 'for b=', b, 'start:', blocks*b, 'end:', blocks*(b+1)-1
#                 b_uids[0]   = 'Hello b_uids'
#                 print b_uids[0]
                b_uids[b]   = uidss[blocks*b:blocks*(b+1)-1]
                b_bjds[b]   = bjds[blocks*b:blocks*(b+1)-1]
                b_rfluxs[b] = rfluxs[blocks*b:blocks*(b+1)-1]
                b_rsigs[b]  = rsigs[blocks*b:blocks*(b+1)-1]
                if b == 9:
                    b_uids[b]   = uidss[blocks*b:]
                    b_bjds[b]   = bjds[blocks*b:]
                    b_rfluxs[b] = rfluxs[blocks*b:]
                    b_rsigs[b]  = rsigs[blocks*b:]
            
                (sc_hjd, sc_flux, sc_sig, sc_baseline) = detrend(b_bjds[b], b_rfluxs[b], b_rsigs[b])
            
                i=0
                updates = []
                uids = b_uids[b]
                for i in xrange(len(sc_hjd)):
                    updates.append([round(float(sc_flux[i]),6), round(float(sc_sig[i]),6), uids[i]])
        
                keplcwriter.update('update stars set DTR_FLUX = ?, DTR_ERR = ? where uid = ?;',
                                    updates, True)
                b+=1
                
            stop = watch.stop()
            stop = str(stop)   
            log.write('\t' + 'staruid ' + ustar + '_SC detrended and updated in ' + stop +  's') 
            
        else:
            (sc_hjd, sc_flux, sc_sig, sc_baseline) = detrend(bjd, rflux, rsig)
            
            i=0
            updates = []
            for i in xrange(len(sc_hjd)):
                updates.append([round(float(sc_flux[i]),6), round(float(sc_sig[i]),6), uids[i]])
    
            keplcwriter.update('update stars set DTR_FLUX = ?, DTR_ERR = ? where uid = ?;',
                                updates, True)
            
            stop = watch.stop()
            stop = str(stop)   
            log.write('\t' + 'staruid ' + ustar + '_LC detrended and updated in ' + stop +  's')     
            
            if nrstars == 100:
                dstop = datetime.datetime.today()
                final = dstop-start
                final = str(final) 
                dstop = str(dstop)
                nrs = str(nrstars)
                log.write()
                log.write(dstop + ' Detrended ' + nrs + ' stars detrended, plotted, and updated in ' + final)
            
#         watch.start()
#         plotname  = options.rootdir + options.plotdir + starkic + '_kepq3_dtr.png'
#         pl.plot(sc_hjd, sc_flux,'k.')
#         pl.xticks(fontsize = options.fsize)
#         pl.yticks(fontsize = options.fsize)
#         pl.xlabel('BJD', fontsize=options.fsize)
#         pl.ylabel('DTR_FLUX', fontsize=options.fsize)
#         pl.title(starkic +'_Kepq3: DTR_FLUX', fontsize=options.fsize)
#         pl.savefig(plotname)
#     #   pl.show()
#         pl.clf()
#         kstar = str(starkic)
#         stop = watch.stop()
#         stop = str(stop)
#         log.write('\t' + 'plotted and saved: '+ kstar + '_kepq3_dtr.png in ' + stop + 's')
#         log.write()
    keplcwriter.close()
     
    dstop = datetime.datetime.today()
    final = dstop-start
    final = str(final) 
    dstop = str(dstop)
    nrstars = str(nrstars)
    log.write()
    log.write(dstop + ' Finished with ' + nrstars + ' stars detrended, plotted, and updated in ' + final)
    log.write('done')   
    
        
        
        
        
        
        
