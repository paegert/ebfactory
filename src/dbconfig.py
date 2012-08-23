'''
Created on Jun 19, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.2 $
@date     \$Date: 2012/08/23 20:30:53 $

$Log: dbconfig.py,v $
Revision 1.2  2012/08/23 20:30:53  paegerm
raw kight curve and comments added

raw light curve and comments added

Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision

'''

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
        self.dictcols  = ['ID', 'Ra', 'Dec', 'Period', 'T0', 'Vmag', 'Vamp', 
                          'varcls', 'GCVS_ID', 'GCVS_type', 'fmin', 'fmax', 
                          'stddev', 'chi2', 'sdir', 'ir12', 'ir25', 'ir60', 
                          'ir100', 'jmag', 'hmag', 'kmag', 'tmassname']
        self.dicttypes = ['TEXT', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 
                          'TEXT', 'TEXT', 'TEXT', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'TEXT', 'REAL', 'REAL', 'REAL', 
                          'REAL', 'REAL', 'REAL', 'REAL', 'TEXT']
        self.dictnulls = ['NOT NULL', ' NOT NULL', ' NOT NULL', '', '', '', '', 
                          '', '', '', '', '', 
                          '', '', '', '', '', '', 
                          '', '', '', '', '']
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
                           ('tmassname', 'a20')]

        # raw light curve
        self.rlctname = 'stars'
        self.rlccols  = ['staruid', 'hjd', 'vmag', 'vmag_err', 'quality']
        self.rlctypes = ['INTEGER', 'REAL', 'REAL', 'REAL', 'TEXT']
        self.rlcnulls = [' NOT NULL', ' NOT NULL', '', '', '']
        
        # phased light curve
        self.plctname = 'stars'
        self.plccols  = ['staruid', 'phase', 'normmag', 'errnormmag']
        self.plctypes = ['INTEGER', 'REAL', 'REAL', 'REAL']
        self.plcnulls = [' NOT NULL', '', '', '']
        
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
        