'''
Created on Jul 10, 2013

@author  parvizm

'''


from optparse import OptionParser
import os
import subprocess
import matplotlib.pyplot as pl

import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr

import dbconfig
from functions import *
from stopwatch import *
from logfile import *

    
    
def get_polyopts():
    usage = '%prog [options] [fitname]'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Mast',
                      help='name of database configuration (default = Mast')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='kepebdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--plc', dest='plcname', type='string', 
                      default='keplerrplc.sqlite',
                      help='database file with phased light curves')
    parser.add_option('--blc', dest='blcname', type='string', 
                      default='mastblc.sqlite',
                      help='database file with binned light curves')
    parser.add_option('--mps', dest='mpsname', type='string', 
                      default='mastfit.sqlite',
                      help='database file with fitted light curves')
    parser.add_option('--fsize', dest='fsize', type='int', 
                      default=18,
                      help='font size for plots (default: 18')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='/Users/mahmoudparvizi/ebf/src',
                      help='directory for database files (default = ./)')
    parser.add_option('--dbdir', dest='dbdir', type='string', 
                      default='/Users/mahmoudparvizi/kepler/',
                      help='directory for polyfit files (default = ./)')
    parser.add_option('--polydir', dest='polydir', type='string', 
                      default='/Users/mahmoudparvizi/polyfit/',
                      help='directory for polyfit files (default = ./)')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars order by uid;',
                      help='select statement for dictionary ' +
                           '(Default: select * from stars order by uid;)')
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')
    parser.add_option('--polyopt', dest='polyopt', type='string', 
                      default= ' --find-knots --find-step ',
                      help='cmd line options for polyfit entered within ""; example: --polyopt "--step-size 0.005";  (default: None) ')
   
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'
        
    if (options.polydir[-1] != '/'):
        options.polydir += '/'
    
    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")
        

    return options

def getfit(outstring, staruid):

    fit    = [staruid]
    chi2   = 1.0e11
    ln     = 0
    outstring = outstring.split('\n')
    for line in outstring:
        if line.startswith("# Final chi2:    "):
            chi2 = float(line[17:-1])
            continue
        elif line.startswith('#'):
            continue
        elif len(line) == 0:
            continue
        else:
            splitted = line.split('\t')
#             print 'chi2 = ', chi2
#             print 'splitted[0] = ', type(splitted[0]), splitted[0]
#             print 'splitted[1] = ', type(splitted[1]), splitted[1]
            if splitted[0] == 999:
                splitted[0] = None
            fit.append(round(float(splitted[0]),6))
            if splitted[1] == 999:
                splitted[1] = None
            fit.append(round(float(splitted[1]),6))
            continue
        
    return (chi2, fit)



def fitlc(star, plc, blc, mps, options):
    
    if options.debug > 0:
        print 'processing', star['KIC']
    fsize = options.fsize
    polyinname = star['KIC'] + '.tmp'
    os.chdir(options.polydir)
    polyfile = open(polyinname, 'w')
    for entry in blc:
        polyfile.write(str(entry['phase']) + ' ' + 
                       str(entry['normmag']) + ' ' + 
                       str(entry['errnormmag']) + '\n')
    polyfile.close()
    
    
    oldargs = ["mastpolyfit", "--find-knots", "find-step", "--four-chain", polyinname]
#     print oldargs
    newargs = ["mastpolyfit", "--find-knots", "find-step", "--two-chain", polyinname]
