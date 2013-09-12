
from optparse import OptionParser

import numpy as np
import matplotlib.pyplot as pl

import dbconfig
import dbwriter as dbw
import dbreader as dbr
import logfile as lf
import datetime
from stopwatch import *

        

if __name__ == '__main__':

    usage = '%prog [options]'
    parser = OptionParser(usage=usage)
    
    parser.add_option('--log', dest='logfile', type='string', 
                      default='Q3_candidate_log.txt',
                      help='name of logfile (default = log_tp.txt')
    
    parser.add_option('--clog_eb', dest='clog_eb', type='string', 
                      default='Q3_can_EB_log.txt',
                      help='name of can_EB_logfile (default = _can_EB_log.txt')
    parser.add_option('--clog_ec', dest='clog_ec', type='string', 
                      default='Q3_can_EC_log.txt',
                      help='name of can_EC_logfile (default = _can_EC_log.txt')
    parser.add_option('--clog_ed', dest='clog_ed', type='string', 
                      default='Q3_can_ED_log.txt',
                      help='name of can_ED_logfile (default = _can_ED_log.txt')
    parser.add_option('--clog_esd', dest='clog_esd', type='string', 
                      default='Q3_can_ESD_log.txt',
                      help='name of can_ESD_logfile (default = _can_ESD_log.txt')  
    
    parser.add_option('--clog_var', dest='clog_var', type='string', 
                      default='Q3_can_VAR_log.txt',
                      help='name of can_VAR_logfile (default = _can_VAR_log.txt')  
    parser.add_option('--clog_dco', dest='clog_dco', type='string', 
                      default='Q3_can_DCEP-FO_log.txt',
                      help='name of can_DCEP-FO_logfile (default = _can_DCEP-FO_log.txt')
    parser.add_option('--clog_dcu', dest='clog_dcu', type='string', 
                      default='Q3_can_DCEP-FU_log.txt',
                      help='name of can_DCEP-FU_logfile (default = _can_DCEP-FU_log.txt')
    parser.add_option('--clog_dst', dest='clog_dst', type='string', 
                      default='Q3_can_DSCT_log.txt',
                      help='name of can_DSCT_logfile (default = _can_DSCT_log.txt')
    parser.add_option('--clog_mra', dest='clog_mra', type='string', 
                      default='Q3_can_MIRA_log.txt',
                      help='name of can_MIRA_logfile (default = _can_MIRA_log.txt')
    parser.add_option('--clog_rra', dest='clog_rra', type='string', 
                      default='Q3_can_RRAB_log.txt',
                      help='name of can_RRAB_logfile (default = _can_RRAB_log.txt')
    parser.add_option('--clog_rrc', dest='clog_rrc', type='string', 
                      default='Q3_can_RRC_log.txt',
                      help='name of can_RRC_logfile (default = _can_RRC_log.txt')
    parser.add_option('--clog_msc', dest='clog_msc', type='string', 
                      default='Q3_can_MISC_log.txt',
                      help='name of can_MISC_logfile (default = _can_MISC_log.txt')
    
    parser.add_option('--clog_cvar', dest='clog_cvar', type='string', 
                      default='Q3_can_CVAR_log.txt',
                      help='name of can_CVAR_logfile (default = _can_CVAR_log.txt')  
    parser.add_option('--clog_cdco', dest='clog_cdco', type='string', 
                      default='Q3_can_CDCEP-FO_log.txt',
                      help='name of can_CDCEP-FO_logfile (default = _can_CDCEP-FO_log.txt')
    parser.add_option('--clog_cdcu', dest='clog_cdcu', type='string', 
                      default='Q3_can_CDCEP-FU_log.txt',
                      help='name of can_CDCEP-FU_logfile (default = _can_CDCEP-FU_log.txt')
    parser.add_option('--clog_cdst', dest='clog_cdst', type='string', 
                      default='Q3_can_CDSCT_log.txt',
                      help='name of can_CDSCT_logfile (default = _can_CDSCT_log.txt')
    parser.add_option('--clog_cmra', dest='clog_cmra', type='string', 
                      default='Q3_can_CMIRA_log.txt',
                      help='name of can_CMIRA_logfile (default = _can_CMIRA_log.txt')
    parser.add_option('--clog_crra', dest='clog_crra', type='string', 
                      default='Q3_can_CRRAB_log.txt',
                      help='name of can_CRRAB_logfile (default = _can_CRRAB_log.txt')
    parser.add_option('--clog_crrc', dest='clog_crrc', type='string', 
                      default='Q3_can_CRRC_log.txt',
                      help='name of can_CRRC_logfile (default = _can_CRRC_log.txt')
    parser.add_option('--clog_cmsc', dest='clog_cmsc', type='string', 
                      default='Q3_can_CMISC_log.txt',
                      help='name of can_CMISC_logfile (default = _can_CMISC_log.txt')
    
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Kepq3',
                      help='name of database configuration (default = Kepq3)')
    parser.add_option('--ebdict', dest='ebdictname', type='string', 
                      default='kepebdict.sqlite',
                      help='eb-dictionary database file')
    parser.add_option('--q3dict', dest='q3dictname', type='string', 
                      default='kepq3dict.sqlite',
                      help='q3-dictionary database file')
    parser.add_option('--q3Cdict', dest='q3Cdictname', type='string', 
                      default='kepq3cls.sqlite',
                      help='q3-class dictionary database file')
    parser.add_option('--rplc', dest='rplcname', type='string', 
                       default='kepq3rplc_12.sqlite',
                       help='database file with phased light curves (default = kepq3rplc_XX.sqlite)')
    parser.add_option('--blc', dest='blcname', type='string', 
                      default='kepq3blc_12.sqlite',
                      help='database file with binned light curves')
    parser.add_option('--fit', dest='fitname', type='string', 
                      default='kepq3fit_12.sqlite',
                      help='database file with fitted light curves')
    parser.add_option('--fsize', dest='fsize', type='int', 
                      default=18,
                      help='font size for plots (default: 18')
    
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='/home/parvizm/ebf/',
                      help='directory for period script (default = ./)')
    parser.add_option('--dbdir', dest='dbdir', type='string', 
                      default='/home/parvizm/kepler/',
                      help='directory for database files (default = ./)')
    parser.add_option('--plotdir', dest='plotdir', type='string', 
                      default='/home/parvizm/can_plots/',
                      help='directory for database files')

   
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'
    if (options.dbdir[-1] != '/'):
        options.dbdir += '/'
    if (options.plotdir[-1] != '/'):
        options.plotdir += '/'
        
    cls = getattr(dbconfig, options.dbconfig)
    dbconfig = cls()
         
    ebdictreader  = dbr.DbReader(options.dbdir + options.ebdictname)
    q3dictreader  = dbr.DbReader(options.dbdir + options.q3dictname)
    q3Cdictreader = dbr.DbReader(options.dbdir + options.q3Cdictname)
    q3rplcreader  = dbr.DbReader(options.dbdir + options.rplcname)
    q3blcreader   = dbr.DbReader(options.dbdir + options.blcname)
    q3fitreader   = dbr.DbReader(options.dbdir + options.fitname)

    start = datetime.datetime.today()  
    dstart = str(start)
    watch = Stopwatch()
    
    log = lf.Logfile(options.logfile, True, True)
    
    clogeb  = lf.Logfile(options.clog_eb,  True, False)
    clogec  = lf.Logfile(options.clog_ec,  True, False)
    cloged  = lf.Logfile(options.clog_ed,  True, False)
    clogesd = lf.Logfile(options.clog_esd, True, False)
    
    clogvar = lf.Logfile(options.clog_var, True, False)
    clogdco = lf.Logfile(options.clog_dco, True, False)
    clogdcu = lf.Logfile(options.clog_dcu, True, False)
    clogdst = lf.Logfile(options.clog_dst, True, False)
    clogmra = lf.Logfile(options.clog_mra, True, False)
    clogrra = lf.Logfile(options.clog_rra, True, False)
    clogrrc = lf.Logfile(options.clog_rrc, True, False)
    clogmsc = lf.Logfile(options.clog_msc, True, False)
    
    clogcvar = lf.Logfile(options.clog_cvar, True, False)
    clogcdco = lf.Logfile(options.clog_cdco, True, False)
    clogcdcu = lf.Logfile(options.clog_cdcu, True, False)
    clogcdst = lf.Logfile(options.clog_cdst, True, False)
    clogcmra = lf.Logfile(options.clog_cmra, True, False)
    clogcrra = lf.Logfile(options.clog_crra, True, False)
    clogcrrc = lf.Logfile(options.clog_crrc, True, False)
    clogcmsc = lf.Logfile(options.clog_cmsc, True, False)
        
    log.write('VARIABLE CANDIDATE REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    log.write()
    
    clogeb.write('#EB CANDIDTAE REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogeb.write('#')
    clogeb.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogec.write('#EC CANDIDTAE REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogec.write('#')
    clogec.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    cloged.write('#ED CANDIDTAE REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    cloged.write('#')
    cloged.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogesd.write('#ESD CANDIDTAE REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogesd.write('#')
    clogesd.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    
    clogvar.write('#VAR CANDIDTAE REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogvar.write('#')
    clogvar.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogdco.write('#DCEP-FO CANDIDTAE REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogdco.write('#')
    clogdco.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogdcu.write('#DCEP-FU CANDIDTAE REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogdcu.write('#')
    clogdcu.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogdst.write('#DSCT CANDIDTAE REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogdst.write('#')
    clogdst.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogmra.write('#MIRA CANDIDTAE REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogmra.write('#')
    clogmra.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogrra.write('#RRAB CANDIDTAE REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogrra.write('#')
    clogrra.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogrrc.write('#RRC CANDIDTAE REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogrrc.write('#')
    clogrrc.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogmsc.write('#MISC CANDIDTAE REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogmsc.write('#')
    clogmsc.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')

    clogcvar.write('#VAR CANDIDTAE CATALOGED AS EB REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogcvar.write('#')
    clogcvar.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogcdco.write('#DCEP-FO CANDIDTAE CATALOGED AS EB REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogcdco.write('#')
    clogcdco.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogcdcu.write('#DCEP-FU CANDIDTAE CATALOGED AS EB REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogcdcu.write('#')
    clogcdcu.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogcdst.write('#DSCT CANDIDTAE CATALOGED AS EB REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogcdst.write('#')
    clogcdst.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogcmra.write('#MIRA CANDIDTAE CATALOGED AS EB REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogcmra.write('#')
    clogcmra.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogcrra.write('#RRAB CANDIDTAE CATALOGED AS EB REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogcrra.write('#')
    clogcrra.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogcrrc.write('#RRC CANDIDTAE CATALOGED AS EB REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogcrrc.write('#')
    clogcrrc.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    clogcmsc.write('#MISC CANDIDTAE CATALOGED AS EB REPORT: Kepler Q3 Data Set (ClassProb >= 0.90 Period < 30d)')
    clogcmsc.write('#')
    clogcmsc.write('#Num' + '\t' + '\t' + 'UID' + '\t' + '\t' + 'KIC')
    
    log.write(dstart +' Begin KIC compare between stars in ' + options.q3Cdictname + 
              ' and ' + options.ebdictname + '.')
    log.write()
    
    nrstars = 1
    nrsame  = 0
    
    nreb  = 0
    nrec  = 0
    nred  = 0
    nresd = 0
    
    nrvar = 0
    nrdco = 0
    nrdcu = 0
    nrdst = 0
    nrmra = 0
    nrrra = 0
    nrrrc = 0
    nrmsc = 0
    
    nrcvar = 0
    nrcdco = 0
    nrcdcu = 0
    nrcdst = 0
    nrcmra = 0
    nrcrra = 0
    nrcrrc = 0
    nrcmsc = 0
    
    nrplot = 0
        
    eb = ebdictreader.fetchall('select UID, KIC from stars order by UID;')
    ebuid = [x[0] for x in eb]
    ebkic = [x[1] for x in eb]
    ebkics = [0]*len(eb)
    for i in range (0,len(eb)):
        ebkics[i] = ebkic[i]
    
    q3Cgenerator = q3Cdictreader.fetchall('select staruid, id, cls1, prob1 from classification where prob1 >= 0.90;')
    for star in q3Cgenerator:
        staruid = star['staruid']
        kic = star['id']
        cls1 = star['cls1']
        if cls1 == None or len(cls1) == 0:
            continue
        prb1 = star['prob1']
        if prb1 == None:
            continue
        
        q3per = q3dictreader.fetchall('select period from vars where staruid = ' + str(staruid) + ';')
        for p in q3per:
            period = p['period']
        
        if cls1 == 'EC':
            if kic in ebkics:
                nrsame+=1
                log.write(str(nrstars) + ' skipping: found ' + str(kic) + ' in kepebdict.sqlite')
                continue
            nreb+=1
            nrec+=1
            clogeb.write(str(nreb) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
            clogec.write(str(nrec) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
            pname = 'EB(EC)'
            plotdir = options.plotdir + 'eb/'
            
        elif cls1 == 'ED':
            if kic in ebkics:
                nrsame+=1
                log.write(str(nrstars) + ' skipping: found ' + str(kic) + ' in kepebdict.sqlite')
                continue
            nreb+=1
            nred+=1
            clogeb.write(str(nreb) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
            cloged.write(str(nred) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
            pname = 'EB(ED)'
            plotdir = options.plotdir + 'eb/'
            
        elif cls1 == 'ESD':
            if kic in ebkics:
                nrsame+=1
                log.write(str(nrstars) + ' skipping: found ' + str(kic) + ' in kepebdict.sqlite')
                continue
            nreb+=1
            nresd+=1
            clogeb.write(str(nreb) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
            clogesd.write(str(nresd) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
            pname = 'EB(ESD)'
            plotdir = options.plotdir + 'eb/'
            
        elif cls1 == 'DCEP-FO':
            if kic in ebkics:
                nrcvar+=1
                nrcdco+=1
                log.write(str(nrstars) + ' Flag: DCEP-FO found ' + str(kic) + ' in kepebdict.sqlite')
                clogcvar.write(str(nrcvar) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                clogcdco.write(str(nrcdco) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                pname = 'KEBC3-DCEP-FO'
                plotdir = options.plotdir + 'dcep_fo_c/'
            else:    
                nrvar+=1
                nrdco+=1
                clogvar.write(str(nrvar) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                clogdco.write(str(nrdco) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                pname = 'DCEP-FO'
                plotdir = options.plotdir + 'dcep_fo/'
            
        elif cls1 == 'DCEP-FU':
            if kic in ebkics:
                nrcvar+=1
                nrcdcu+=1
                log.write(str(nrstars) + ' Flag: DCEP-FU found ' + str(kic) + ' in kepebdict.sqlite')
                clogcvar.write(str(nrcvar) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                clogcdcu.write(str(nrcdcu) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                pname = 'KEBC3-DCEP-FU'
                plotdir = options.plotdir + 'dcep_fu_c/'
            else:
                nrvar+=1
                nrdcu+=1
                clogvar.write(str(nrvar) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                clogdcu.write(str(nrdcu) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic)) 
                pname = 'DCEP-FU' 
                plotdir = options.plotdir + 'dcep_fu/'    
                        
        elif cls1 == 'DSCT':
            if kic in ebkics:
                nrcvar+=1
                nrcdst+=1
                log.write(str(nrstars) + ' Flag: DSCT found ' + str(kic) + ' in kepebdict.sqlite')
                clogcvar.write(str(nrcvar) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                clogcdst.write(str(nrcdst) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                pname = 'KEBC3-DSCT'
                plotdir = options.plotdir + 'dsct_c/'
            else:
                nrvar+=1
                nrdst+=1
                clogvar.write(str(nrvar) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                clogdst.write(str(nrdst) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic)) 
                pname = 'DSCT'  
                plotdir = options.plotdir + 'dsct/'    
                        
        elif cls1 == 'MIRA':
            if kic in ebkics:
                nrcvar+=1
                nrcmra+=1
                log.write(str(nrstars) + ' Flag: MIRA found ' + str(kic) + ' in kepebdict.sqlite')
                clogcvar.write(str(nrcvar) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                clogcmra.write(str(nrcmra) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                pname = 'KEBC3-MIRA'
                plotdir = options.plotdir + 'mira_c/'
            else:
                nrvar+=1
                nrmra+=1
                clogvar.write(str(nrvar) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                clogmra.write(str(nrmra) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic)) 
                pname = 'MIRA' 
                plotdir = options.plotdir + 'mira/'
                
        elif cls1 == 'RRAB':
            if kic in ebkics:
                nrcvar+=1
                nrcrra+=1
                log.write(str(nrstars) + ' Flag: RRAB found ' + str(kic) + ' in kepebdict.sqlite')
                clogcvar.write(str(nrcvar) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                clogcrra.write(str(nrcrra) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                pname = 'KEBC3-RRAB'
                plotdir = options.plotdir + 'rrab_c/'
            else:
                nrvar+=1
                nrrra+=1
                clogvar.write(str(nrvar) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                clogrra.write(str(nrrra) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic)) 
                pname = 'RRAB'
                plotdir = options.plotdir + 'rrab/'     
                          
        elif cls1 == 'RRC':
            if kic in ebkics:
                nrcvar+=1
                nrcrrc+=1
                log.write(str(nrstars) + ' Flag: RRC found ' + str(kic) + ' in kepebdict.sqlite')
                clogcvar.write(str(nrcvar) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                clogcrrc.write(str(nrcrrc) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                pname = 'KEBC3-RRC'
                plotdir = options.plotdir + 'rrc_c/'
            else:
                nrvar+=1
                nrrrc+=1
                clogvar.write(str(nrvar) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
                clogrrc.write(str(nrrrc) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic)) 
                pname = 'RRC'
                plotdir = options.plotdir + 'rrc/'    
                            
        elif cls1 == 'MISC':
            if kic in ebkics:
                nrcmsc+=1
                log.write(str(nrstars) + ' Flag: MISC found ' + str(kic) + ' in kepebdict.sqlite')
                clogcmsc.write(str(nrcmsc) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic))
            else:
                nrmsc+=1
                clogmsc.write(str(nrmsc) + '\t' + '\t' + str(staruid) + '\t' + '\t' + str(kic)) 
            continue  
            
        log.write(str(nrstars) + ' logging and plotting ' + str(kic))    
            
        rplc = q3rplcreader.fetchall('select * from stars where staruid = ' + str(staruid) + ' and SLC_FLAG = 0;')
        if rplc == None or len(rplc)==0:
            continue
        blc  = q3blcreader.fetchall('select * from stars where staruid = ' + str(staruid) + ';')
        if blc == None or len(blc)==0:
            continue
        fit  = q3fitreader.fetchall('select * from midpoints where staruid = ' + str(staruid) + ';')
        if fit == None or len(fit)==0:
            continue
        rplc_phases  = [x[3] for x in rplc]
        rplc_dfluxes = [x[10] for x in rplc] 
        blc_phases   = [x[2] for x in blc]
        blc_dfluxes  = [x[3] for x in blc]
        fit_phases   = [[x[2], x[4], x[6], x[8], x[10], x[12], x[14], x[16]] for x in fit]
        fit_dfluxes  = [[x[3], x[5], x[7], x[9], x[11], x[13], x[15], x[17]] for x in fit]

        plotname = plotdir + str(kic) + '_Q3_' + pname + '_candidate.png'
        pl.plot(rplc_phases, rplc_dfluxes, 'k.',
                blc_phases, blc_dfluxes, 'r.',
                fit_phases, fit_dfluxes, 'bo')
        pl.xticks(fontsize = options.fsize)
        pl.yticks(fontsize = options.fsize)
        pl.xlim(-0.5, 0.5)
        pl.xlabel('Phase (Period = ' + str(period) + 'd)', fontsize=options.fsize)
        pl.ylabel('normalized flux', fontsize=options.fsize)
        pl.legend(('dtr_flux', 'bin_flux', 'fit_flux'), loc=0)
        pl.title(pname + '_candidate_KIC_' + str(kic), fontsize=options.fsize)
        pl.savefig(plotname)
        pl.clf()
        log.write('\t' + '-saved plot to ' + plotname) 
        nrplot+=1  
        nrstars+=1   
        
    ebdictreader.close()   
    q3dictreader.close() 
    q3Cdictreader.close()
    q3rplcreader.close()
    q3blcreader.close()
    q3fitreader.close()
    
    dstop = datetime.datetime.today()
    final = dstop-start
    final = str(final) 
    dstop = str(dstop)
    log.write()
    log.write(dstop)
    log.write('Finished with Q3 VARIABLE CANDIDATE REPORT (period < 30d) KIC recovery from Kepler Q3 data set in ' + final)
    log.write()
    log.write('\t' + 'Identified (probability >= 0.90) ' + str(nreb) + 
              ' EBs (period < 30d) in Kepler Q3 data set not in ' + options.ebdictname)
    log.write()
    log.write('\t' + 'Classified ' + str(nrec)  + ' of those as EC')
    log.write('\t' + 'Classified ' + str(nred)  + ' of those as ED')
    log.write('\t' + 'Classified ' + str(nresd) + ' of those as ESD')
    log.write()
    log.write('\t' + 'Identified (probability >= 0.90) ' + str(nrvar) + 
              ' Other Variables (period < 30d) in Kepler Q3 data set not in ' + options.ebdictname)
    log.write('\t' + 'Classified ' + str(nrdco) + ' of those as DCEP-FO')
    log.write('\t' + 'Classified ' + str(nrdcu) + ' of those as DCEP-FU')
    log.write('\t' + 'Classified ' + str(nrdst) + ' of those as DSCT')
    log.write('\t' + 'Classified ' + str(nrmra) + ' of those as MIRA')
    log.write('\t' + 'Classified ' + str(nrrra) + ' of those as RRAB')
    log.write('\t' + 'Classified ' + str(nrrrc) + ' of those as RRC')
    log.write('\t' + 'Classified ' + str(nrmsc) + ' of those as MISC') 
    log.write()
    log.write('\t' + 'Identified (probability >= 0.90) ' + str(nrcvar) + 
              ' Other Variables (period < 30d) in Kepler Q3 data set cataloged as EB in ' + options.ebdictname)
    log.write('\t' + 'Classified ' + str(nrcdco) + ' of those EBs as DCEP-FO')
    log.write('\t' + 'Classified ' + str(nrcdcu) + ' of those EBs as DCEP-FU')
    log.write('\t' + 'Classified ' + str(nrcdst) + ' of those EBs as DSCT')
    log.write('\t' + 'Classified ' + str(nrcmra) + ' of those EBs as MIRA')
    log.write('\t' + 'Classified ' + str(nrcrra) + ' of those EBs as RRAB')
    log.write('\t' + 'Classified ' + str(nrcrrc) + ' of those EBs as RRC')
    log.write('\t' + 'Classified ' + str(nrcmsc) + ' of those EBs as MISC')
    log.write('done')

    
    
    
    
    
    
