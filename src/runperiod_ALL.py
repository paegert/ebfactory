
from optparse import OptionParser
import os
import tempfile

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
                      default='LOG_ALLPER_12.txt',
                      help='name of logfile (default = log_pd.txt')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Kepebper',
                      help='name of database configuration (default = Kepq3)')
    parser.add_option('--ebdict', dest='ebdictname', type='string', 
                      default='kepebdict.sqlite',
                      help='KEBC3 dictionary database file')   
    parser.add_option('--q3dict', dest='q3dictname', type='string', 
                      default='kepq3dict.sqlite',
                      help='q3 dictionary database file')
    parser.add_option('--pddict', dest='pddictname', type='string', 
                      default='kepebdict_per3.sqlite',
                      help='q3 dictionary database file')
    parser.add_option('--keplc', dest='keplcname', type='string', 
                      default='kepq3rplc_12.sqlite',
                      help='database file to read raw_flux & write dtr_flux')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='/home/parvizm/ebf/',
                      help='directory for period script (default = ./)')
    parser.add_option('--dbdir', dest='dbdir', type='string', 
                      default='/home/parvizm/kepler/',
                      help='directory for database files (default = ./)')
#     parser.add_option('--vtdir', dest='vtdir', type='string', 
#                       default='./VARTOOLS1.202/',
#                       help='directory for vartools files (default = ./VARTOOLS1.202)')
    parser.add_option('--fc2dir', dest='fc2dir', type='string', 
                      default='/home/parvizm/FastChi2-1.03/',
                      help='directory for fc2 files (default = ./FastChi2-1.03)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    if (options.dbdir[-1] != '/'):
        options.dbdir += '/'
       
#     if (options.vtdir[-1] != '/'):
#         options.vtdir += '/'

    if (options.fc2dir[-1] != '/'):
        optionsfc2tdir += '/'

    cls = getattr(dbconfig, options.dbconfig)
    dbconfig = cls()
         
    ebdictreader = dbr.DbReader(options.dbdir + options.ebdictname)
    q3dictreader = dbr.DbReader(options.dbdir + options.q3dictname)
    
#     tname = [dicttnamea1, dicttnamea2, dicttnameb1, dicttnameb2, dicttnamef1, dicttnamef2]
#     cols  = [dictcolsa1, dictcolsa2, dictcolsb1, dictcolsb2, dictcolsf1, dictcolsf2]
#     types = [dicttypesa1, dicttypesa2, dicttypesb1, dicttypesb2, dicttypesf1, dicttypesf2]
#     nulls = [dictnullsa1, dictnullsa2, dictnullsb1, dictnullsb2, dictnullsf1, dictnullsf2 ]

    dictwritera1 = dbw.DbWriter(options.dbdir + options.pddictname, 
                                dbconfig.dictcolsa1, dbconfig.dicttnamea1, dbconfig.dicttypesa1, dbconfig.dictnullsa1, 
                                isolevel = None)
    dictwritera2 = dbw.DbWriter(options.dbdir + options.pddictname, 
                                dbconfig.dictcolsa2, dbconfig.dicttnamea2, dbconfig.dicttypesa2, dbconfig.dictnullsa2, 
                                isolevel = None)
    dictwriterb1 = dbw.DbWriter(options.dbdir + options.pddictname, 
                                dbconfig.dictcolsb1, dbconfig.dicttnameb1, dbconfig.dicttypesb1, dbconfig.dictnullsb1, 
                                isolevel = None)
    dictwriterb2 = dbw.DbWriter(options.dbdir + options.pddictname, 
                                dbconfig.dictcolsb2, dbconfig.dicttnameb2, dbconfig.dicttypesb2, dbconfig.dictnullsb2, 
                                isolevel = None)
    dictwriterf1 = dbw.DbWriter(options.dbdir + options.pddictname, 
                                dbconfig.dictcolsf1, dbconfig.dicttnamef1, dbconfig.dicttypesf1, dbconfig.dictnullsf1, 
                                isolevel = None)
    dictwriterf2 = dbw.DbWriter(options.dbdir + options.pddictname, 
                                dbconfig.dictcolsf2, dbconfig.dicttnamef2, dbconfig.dicttypesf2, dbconfig.dictnullsf2, 
                                isolevel = None)
    
    
    
    dstart = datetime.datetime.today()  
    watch = Stopwatch()
    
    log = lf.Logfile(options.logfile, True, True)
    log.write('PERIOD FINDING REPORT: ALL METHODS (0.1 < period < 30d)')
    log.write()
    log.write(str(dstart) +' Begin period finding on KEBC3 stars in ' + options.q3dictname + '.')
    log.write()

    os.chdir(options.dbdir) 
    keplcname = ['kepq3rplc_12.sqlite', 'kepq3rplc_34.sqlite', 'kepq3rplc_56.sqlite', 'kepq3rplc_78.sqlite', 'kepq3rplc_9.sqlite']
    nrstars = 0
    ebgenerator = ebdictreader.fetchall('select KIC, period from stars where period < 30 order by uid;')
    for star in ebgenerator:
#         if nrstars == 10:
#             break
        starkic = star['KIC']
        period  = star['period']
        
        q3uid = q3dictreader.fetchall('select uid from stars where KIC = ' + str(starkic) + ';')
        if q3uid == None or len(q3uid)==0:
            if options.debug != 0:
                print 'DEBUG: skipping', starkic
            continue
        for u in q3uid:
            staruid = u['uid']
            
        for k in range(0,len(keplcname)):
            keplcreader = dbr.DbReader(options.dbdir + keplcname[k])
            keplc = keplcreader.fetchall('select * from stars where staruid = ' + str(staruid) + ' and SLC_FLAG = 0;')
            if keplc == None or len(keplc)==0:
                if options.debug != 0:
                    print 'DEBUG: skipping ', starkic
                continue
        
            inslista1 = []
            a1p1 = None
            a1a1 = None
            a1s1 = None
            a1n1 = None
            a1p2 = None
            a1a2 = None
            a1s2 = None
            a1n2 = None
            a1p3 = None
            a1a3 = None
            a1s3 = None
            a1n3 = None
            toinsa1 = (staruid, starkic, period, 
                     a1p1, a1a1, a1s1, a1n1, a1p2, a1a2, a1s2, a1n2, a1p3, a1a3, a1s3, a1n3)
            inslista1.append(toinsa1)
            if len(inslista1) > 0:
                dictwritera1.insert(inslista1, True)
                
            inslista2 = []
            a2p1 = None
            a2a1 = None
            a2s1 = None
            a2n1 = None
            a2p2 = None
            a2a2 = None
            a2s2 = None
            a2n2 = None
            a2p3 = None
            a2a3 = None
            a2s3 = None
            a2n3 = None 
            toinsa2 = (staruid, starkic, period, 
                     a2p1, a2a1, a2s1, a2n1, a2p2, a2a2, a2s2, a2n2, a2p3, a2a3, a2s3, a2n3)
            inslista2.append(toinsa2)
            if len(inslista2) > 0:
                dictwritera2.insert(inslista2, True)     
                  
            inslistb1 = []      
            b1p1 = None
            b1t1 = None
            b1sn1 = None
            b1sr1 = None
            b1sd1 = None
            b1p2 = None
            b1t2 = None
            b1sn2 = None
            b1sr2 = None
            b1sd2 = None
            b1p3 = None
            b1t3 = None
            b1sn3 = None
            b1sr3 = None
            b1sd3 = None
            toinsb1 = (staruid, starkic, period, 
                     b1p1, b1t1, b1sn1, b1sr1, b1sd1, b1p2, b1t2, b1sn2, b1sr2, b1sd2, b1p3, b1t3, b1sn3, b1sr3, b1sd3)
            inslistb1.append(toinsb1)
            if len(inslistb1) > 0:
                dictwriterb1.insert(inslistb1, True)
                
            inslistb2 = []
            b2p1 = None
            b2t1 = None
            b2sn1 = None
            b2sr1 = None
            b2sd1 = None
            b2p2 = None
            b2t2 = None
            b2sn2 = None
            b2sr2 = None
            b2sd2 = None       
            b2p3 = None
            b2t3 = None
            b2sn3 = None
            b2sr3 = None
            b2sd3 = None   
            toinsb2 = (staruid, starkic, period, 
                     b2p1, b2t1, b2sn1, b2sr1, b2sd1, b2p2, b2t2, b2sn2, b2sr2, b2sd2, b2p3, b2t3, b2sn3, b2sr3, b2sd3)
            inslistb2.append(toinsb2)
            if len(inslistb2) > 0:
                dictwriterb2.insert(inslistb2, True)
            
            inslistf1 = []     
            f1p1 = None
            f1c1 = None
            toinsf1 = (staruid, starkic, period, f1p1, f1c1)
            inslistf1.append(toinsf1)
            if len(inslistf1) > 0:
                dictwriterf1.insert(inslistf1, True)
            
            inslistf2 = []     
            f2p1 = None
            f2c1 = None
            toinsf2 = (staruid, starkic, period, f2p1, f2c1)
            inslistf2.append(toinsf2)
            if len(inslistf2) > 0:
                dictwriterf2.insert(inslistf2, True)
                
            nrstars += 1
            log.write()
            log.write('processing KIC: ' + str(starkic)) 
            uids   = [x[0] for x in keplc]
            bjd    = [x[2] for x in keplc]
            dflux  = [x[10] for x in keplc]
            dsig   = [x[11] for x in keplc]
            
            if options.debug != 0:
                print 'DEBUG: # of rows in long-cadence lc =', len(uids)
                print 'DEBUG: input data (1st row) from lc db', 'UID =', uids[0], 'BJD =', bjd[0], 'FLUX =', dflux[0], 'ERR =', dsig[0]
    
     # AoV1 Period Search (nharm = 3, nbin = 200 0.1d <= period <= 30d)  
    #         os.chdir(options.vtdir)
            watch.start()
            fd, fout = tempfile.mkstemp()
            for i in range(0,len(uids)):
                if bjd[i] == None or dflux[i] == None or dsig[i] == None: 
                    continue # this happens if values are missing
                os.write(fd, "%f %f %f\n" % (bjd[i], dflux[i], dsig[i]))
            os.close(fd)
       
            if options.debug != 0:
                print 'DEBUG: AoV1 long-cadence lc input file written'
            
            sd, sout = tempfile.mkstemp()
            os.close(sd)
            
            os.system( "vartools -i %s -oneline -ascii -aov Nbin 200 0.1 30 0.1 0.01 3 0 > %s" % (fout,sout))        
            
            aov1file = open(sout, 'r')
            lines = aov1file.readlines()
            
            if options.debug != 0:
                print 'DEBUG: sout =', lines
            
            for line in lines:
                if line.startswith("Period_1_0 "):
                    per1split = line.split('Period_1_0         =')
                if line.startswith("AOV_1_0 "):
                    aov1split = line.split('AOV_1_0            =')
                if line.startswith("AOV_SNR_1_0 "):
                    snr1split = line.split('AOV_SNR_1_0        =')
                if line.startswith("AOV_NEG_LN_FAP_1_0 "):
                    neg1split = line.split('AOV_NEG_LN_FAP_1_0 =')
                if line.startswith("Period_2_0 "):
                    per2split = line.split('Period_2_0         =')
                if line.startswith("AOV_2_0 "):
                    aov2split = line.split('AOV_2_0            =')
                if line.startswith("AOV_SNR_2_0 "):
                    snr2split = line.split('AOV_SNR_2_0        =')
                if line.startswith("AOV_NEG_LN_FAP_2_0 "):
                    neg2split = line.split('AOV_NEG_LN_FAP_2_0 =')     
                if line.startswith("Period_3_0 "):
                    per3split = line.split('Period_3_0         =')
                if line.startswith("AOV_3_0 "):
                    aov3split = line.split('AOV_3_0            =')
                if line.startswith("AOV_SNR_3_0 "):
                    snr3split = line.split('AOV_SNR_3_0        =')
                if line.startswith("AOV_NEG_LN_FAP_3_0 "):
                    neg3split = line.split('AOV_NEG_LN_FAP_3_0 =')         
                    if options.debug != 0:  
                        print 'DEBUG: per1split[1] =', per1split[1]
                        print 'DEBUG: snr1split[1] =', snr1split[1]
                        print 'DEBUG: aov1split[1] =', aov1split[1]
                        print 'DEBUG: neg1split[1] =', neg1split[1]
                        print 'DEBUG: per2split[1] =', per2split[1]
                        print 'DEBUG: snr2split[1] =', snr2split[1]
                        print 'DEBUG: aov2split[1] =', aov2split[1]
                        print 'DEBUG: neg2split[1] =', neg2split[1]
                        print 'DEBUG: per3split[1] =', per3split[1]
                        print 'DEBUG: snr3split[1] =', snr3split[1]
                        print 'DEBUG: aov3split[1] =', aov3split[1]
                        print 'DEBUG: neg3split[1] =', neg3split[1]
                    
                    period1 = round(float(per1split[1]),6)
                    snr1    = round(float(snr1split[1]),6)
                    aov1    = round(float(aov1split[1]),6)
                    neg1    = round(float(neg1split[1]),6)
                    period2 = round(float(per2split[1]),6)
                    snr2    = round(float(snr2split[1]),6)
                    aov2    = round(float(aov2split[1]),6)
                    neg2    = round(float(neg2split[1]),6)
                    period3 = round(float(per3split[1]),6)
                    snr3    = round(float(snr3split[1]),6)
                    aov3    = round(float(aov3split[1]),6)
                    neg3    = round(float(neg3split[1]),6)                
                else: continue
            aov1file.close()
            os.chdir(options.dbdir)
            
            if options.debug != 0:
                print 'DEBUG: AoV1_PER1 =', period1, 'AoV1_AOV1 =', aov1, 'AoV1_SNR1 =', snr1, 'AoV1_NEG1 =', neg1 
                print 'DEBUG: AoV1_PER2 =', period2, 'AoV1_AOV2 =', aov2, 'AoV1_SNR2 =', snr2, 'AoV1_NEG2 =', neg2
                print 'DEBUG: AoV1_PER3 =', period3, 'AoV1_AOV3 =', aov3, 'AoV1_SNR3 =', snr3, 'AoV1_NEG3 =', neg3  
                
            updates = []         
            updates.append([period1, aov1, snr1, neg1, period2, aov2, snr2, neg2, period3, aov3, snr3, neg3, staruid])
            dictwritera1.update('update aov1 set AoV1_PER1 = ?, AoV1_AOV1 = ?, AoV1_SNR1 = ?, AoV1_NEG1 = ?, ' +
             'AoV1_PER2 = ?, AoV1_AOV2 = ?, AoV1_SNR2 = ?, AoV1_NEG2 = ?, ' + 
             'AoV1_PER3 = ?, AoV1_AOV3 = ?, AoV1_SNR3 = ?, AoV1_NEG3 = ? ' + 
             'where staruid = ?;', updates, True)
            os.chdir(options.rootdir)
            stop = watch.stop()  
            log.write('\t' + 'KIC ' + str(starkic) + ': AoV1 periods found and updated in ' + str(stop) +  's')    
            
     # AoV2 Period Search (nharm = 3, nbin = 50 0.1d <= period <= 30d)   
     #         os.chdir(options.vtdir)
            watch.start()
            fd, fout = tempfile.mkstemp()
            for i in range(0,len(uids)):
                if bjd[i] == None or dflux[i] == None or dsig[i] == None: 
                    continue # this happens if values are missing
                os.write(fd, "%f %f %f\n" % (bjd[i], dflux[i], dsig[i]))
            os.close(fd)
       
            if options.debug != 0:
                print 'DEBUG: AoV2 long-cadence lc input file written'
            
            sd, sout = tempfile.mkstemp()
            os.close(sd)   
            os.system( "vartools -i %s -oneline -ascii -aov Nbin 50 0.1 30 0.1 0.01 3 0 > %s" % (fout,sout))        
            
            aov2file = open(sout, 'r')
            lines = aov2file.readlines()
            
            if options.debug != 0:
                print 'DEBUG: sout =', lines
            
            for line in lines:
                if line.startswith("Period_1_0 "):
                    per1split = line.split('Period_1_0         =')
                if line.startswith("AOV_1_0 "):
                    aov1split = line.split('AOV_1_0            =')
                if line.startswith("AOV_SNR_1_0 "):
                    snr1split = line.split('AOV_SNR_1_0        =')
                if line.startswith("AOV_NEG_LN_FAP_1_0 "):
                    neg1split = line.split('AOV_NEG_LN_FAP_1_0 =')
                if line.startswith("Period_2_0 "):
                    per2split = line.split('Period_2_0         =')
                if line.startswith("AOV_2_0 "):
                    aov2split = line.split('AOV_2_0            =')
                if line.startswith("AOV_SNR_2_0 "):
                    snr2split = line.split('AOV_SNR_2_0        =')
                if line.startswith("AOV_NEG_LN_FAP_2_0 "):
                    neg2split = line.split('AOV_NEG_LN_FAP_2_0 =')     
                if line.startswith("Period_3_0 "):
                    per3split = line.split('Period_3_0         =')
                if line.startswith("AOV_3_0 "):
                    aov3split = line.split('AOV_3_0            =')
                if line.startswith("AOV_SNR_3_0 "):
                    snr3split = line.split('AOV_SNR_3_0        =')
                if line.startswith("AOV_NEG_LN_FAP_3_0 "):
                    neg3split = line.split('AOV_NEG_LN_FAP_3_0 =')         
                    if options.debug != 0:  
                        print 'DEBUG: per1split[1] =', per1split[1]
                        print 'DEBUG: snr1split[1] =', snr1split[1]
                        print 'DEBUG: aov1split[1] =', aov1split[1]
                        print 'DEBUG: neg1split[1] =', neg1split[1]
                        print 'DEBUG: per2split[1] =', per2split[1]
                        print 'DEBUG: snr2split[1] =', snr2split[1]
                        print 'DEBUG: aov2split[1] =', aov2split[1]
                        print 'DEBUG: neg2split[1] =', neg2split[1]
                        print 'DEBUG: per3split[1] =', per3split[1]
                        print 'DEBUG: snr3split[1] =', snr3split[1]
                        print 'DEBUG: aov3split[1] =', aov3split[1]
                        print 'DEBUG: neg3split[1] =', neg3split[1]
                    
                    period1 = round(float(per1split[1]),6)
                    snr1    = round(float(snr1split[1]),6)
                    aov1    = round(float(aov1split[1]),6)
                    neg1    = round(float(neg1split[1]),6)
                    period2 = round(float(per2split[1]),6)
                    snr2    = round(float(snr2split[1]),6)
                    aov2    = round(float(aov2split[1]),6)
                    neg2    = round(float(neg2split[1]),6)
                    period3 = round(float(per3split[1]),6)
                    snr3    = round(float(snr3split[1]),6)
                    aov3    = round(float(aov3split[1]),6)
                    neg3    = round(float(neg3split[1]),6)                
                else: continue
            aov2file.close()
            os.chdir(options.dbdir)
            
            if options.debug != 0:
                print 'DEBUG: AoV2_PER1 =', period1, 'AoV2_AOV1 =', aov1, 'AoV2_SNR1 =', snr1, 'AoV2_NEG1 =', neg1 
                print 'DEBUG: AoV2_PER2 =', period2, 'AoV2_AOV2 =', aov2, 'AoV2_SNR2 =', snr2, 'AoV2_NEG2 =', neg2
                print 'DEBUG: AoV2_PER3 =', period3, 'AoV2_AOV3 =', aov3, 'AoV2_SNR3 =', snr3, 'AoV2_NEG3 =', neg3  
                
            updates = []         
            updates.append([period1, aov1, snr1, neg1, period2, aov2, snr2, neg2, period3, aov3, snr3, neg3, staruid])
            dictwritera2.update('update aov2 set AoV2_PER1 = ?, AoV2_AOV1 = ?, AoV2_SNR1 = ?, AoV2_NEG1 = ?, ' +
             'AoV2_PER2 = ?, AoV2_AOV2 = ?, AoV2_SNR2 = ?, AoV2_NEG2 = ?, ' + 
             'AoV2_PER3 = ?, AoV2_AOV3 = ?, AoV2_SNR3 = ?, AoV2_NEG3 = ? ' + 
             'where staruid = ?;', updates, True)
            os.chdir(options.rootdir) 
            stop = watch.stop()   
            log.write('\t' + 'KIC ' + str(starkic) + ': AoV2 periods found and updated in ' + str(stop) +  's')   
    
    # BLS1 Period Search (nharm = 3, nbin = 200 0.1d <= period <= 30d)  
    #         os.chdir(options.vtdir)
            watch.start()
            fd, fout = tempfile.mkstemp()
            for i in range(0,len(uids)):
                if bjd[i] == None or dflux[i] == None or dsig[i] == None: 
                    continue # this happens if values are missing
                os.write(fd, "%f %f %f\n" % (bjd[i], dflux[i], dsig[i]))
            os.close(fd)
       
            if options.debug != 0:
                print 'DEBUG: BLS_1 long-cadence lc input file written'
            
            sd, sout = tempfile.mkstemp()
            os.close(sd)
            
            os.system( "vartools -i %s -oneline -ascii -BLS q 0.01 0.1 0.1 30.0 100000 200 0 3 0 0 0 > %s" % (fout, sout))   
            
            bls1file = open(sout, 'r')
            lines = bls1file.readlines()
            
            if options.debug != 0:
                print 'DEBUG: sout =', lines
            
            for line in lines:
                if line.startswith("BLS_Period_1_0 "):
                    per1split = line.split('BLS_Period_1_0               = ')
                if line.startswith("BLS_Tc_1_0 "):
                    tc1split = line.split('BLS_Tc_1_0                   =')
                if line.startswith("BLS_SN_1_0  "):
                    sn1split = line.split('BLS_SN_1_0                   =')
                if line.startswith("BLS_SR_1_0 "):
                    sr1split = line.split('BLS_SR_1_0                   =')
                if line.startswith("BLS_SDE_1_0 "):
                    sde1split = line.split('BLS_SDE_1_0                  =')     
                if line.startswith("BLS_Period_2_0 "):
                    per2split = line.split('BLS_Period_2_0               = ')
                if line.startswith("BLS_Tc_2_0 "):
                    tc2split = line.split('BLS_Tc_2_0                   =')
                if line.startswith("BLS_SN_2_0  "):
                    sn2split = line.split('BLS_SN_2_0                   =')
                if line.startswith("BLS_SR_2_0 "):
                    sr2split = line.split('BLS_SR_2_0                   =')
                if line.startswith("BLS_SDE_2_0 "):
                    sde2split = line.split('BLS_SDE_2_0                  =')            
                if line.startswith("BLS_Period_3_0 "):
                    per3split = line.split('BLS_Period_3_0               = ')
                if line.startswith("BLS_Tc_3_0 "):
                    tc3split = line.split('BLS_Tc_3_0                   =')
                if line.startswith("BLS_SN_3_0  "):
                    sn3split = line.split('BLS_SN_3_0                   =')
                if line.startswith("BLS_SR_3_0 "):
                    sr3split = line.split('BLS_SR_3_0                   =')
                if line.startswith("BLS_SDE_3_0 "):
                    sde3split = line.split('BLS_SDE_3_0                  =')  
                    
                    if options.debug != 0:  
                        print 'DEBUG: per1split[1] =', per1split[1]
                        print 'DEBUG: tc1plit[1] =', tc1split[1]
                        print 'DEBUG: sn1split[1] =', sn1split[1]
                        print 'DEBUG: sr1split[1] =', sr1split[1]
                        print 'DEBUG: sde1split[1] =', sde1split[1]
                        print 'DEBUG: per2split[1] =', per2split[1]
                        print 'DEBUG: tc2plit[1] =', tc2split[1]
                        print 'DEBUG: sn2split[1] =', sn2split[1]
                        print 'DEBUG: sr2split[1] =', sr2split[1]
                        print 'DEBUG: sde2split[1] =', sde2split[1]
                        print 'DEBUG: per3split[1] =', per3split[1]
                        print 'DEBUG: tc3plit[1] =', tc3split[1]
                        print 'DEBUG: sn3split[1] =', sn3split[1]
                        print 'DEBUG: sr3split[1] =', sr3split[1]
                        print 'DEBUG: sde3split[1] =', sde3split[1]
                                     
                    period1 = round(float(per1split[1]),6)
                    tc1    = round(float(tc1split[1]),6)
                    sn1    = round(float(sn1split[1]),6)
                    sr1    = round(float(sr1split[1]),6)
                    sde1    = round(float(sde1split[1]),6)
                    period2 = round(float(per2split[1]),6)
                    tc2    = round(float(tc2split[1]),6)
                    sn2    = round(float(sn2split[1]),6)
                    sr2    = round(float(sr2split[1]),6)
                    sde2    = round(float(sde2split[1]),6)
                    period3 = round(float(per3split[1]),6)
                    tc3    = round(float(tc3split[1]),6)
                    sn3    = round(float(sn3split[1]),6)
                    sr3    = round(float(sr3split[1]),6)
                    sde3    = round(float(sde3split[1]),6)
                else: continue
            bls1file.close()
            os.chdir(options.dbdir)
            
            if options.debug != 0:
                print 'DEBUG: BLS1_PER1 =', period1, 'BLS1_TC1 =', tc1, 'BLS1_SN1 =', sn1, 'BLS1_SR1 =', sr1, 'BLS1_SDE1 =', sde1
                print 'DEBUG: BLS1_PER2 =', period2, 'BLS1_TC2 =', tc2, 'BLS1_SN2 =', sn2, 'BLS1_SR2 =', sr2, 'BLS1_SDE2 =', sde2
                print 'DEBUG: BLS1_PER3 =', period3, 'BLS1_TC3 =', tc3, 'BLS1_SN3 =', sn3, 'BLS1_SR3 =', sr3, 'BLS1_SDE3 =', sde3
                
            updates = []         
            updates.append([period1, tc1, sn1, sr1, sde1, period2, tc2, sn2, sr2, sde2, period3, tc3, sn3, sr3, sde3, staruid])
            dictwriterb1.update('update bls1 set BLS1_PER1 = ?, BLS1_TC1 = ?, BLS1_SN1 = ?, BLS1_SR1 = ?, BLS1_SDE1 = ?, ' +
                              'BLS1_PER2 = ?, BLS1_TC2 = ?, BLS1_SN2 = ?, BLS1_SR2 = ?, BLS1_SDE2 = ?, ' + 
                              'BLS1_PER3 = ?, BLS1_TC3 = ?, BLS1_SN3 = ?, BLS1_SR3 = ?, BLS1_SDE3 = ? ' + 
                              'where staruid = ?;', updates, True)
            os.chdir(options.rootdir)                    
            stop = watch.stop()  
            log.write('\t' + 'KIC ' + str(starkic) + ': BLS1 periods found and updated in ' + str(stop) +  's') 
    
    
    # BLS2 Period Search (nharm = 3, nbin = 50 0.1d <= period <= 30d)  
    #         os.chdir(options.vtdir)
            watch.start()
            fd, fout = tempfile.mkstemp()
            for i in range(0,len(uids)):
                if bjd[i] == None or dflux[i] == None or dsig[i] == None: 
                    continue # this happens if values are missing
                os.write(fd, "%f %f %f\n" % (bjd[i], dflux[i], dsig[i]))
            os.close(fd)
       
            if options.debug != 0:
                print 'DEBUG: BLS_2 long-cadence lc input file written'
            
            sd, sout = tempfile.mkstemp()
            os.close(sd)
            
            os.system( "vartools -i %s -oneline -ascii -BLS q 0.01 0.1 0.1 30.0 100000 50 0 3 0 0 0 > %s" % (fout, sout))   
            
            bls2file = open(sout, 'r')
            lines = bls2file.readlines()
            
            if options.debug != 0:
                print 'DEBUG: sout =', lines
            
            for line in lines:
                if line.startswith("BLS_Period_1_0 "):
                    per1split = line.split('BLS_Period_1_0               = ')
                if line.startswith("BLS_Tc_1_0 "):
                    tc1split = line.split('BLS_Tc_1_0                   =')
                if line.startswith("BLS_SN_1_0  "):
                    sn1split = line.split('BLS_SN_1_0                   =')
                if line.startswith("BLS_SR_1_0 "):
                    sr1split = line.split('BLS_SR_1_0                   =')
                if line.startswith("BLS_SDE_1_0 "):
                    sde1split = line.split('BLS_SDE_1_0                  =')     
                if line.startswith("BLS_Period_2_0 "):
                    per2split = line.split('BLS_Period_2_0               = ')
                if line.startswith("BLS_Tc_2_0 "):
                    tc2split = line.split('BLS_Tc_2_0                   =')
                if line.startswith("BLS_SN_2_0  "):
                    sn2split = line.split('BLS_SN_2_0                   =')
                if line.startswith("BLS_SR_2_0 "):
                    sr2split = line.split('BLS_SR_2_0                   =')
                if line.startswith("BLS_SDE_2_0 "):
                    sde2split = line.split('BLS_SDE_2_0                  =')            
                if line.startswith("BLS_Period_3_0 "):
                    per3split = line.split('BLS_Period_3_0               = ')
                if line.startswith("BLS_Tc_3_0 "):
                    tc3split = line.split('BLS_Tc_3_0                   =')
                if line.startswith("BLS_SN_3_0  "):
                    sn3split = line.split('BLS_SN_3_0                   =')
                if line.startswith("BLS_SR_3_0 "):
                    sr3split = line.split('BLS_SR_3_0                   =')
                if line.startswith("BLS_SDE_3_0 "):
                    sde3split = line.split('BLS_SDE_3_0                  =')  
                    
                    if options.debug != 0:  
                        print 'DEBUG: per1split[1] =', per1split[1]
                        print 'DEBUG: tc1plit[1] =', tc1split[1]
                        print 'DEBUG: sn1split[1] =', sn1split[1]
                        print 'DEBUG: sr1split[1] =', sr1split[1]
                        print 'DEBUG: sde1split[1] =', sde1split[1]
                        print 'DEBUG: per2split[1] =', per2split[1]
                        print 'DEBUG: tc2plit[1] =', tc2split[1]
                        print 'DEBUG: sn2split[1] =', sn2split[1]
                        print 'DEBUG: sr2split[1] =', sr2split[1]
                        print 'DEBUG: sde2split[1] =', sde2split[1]
                        print 'DEBUG: per3split[1] =', per3split[1]
                        print 'DEBUG: tc3plit[1] =', tc3split[1]
                        print 'DEBUG: sn3split[1] =', sn3split[1]
                        print 'DEBUG: sr3split[1] =', sr3split[1]
                        print 'DEBUG: sde3split[1] =', sde3split[1]
                                     
                    period1 = round(float(per1split[1]),6)
                    tc1    = round(float(tc1split[1]),6)
                    sn1    = round(float(sn1split[1]),6)
                    sr1    = round(float(sr1split[1]),6)
                    sde1    = round(float(sde1split[1]),6)
                    period2 = round(float(per2split[1]),6)
                    tc2    = round(float(tc2split[1]),6)
                    sn2    = round(float(sn2split[1]),6)
                    sr2    = round(float(sr2split[1]),6)
                    sde2    = round(float(sde2split[1]),6)
                    period3 = round(float(per3split[1]),6)
                    tc3    = round(float(tc3split[1]),6)
                    sn3    = round(float(sn3split[1]),6)
                    sr3    = round(float(sr3split[1]),6)
                    sde3    = round(float(sde3split[1]),6)
                else: continue
            bls2file.close()
            os.chdir(options.dbdir)
            
            if options.debug != 0:
                print 'DEBUG: BLS2_PER1 =', period1, 'BLS2_TC1 =', tc1, 'BLS2_SN1 =', sn1, 'BLS2_SR1 =', sr1, 'BLS2_SDE1 =', sde1
                print 'DEBUG: BLS2_PER2 =', period2, 'BLS2_TC2 =', tc2, 'BLS2_SN2 =', sn2, 'BLS2_SR2 =', sr2, 'BLS2_SDE2 =', sde2
                print 'DEBUG: BLS2_PER3 =', period3, 'BLS2_TC3 =', tc3, 'BLS2_SN3 =', sn3, 'BLS2_SR3 =', sr3, 'BLS2_SDE3 =', sde3
                
            updates = []         
            updates.append([period1, tc1, sn1, sr1, sde1, period2, tc2, sn2, sr2, sde2, period3, tc3, sn3, sr3, sde3, staruid])
            dictwriterb2.update('update bls2 set BLS2_PER1 = ?, BLS2_TC1 = ?, BLS2_SN1 = ?, BLS2_SR1 = ?,BLS2_SDE1 = ?, ' +
                              'BLS2_PER2 = ?, BLS2_TC2 = ?, BLS2_SN2 = ?, BLS2_SR2 = ?, BLS2_SDE2 = ?, ' + 
                              'BLS2_PER3 = ?, BLS2_TC3 = ?, BLS2_SN3 = ?, BLS2_SR3 = ?, BLS2_SDE3 = ? ' + 
                              'where staruid = ?;', updates, True)
            os.chdir(options.rootdir)                    
            stop = watch.stop()  
            log.write('\t' + 'KIC ' + str(starkic) + ': BLS2 period found and updated in ' + str(stop) +  's') 
    
            
    # FC2_1 Period Search (nharm = 3 0.1d <= period <= 30d) 
            os.chdir(options.fc2dir)
            watch.start()
            fd, fout = tempfile.mkstemp()
            os.write(fd, "FastChi2 Data:\n")
            n = len(uids)
            sn = str(n)
            os.write(fd, sn + '\n')
            for i in range(0,len(uids)):
                if bjd[i] == None or dflux[i] == None or dsig[i] == None: 
                    continue # this happens if values are missing
                os.write(fd, "%f %f %f\n" % (bjd[i], dflux[i], dsig[i]))
            os.close(fd)
       
            if options.debug != 0:
                print 'DEBUG: FC21 long-cadence lc input file written'
            
            sd, sout = tempfile.mkstemp()
            os.close(sd)
            
            os.system( "./runchi2 3 30 -f 0.3 -i %s -o %s" % (fout, sout))        
            
            fc21file = open(sout, 'r')
            lines = fc21file.readlines()
                    
            if options.debug != 0:
                print 'DEBUG: sout =', lines
                
            for line in lines:
                if line.startswith("# "):
                    continue
                elif line.startswith("FastChi2 Data:"):
                    splitted = line.split("\t")
                     
                    if options.debug != 0:  
                        print 'DEBUG: splitted[1] =', splitted[1], 'splitted[3] =', splitted[3]
                     
                    period = round(float(splitted[1]),6)
                    chm = round(float(splitted[3]),6)
                else: continue
            fc21file.close()
            os.chdir(options.dbdir)
             
            if options.debug != 0:
                print 'DEBUG: FC21_PER1 =', period, 'FC21_CHM1 =', chm
                 
            updates = []         
            updates.append([period, chm, staruid])
            dictwriterf1.update('update fc21 set FC21_PER1 = ?, FC21_CHM1 = ? where staruid = ?;', updates, True)
            os.chdir(options.rootdir)                     
            stop = watch.stop()  
            log.write('\t' + 'KIC ' + str(starkic) + ': FC21 period found and updated in ' + str(stop) +  's')     
             
    # FC2_2 Period Search (nharm = 6 0.1d <= period <= 30d)   
            os.chdir(options.fc2dir)
            watch.start()
            fd, fout = tempfile.mkstemp()
            os.write(fd, "FastChi2 Data:\n")
            n = len(uids)
            sn = str(n)
            os.write(fd, sn + '\n')
            for i in range(0,len(uids)):
                if bjd[i] == None or dflux[i] == None or dsig[i] == None: 
                    continue # this happens if values are missing
                os.write(fd, "%f %f %f\n" % (bjd[i], dflux[i], dsig[i]))
            os.close(fd)
       
            if options.debug != 0:
                print 'DEBUG: FC2_2 long-cadence lc input file written'
            
            sd, sout = tempfile.mkstemp()
            os.close(sd)
            
            os.system( "./runchi2 6 30 -f 0.3 -i %s -o %s" % (fout, sout))        
            
            fc22file = open(sout, 'r')
            lines = fc22file.readlines()
                    
            if options.debug != 0:
                print 'DEBUG: sout =', lines
                
            for line in lines: 
                if line.startswith("# "):
                    continue
                elif line.startswith("FastChi2 Data:"):
                    splitted = line.split("\t")
                     
                    if options.debug != 0:  
                        print 'DEBUG: splitted[1] =', splitted[1], 'splitted[3] =', splitted[3]
                     
                    period = round(float(splitted[1]),6)
                    chm = round(float(splitted[3]),6)
    
                else: continue
            fc22file.close()
            os.chdir(options.dbdir)
             
            if options.debug != 0:
                print 'DEBUG: FC22_PER1 =', period, 'FC22_CHM1 =', chm
                 
            updates = []         
            updates.append([period, chm, staruid])
            dictwriterf2.update('update fc22 set FC22_PER1 = ?, FC22_CHM1 = ? where staruid = ?;', updates, True)
            os.chdir(options.rootdir)             
            stop = watch.stop()   
            log.write('\t' + 'KIC ' + str(starkic) + ': FC21 period found and updated in ' + str(stop) +  's')          
            
            if nrstars == 100:
                dstop = datetime.datetime.today()
                final = dstop-dstart 
                log.write()
                log.write(str(dstop) + ' Found period and updated dictionary for ' + str(nrstars) + ' stars in ' + str(final))
        
    dictwriter.close()
    ebdictreader.close()  
    q3dictreader.close()
    keplcreader.close()
  
    dstop = datetime.datetime.today()
    final = dstop-dstart
    log.write()
    log.write(str(dstop) + ' Finished with period finding for ' + str(nrstars) + ' stars in ' + str(final))
    log.write('done')   

    
    
    
    
    
    
