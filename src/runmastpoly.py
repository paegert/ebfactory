'''
Created on Jul 2, 2012

@package  runpoly
@author   map
@version  \$Revision: 1.2 $
@date     \$Date: 2013/07/02 17:16:04 $

$Log: runmastpoly.py,v $
Revision 1.2  2013/07/02 17:16:04  paegerm
corrected "fail bug"

Revision 1.1  2013/07/02 14:58:49  paegerm
initial revision

Revision 1.7  2012/11/30 20:37:27  paegerm
pass options to fitlc, add clscol option
adding period to plots
adding logfile option

pass options to fitlc, add clscol option
adding period to plots
adding logfile option

Revision 1.6  2012/09/24 21:42:58  paegerm
adding dbconfig option, adding fontsize

Revision 1.5  2012/08/23 16:36:54  paegerm
make fitlc silent for debug = 0

Revision 1.4  2012/08/22 15:47:37  paegerm
Changing font size of plots for successful fits

Revision 1.3  2012/08/16 22:26:51  paegerm
adding get_polyopts, adding debug variable

Revision 1.2  2012/07/30 19:28:27  paegerm
correcting index-error in fitlc, creation of fitphases and fitvalues

Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision

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



def getfit(outstring, staruid):
#     coeffs = []
    fit    = [staruid]
    chi2   = 1.0e11
    ln     = 0
    
#     print 'outstring: ', outstring #DEBUG TEST
    
    outstring = outstring.split('\n')
    for line in outstring:
        if line.startswith("# Final chi2:    "):
            chi2 = float(line[17:-1])
            continue
#         elif line.startswith('# knot '):
#             splitted = line.split('\t')
#             coeffs.append(float(splitted[1]))
#             coeffs.append(float(splitted[2]))
#             coeffs.append(float(splitted[3]))
#             coeffs.append(float(splitted[4]))
        elif line.startswith('#'):
            continue
        elif len(line) == 0:
            continue
        else:
            splitted = line.split('\t')
#             print 'chi2 = ', chi2
#             print 'splitted[0] = ', splitted[0]
#             print 'splitted[1] = ', splitted[1]
            if splitted[0] == 999:
                splitted[0] = None
            fit.append(round(float(splitted[0]),6))
            if splitted[1] == 999:
                splitted[1] = None
            fit.append(round(float(splitted[1]),6))
            continue
        
#     print 'fit = ', fit
#             fit.append([staruid, round(float(splitted[0]), 6), round(float(splitted[1]), 6)])
#             ln += 1
#             i = (ln-1)*2
#             print 'i = ', i
#             val[i] = round(float(splitted[0]), 6)
#             print 'val = ', val
#             val[i+1] = round(float(splitted[1]), 6)

#     return (chi2, coeffs, fit)
    return (chi2, fit)



def fitlc(star, plc, blc, options):
    
    if options.debug > 0:
        print 'processing', star['KIC']
    fsize = options.fsize
    polyinname = star['KIC'] + '.tmp'
    polyfile = open(polyinname, 'w')
    for entry in blc:
        polyfile.write(str(entry['phase']) + ' ' + 
                       str(entry['normmag']) + ' ' + 
                       str(entry['errnormmag']) + '\n')
    polyfile.close()
    
    
    oldargs = ["mastpolyfit", "--find-knots", "find-step", "--midpoints", "--four-chain", polyinname]
#     print oldargs
    newargs = ["mastpolyfit", "--find-knots", "find-step", "--midpoints", "--two-chain", polyinname]
#     print newargs

    plcphases = [x[3] for x in plc]
    plcmags   = [x[8] for x in plc]
    blcphases = [x[2] for x in blc]
    blcmags   = [x[3] for x in blc]
    
    oldchi2   = 1.0e11
#     oldcoeffs = []
    oldfit    = []
    newchi2   = 1.0e11
#     newcoeffs = []
    newfit    = []
    usefit    = None
    

    p = subprocess.Popen(oldargs, stdout=subprocess.PIPE)
    (outstring, errstring) = p.communicate()
    resold = p.returncode
    if (resold == 0):
#         (oldchi2, oldcoeffs, oldfit) = getfit(outstring, star['uid'])
        (oldchi2, oldfit) = getfit(outstring, star['uid'])
    if (options.debug > 0):
        print 'resold = ', resold, ' old chi2 = ', oldchi2

    p = subprocess.Popen(newargs, stdout=subprocess.PIPE)
    (outstring, errstring) = p.communicate()
    resnew = p.returncode
    if (resnew == 0):
#         (newchi2, newcoeffs, newfit) = getfit(outstring, star['uid'])
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
#     
#     print 'usefit = ', usefit #DEBUG TEST

    os.remove(polyinname)            
    fit    = None
    chi2   = None
#     coeffs = None
    
#     varcls = star['varcls']
#     if varcls == None:
#         varcls = 'not classified'
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
#         return (False, chi2, coeffs, fit)
        return (False, chi2, fit)
    

    if (usefit == 'new'):
        chi2   = newchi2
#         coeffs = newcoeffs
        fit    = newfit
        
    elif (usefit == 'old'):
        chi2   = oldchi2
#         coeffs = oldcoeffs
        fit    = oldfit  
        
#     print usefit, ' = ', fit, len(fit) #DEBUG TEST
        
    fitphases = []
    fitvalues = []
    for i in range(len(fit)/2):
        j = i*2+1
        k = i*2+2
        fitphases.append(fit[j])
        fitvalues.append(fit[k])
        

    #fsize = 18
    
    plotname = 'mastfit_plots/' + star['KIC'] + '_polyfit.png'
#    fig = pl.figure()
#    ax  = fig.add_subplot(111)
#    for tick in ax.xaxis.get_major_ticks():
#        tick.label.fontsize = 20
    pl.plot(plcphases, plcmags, 'k.', 
            blcphases, blcmags, 'r.', 
            fitphases, fitvalues, 'b-')
    pl.xticks(fontsize = fsize)
    pl.yticks(fontsize = fsize)
    pl.xlim(-0.5, 0.5)
    tmp = 'Phase (Period = ' + str(star['Period']) + ' d)'
    pl.xlabel(tmp, fontsize=options.fsize)
    pl.ylabel('normalized mag', fontsize=options.fsize)
    pl.title(star['KIC'] + ' ' + 'polfit_Kep_EB', fontsize=options.fsize)
    pl.savefig(plotname)
    # pl.show()
    pl.clf()
    
#     return (True, chi2, coeffs, fit)
    return (True, chi2, fit)
    
    
    
def get_polyopts():
    usage = '%prog [options] [fitname]'
    parser = OptionParser(usage=usage)
    parser.add_option('--blc', dest='blcname', type='string', 
                      default='mastblc.sqlite',
                      help='database file with binned light curves')
    parser.add_option('--clscol', dest='clscol', type='string', 
                      default='varcls',
                      help='dictionary column for class (varcls)')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Mast',
                      help='name of database configuration (default = Mast')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='kepebdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--fit', dest='fitname', type='string', 
                      default='mastfit.sqlite',
                      help='database file with fitted light curves')
    parser.add_option('--fsize', dest='fsize', type='int', 
                      default=8,
                      help='font size for plots (default: 8')
    parser.add_option('--logfile', dest='logfile', type='string', 
                      default=None,
                      help='name of logfile (None)')
    parser.add_option('--plc', dest='plcname', type='string', 
                      default='keplerrplc.sqlite',
                      help='database file with phased light curves')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='/dev/shm/kepler/',
                      help='directory for database files (default = ./)')
    parser.add_option('--polydir', dest='polydir', type='string', 
                      default='/dev/shm/kepler/',
                      help='directory for polyfit files (default = ./)')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars order by uid;',
                      help='select statement for dictionary ' +
                           '(Default: select * from stars order by uid;)')
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')
    parser.add_option('--polyopt', dest='polyopt', type='string', 
                      default= ' --find-knots --find-step --midpoints ',
                      help='cmd line options for polyfit entered within ""; example: --polyopt "--step-size 0.005";  (default: None) ')
   
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'
        
    if (options.polydir[-1] != '/'):
        options.polydir += '/'

    if (len(args) == 1):
        options.fitname = args[0]
    
    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")
        
    
    options.lf = Logfile(options.logfile, True, True)

    return options



if __name__ == '__main__':

    options = get_polyopts()
    
    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()
    
    # enforce creation if database or table does not exist
#     tmpwriter = dbw.DbWriter(options.rootdir + options.fitname, 
#                              dbc.cffcols, dbc.cfftname, 
#                              dbc.cfftypes, dbc.cffnulls)
#     tmpwriter.close()
#     tmpwriter = dbw.DbWriter(options.rootdir + options.fitname, 
#                              dbc.fitcols, dbc.fittname, 
#                              dbc.fittypes, dbc.fitnulls)
#     tmpwriter.close()
    tmpwriter = dbw.DbWriter(options.rootdir + options.fitname, 
                             dbc.kmncols, dbc.kmntname, 
                             dbc.kmntypes, dbc.kmnnulls)
    tmpwriter.close()

    watch = Stopwatch()
    watch.start()
    
    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    plcreader  = dbr.DbReader(options.rootdir + options.plcname)
    blcreader  = dbr.DbReader(options.rootdir + options.blcname)
    
    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, 
                              dbc.dictcols)
#     cffwriter  = dbw.DbWriter(options.rootdir + options.fitname, 
#                               dbc.cffcols, dbc.cfftname)
#     fitwriter  = dbw.DbWriter(options.rootdir + options.fitname, 
#                               dbc.fitcols, dbc.fittname)
    fitwriter  = dbw.DbWriter(options.rootdir + options.fitname, 
                              dbc.kmncols, dbc.kmntname, dbc.kmntypes, dbc.kmnnulls, dbc.npkmntype)
    
    generator = dictreader.traverse(options.select, None, 100)
    nrstars   = 0
    failed    = 0
    olddir    = options.rootdir
    for star in generator:
        nrstars += 1
        plc = plcreader.getlc(star['uid'], 'stars', 'phase')
        blc = blcreader.getlc(star['uid'], 'stars', 'phase')
#         cffwriter.deletebystaruid(star['staruid'])
#         fitwriter.deletebystaruid(star['staruid'])
#         if (options.rootdir + star['sdir'] != olddir):
#             olddir = options.rootdir + star['sdir']
#             os.chdir(olddir)
        if not os.path.exists('mastfit_plots'):
            os.mkdir('mastfit_plots')
        if not os.path.exists('failed'):
            os.mkdir('failed')
#         (ok, chi2, coeffs, fit) = fitlc(star, plc, blc, options)
        (ok, chi2, fit) = fitlc(star, plc, blc, options)
#                                        options.debug, options.fsize)
        dictwriter.update('update stars set chi2 = ? where uid = ?;', 
                          [(chi2, star['uid'])])
        if ok == False:
            failed += 1
            continue
#         print len(fit)
        if (len(fit) == 17):
            fitwriter.insert((fit,), True)
#           coeffs.append(0.0)
#           coeffs.insert(0, star['uid'])
#         
                
#         cffwriter.insert((coeffs,), True)
        
    dictreader.close()
    plcreader.close()
    blcreader.close()
    
    dictwriter.commit()
    
    dictwriter.close()
#     cffwriter.close()
    fitwriter.close()
        

    print nrstars, ' processed, ', failed, ' lightcurves failed'
    print watch.stop(), ' seconds'
    print ''
    print 'Done'
    