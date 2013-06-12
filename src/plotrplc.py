
'''
Created on Jun 06, 2013

@package  ebf
@author   mparvizi
@version  \$ 1.0 $
@date     \$Date: 2013/06/12 22:28:56 $
'''
from optparse import OptionParser
from stopwatch import *

import os
import numpy as np
import matplotlib.pyplot as pl

if __name__ == '__main__':
    usage = '%prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--fsize', dest='fsize', type='int', 
                      default=8,
                      help='font size for plots (default: 8')
    parser.add_option('--impdir', dest='impdir', type='string', 
                      default='rplc_files_test',
                      help='directory for light curve data files')
    parser.add_option('--plotdir', dest='plotdir', type='string', 
                      default='rplc_plots',
                      help='directory for plotted light curves')
    parser.add_option('--rplc', dest='rplcnames', type='string', 
                      default='rplc_to_plot.txt',
                      help='text file with raw/phased light curve file names')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for .txt file with lc names')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'
    if (options.impdir[-1] != '/'):
        options.impdir += '/'
    if (options.plotdir[-1] != '/'):
        options.plotdir += '/'
    if (len(args) == 1):
        options.rplcnames = args[0]
        
    watch = Stopwatch()
    watch.start()
    
#Read in lc filenames to open
lcdtype = [('bjd', 'f8'), ('phase', 'f8'), ('raw_flux', 'f8'), ('raw_err', 'f8'),
           ('corr_flux', 'f8'), ('corr_err', 'f8'),('dtr_flux', 'f8'), ('dtr_err', 'f8')]

for line in open(options.rootdir + options.impdir + options.rplcnames).readlines(): 
        fname = options.rootdir + options.impdir + line.rstrip('\n')
        print 'path: ' + fname  
    
        lcimport = 0
        if os.path.exists(options.rootdir + options.impdir):
            print 'found: ' + fname
            lcimport += 1
            lcarr = np.loadtxt(fname, dtype = lcdtype)
            bjd =  lcarr['bjd']
            phase = lcarr['phase']
            rflux  = lcarr['raw_flux']
            cflux  = lcarr['corr_flux']
            dflux  = lcarr['dtr_flux']
        
        #bjd_raw_lc
            plotname  = options.rootdir + options.plotdir + 'bjd_raw_' + line.rstrip('\n') + '.png'
            pl.plot(bjd, rflux,'.')
            
            pl.xticks(fontsize = options.fsize)
            pl.yticks(fontsize = options.fsize)
            pl.xlabel('bjd', fontsize=options.fsize)
            pl.ylabel('raw_flux', fontsize=options.fsize)
            pl.title('Kepler EB Light Curve: ' + 'bjd_raw_' + line.rstrip('\n'), 
                     fontsize=options.fsize)
            pl.savefig(plotname)
        #   pl.show()
            pl.clf()
            print 'saved file: ' + plotname
            
        #phased_raw_lc
            plotname  = options.rootdir + options.plotdir + 'phased_raw_' + line.rstrip('\n') + '.png'
            pl.plot(phase, rflux,'.')
            
            pl.xticks(fontsize = options.fsize)
            pl.yticks(fontsize = options.fsize)
            pl.xlim(-0.5, 0.5)
            pl.xlabel('phase', fontsize=options.fsize)
            pl.ylabel('raw_flux', fontsize=options.fsize)
            pl.title('Kepler EB Light Curve: ' + 'phased_raw_' + line.rstrip('\n'), 
                     fontsize=options.fsize)
            pl.savefig(plotname)
        #   pl.show()
            pl.clf()
            print 'saved file: ' + plotname
                    
        #bjd_corr_lc
            plotname  = options.rootdir + options.plotdir + 'bjd_corr_' + line.rstrip('\n') + '.png'
            pl.plot(bjd, cflux,'.')
            
            pl.xticks(fontsize = options.fsize)
            pl.yticks(fontsize = options.fsize)
            pl.xlabel('bjd', fontsize=options.fsize)
            pl.ylabel('corr_flux', fontsize=options.fsize)
            pl.title('Kepler EB Light Curve: ' + 'bjd_corr_' + line.rstrip('\n'), 
                     fontsize=options.fsize)
            pl.savefig(plotname)
        #   pl.show()
            pl.clf()
            print 'saved file: ' + plotname
            
            #phased_corr_lc
            plotname  = options.rootdir + options.plotdir + 'phased_corr_' + line.rstrip('\n') + '.png'
            pl.plot(phase, cflux,'.')
            
            pl.xticks(fontsize = options.fsize)
            pl.yticks(fontsize = options.fsize)
            pl.xlim(-0.5, 0.5)
            pl.xlabel('phase', fontsize=options.fsize)
            pl.ylabel('corr_flux', fontsize=options.fsize)
            pl.title('Kepler EB Light Curve: ' + 'phased_corr_' + line.rstrip('\n'), 
                     fontsize=options.fsize)
            pl.savefig(plotname)
        #   pl.show()
            pl.clf()
            print 'saved file: ' + plotname
            
            #bjd_dtr_lc
            plotname  = options.rootdir + options.plotdir + 'bjd_dtr_' + line.rstrip('\n') + '.png'
            pl.plot(bjd, dflux,'.')
            
            pl.xticks(fontsize = options.fsize)
            pl.yticks(fontsize = options.fsize)
            pl.xlabel('bjd', fontsize=options.fsize)
            pl.ylabel('dtr_flux', fontsize=options.fsize)
            pl.title('Kepler EB Light Curve: ' + 'bjd_dtr_' + line.rstrip('\n'), 
                     fontsize=options.fsize)
            pl.savefig(plotname)
        #   pl.show()
            pl.clf()
            print 'saved file: ' + plotname
            
            #phased_dtr_lc
            plotname  = options.rootdir + options.plotdir + 'phased_dtr_' + line.rstrip('\n') + '.png'
            pl.plot(phase, dflux,'.')
            
            pl.xticks(fontsize = options.fsize)
            pl.yticks(fontsize = options.fsize)
            pl.xlim(-0.5, 0.5)
            pl.xlabel('phase', fontsize=options.fsize)
            pl.ylabel('dtr_flux', fontsize=options.fsize)
            pl.title('Kepler EB Light Curve: ' + 'phased_dtr_' + line.rstrip('\n'), 
                     fontsize=options.fsize)
            pl.savefig(plotname)
        #   pl.show()
            pl.clf()
            print 'saved file: ' + plotname