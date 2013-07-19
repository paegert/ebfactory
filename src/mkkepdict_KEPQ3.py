'''
Created on Jul 2, 2013

@package  mkkepdict
@author   map
@version  \$Revision: 1.1 $
@date     \$Date: 2013/07/19 20:25:04 $

Make dictionary database for Kepler Q3_Data

$Log: mkkepdict_KEPQ3.py,v $
Revision 1.1  2013/07/19 20:25:04  paegerm
initial revision

Revision 1.1  2013/06/10 22:47:07  parvizm
initial revision

'''

from optparse import OptionParser

import pyfits as pf
import math

import dbwriter as dbw
import dbreader as dbr

import dbconfig
import datetime
from stopwatch import *


if __name__ == '__main__':
    usage = '%prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='debug', type='int', default=0,
                      help='debug setting (default: 0)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Kepq3',
                      help='name of database configuration (default = Kepq3')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='kepq3dict.sqlite',
                      help='dictionary database file')
    parser.add_option('--keplc', dest='keplcname', type='string', 
                      default='kepq3rplc_9.sqlite',
                      help='kepq3 lc database file')
    parser.add_option('--list', dest='listname', type='string', 
                      default='Q3_9_list.txt',
                      help='FITS data file list')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for .py scripts files (default = ./)')
    parser.add_option('--fitsdir', dest='fitsdir', type='string', 
                      default='/home/parvizm/REU/kepq3files/',
                      help='directory for fits data list (default = /home/parvizm/REU/kepq3files/')
    parser.add_option('--subdir', dest='subdir', type='string', 
                      default='Q3_9',
                      help='directory for fits files')
#     parser.add_option('--fitsdir', dest='fitsdir', type='string', 
#                       default='./',
#                       help='directory for fits data list (default = ./')
#     parser.add_option('--subdir', dest='subdir', type='string', 
#                       default='./',
#                       help='directory for fits files')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'
    if (options.fitsdir[-1] != '/'):
        options.fitsdir += '/'
    if (options.subdir[-1] != '/'):
        options.subdir += '/'

    if (len(args) == 2):
        options.dictname  = args[0]
        options.keplcname = args[1]
    
    start = datetime.datetime.today()  
    watch_x = Stopwatch()
    watch_y = Stopwatch()
    
    
    cls = getattr(dbconfig, options.dbconfig)
    dbconfig = cls()

    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, 
                              dbconfig.dictcols, dbconfig.dicttname, 
                              dbconfig.dicttypes, dbconfig.dictnulls)
#     dictwriter.create_dict_idx()
    dictreader = dbr.DbReader (options.rootdir + options.dictname)
    keplcwriter = dbw.DbWriter(options.rootdir + options.keplcname, 
                              dbconfig.keplccols, dbconfig.keplctname, 
                              dbconfig.keplctypes, dbconfig.keplcnulls)
    keplcwriter.create_lc_idx()
    
