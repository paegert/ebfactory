'''
Created on Jun 19, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.16 $
@date     \$Date: 2013/09/05 18:44:08 $

$Log: dbconfig.py,v $
Revision 1.16  2013/09/05 18:44:08  paegerm
adding npviewtype
keep reference to raw lc in nplc for Asas
change KIC to id in translation table (t)

adding npviewtype
keep reference to raw lc in nplc for Asas
change KIC to id in translation table (t)

Revision 1.15  2013/08/13 19:18:13  paegerm
adding fmin, fmax to self.t for Asas

Revision 1.14  2013/08/13 18:20:57  paegerm
formatting code

Revision 1.13  2013/07/31 19:24:35  parvizm
Added classes for Kepq3test, Kepq3flat, kepq3FC2, kepq3var

Revision 1.12  2013/07/31 19:11:09  paegerm
adding missing stats to Mast, adding npblctype

Revision 1.11  2013/07/31 16:51:14  paegerm
adding netselect and remark to netdict
Mast: add uid to npdicttype for Mast, adding missing clolumns (blc*, chi2)

Revision 1.10  2013/07/05 14:45:35  paegerm
correcting login, adding raw and phased lightcurve  for Asas

Revision 1.9  2013/07/02 21:17:12  parvizm
Added 'VARCLS" to Kepq3

Revision 1.8  2013/07/02 20:33:19  parvizm
Added Kepq3

Revision 1.7  2013/07/02 14:58:02  parvizm
Updated to include "midpoints" table

Revision 1.6  2013/06/10 22:45:17  parvizm
Mast added for new version of Kepler EBs

Revision 1.5  2013/06/03 19:29:46  paegerm
add KeplerEBs
add runname to classification database

Revision 1.4  2012/11/30 20:27:55  paegerm
adding Verr to missingstats for Asas, adding calcls, calprob to Asas dict,
correcting index in getto and getperiod for Asas

Revision 1.3  2012/09/24 21:24:18  paegerm
adding class for LINEAR database, adding statistic functions, 
adding rlcuid to phased light curve

Revision 1.2  2012/08/23 20:30:53  paegerm
raw light curve and comments added

Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision

'''

import numpy as np


