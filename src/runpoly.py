'''
Created on Jul 2, 2012

@package  runpoly
@author   map
@version  \$Revision: 1.8 $
@date     \$Date: 2013/07/26 20:07:27 $

$Log: runpoly.py,v $
Revision 1.8  2013/07/26 20:07:27  paegerm
adding midpoints and fullfit options, switching to mastpolyfit

adding midpoints and fullfit options, switching to mastpolyfit

Revision 1.7  2012/11/30 20:37:27  paegerm
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
    coeffs = []
    coeffs.append(staruid)
    fit    = []
    chi2   = 1.0e11
    outstring = outstring.split('\n')
    for line in outstring:
        if line.startswith("# Final chi2:    "):
            chi2 = float(line[17:-1])
        elif line.startswith('# knot '):
            splitted = line.split('\t')
            coeffs.append(float(splitted[1]))
            coeffs.append(float(splitted[2]))
            coeffs.append(float(splitted[3]))
            coeffs.append(float(splitted[4]))
        elif line.startswith('#'):
            continue
        elif len(line) == 0:
            continue
        else:
            splitted = line.split('\t')
            if ((abs(float(splitted[0]) - 999.0) <= 1.0e-6) and
                (abs(float(splitted[1]) - 999.0) <= 1.0e-6)):
                fit.append([staruid, 0.0, 0.0])
            else:
                fit.append([staruid, float(splitted[0]), float(splitted[1])])

    return (chi2, coeffs, fit)



def fitlc(star, plc, blc, options):
    if options.debug > 0:
        options.lf.write('processing ' + star['id'] + ' ' + str(star['uid']))
    polyinname = star['id'] + '.tmp'
    polyfile = open(polyinname, 'w')
    for entry in blc:
        polyfile.write(str(round(entry['phase'], 2)) + ' ' + 
                       str(round(entry['normmag'], 5)) + ' ' + 
                       str(round(entry['errnormmag'], 5)) + '\n')
    polyfile.close()
    
    oldargs = ('mastpolyfit', '--find-knots', '--find-step', '--midpoints',  
               '--four-chain', polyinname)
    newargs = ('mastpolyfit', '--find-knots', '--find-step', '--midpoints', 
               '--two-chain', polyinname)

    plcphases = [x[3] for x in plc]
    plcmags   = [x[4] for x in plc]
    blcphases = [x[2] for x in blc]
    blcmags   = [x[3] for x in blc]
    
    oldchi2   = 1.0e11
    oldcoeffs = []
    oldfit    = []
    newchi2   = 1.0e11
    newcoeffs = []
    newfit    = []
    usefit    = None

    p = subprocess.Popen(oldargs, stdout=subprocess.PIPE)
    (outstring, errstring) = p.communicate()
    resold = p.returncode
    if (resold == 0):
        (oldchi2, oldcoeffs, oldfit) = getfit(outstring, star['uid'])
    if (options.debug > 1):
        print 'resold = ', resold, ' old chi2 = ', oldchi2

    p = subprocess.Popen(newargs, stdout=subprocess.PIPE)
    (outstring, errstring) = p.communicate()
    resnew = p.returncode
    if (resnew == 0):
        (newchi2, newcoeffs, newfit) = getfit(outstring, star['uid'])
    if (options.debug > 1):
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
    if usefit == 'new':
        options.lf.write('using new fit (2 chains) for ' + str(star['uid']))

    # call polyfit again for getting the full fit (theoretical lightcurve)
    tmpchi2 = 1.0e11
    coeffs  = []
    fullfit  = []
    args    = ('mastpolyfit', '--find-knots', '--find-step',  
               '--four-chain', polyinname)
    if (usefit == 'new'):
        args = ('mastpolyfit', '--find-knots', '--find-step',  
                '--two-chain', polyinname)
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    (outstring, errstring) = p.communicate()
    res = p.returncode
    if (res == 0):
        (tmpchi2, coeffs, fullfit) = getfit(outstring, star['uid'])
    if (options.debug > 1):
        print 'res = ', res, ' tmpchi2 = ', tmpchi2
        print ''

    os.remove(polyinname)            

    chi2   = None
    coeffs = None
    fit    = None
    varcls = star['varcls']
    legends = ['raw', 'binned']
    fsize = options.fsize
    if varcls == None:
        varcls = 'not classified'
    if (usefit == None):
        plotname = 'failed/' + star['id'] + '.png'
        pl.plot(plcphases, plcmags, 'k.',
                blcphases, blcmags, 'r.')
        pl.xlim(-0.5, 0.5)
        tmp = 'Phase (Period = ' + str(star['Period']) + ' d)'
        pl.xlabel(tmp, fontsize = fsize)
        pl.ylabel('Flux')
        pl.title(star['id'] + '  ' + varcls)
#        pl.legend(legends)
        pl.savefig(plotname)
        pl.clf()
        return (False, chi2, coeffs, fullfit, fit)
    
    chi2   = oldchi2
    coeffs = oldcoeffs
    fit    = oldfit
    if (usefit == 'new'):
        chi2   = newchi2
        coeffs = newcoeffs
        fit    = newfit
        
    fitphases  = [x[1] for x in fit]
    fitvalues  = [x[2] for x in fit]
    fullphases = [x[1] for x in fullfit]
    fullvalues = [x[2] for x in fullfit]

    legends = ['raw', 'binned', 'polyfit', 'gridpoints']
    plotname = 'plots/' + star['id'] + '.png'
#    fig = pl.figure()
#    ax  = fig.add_subplot(111)
#    for tick in ax.xaxis.get_major_ticks():
#        tick.label.fontsize = 20
    pl.plot(plcphases, plcmags, 'k.', 
            blcphases, blcmags, 'r.', 
            fullphases, fullvalues, 'b-',
            fitphases, fitvalues, 'go')
    pl.xticks(fontsize = fsize)
    pl.yticks(fontsize = fsize)
    pl.xlim(-0.5, 0.5)
    tmp = 'Phase (Period = ' + str(star['Period']) + ' d)'
    pl.xlabel(tmp, fontsize=options.fsize)
    pl.ylabel('normalized mag', fontsize = fsize)
    pl.title(star['id'] + '  ' + varcls, fontsize = fsize)
#    pl.legend(legends)
    pl.savefig(plotname)
#    pl.show()
    pl.clf()
    
    if options.fittype == 'midpoints':
        newfit = [star['uid']]
        for i in xrange(len(fit)):
            newfit.append(fit[i][1])
            newfit.append(fit[i][2])
        fit = newfit
    
    return (True, chi2, coeffs, fullfit, fit)
    
    
    
def get_polyopts():
    usage = '%prog [options] [fitname]'
    parser = OptionParser(usage=usage)
    parser.add_option('--blc', dest='blcname', type='string', 
                      default='asasblc.sqlite',
                      help='database file with binned light curves')
    parser.add_option('--clscol', dest='clscol', type='string', 
                      default='varcls',
                      help='dictionary column for class (varcls)')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--fit', dest='fitname', type='string', 
                      default='asasfit.sqlite',
                      help='database file with fitted light curves')
    parser.add_option('--fittype', dest='fittype', type='string', 
                      default='coeffs',
                      help='coeffs (default) / midpoints')
    parser.add_option('--fsize', dest='fsize', type='int', 
                      default=18,
                      help='font size for plots (default: 18')
    parser.add_option('--fullfit', dest='fullfit', action='store_true', 
                      default=False,
                      help='store fitted lightcurve (False)')
    parser.add_option('--logfile', dest='logfile', type='string', 
                      default=None,
                      help='name of logfile (None)')
    parser.add_option('--plc', dest='plcname', type='string', 
                      default='asasplc.sqlite',
                      help='database file with phased light curves')
    parser.add_option('--polydir', dest='polydir', type='string', 
                      default=None,
                      help='directory for polyfit files (default = rootdir)')
    parser.add_option('--polyopt', dest='polyopt', type='string', 
                      default= ' --find-knots --find-step --midpoints ',
                      help='cmd line options for polyfit entered within ""; ' +
                           'example: --polyopt "--step-size 0.005"; ' +
                           '(default:  --find-knots --find-step --midpoints )')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./)')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars order by sdir, uid;',
                      help='select statement for dictionary ' +
                           '(Default: select * from stars order by sdir, uid;)')
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')
   
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    if (len(args) == 1):
        options.fitname = args[0]
        
    if (options.polydir == None):
        options.polydir = options.rootdir
    if (options.polydir[-1] != '/'):
        options.polydir += '/'

    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")
    
    options.lf = Logfile(options.rootdir + options.logfile, True, True)

    return options



if __name__ == '__main__':

    options = get_polyopts()
    
    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()
    
    # enforce creation if database or table does not exist
    tmpwriter = dbw.DbWriter(options.rootdir + options.fitname, 
                             dbc.cffcols, dbc.cfftname, 
                             dbc.cfftypes, dbc.cffnulls)
    tmpwriter.close()
    tmpwriter = dbw.DbWriter(options.rootdir + options.fitname, 
                             dbc.fitcols, dbc.fittname, 
                             dbc.fittypes, dbc.fitnulls)
    tmpwriter.close()
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
    cffwriter  = dbw.DbWriter(options.rootdir + options.fitname, 
                              dbc.cffcols, dbc.cfftname)
    fitwriter  = dbw.DbWriter(options.rootdir + options.fitname, 
                              dbc.fitcols, dbc.fittname)
    midwriter  = dbw.DbWriter(options.rootdir + options.fitname,
                              dbc.kmncols, dbc.kmntname)
    
    generator = dictreader.traverse(options.select, None, 1000)
    nrstars   = 0
    failed    = 0
    olddir    = options.rootdir
    for star in generator:
        nrstars += 1
        plc = plcreader.getlc(star['uid'], 'stars', 'phase')
        blc = blcreader.getlc(star['uid'], 'stars', 'phase')
        cffwriter.deletebystaruid(star['uid'])
        fitwriter.deletebystaruid(star['uid'])
        midwriter.deletebystaruid(star['uid'])
        if (options.rootdir + star['sdir'] != olddir):
            olddir = options.rootdir + star['sdir']
            os.chdir(olddir)
            if not os.path.exists('plots'):
                os.mkdir('plots')
            if not os.path.exists('failed'):
                os.mkdir('failed')
        (ok, chi2, coeffs, fit, midpoints) = fitlc(star, plc, blc, options)
        dictwriter.update('update stars set chi2 = ? where uid = ?;', 
                          [(chi2, star['uid'])])
        if ok == False:
            failed += 1
            continue
        
        if (len(coeffs) == 9):
            for i in range(0, 8):
                coeffs.append(0.0)
        cffwriter.insert((coeffs,), True)
        if options.fullfit == True:
            fitwriter.insert(fit, True)
        if options.fittype == 'midpoints':
            midwriter.insert([midpoints], True)
        
    dictreader.close()
    plcreader.close()
    blcreader.close()
    
    dictwriter.commit()
    
    dictwriter.close()
    cffwriter.close()
    fitwriter.close()    
    midwriter.close()

    print nrstars, ' processed, ', failed, ' lightcurves failed'
    print watch.stop(), ' seconds'
    print ''
    print 'Done'
    