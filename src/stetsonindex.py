''' 

 NAME:
       stetson_index.pro

 UPDATED: 7/26/13  Joey Rodriguez

 PURPOSE:
Computes Stetson J K and L indices for a list of Light curves

 CALLING SEQUENCE:
       .r stetson_index.pro

 INPUTS:
        light_curves.dat =   a list of light curves file names    
 OUTPUT: 
         Stetson_Results.txt =  a file Stetson_Results.txt with columns:File, 
         Mean Mag,; Stetson J index, Stetson K Index, Stetson L index

Python port of Stetson index (IDL) retrieved from Nathan

$Log: stetsonindex.py,v $
Revision 1.1  2013/08/13 19:39:05  paegerm
iniitial revision

'''


import os
import numpy as np
from math import *

from stopwatch import *


lcdtype = [('hjd', 'f4'), ('mag', 'f4'), ('magerr', 'f4')]


def stetson(lclistname, resname): 
    # readcol,'./light_curves.dat',list, format = '(a)'
    # openw,1,'Stetson_Results.txt'
    ifile = open(lclistname)
    lclist = ifile.readlines()
    ifile.close()
    lclist = [x[:-1] for x in lclist]    # clip newline
    ofile = open(resname, 'w')
    
    nrlcs = 0
    # for j = 0l,n_elements(list)-1 do begin
    for j in xrange(len(lclist)):
        if (len(lclist[j]) == 0) or (lclist[j][0] == '#'):
            continue
        nrlcs += 1
        # Set the path to the location of the light curve files.
        # readcol,'./'+List[j],newtimes,star,starerr, format = '(d,d,d)' 
        arr = np.loadtxt(lclist[j], dtype = lcdtype)
        wk = 1.0  #Weighting Factor

        # n = n_elements(Time)
        # MeanMag = Mean(Mag,/double)
        n = len(arr)
        meanmag = arr['mag'].mean()

        # Jt = fltarr(n)*0.0
        # jb = fltarr(n)*0.0
        # kt = fltarr(n)*0.0
        # kb = fltarr(n)*0.0
        jt = np.zeros(n, float)
        jb = np.zeros(n, float)
        kt = np.zeros(n, float)
        kb = np.zeros(n, float)

        # for i = 0L, n-2,2 do begin
        for i in xrange(0, n -2, 2):
            # Sigi = (Mag[i] - MeanMag)/(Magerr[i])*(sqrt(n/(n-1)))
            # Sigj = (Mag[i+1] - MeanMag)/(Magerr[i+1])*(sqrt(n/(n-1)))
            sigi = (arr['mag'][i] - meanmag) / (arr['magerr'][i]) * \
                   (sqrt(n / (n - 1)))
            sigj = (arr['mag'][i + 1] - meanmag) / (arr['magerr'][i + 1]) * \
                   (sqrt(n / (n - 1)))
            # Pk = Sigi*Sigj  # pg 853 Stetson 1996 Eq 2 Kinemuchi
            # if Pk gt 0.0 then sgnPk = 1.0
            # if Pk eq 0.0 then sgnPk = 0.0
            # if Pk lt 0.0 then sgnPk = -1.0
            pk = sigi * sigj
            sgnpk = 0.0
            if pk > 0.0:
                sgnpk = 1.0
            if pk < 0.0:
                sgnpk = -1.0

            # Jt[i] = wk*sgnpk*(sqrt(abs(pk)))   # Kinemuchi eq.1 (Numerator)
            # Jb[i] = (wk)                       # Kinemuchi eq.1 (Denominator)
            # Kt[i] = Abs(Sigi)                  # Kinemuchi eq.5 (Numerator)
            # Kb[i] = abs(sigi^(2.0))            # Kinemuchi eq.5 (Denominator)
            jt[i] = wk * sgnpk * (sqrt(abs(pk))) # Kinemuchi eq.1 (Numerator)
            jb[i] = wk                           # Kinemuchi eq.1 (Denominator)
            kt[i] = abs(sigi)                    # Kinemuchi eq.5 (Numerator)
            kb[i] = abs(sigi * sigi)             # Kinemuchi eq.5 (Denominator)
        # endfor

        # J_stet = Total(Jt,/double)/Total(Jb,/double)        # Eq 1
        # K_stet = 1.0/n*Total(Kt)/(sqrt((1.0/n)*total(Kb)))  # Eq 5
        # L_stet = J_stet*K_stet/(0.7908)                     # Eq 7
        j_stet = np.sum(jt) / sum(jb)                                   # Eq 1
        k_stet = 1.0 / n * np.sum(kt) / (sqrt((1.0 / n) * np.sum(kb)))  # Eq 5
        l_stet = j_stet * k_stet / (0.7908)                             # Eq 7

        # printf, 1, list[j],MeanMag ,J_stet , K_stet , L_stet ,
        #            format= '(A,f15.10,f15.10,f15.10,f15.10)'
        oline = '%s  %15.10f, %15.10f %15.10f %15.10f\n' % \
                 (lclist[j], meanmag, j_stet, k_stet, l_stet)
        ofile.write(oline)
    # endfor

    # close,1
    ofile.close()
    return nrlcs
    # end

if __name__ == '__main__':
    mdir = '/home/map/data/asas10/sim/tmp1026_0825/'
    os.chdir(mdir)
    lcname = 'lclist.txt'
    ofname = 'stetsonout.txt'
    
    watch = Stopwatch()
    watch.start()
    nrlcs = stetson(lcname, ofname)
    print nrlcs, 'lightcurves in', watch.stop(), 's'
    
    print 'done'
