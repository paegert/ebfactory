'''
Created on Aug 27, 2012

@package  importlcs
@author   map
@version  \$Revision: 1.1 $
@date     \$Date: 2013/08/13 19:22:43 $

Import lightcurves from textfiles. 

$Log: importlcs.py,v $
Revision 1.1  2013/08/13 19:22:43  paegerm
initial revision

Initial revision
'''

from optparse import OptionParser

import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr

import dbconfig
from functions import *
from stopwatch import *



if __name__ == '__main__':
    usage = '%prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Asas',
                      help='name of database configuration (default = Asas')
    parser.add_option('--nodel', dest='delete', action='store_false', default=True,
                      help='per staruid: delete old entries in plc (default = True)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='asasdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--ext', dest='ext', type='string', default='',
                      help='filename extension (default = empty string)')
    parser.add_option('--rawlc', dest='rlcname', type='string', 
                      default='asaslc.sqlite',
                      help='database file with raw light curves')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for database files (default = ./)')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars;',
                      help='select statement for dictionary (Default: select * from stars;)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    if (len(args) == 1):
        options.plcname = args[0]
        
    watch = Stopwatch()
    watch.start()

    cls = getattr(dbconfig, options.dbconfig)
    dbconfig = cls()

    dictreader = dbr.DbReader(options.rootdir + options.dictname)   
    generator  = dictreader.traverse(options.select, None, 1000)
    rlcwriter  = dbw.DbWriter(options.rootdir + options.rlcname, 
                              dbconfig.rlccols, 'stars', dbconfig.rlctypes, 
                              dbconfig.rlcnulls)

    nrstars    = 0
    for star in generator:
        nrstars += 1
        staruid  = star['uid']
        sdir     = star['sdir']
        rlc      = []
        entries  = 0
        quality  = None
        fname    = options.rootdir + sdir + '/' + star['id'] + options.ext
        if options.delete == True:
            rlcwriter.deletebystaruid(staruid)
        for line in open(fname):
            line = line[:-1]
            if (len(line) == 0) or (line.startswith('#') == True):
                continue
            splitted = line.split()
            hjd = float(splitted[0])
            mag = float(splitted[1])
            err = float(splitted[2])
            quality = None
            if options.dbconfig == 'Asas':
                if len(splitted) == 4:
                    quality = None
                elif len(splitted) == 13:
                    quality = splitted[-2]
                    err = splitted[6]
                else:
                    print 'incompatible len = ', len(splitted), 'in', fname
                    exit(1)
            rlc.append([staruid, hjd, mag, err, quality])
            entries += 1
        if entries > 0:
            rlcwriter.insert(rlc, True)
        print entries, 'entries for', star['id']
        
    print nrstars, 'imported in', watch.stop(), 's'
    print 'Done'