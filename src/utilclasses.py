'''
@package: utilclasses
@author   : map
@version  : \$Revision: 1.1 $
@Date      : \$Date: 2013/12/05 18:13:47 $

non-GUI utility classes for ebf

$Log: utilclasses.py,v $
Revision 1.1  2013/12/05 18:13:47  paegerm
initial revision

Initial revision
'''


class LogData():
    '''
    Data Container
    '''
    def __init__(self, fname = None):
        self.idx  = []
        self.terr = []
        self.verr = []
        self.dold = []
        self.dnew = []
        self.fname = fname
        if (self.fname != None):
            self.load_file(self.fname)
            
            
            
    def load_file(self, fname = None):
        if fname == None or len(fname) == 0:
            return
        self.fname = fname
        for line in open(self.fname):
            if 'trainerr' not in line:
                continue
            splitted = line.split()
            i = int(splitted[0])
            if i == 1 or i == 2:
                continue
            self.idx.append(i)
            self.terr.append(float(splitted[3][:-1]))
            self.verr.append(float(splitted[6][:-1]))
            self.dold.append(float(splitted[9][:-1]))
            self.dnew.append(float(splitted[12][:-1]))



if __name__ == '__main__':
    pass