#     print newargs

    plcphases = [x[3] for x in plc]
    plcmags   = [x[8] for x in plc]
    blcphases = [x[2] for x in blc]
    blcmags   = [x[3] for x in blc]
    mpsphases = [[x[2], x[4], x[6], x[8], x[10], x[12], x[14], x[16]] for x in mps]
    mpsmags   = [[x[3], x[5], x[7], x[9], x[11], x[13], x[15], x[17]] for x in mps]
    
    oldchi2   = 1.0e11
    oldfit    = []
    newchi2   = 1.0e11
    newfit    = []
    usefit    = None

    p = subprocess.Popen(oldargs, stdout=subprocess.PIPE)
    (outstring, errstring) = p.communicate()
    resold = p.returncode
    if (resold == 0):
        (oldchi2, oldfit) = getfit(outstring, star['uid'])
    if (options.debug > 0):
        print 'resold = ', resold, ' old chi2 = ', oldchi2

    p = subprocess.Popen(newargs, stdout=subprocess.PIPE)
    (outstring, errstring) = p.communicate()
    resnew = p.returncode
    if (resnew == 0):
        (newchi2, newfit) = getfit(outstring, star['uid'])
    if (options.debug > 0):
        print 'resnew = ', resnew, ' new chi2 = ', newchi2

    if (resold == 0):
        if (resnew == 0):
            if (oldchi2 > 1.0e6) and (newchi2 > 1.0e6):
                usefit = None
            elif (newchi2 < oldchi2):
                usefit = 'new'
            else:
                usefit = 'old'
        else:
            if (oldchi2 > 1.0e6):
                usefit = None
            else:
                usefit = 'old'
    else:
        if (resnew == 0) and (newchi2 < 1.0e6):
            usefit = 'new'
        else:
            usefit = None

    os.remove(polyinname) 
    os.chdir(options.rootdir)
               
    fit    = None
    chi2   = None

    if (usefit == None):
        plotname = 'failed/' + star['KIC'] + '.png'
        pl.plot(plcphases, plcmags, 'k.',
                blcphases, blcmags, 'r.')
        pl.xlim(-0.5, 0.5)
        tmp = 'Phase (Period = ' + str(star['Period']) + ' d)'
        pl.xlabel(tmp, fontsize=options.fsize)
        pl.ylabel('Flux')
        pl.title(star['KIC'] + '  EB')
        pl.savefig(plotname)
        pl.clf()

        return (False, chi2, fit)
    

    if (usefit == 'new'):
        chi2   = newchi2
        fit    = newfit
        
    elif (usefit == 'old'):
        chi2   = oldchi2
        fit    = oldfit  
        
    fitphases = []
    fitvalues = []
    for i in range(len(fit)/2):
        j = i*2+1
        k = i*2+2
        fitphases.append(fit[j])
        fitvalues.append(fit[k])
    
    plotname = options.rootdir + 'mastfit_plots/' + star['KIC'] + '_mastpolyfit.png'
    pl.plot(plcphases, plcmags, 'k.', 
            blcphases, blcmags, 'r.', 
            fitphases, fitvalues, 'g.',
            mpsphases, mpsmags, 'b.')
    pl.xticks(fontsize = options.fsize)
    pl.yticks(fontsize = options.fsize)
    pl.xlim(-0.5, 0.5)
    tmp = 'Phase (Period = ' + str(star['Period']) + ' d)'
    pl.xlabel(tmp, fontsize=options.fsize)
    pl.legend(('raw_flux', 'bin_flux', 'fit_flux', 'mps_flux'), loc=0)
    pl.ylabel('normalized mag', fontsize=options.fsize)
    pl.title(star['KIC'] + ' Kep-EB', fontsize=options.fsize)
    pl.savefig(plotname)
    # pl.show()
    pl.clf()

    return (True, chi2, fit)
    




if __name__ == '__main__':

    options = get_polyopts()
    
    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()

    watch = Stopwatch()
    watch.start()
    
    os.chdir(options.dbdir)
    
    dictreader = dbr.DbReader(options.dbdir + options.dictname)
    plcreader  = dbr.DbReader(options.dbdir + options.plcname)
    blcreader  = dbr.DbReader(options.dbdir + options.blcname)
    mpsreader  = dbr.DbReader(options.dbdir + options.mpsname)
    
    generator = dictreader.traverse(options.select, None, 100)
    nrstars   = 0
    failed    = 0
    
    os.chdir(options.rootdir)

    for star in generator:
        nrstars += 1
        plc = plcreader.getlc(star['uid'], 'stars', 'phase')
        blc = blcreader.getlc(star['uid'], 'stars', 'phase')
        mps = mpsreader.getlc(star['uid'], 'midpoints')

        os.chdir(options.rootdir)
        if not os.path.exists('mastfit_plots'):
            os.mkdir('mastfit_plots')
        if not os.path.exists('failed'):
            os.mkdir('failed')
        (ok, chi2, fit) = fitlc(star, plc, blc, mps, options)
        if ok == False:
            failed += 1
            continue
        
    os.chdir(options.dbdir)   
    dictreader.close()
    plcreader.close()
    blcreader.close()
    mpsreader.close()
    os.chdir(options.rootdir)

        

    print nrstars, ' processed, ', failed, ' lightcurves failed'
    print watch.stop(), ' seconds'
    print ''
    print 'Done'
    