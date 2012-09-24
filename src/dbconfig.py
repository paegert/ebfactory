'''
Created on Jun 19, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.3 $
@date     \$Date: 2012/09/24 21:24:18 $

$Log: dbconfig.py,v $
Revision 1.3  2012/09/24 21:24:18  paegerm
adding class for LINEAR database, adding statistic functions,
adding rlcuid to phased light curve

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
        self.t         = {'id' : 1, 'mag' : 5, 'mean' : 5, 'median' : 24,
                          'varcls' : 20}
        self.dictcols  = ['ID', 'Ra', 'Dec', 'Period', 'T0', 'Vmag', 'Vamp', 
                          'varcls', 'GCVS_ID', 'GCVS_type', 'fmin', 'fmax', 
                          'stddev', 'chi2', 'sdir', 'ir12', 'ir25', 'ir60', 
                          'ir100', 'jmag', 'hmag', 'kmag', 'tmassname', 
                          'Verr', 'Vmedian', 'plcmaxgap']
        self.dicttypes = ['TEXT', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 
                          'TEXT', 'TEXT', 'TEXT', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'TEXT', 'REAL', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'REAL', 'REAL', 'TEXT', 
                          'REAL', 'REAL', 'REAL']
        self.dictnulls = ['NOT NULL', ' NOT NULL', ' NOT NULL', '', '', '', '', 
                          '', '', '', '', '', 
                          '', '', '', '', '', '', 
                          '', '', '', '', '',
                          '', '', '']
        self.varclsindex = 8
        self.sdirindex   = 15
        self.npdicttype = [('uid', 'i4'), ('id', 'a13'), 
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
                           ('Vmedian', 'f4'), ('plcmaxgap', 'f4')]

        # raw light curve
        self.rlctname = 'stars'
        self.rlccols  = ['staruid', 'hjd', 'vmag', 'vmag_err', 'quality']
        self.rlctypes = ['INTEGER', 'REAL', 'REAL', 'REAL', 'TEXT']
        self.rlcnulls = [' NOT NULL', ' NOT NULL', '', '', '']
        self.rlnptype = [('uid', 'i4'), ('staruid', 'i4'), ('hjd', 'f8'),
                         ('mag', 'f4'), ('err', 'f4'), ('quality', 'a10')]
        
        # phased light curve
        self.plctname = 'stars'
        self.plccols  = ['staruid', 'rlcuid', 'phase', 'normmag', 'errnormmag']
        self.plctypes = ['INTEGER', 'INTEGER', 'REAL', 'REAL', 'REAL']
        self.plcnulls = [' NOT NULL', ' NOT NULL', '', '', '']
        
        # binned light curve
        self.blctname = 'stars'
        self.blccols  = ['staruid', 'phase', 'normmag', 'errnormmag']
        self.blctypes = ['INTEGER', 'REAL', 'REAL', 'REAL']
        self.blcnulls = [' NOT NULL', '', '', '']

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
        self.cffnulls = [' NOT NULL', ' NOT NULL', ' NOT NULL', ' NOT NULL', ' NOT NULL', 
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

        # fitted light curve from polyfit        
        self.fittname = 'fit'
        self.fitcols  = ['staruid', 'phase', 'value']
        self.fittypes = ['INTEGER', 'REAL', 'REAL']
        self.fitnulls = [' NOT NULL', ' NOT NULL', ' NOT NULL']

        self.missingstats = 'update stars ' \
                            'set Vmed = ? where uid = ?;'
        self.allstats = 'update stars ' \
                        'set Vmag = ?, Verr = ?, medmag = ?, ramp = ?, ' + \
                        'fmin = ?, fmax = ? where uid = ?;'
        
        # trained network
        self.netdicttname = 'netdict'
        self.netdictcols  = ['name', 'nin', 'nout', 'ndata', 'nhidden', 
                             'beta', 'momentum', 'eta', 'outtype', 'multires',
                             'mdelta', 'w1rows', 'w1cols', 'w2rows', 'w2cols', 
                             'nrclasses', 'trainerror', 'validerror', 'stopcount',
                             'allpercent', 'comment']
        self.netdicttypes  = ['TEXT', 'INTEGER', 'INTEGER', 'INTEGER', 'INTEGER', 
                              'REAL', 'REAL', 'REAL', 'TEXT', 'BOOL', 
                              'REAL', 'INTEGER', 'INTEGER', 'INTEGER', 'INTEGER', 
                              'INTEGER', 'REAL', 'REAL', 'REAL',
                              'REAL', 'TEXT']
        self.netdictnulls  = [' NOT NULL UNIQUE', ' NOT NULL', ' NOT NULL', ' NOT NULL', ' NOT NULL', 
                              ' NOT NULL', ' NOT NULL', ' NOT NULL', ' NOT NULL', ' NOT NULL', 
                              '', ' NOT NULL', ' NOT NULL', ' NOT NULL', ' NOT NULL', 
                              ' NOT NULL', '', '', '', '', '']
        
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
        self.clscols       = ['staruid', 'id', 'cls1', 'prob1', 
                              'cls2', 'prob2', 'cls3', 'prob3']
        self.clstypes      = ['INTEGER', 'TEXT', 'REAL', 'REAL', 
                              'REAL', 'REAL', 'REAL', 'REAL', ]
        self.clsnulls      = [' NOT NULL', '', '', '',
                              '', '', '', '']
        

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
        return star[3]
    
    
    def getshift(self, star):
        return 0.0
    
    def gett0(self, star):
        return star[4]




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
        
    
        
if __name__ == '__main__':
    x = Linear()
    print x.cffcols
    print dir(x)
    