class Asas(object):
    '''
    class wrapper for ASAS column definitions, types etc
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
        # dictionary
        self.dicttname = 'stars'
        self.t         = {'id' : 1, 'mag' : 6, 'mean' : 6, 'magamp' : 7, 
                          'fmin' : 11, 'fmax' : 12, 'median' : 24, 
                          'varcls' : 20}
        self.dictcols  = ['ID', 'Ra', 'Dec', 'Period', 'T0', 'Vmag', 'Vamp', 
                          'varcls', 'GCVS_ID', 'GCVS_type', 'fmin', 'fmax', 
                          'stddev', 'chi2', 'sdir', 'ir12', 'ir25', 'ir60', 
                          'ir100', 'jmag', 'hmag', 'kmag', 'tmassname', 
                          'Verr', 'Vmedian', 'plcmaxgap', 'calcls', 'calprob']
        self.dicttypes = ['TEXT', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 
                          'TEXT', 'TEXT', 'TEXT', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'TEXT', 'REAL', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'REAL', 'REAL', 'TEXT', 
                          'REAL', 'REAL', 'REAL', 'TEXT', 'REAL']
        self.dictnulls = ['NOT NULL', ' NOT NULL', ' NOT NULL', '', '', '', '', 
                          '', '', '', '', '', 
                          '', '', '', '', '', '', 
                          '', '', '', '', '',
                          '', '', '', '', '']
        self.varclsindex = 8
        self.sdirindex   = 15
        self.npdicttype = [('uid', 'i4'), ('id', 'a20'), 
                           ('ra', 'f4'),  ('dec', 'f4'), 
                           ('period', 'f4'), ('t0', 'f4'), 
                           ('vmag', 'f4'), ('Vamp', 'f4'), ('varcls', 'a20'), 
                           ('GCVS_ID', 'a20'), ('GCVS_type', 'a20'),            
                           ('fmin', 'f4'), ('fmax', 'f4'), 
                           ('stddev', 'f4'), ('chi2', 'f4'),  
                           ('sdir', 'a5'), ('IR12', 'f4'), ('IR25', 'f4'), 
                           ('IR60', 'f4'), ('IR100', 'f4'), 
                           ('jmag', 'f4'), ('hmag', 'f4'), ('kmag', 'f4'), 
                           ('tmassname', 'a20'), ('Verr', 'f4'), 
                           ('Vmedian', 'f4'), ('plcmaxgap', 'f4'),
                           ('calcls', 'a20'), ('calprob', 'f4')]
        
        self.npviewtype = [('uid', 'i4'), ('id', 'a20'), 
                           ('ra', 'f4'),  ('dec', 'f4'), 
                           ('period', 'f4'), ('t0', 'f4'), 
                           ('vmag', 'f4'), ('Vamp', 'f4'), ('varcls', 'a20'), 
                           ('GCVS_ID', 'a20'), ('GCVS_type', 'a20'),            
                           ('fmin', 'f4'), ('fmax', 'f4'), 
                           ('stddev', 'f4'), ('chi2', 'f4'),  
                           ('sdir', 'a5'), ('IR12', 'f4'), ('IR25', 'f4'), 
                           ('IR60', 'f4'), ('IR100', 'f4'), 
                           ('jmag', 'f4'), ('hmag', 'f4'), ('kmag', 'f4'), 
                           ('tmassname', 'a20'), ('Verr', 'f4'), 
                           ('Vmedian', 'f4'), ('plcmaxgap', 'f4'),
                           ('calcls', 'a20'), ('calprob', 'f4'), ('tcls', 'a10')]

        
        # periodic variables = dictionary + staruid
        self.vartname  = 'stars'
        self.varcols   = self.dictcols.append('staruid')
        self.vartypes  = self.dicttypes.append('INTEGER')
        self.varnulls  = self.dictnulls.append(' NOT NULL')
        self.npvartype = self.npdicttype.append(('staruid', 'i4'))
        
        # fluxratios, t0 from diffrerent lc
        self.frt0tname = 'stars'
        self.frt0cols  = ['staruid', 'frphase', 't0phase', 'frbin', 't0bin',
                          'frfit', 't0fit', 
                          'stetj', 'stetk', 'stetl']
        self.frt0types = ['INTEGER', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL']
        self.frt0nulls = ['NOT NULL', '', '', '', '', '', '', '', '', '']
        
        # raw light curve
        self.rlctname = 'stars'
        self.rlccols  = ['staruid', 'hjd', 'vmag', 'vmag_err', 'quality']
        self.rlctypes = ['INTEGER', 'REAL', 'REAL', 'REAL', 'TEXT']
        self.rlcnulls = [' NOT NULL', ' NOT NULL', '', '', '']
        self.rlnptype = [('uid', 'i4'), ('staruid', 'i4'), ('hjd', 'f8'),
                         ('mag', 'f4'), ('err', 'f4'), ('quality', 'a10')]
        
        # normalized and phased raw light curve
        self.nplctname  = 'stars'
        self.nplccols   = ['staruid', 'rlcuid', 'hjd', 
                           'phase', 'normmag', 'errnormmag']
        self.nplctypes  = ['INTEGER', 'INTEGER', 'REAL', 
                           'REAL', 'REAL', 'REAL']
        self.nplcnulls  = [' NOT NULL', ' NOT NULL', ' NOT NULL', 
                           '', '', '']
        self.nplctype   = [('uid', 'i4'), ('staruid', 'i4'), ('rlcuid', 'i4'), 
                           ('hjd', 'f8'),
                           ('phase', 'f4'), ('mag', 'f4'), ('err', 'f4')]
        
        # phased light curve
        self.plctname = 'stars'
        self.plccols  = ['staruid', 'rlcuid', 'phase', 'normmag', 'errnormmag']
        self.plctypes = ['INTEGER', 'INTEGER', 'REAL', 'REAL', 'REAL']
        self.plcnulls = [' NOT NULL', ' NOT NULL', '', '', '']
        
        # raw and phased together
        self.rplctname = 'stars'
        self.rplccols  = ['staruid','bjd', 'phase', 'raw_flux', 'raw_error',
                          'corr_flux','corr_err', 'dtr_flux', 'dtr_err']
        self.rplctypes = ['INTEGER', 'REAL', 'REAL', 'REAL', 'REAL','REAL',
                          'REAL', 'REAL', 'REAL']
        self.rplcnulls = [' NOT NULL', ' NOT NULL', 'NOT NULL',
                           '', '','','','','']
        self.nprplctype = [('staruid', 'i4'), ('bjd', 'f8'), ('phase', 'f8'), 
                           ('raw_flux', 'f8'), ('raw_err', 'f8'), 
                           ('corr_flux', 'f8'), ('corr_err', 'f8'),
                           ('dtr_flux', 'f8'), ('dtr_err', 'f8')]
        
        # binned light curve
        self.blctname = 'stars'
        self.blccols  = ['staruid', 'phase', 'normmag', 'errnormmag']
        self.blctypes = ['INTEGER', 'REAL', 'REAL', 'REAL']
        self.blcnulls = [' NOT NULL', '', '', '']
        self.blcnptype= [('uid', 'i4'), ('staruid', 'i4'), ('phase', 'f4'),
                         ('normmag', 'f4'), ('errornormmag', 'f4')]
        

        # knots and coefficients from polyfit
        self.cfftname = 'coeffs'
        self.cffcols  = ['staruid', 'knot1', 'c11', 'c12', 'c13', 
                         'knot2', 'c21', 'c22', 'c23',
                         'knot3', 'c31', 'c32', 'c33',
                         'knot4', 'c41', 'c42', 'c43']
        self.cfftypes = ['INTEGER', 'REAL', 'REAL', 'REAL', 'REAL', 
                         'REAL', 'REAL', 'REAL', 'REAL', 
                         'REAL', 'REAL', 'REAL', 'REAL', 
                         'REAL', 'REAL', 'REAL', 'REAL']
        self.cffnulls = [' NOT NULL', ' NOT NULL', ' NOT NULL', ' NOT NULL', 
                         ' NOT NULL', 
                         ' NOT NULL', ' NOT NULL', ' NOT NULL', ' NOT NULL', 
                         '', '', '', '', 
                         '', '', '', '']
        self.npcoefftype = [('uid', 'i4'), ('staruid', 'i4'), 
                            ('knot1', 'f4'), ('c11', 'f4'), ('c12', 'f4'), 
                            ('c13', 'f4'), 
                            ('knot2', 'f4'), ('c21', 'f4'), ('c22', 'f4'), 
                            ('c23', 'f4'), 
                            ('knot3', 'f4'), ('c31', 'f4'), ('c32', 'f4'), 
                            ('c33', 'f4'), 
                            ('knot4', 'f4'), ('c41', 'f4'), ('c42', 'f4'), 
                            ('c43', 'f4')]

        # fitted theoretical light curve from polyfit        
        self.fittname = 'fit'
        self.fitcols  = ['staruid', 'phase', 'value']
        self.fittypes = ['INTEGER', 'REAL', 'REAL']
        self.fitnulls = [' NOT NULL', ' NOT NULL', ' NOT NULL']
        self.npfittype = [('uid', 'i4'), ('staruid', 'i4'), 
                          ('phase', 'f4'), ('value', 'f4')]
        
        
        # knots, midpoints, and flux from polyfit --midpoints
        self.kmntname = 'midpoints'
        self.kmncols  = ['staruid', 'knot1', 'k1_flux', 'mid1', 'm1_flux', 
                         'knot2', 'k2_flux', 'mid2', 'm2_flux',
                         'knot3', 'k3_flux', 'mid3', 'm3_flux',
                         'knot4', 'k4_flux', 'mid4', 'm4_flux']
        self.kmntypes = ['INTEGER', 'REAL', 'REAL', 'REAL', 'REAL', 
                         'REAL', 'REAL', 'REAL', 'REAL', 
                         'REAL', 'REAL', 'REAL', 'REAL', 
                         'REAL', 'REAL', 'REAL', 'REAL']
        self.kmnnulls = [' NOT NULL', ' NOT NULL', ' NOT NULL', ' NOT NULL', 
                         ' NOT NULL', 
                         ' NOT NULL', ' NOT NULL', ' NOT NULL', ' NOT NULL', 
                         '', '', '', '', 
                         '', '', '', '']
        self.npkmntype = [('uid', 'i4'), ('staruid', 'i4'), 
                            ('knot1', 'f4'), ('k1_flux', 'f4'), ('mid1', 'f4'), 
                            ('m1_flux', 'f4'), 
                            ('knot2', 'f4'), ('k2_flux', 'f4'), ('mid2', 'f4'), 
                            ('m2_flux', 'f4'), 
                            ('knot3', 'f4'), ('k3_flux', 'f4'), ('mid3', 'f4'), 
                            ('m3_flux', 'f4'), 
                            ('knot4', 'f4'), ('k4_flux', 'f4'), ('mid4', 'f4'), 
                            ('m4_flux', 'f4')]
        
        # Kepq3 bjd, phased, raw, and dtr 
        self.keplctname = 'stars'
        self.keplccols  = ['staruid','BJD', 'PHASE', 
                          'SAP_FLUX', 'SAP_ERR', 'SAP_BKG', 'SAP_BKG_ERR',
                          'PDCSAP_FLUX','PDCSAP_ERR', 'DTR_FLUX', 'DTR_ERR', 
                          'SLC_FLAG']
        self.keplctypes = ['INTEGER', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL', 'INTEGER']
        self.keplcnulls = ['NOT NULL', '', '',
                           '', '', '', '',
                           '', '', '', '', '']
        self.npkeplctype = [('staruid', 'i4'), ('BJD', 'f4'),  ('PHASE', 'f4'), 
                            ('SAP_FLUX', 'f4'), ('SAP_ERR', 'f4'), 
                            ('SAP_BKG', 'f4'), ('SAP_BKG_ERR', 'f4'),
                            ('PDCSAP_FLUX', 'f4'), ('PDCSAP_ERR', 'f4'), 
                            ('DTR_FLUX', 'f4'), ('DTR_ERR', 'f4'),
                            ('SLC_FLAG', 'i1')]

        

        self.missingstats = 'update stars ' \
                            'set Vmedian = ?, Verr = ? where uid = ?;'
        self.allstats = 'update stars ' \
                        'set Vmag = ?, Verr = ?, medmag = ?, ramp = ?, ' + \
                        'fmin = ?, fmax = ? where uid = ?;'
        
        # trained network
        self.netdicttname = 'netdict'
        self.netdictcols  = ['name', 'nin', 'nout', 'ndata', 'nhidden', 
                             'beta', 'momentum', 'eta', 'outtype', 'multires',
                             'mdelta', 'w1rows', 'w1cols', 'w2rows', 'w2cols', 
                             'nrclasses', 'trainerror', 'validerror', 'stopcount',
                             'allpercent', 'comment', 'netselect', 'remark']
        self.netdicttypes  = ['TEXT', 'INTEGER', 'INTEGER', 'INTEGER', 'INTEGER', 
                              'REAL', 'REAL', 'REAL', 'TEXT', 'BOOL', 
                              'REAL', 'INTEGER', 'INTEGER', 'INTEGER', 'INTEGER', 
                              'INTEGER', 'REAL', 'REAL', 'REAL',
                              'REAL', 'TEXT', 'TEXT', 'TEXT']
        self.netdictnulls  = [' NOT NULL UNIQUE', ' NOT NULL', ' NOT NULL', 
                              ' NOT NULL', ' NOT NULL', 
                              ' NOT NULL', ' NOT NULL', ' NOT NULL', 
                              ' NOT NULL', ' NOT NULL', 
                              '', ' NOT NULL', ' NOT NULL', ' NOT NULL', 
                              ' NOT NULL', 
                              ' NOT NULL', '', '', '', '', '', '', '']
        
        self.netclasstname = 'classes'
        self.netclasscols  = ['netuid', 'i', 'class']
        self.netclasstypes = ['INTEGER', 'INTEGER', 'TEXT']
        self.netclassnulls = [' NOT NULL', ' NOT NULL', ' NOT NULL']
        
        self.netvectname   = 'vector'
        self.normsubname   = 'normsubtract'
        self.normdevname   = 'normdivide'
        self.netveccols    = ['netuid', 'name', 'i', 'val']
        self.netvectypes   = ['INTEGER', 'TEXT', 'INTEGER', 'REAL']
        self.netvecnulls   = [' NOT NULL', ' NOT NULL', ' NOT NULL', ' NOT NULL']
        
        self.netmattname   = 'matrix'
        self.confmatname   = 'confmat'
        self.netmatcols    = ['netuid', 'name', 'i', 'j', 'val']
        self.netmattypes   = ['INTEGER', 'TEXT', 'INTEGER', 'INTEGER', 'INTEGER']
        self.netmatnulls   = [' NOT NULL', ' NOT NULL', ' NOT NULL', 
                              ' NOT NULL', ' NOT NULL']
        
        self.netwtname     = 'weights'
        self.netwcols      = ['netuid', 'layer', 'i', 'j', 'value']
        self.netwtypes     = ['INTEGER', 'INTEGER', 'INTEGER', 'INTEGER', 'REAL']
        self.netwnulls     = [' NOT NULL', ' NOT NULL', ' NOT NULL', 
                              ' NOT NULL', ' NOT NULL']
        
        # classification
        self.clstname      = 'classification'
        self.clscols       = ['staruid', 'id', 'runname', 'cls1', 'prob1', 
                              'cls2', 'prob2', 'cls3', 'prob3']
        self.clstypes      = ['INTEGER', 'TEXT', 'TEXT', 'REAL', 'REAL', 
                              'REAL', 'REAL', 'REAL', 'REAL', ]
        self.clsnulls      = [' NOT NULL', '', '', '',
                              '', '', '', '', '']
        

    def makerlcstats(self, staruid, nprlc):
        mean   = round(nprlc['mag'].mean(), 4)    
        stddev = round(nprlc['mag'].std(), 4)
        median = round(np.median(nprlc['mag']), 4)
        fmax   = round(nprlc['mag'].max(), 4)
        fmin   = round(nprlc['mag'].min(), 4)
        amp    = fmax - fmin
        fmax  /= mean
        fmin  /= mean
        return [mean, stddev, median, amp, fmin, fmax, staruid]

        
        
    def makemissingstats(self, staruid, nprlc):
        median = round(np.median(nprlc['mag']), 4)
        stddev = round(nprlc['mag'].std(), 4)
        return [median, stddev, staruid]
    
    
    def getperiod(self, star):
        return star[4]
    
    
    def getshift(self, star):
        return 0.0
    
    def gett0(self, star):
        return star[5]




class Linear(Asas):
    '''
    class wrapper for Hakeems LINEAR light curves
    '''
    
    def __init__(self):
        
        super(Linear, self).__init__()
        
        # dictionary
        self.dicttname = 'stars'
        
        # NO 0 OFFSET because col 0 is UID
        self.t         = {'id' : 1, 'mag' : 6, 'mean' : 26, 'median' : 12,
                          'varcls' : 20}
        self.dictcols  = ['ID', 'raLIN', 'decLIN', 'Ra', 'Dec', 'rmag', 
                          'ug', 'gr', 'ri', 'iz', 'jk', 'medmag',
                          'stddev', 'rms', 'chi2', 'Period', 'phi1', 'S', 'prior',
                          'varcls', 'ramp', 'fmin', 'fmax', 'sdir', 'T0', 
                          'meanmag', 'errmag', 'plcmaxgap']
        self.dicttypes = ['TEXT', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'INEGER', 'REAL', 
                          'TEXT', 'REAL', 'REAL', 'REAL', 'TEXT', 'REAL', 
                          'REAL', 'REAL', 'REAL']
        self.dictnulls = ['NOT NULL', ' NOT NULL', ' NOT NULL', ' NOT NULL', '',
                          '', '', '', '', '', '', 
                          '', '', '', '', '', '', '', 
                          '', '', '', '', '', '', 
                          '', '', '']
        self.npdicttype = [('uid', 'i4'), ('id', 'a13'), 
                           ('ralin', 'f4'),  ('declin', 'f4'), 
                           ('ra', 'f4'),  ('dec', 'f4'), ('rmag', 'f4'),
                           ('ug', 'f4'), ('gr', 'f4'), ('ri', 'f4'), 
                           ('iz', 'f4'), ('jk', 'f4'), ('medmag', 'f4'),
                           ('stddev', 'f4'), ('rms', 'f4'), ('chi2', 'f4'), 
                           ('period', 'f4'), ('phi1', 'f4'), ('S', 'i4'), 
                           ('prior', 'i4'),
                           ('varcls', 'a20'), ('ramp', 'f4'), ('fmin', 'f4'), 
                           ('fmax', 'f4'), ('sdir', 'a20'), ('T0', 'f4'),
                           ('meanmag', 'f4'), ('errmag', 'f4'), 
                           ('plcmaxgap', 'f4')]

        self.varclsindex = 20
        self.sdirindex = 24
        self.missingstats = 'update stars ' \
                            'set meanmag = ?, errmag = ?, ramp = ?, ' + \
                            'fmin = ?, fmax = ? where uid = ?;'
        self.allstats = 'update stars ' \
                        'set meanmag = ?, errmag = ?, medmag = ?, ramp = ?, ' + \
                        'fmin = ?, fmax = ? where uid = ?;'
        
        # raw light curve
        self.rlctname = 'stars'
        self.rlccols  = ['staruid', 'hjd', 'vmag', 'vmag_err', 'quality']
        self.rlctypes = ['INTEGER', 'REAL', 'REAL', 'REAL', 'TEXT']
        self.rlcnulls = [' NOT NULL', ' NOT NULL', '', '', '']
        
        
    def makemissingstats(self, staruid, nprlc):
        mean   = round(nprlc['mag'].mean(), 4)    
        stddev = round(nprlc['mag'].std(), 4)
        fmax   = round(nprlc['mag'].max(), 4)
        fmin   = round(nprlc['mag'].min(), 4)
        amp    = fmax - fmin
        fmax  /= mean
        fmin  /= mean
        return[mean, stddev, amp, fmin, fmax, staruid]


    def getperiod(self, star):
        return star[16]



    def getshift(self, star):
        return star[17]
    
    
    def gett0(self, star):
        return star[25]



class KeplerEBs(Asas):
    '''
    class wrapper for Kepler EBs
    '''
    
    def __init__(self):
        
        super(KeplerEBs, self).__init__()
        
        # dictionary
        self.dicttname = 'stars'
        
        # NO 0 OFFSET because col 0 is UID
        self.t         = {'id' : 1, 'mag' : 6, 'mean' : 20, 'median' : 21,
                          'varcls' : 7}
        self.dictcols  = ['ID', 'Ra', 'Dec', 'Period', 'T0', 'kmag', 'varcls', 
                          't2t1', 'r1r2', 'q', 'esinw', 'ecosw', 'ff', 'sini',
                          'fmin', 'fmax', 'stddev', 'chi2', 'sdir', 
                          'fmean', 'fmedian', 'plcmaxgap']
        self.dicttypes = ['TEXT', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'TEXT',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'REAL', 'REAL', 'TEXT',
                          'REAL', 'REAL', 'REAL']
        self.dictnulls = ['NOT NULL', '', '', '', '', '', '', 
                          '', '', '', '', '', '', '', 
                          '', '', '', '', '', 
                          '', '', '']
        self.npdicttype = [('uid', 'i4'), ('id', 'a11'), 
                           ('ra', 'f4'),  ('dec', 'f4'), 
                           ('period', 'f4'), ('t0', 'f8'),
                           ('kmag', 'f4'), ('varcls', 'a12'),
                           ('t2t1', 'f4'), ('r1r2', 'f4'), ('q', 'f4'), 
                           ('esinw', 'f4'), ('ecosw', 'f4'), ('ff', 'f4'), 
                           ('sini', 'f4'), ('fmin', 'f4'), ('fmax', 'f4'), 
                           ('stddev', 'f4'), ('chi2', 'f4'), ('sdir', 'a10'), 
                           ('fmean', 'f4'), ('fmedian', 'f4'), 
                           ('plcmaxgap', 'f4')] 
        self.sdirindex   = 19
                           
     
     
class Mast(KeplerEBs):
    '''
    class wrapper for Kepler EBs
    '''
    
    def __init__(self):
        
        super(Mast, self).__init__()
        
        # dictionary
        self.dicttname = 'stars'
        
        # NO 0 OFFSET because col 0 is UID
        self.t         = {'id' : 1, 'period' : 2, 'bjd0' : 3, 'morph' : 4,
                          'mag' : 13, 'varcls' : 18, 'fmin' : 31, 'fmax' : 32 }
        self.dictcols  = ['KIC', 'period', 'bjd0', 'morph', 'T21', 
                          'rho12', 'q', 'e_sin_omega', 'e_cos_omega', 'FF', 
                          'sin_i', 'Teff', 'kmag', 'RA', 'DEC', 
                          'SC', 'sdir', 'cls', 'rf_min', 'rf_max',
                          'rf_mean', 'rf_median', 'cf_min', 'cf_max','cf_mean', 
                          'cf_median', 'df_min', 'df_max','df_mean', 'df_median',
                          'blc_min', 'blc_max', 'blc_std', 'blc_std2', 'chi2']

        self.dicttypes = ['TEXT', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'TEXT', 'TEXT', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL']

        self.dictnulls = ['NOT NULL', ' NOT NULL', ' NOT NULL', 
                          '', '', '', '', '',
                          '', '', '', '', '',
                          '', '', '', '', '', 
                          '', '', '', '', '',
                          '', '', '', '', '',
                          '', '', '', '', '',
                          '', '']
        self.npdicttype = [('uid', 'i4'), ('KIC', 'a10'), 
                           ('period', 'f8'),  ('bjd0', 'f8'), 
                           ('morph', 'f2'), ('T21', 'f8'), 
                           ('rho12', 'f8'), ('q', 'f8'), ('e_sin_omega', 'f8'), 
                           ('e_cos_omega', 'f8'), ('FF', 'f8'),            
                           ('sin_i', 'f8'), ('Teff', 'f4'), 
                           ('kmag', 'f4'), 
                           ('RA', 'f4'), ('DEC', 'f4'), 
                           ('SC', 'i1'), ('sdir', 'a10'), ('cls', 'a12'),
                           ('rf_min', 'f4'), ('rf_max','f4'), ('rf_mean', 'f4'), 
                           ('rf_median', 'f4'),
                           ('cf_min', 'f4'), ('cf_max','f4'), ('cf_mean', 'f4'), 
                           ('cf_median', 'f4'),
                           ('df_min','f4'), ('df_max','f4'), ('df_mean', 'f4'), 
                           ('df_median','f4'), ('chi2', 'f4')]


        self.sdirindex   = 31
        
        

        self.missingstats = 'update stars ' \
                            'set blc_min = ?, blc_max = ? where uid = ?;'
        
        
    def makemissingstats(self, staruid, npblc):
#        median = round(np.median(npblc['normmag']), 4)
#        mean   = round(npblc['normmag'].mean(), 4)
        fmin = round(npblc['normmag'].min(), 4)
        fmax = round(npblc['normmag'].max(), 4)
        return [fmin, fmax, staruid]


        
class Kepq3(Mast):
    '''
    class wrapper for Kepler Q3 data
    '''

    def __init__(self):

        super(Kepq3, self).__init__()

        # dictionary
        self.dicttname = 'stars'

        # NO 0 OFFSET because col 0 is UID
        self.t         = {'id' : 1, 'RA' : 2, 'DEC' : 3, 'KEPMAG' : 14}
        self.dictcols  = ['KIC', 'RA', 'DEC', 'PMRA', 'PMDEC',
                          'GMAG', 'RMAG', 'IMAG', 'ZMAG', 'D51MAG',
                          'JMAG', 'HMAG', 'KMAG', 'KEPMAG', 'VARCLS',
                          'TEFF', 'LOGG', 'FEH', 'AV', 'RADIUS',
                          'PERIOD', 'SNR', 'AOV', 'FC2_PER', 'FC2_CHM',
                          'AoV2_PER', 'AoV2_AOV', 'AoV2_SNR', 'AoV2_NEG']

        self.dicttypes = ['TEXT', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL', 'TEXT',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL']
        self.dictnulls = [' NOT NULL UNIQUE ', '', '', '', '',
                          '', '', '', '', '',
                          '', '', '', '', '',
                          '', '', '', '', '',
                          '', '', '', '', '',
                          '', '', '', '']
        self.npdicttype = [('KIC', 'a10'), ('RA', 'f4'),  ('DEC', 'f4'), 
                           ('PMRA', 'f4'), ('PMDEC', 'f4'),
                           ('GMAG', 'f4'), ('RMAG', 'f4'), ('IMAG', 'f4'), 
                           ('ZMAG', 'f4'), ('D51MAG', 'f4'),
                           ('JMAG', 'f4'), ('HMAG', 'f4'), ('KMAG', 'f4'), 
                           ('KEPMAG', 'f4'), ('VARCLS', 'a12'),
                           ('TEFF', 'f4'), ('LOGG', 'f4'), ('FEH', 'f4'), 
                           ('AV', 'f4'), ('RADIUS', 'f4'),
                           ('PERIOD', 'f4'), ('SNR', 'f4'), ('AOV', 'f4'), 
                           ('FC2_PER', 'f4'), ('FC2_CHM', 'f4'),
                           ('AoV2_PER', 'f4'), ('AoV2_AOV', 'f4'), 
                           ('AoV2_SNR', 'f4'), ('AoV2_NEG', 'f4')]
        self.sdirindex   = 29

        
class Kepq3test(Mast):
    '''
    class wrapper for Kepler Q3 data
    '''
    
    def __init__(self):
        
        super(Kepq3test, self).__init__()
        
        # dictionary
        self.dicttname = 'stars'
        
        # NO 0 OFFSET because col 0 is UID
        self.t         = {'id' : 1, 'RA' : 2, 'DEC' : 3, 'KEPMAG' : 14}
        self.dictcols  = ['KIC', 'RA', 'DEC', 'PMRA', 'PMDEC', 
                          'GMAG', 'RMAG', 'IMAG', 'ZMAG', 'D51MAG',
                          'JMAG', 'HMAG', 'KMAG', 'KEPMAG', 'VARCLS',
                          'TEFF', 'LOGG', 'FEH', 'AV', 'RADIUS', 
                          'PERIOD', 
                          'AoV1_PER', 'AoV1_AOV', 'AoV1_SNR', 'AoV1_NEG',
                          'AoV2_PER', 'AoV2_AOV', 'AoV2_SNR', 'AoV2_NEG',
                          'FC2_PER', 'FC2_CHM',
                          'BLS_PER', 'BLS_SNR']

        self.dicttypes = ['TEXT', 'REAL', 'REAL', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'REAL', 'REAL', 'TEXT',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL']
        
        self.dictnulls = [' NOT NULL UNIQUE ', '', '', '', '',
                          '', '', '', '', '',
                          '', '', '', '', '',
                          '', '', '', '', '',
                          '', '', '', '', '',
                          '', '', '', '', '',
                          '', '', '']
        
        self.npdicttype = [('KIC', 'a10'), ('RA', 'f4'),  ('DEC', 'f4'), 
                           ('PMRA', 'f4'), ('PMDEC', 'f4'), 
                           ('GMAG', 'f4'), ('RMAG', 'f4'), ('IMAG', 'f4'), 
                           ('ZMAG', 'f4'), ('D51MAG', 'f4'),
                           ('JMAG', 'f4'), ('HMAG', 'f4'), ('KMAG', 'f4'), 
                           ('KEPMAG', 'f4'), ('VARCLS', 'a12'),
                           ('TEFF', 'f4'), ('LOGG', 'f4'), ('FEH', 'f4'), 
                           ('AV', 'f4'), ('RADIUS', 'f4'), ('PERIOD', 'f4'), 
                           ('AoV1_PER','f4'), ('AoV1_AOV', 'f4'), 
                           ('AoV1_SNR', 'f4'), ('AoV1_NEG', 'f4'),
                           ('AoV2_PER', 'f4'), ('AoV2_AOV', 'f4'), 
                           ('AoV2_SNR', 'f4'), ('AoV2_NEG', 'f4'),
                           ('FC2_PER', 'f4'), ('FC2_CHM', 'f4'),
                           ('BLS_PER', 'f4'), ('BLS_SNR', 'f4'),] 
        self.sdirindex   = 33
                 
                 
      
class Kepq3flat(Mast):
    '''
    class wrapper for Kepler Q3 data
    '''
    
    def __init__(self):
        
        super(Kepq3flat, self).__init__()
        
        # dictionary
        self.dicttname = 'stars'
        
        # NO 0 OFFSET because col 0 is UID
        self.t         = {'staruid' : 1, 'KIC' : 2, 'PERIOD' : 3, 
                          'A2R_NEG' : 19}
        
        self.dictcols  = ['staruid', 'KIC', 'PERIOD', 
                          'A1F_PER', 'A1F_AOV', 'A1F_SNR', 'A1F_NEG',
                          'A1R_PER', 'A1R_AOV', 'A1R_SNR', 'A1R_NEG',
                          'A2F_PER', 'A2F_AOV', 'A2F_SNR', 'A2F_NEG',
                          'A2R_PER', 'A2R_AOV', 'A2R_SNR', 'A2R_NEG']

        self.dicttypes = ['INTEGER', 'TEXT', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL', 'REAL']
        
        self.dictnulls = [' NOT NULL UNIQUE ', '', '',
                          '', '', '', '',
                          '', '', '', '',
                          '', '', '', '',
                          '', '', '', '']
        
        self.npdicttype = [('staruid', 'i4'), ('KIC', 'a10'), ('PERIOD', 'f4'), 
                           ('AF1_PER', 'f4'), ('AF1_AOV', 'f4'), 
                           ('AF1_SNR', 'f4'), ('AF1_NEG', 'f4'),
                           ('AR1_PER', 'f4'), ('AR1_AOV', 'f4'), 
                           ('AR1_SNR', 'f4'), ('AR1_NEG', 'f4'),
                           ('AF2_PER', 'f4'), ('AF2_AOV', 'f4'), 
                           ('AF2_SNR', 'f4'), ('AF2_NEG', 'f4'),
                           ('AR2_PER', 'f4'), ('AR2_AOV', 'f4'), 
                           ('AR2_SNR', 'f4'), ('AR2_NEG', 'f4')] 
        self.sdirindex   = 19
        
        
                           
class Kepq3FC2(Mast):
    '''
    class wrapper for Kepler Q3 data
    '''
    
    def __init__(self):
        
        super(Kepq3FC2, self).__init__()
        
        # dictionary
        self.dicttname = 'stars'
        
        # NO 0 OFFSET because col 0 is UID
        self.t         = {'id' : 1, 'RA' : 2, 'DEC' : 3, 'KEPMAG' : 14}
        self.dictcols  = ['KIC', 'RA', 'DEC', 'PMRA', 'PMDEC', 
                          'GMAG', 'RMAG', 'IMAG', 'ZMAG', 'D51MAG',
                          'JMAG', 'HMAG', 'KMAG', 'KEPMAG', 'VARCLS',
                          'TEFF', 'LOGG', 'FEH', 'AV', 'RADIUS', 
                          'PERIOD', 'FC2_PER', 'FC2_CHM']

        self.dicttypes = ['TEXT', 'REAL', 'REAL', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'REAL', 'REAL', 'TEXT',
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL',
                          'REAL', 'REAL', 'REAL']
        self.dictnulls = [' NOT NULL UNIQUE ', '', '', '', '',
                          '', '', '', '', '', 
                          '', '', '', '', '',
                          '', '', '', '', '',
                          '', '', '']
        self.npdicttype = [('KIC', 'a10'), ('RA', 'f4'),  ('DEC', 'f4'), 
                           ('PMRA', 'f4'), ('PMDEC', 'f4'), 
                           ('GMAG', 'f4'), ('RMAG', 'f4'), ('IMAG', 'f4'), 
                           ('ZMAG', 'f4'), ('D51MAG', 'f4'),
                           ('JMAG', 'f4'), ('HMAG', 'f4'), ('KMAG', 'f4'), 
                           ('KEPMAG', 'f4'), ('VARCLS', 'a12'),
                           ('TEFF', 'f4'), ('LOGG', 'f4'), ('FEH', 'f4'), 
                           ('AV', 'f4'), ('RADIUS', 'f4'),
                           ('PERIOD', 'f4'), 
                           ('FC2_PER', 'f4'), ('FC2_CHM', 'f4')] 
        self.sdirindex   = 23
       
       
       
class Kepq3var(Mast):
    '''
    class wrapper for Kepler Q3 data
    '''
    
    def __init__(self):
        
        super(Kepq3var, self).__init__()
        
        # dictionary
        self.dicttname = 'stars'
        
        # NO 0 OFFSET because col 0 is UID
        
        self.t         = {'staruid' : 1, 'id' : 2, 'period' : 3, 
                          'fmin' : 5, 'fmax' : 6, 'mag' : 9}
        self.dictcols  = ['staruid', 'KIC', 'period', 'chi2', 
                          'blc_min', 'blc_max', 'dtr_min', 'dtr_max', 'kmag']
        self.dicttypes = ['INTEGER', 'TEXT', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'REAL', 'REAL', 'REAL']
        self.dictnulls = [' NOT NULL UNIQUE ', ' NOT NULL UNIQUE ', '', '', 
                          '', '', '', '', '']
        self.npdicttype = [('uid', 'i6'), ('staruid', 'i6'), ('KIC', 'a10'), 
                           ('period', 'f4'), 
                           ('chi2', 'f4'), ('blc_min', 'f4'), ('blc_max', 'f4'), 
                           ('dtr_min', 'f4'), ('dtr_max', 'f4'), ('kmag', 'f4')] 
        self.sdirindex   = 8
        
