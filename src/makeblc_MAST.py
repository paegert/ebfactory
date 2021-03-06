'''
Created on Jun 28, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.1 $
@date     \$Date: 2013/06/12 22:23:59 $

make phase folded light curves

$Log: makeblc_MAST.py,v $
Revision 1.1  2013/06/12 22:23:59  paegerm
Mast added for new version of Kepler EBs

Revision 1.3  2012/11/30 20:30:27  paegerm
convert del to nodel option

convert del to nodel option

Revision 1.2  2012/09/24 21:34:11  paegerm
adding dbconfig and selfile option, trigger creation if database does not exist
adding nrbins option

Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision

'''

from optparse import OptionParser

import sqlitetools.dbwriter as dbw
import sqlitetools.dbreader as dbr

import dbconfig
from functions import *
from stopwatch import *



if __name__ == '__main__':
    usage = '%prog [options] blcname'
    parser = OptionParser(usage=usage)
    parser.add_option('--blc', dest='blcname', type='string', 
                      default='mastblc.sqlite',
                      help='database file with binned, phased light curves')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('--dbconfig', dest='dbconfig', type = 'string', 
                      default='Mast',
                      help='name of database configuration (default = Mast')
#    parser.add_option('--del', dest='delete', action='store_true', default=False,
#                      help='per staruid: delete old entries in rplc(default = False)')
    parser.add_option('--nodel', dest='delete', action='store_false', default=True,
                      help='per staruid: do not delete old entries in rplc(default = delete)')
    parser.add_option('--dict', dest='dictname', type='string', 
                      default='kepebdict.sqlite',
                      help='dictionary database file')
    parser.add_option('--nrbins', dest='nrbins', type='int', 
                      default=200,
                      help='number of bins per lightcurve (200)')
    parser.add_option('--rplc', dest='rplcname', type='string', 
                      default='keplerrplc.sqlite',
                      help='database file with phased light curves')
    parser.add_option('--rootdir', dest='rootdir', type='string', 
                      default='./',
                      help='directory for database files')
#     parser.add_option('--select2', dest='select2', type='string', 
#                       default='select uid, phase, dtr_flux from stars where staruid = 2 and phase >= -0.0025 and phase <= 0.0025 order by phase asc;',
#                       help='select2 statement for fetchmany line')
    parser.add_option('--select', dest='select', type='string', 
                      default='select * from stars;',
                      help='select statement for dictionary (Default: select * from stars;)')
    parser.add_option('--selfile', dest='selfile', type='string', 
                      default=None,
                      help='file containing select statement (default: None)')
    
    (options, args) = parser.parse_args()
    
    if (options.rootdir[-1] != '/'):
        options.rootdir += '/'

    if (len(args) == 1):
        options.blcname = args[0]

    if options.selfile != None:
        fsel = open(options.rootdir + options.selfile)
        options.select = fsel.read()
        fsel.close()
        options.select = options.select.replace("\n", "")

    cls = getattr(dbconfig, options.dbconfig)
    dbc = cls()

    watch = Stopwatch()
    watch.start()
    
    dictreader = dbr.DbReader(options.rootdir + options.dictname)
    
    generator = dictreader.traverse(options.select, None, 100)
    nrstars   = 0
    dictupd = []
    rplcreader = dbr.DbReader(options.rootdir + options.rplcname)
    blcwriter = dbw.DbWriter(options.rootdir + options.blcname, dbc.blccols,
                             'stars', dbc.blctypes, dbc.blcnulls)
    for star in generator:
        nrstars += 1
        rplc= rplcreader.getlc(star['uid'], order = 'phase')
        
#         # Test of rplc UIDs in bin encapsulating phase 0.0 
#         if nrstars == 2:
#             t_rplcs = np.ndarray((0,))
#             t_rplc = rplcreader.fetchmany(options.select2)
#             for entry in t_rplc:
#                 t_rplcs = np.append(t_rplcs, entry['UID'])
#                 t_rplcs = np.sort(t_rplcs)
#                 t_rplcs.tofile(options.rootdir + 'dtruid_2_99.txt', sep='\n', format="%s")
                
        
        print 'binning ', nrstars, star['uid']
        if options.delete == True:
            blcwriter.deletebystaruid(star['uid'])            
        (blc, mmin, mmax, std) = makebinnedlc_MAST(rplc, star['uid'], options.nrbins)
        blcwriter.insert(blc)
        dictupd.append([mmin, mmax, std, star['uid']])
    
    blcwriter.dbconn.commit()
    dictreader.dbconn.close()
    dictwriter = dbw.DbWriter(options.rootdir + options.dictname, dbc.dictcols)
    updcmd = 'update stars set blc_min = ?, blc_max = ?, blc_std = ? where uid = ?;'
    dictwriter.update(updcmd, dictupd)
    
    print nrstars, ' light curves binned in ', watch.stop(), ' seconds'        
    print 'done'