# Set staruid = 0 for initial dictionary creation or set staruid = 1 for subsequent entries.
#     staruid = 0
    staruid = 1
    
    dinslist = []
    tinslist = []
    hdu      = []
    tbdata   = []
    
    bjd     = []
    s_flux  = []
    s_err   = []
    s_bkg   = []
    b_err   = []
    p_flux  = []
    p_err   = []

    PHASE   = None
    D_FLUX  = None
    D_ERR   = None
    varcls  = None

    
    # open FITS header and insert star into dictionary
    print 'IMPORT REPORT'
    print '\n', start,': Begin Kepler', options.subdir, 'import to', options.dictname, 'and', options.keplcname
    
    f_file = open(options.fitsdir + options.listname, 'r')
    
    for line in f_file:
            
        # open FITS header and insert star into dictionary
        print '\n', '\n', 'processing file: ', line
        watch_x.start()
        try:
            hdu = pf.open(options.fitsdir + options.subdir + line)
        except IOError:
            print '\t', '-corrupt or missing FITS file'
            continue
    
        KIC     = hdu[0].header['KEPLERID']
        RA      = hdu[0].header['RA_OBJ']
        DEC     = hdu[0].header['DEC_OBJ']
        PMRA    = hdu[0].header['PMRA']
        PMDEC   = hdu[0].header['PMDEC']
        GMAG    = hdu[0].header['GMAG'] 
        RMAG    = hdu[0].header['RMAG']
        IMAG    = hdu[0].header['IMAG']
        ZMAG    = hdu[0].header['ZMAG']
        D51MAG  = hdu[0].header['D51MAG']
        JMAG    = hdu[0].header['JMAG']
        HMAG    = hdu[0].header['HMAG']
        KMAG    = hdu[0].header['KMAG']
        KEPMAG  = hdu[0].header['KEPMAG']
        TEFF    = hdu[0].header['TEFF']
        LOGG    = hdu[0].header['LOGG']
        FEH     = hdu[0].header['FEH']
        AV      = hdu[0].header['AV'] 
        RADIUS  = hdu[0].header['RADIUS']
        
        try:
            a = math.isnan(RA)
        except AttributeError: 
            RA = -999
        try:
            a = math.isnan(DEC)
        except AttributeError: 
            DEC = -999
        try:
            a = math.isnan(PMRA)
        except AttributeError: 
            PMRA = -999   
        try:
            a = math.isnan(PMDEC)
        except AttributeError: 
            PMDEC = -999  
        try:
            a = math.isnan(GMAG)
        except AttributeError: 
            GMAG = -999  
        try:
            a = math.isnan(RMAG)
        except AttributeError: 
            RMAG = -999   
        try:
            a = math.isnan(IMAG)
        except AttributeError: 
            IMAG = -999  
        try:
            a = math.isnan(ZMAG)
        except AttributeError: 
            ZMAG = -999
        try:
            a = math.isnan(D51MAG)
        except AttributeError:    
            D51MAG = -999    
        try:
            a = math.isnan(JMAG)
        except AttributeError: 
            JMAG = -999  
        try:
            a = math.isnan(HMAG)
        except AttributeError: 
            HMAG = -999   
        try:
            a = math.isnan(KMAG)
        except AttributeError: 
            KMAG = -999   
        try:
            a = math.isnan(KEPMAG)
        except AttributeError: 
            KEPMAG = -999   
        try:
            a = math.isnan(TEFF)
        except AttributeError: 
            TEFF = -999   
        try:
            a = math.isnan(LOGG)
        except AttributeError: 
            LOGG = -999 
        try:
            a = math.isnan(FEH)
        except AttributeError: 
            FEH = -999
        try:
            a = math.isnan(AV)
        except AttributeError: 
            AV = -999   
        try:
            a = math.isnan(RADIUS)
        except AttributeError: 
            RADIUS = -999    
   
        dinslist = (KIC, RA, DEC, PMRA, PMDEC, GMAG, RMAG, IMAG, ZMAG, D51MAG,
                        JMAG, HMAG, KMAG, KEPMAG, varcls, TEFF, LOGG, FEH, AV, RADIUS)           
        if staruid == 0:
            update = 0
            skip   = 1
            staruid  = 1
            dictwriter.insert((dinslist,), True)
            print '\t', 'staruid', staruid, 'inserted into', options.dictname, 'in', watch_x.stop(), 's'
        else:
            update = 0
            skip   = 0
            generator = dictreader.traverse('select * from stars order by UID;', None)
            for star in generator: 
                staruid = star['UID']
                kic     = int(star['KIC'])
                kepmag  = star['KEPMAG']
                
                if options.debug > 0: 
                    print 'KIC =', type(KIC), KIC, '&', 'kic =', type(kic), kic
                    print 'KEPMAG =', type(KEPMAG), KEPMAG, '&', 'kepmag =', type(kepmag), kepmag
                
                if KIC == kic and KEPMAG != -999 and KEPMAG != kepmag:
                    update = 1
                    dictwriter.update('update stars set KEPMAG = ? where uid = ?;', [(KEPMAG, staruid)])
                    print '\t', '- existing KIC of staruid', staruid, 'no new', options.dictname, 'entry inserted'
                    print '\t', '- new KEPMAG detected for staruid', staruid, 'and updated from', kepmag, 'to', KEPMAG, 'in', watch_x.stop(), 's'
                    break   
                elif KIC == kic and KEPMAG == kepmag:
                    skip = 1
                    print '\t', '- existing KIC of staruid', staruid, 'no new', options.dictname, 'entry inserted'
                    break
                else: 
                    pass
                
        if options.debug > 0:        
            print 'update =', update, '&', 'skip =', skip

        if update == 0 and skip == 0: 
            staruid = staruid+1 
            dictwriter.insert((dinslist,), True)
            print '\t', 'staruid', staruid, 'inserted into', options.dictname, 'in', watch_x.stop(), 's'
         
        #open FITS table and insert light curve into database
        watch_y.start()
        tbdata = hdu[1].data
        
        bjd     = tbdata.field('TIME')
        s_flux  = tbdata.field('SAP_FLUX')
        s_err   = tbdata.field('SAP_FLUX_ERR')
        s_bkg   = tbdata.field('SAP_BKG')
        s_qual  = tbdata.field('SAP_QUALITY')
        b_err   = tbdata.field('SAP_BKG_ERR')
        p_flux  = tbdata.field('PDCSAP_FLUX')
        p_err   = tbdata.field('PDCSAP_FLUX_ERR')
        
        x = 0
        y = 0
        for row in bjd:
            
            if s_qual[x] == 0:
                
                if math.isnan(bjd[x]):
                    BJD = None
                else: BJD = round(float(bjd[x]),6)
                
                if math.isnan(s_flux[x]):
                    S_FLUX = None
                else: S_FLUX = round(float(s_flux[x]),6)
                
                if math.isnan(s_err[x]):
                    S_ERR = None
                else: S_ERR = round(float(s_err[x]),6)
                
                if math.isnan(s_bkg[x]):
                    S_BKG = None
                else: S_BKG = round(float(s_bkg[x]),6)
                
                if math.isnan(b_err[x]):
                    B_ERR = None
                else: B_ERR = round(float(b_err[x]),6)
                
                if math.isnan(p_flux[x]):
                    P_FLUX = None
                else: P_FLUX = round(float(p_flux[x]),6)
                
                if math.isnan(p_err[x]):
                    P_ERR = None
                else: P_ERR = round(float(p_err[x]),6)
                
                if "llc" in line:
                    C_FLAG = 0
                else: C_FLAG = 1 
                 
                tinslist = (staruid, BJD, PHASE, S_FLUX, S_ERR, S_BKG, B_ERR, P_FLUX, P_ERR, D_FLUX, D_ERR, C_FLAG)
                
                if (len(tinslist) > 0):
                    keplcwriter.insert((tinslist,), True)
                y+=1
            x+=1
            
        hdu.close()
        print '\t', y, 'rows of data inserted into', options.keplcname, 'in', watch_y.stop(), 's'
        
         
    dictwriter.close()
    keplcwriter.close()
     
    stop = datetime.datetime.today()
    print '\n', '\n', stop, ': Finished with', staruid, 'stars imported to', options.dictname, 'and', options.keplcname, 'in', stop-start
    print 'done'