'''
@package  ebf
@author   mpaegert
@version  \$Revision: 1.7 $
@date     \$Date: 2013/09/05 18:56:15 $

A simple muulti-layer perceptron, currently restricted to one hidden layer

@requires: numpy

$Log: mlp.py,v $
Revision 1.7  2013/09/05 18:56:15  paegerm
*** empty log message ***

stabilizing training in early stopping, dynamic eta, restoring previous nets
if step leads to negative validation errors twice. 

Revision 1.6  2013/08/07 15:39:55  paegerm
changing debug setting for writeweights

Revision 1.5  2013/07/26 20:26:28  paegerm
adding select string for report, adding logfile (lf) to self, write weights
only for debug > 1

Revision 1.4  2012/11/30 20:34:44  paegerm
Converting spaces

Revision 1.3  2012/09/24 21:38:31  paegerm
adding comment, correcting spelling errors, class mlp --> Mlp

Revision 1.2  2012/07/20 20:22:22  paegerm
Adding documentation, adding normalize option to evaluate(), adding stopval to
earlystopping()
Adding MlpError class

Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision

'''

import copy as cp
from numpy import *
from logfile import *


class MlpError(Exception):
    '''Exception class for mlp'''
    def __init__(self, value):
        '''
        Constructor
        
        @param value: Exception value
        '''
        self.value = value
        
        
    def __str__(self):
        return repr(self.value)
    
    
    

class Mlp(object):
    """ A Multi-Layer Perceptron"""

    def __init__(self, inputs, targets, nhidden, 
                  beta = 1, momentum = 0.9, outtype = 'logistic',
                  multires = False, mdelta = 0.01):
        """ Constructor 
        
        @param  inputs     Input values
        @param  targets    Target values (known classification for example)
        @param  nhidden    Number of neurons in hidden layer
        @param  beta       Scaling parameter for activation function (1.0)
        @param  momentum   Influence of previous learning step (0.9)
        @param  outtype    'linear' or 'logistic' (default) or 'softmax'
        @param  multires   True if multiple results are allowed
        @param  mdelta     Maximum difference for a given class (0.01) 
        """
        
        seterr(all = 'raise')
        # Set up network size
        self.nin = shape(inputs)[1]
        self.nout = shape(targets)[1]
        self.ndata = shape(inputs)[0]
        self.nhidden = nhidden

        self.beta = beta
        self.momentum = momentum
        self.eta = 0.1
        self.niterations = -1
        self.outtype = outtype
        self.multires = multires     # true if multiple results allowed
        self.mdelta   = mdelta       # allowed difference for multiple results

        self.cm = None
        self.trainstats  = None
        self.validstats  = None
        self.teststats   = None
        self.trainerror = -1.0
        self.validerror = -1.0
        self.stopcount  = -1
        self.allpercent = 0.0
        self.debug      = 0
        self.subdir     = './'
        self.writeweights = False
        
        self.normsubtract = None
        self.normdivide   = None
        self.classes      = None
        self.comment      = ''
        self.select       = ''
        self.lf           = None

        # Initialise network
        self.weights1 = ((random.rand(self.nin + 1, self.nhidden) - 0.5) * 2 / 
                         sqrt(self.nin))
        self.weights2 = ((random.rand(self.nhidden + 1, self.nout) - 0.5) * 2 / 
                         sqrt(self.nhidden))



    def setnormvalues(self, subtract, divide):
        '''
        Set normalization vectors for input values:
            normalizedvalue = (value - subtract) / divide
        Usually subtract is the mean value, divide the standard deviation
        
        @param  subtract    Vector of values to subtract from each input column
        @param  divide      Vector of values to divide difference by
        '''
        self.normsubtract = subtract
        self.normdivide   = divide
    
    
    
    def getnormvalues(self):
        '''
        Return normalization vectors
        
        @return (normsubtract, normdivide)
        '''
        return (self.normsubtract, self.normdivide)



    def setclasses(self, classes):
        '''
        Set vector of classes
        
        @param  classes    String vector of classes to train on
        '''
        self.classes = classes
    
    
    
    def getclasses(self):
        '''Return classes network has been trained on'''
        return self.classes
    


    def earlystopping(self, inputs, targets, valid, validtargets, eta, 
                      niterations = 100, stopval = 0.001, makestats = True):
        '''
        Train network with validation set, stop if nothing else can be learned.
        Learning stops if the validation error does falls below a limit.
        
        @param  inputs         Input values
        @param  targets        Target values (known classification for example)
        @param  valid          Validation set
        @param  validtargets   Target values for validation set
        @param  eta            Learning rate
        @param  niterations    Number of iterations before shuffling 
        @param  stopval        stop at this value of validation error
        @param  makestats      True if statistics for report are generated (True)
        
        @return   (validationerror, trainingerror)
        '''

        # add the bias nodes
        valid = concatenate((valid, -ones((shape(valid)[0], 1))), axis = 1)
        lenval = len(valid)
        lentrain = len(inputs)
        
        self.eta = eta
        self.trainstats = None
        self.validstats = None
        if (makestats == True):
            self.trainstats = targets.sum(axis = 0)
            self.validstats = validtargets.sum(axis = 0)

        old_val_error1 = 100002
        old_val_error2 = 100001
        self.validerror  = 100000
        dnew = old_val_error1 - self.validerror
        dold = old_val_error2 - old_val_error1

        self.stopcount = 0
        if ((self.writeweights == True) or (self.debug > 1)):
            fnhidden = '%s/hidden%d' % (self.subdir, self.stopcount)
            fnoutput = '%s/output%d' % (self.subdir, self.stopcount)
            savetxt(fnhidden, self.weights1, '%8.4f')
            savetxt(fnoutput, self.weights2, '%8.4f')
            
        oldnet = None
        saveta = eta
        savoldvalerror1 = 0.0
        savoldvalerror2 = 0.0
        steprestored    = 0
        nretareject     = 0
        lastrestored    = -10
        lastnegative    = -10
        mainbreak       = True
        while ((dnew > stopval * self.eta / eta) or 
               (dold > stopval * self.eta / eta)):
            if ((oldnet == None) or 
                ((self.validerror < old_val_error1) and 
                 (self.validerror < old_val_error2))):
                oldnet = cp.deepcopy(self)
                saveta = eta
                savoldvalerror1 = old_val_error1
                savoldvalerror2 = old_val_error2
            self.stopcount += 1
            self.trainerror = self.mlptrain(inputs, targets, eta, niterations)
            old_val_error2 = old_val_error1
            old_val_error1 = self.validerror
            validout = self._mlpfwd(valid)
            self.validerror = 0.5 * sum((validtargets - validout) ** 2)
            addon = ''
            dold  = old_val_error2 - old_val_error1
            dnew  = old_val_error1 - self.validerror
            if dnew < 0.0:
                lastnegative = self.stopcount
#            if self.validerror > old_val_error2:
            if dold <= 0.0 and dnew < 0.0:
                nretareject = 0
                if (eta > 0.25 * self.eta):
                    eta = 0.9 * saveta
                addon = 'restoring ' + str(oldnet.stopcount) + \
                        ', eta = ' + str(round(eta, 2))
            elif ((dnew > 0.0) and (abs(dold - dnew) < 0.001) and 
                  (self.stopcount - lastrestored > 10) and
                  (self.stopcount - lastnegative > 10)):
                neweta = 1.1 * eta
                testeta = cp.deepcopy(self)
                testtrainerror = testeta.mlptrain(inputs, targets, neweta, 
                                                  niterations)
                testvalidout = testeta._mlpfwd(valid)
                testvaliderror = 0.5 * sum((validtargets - testvalidout) ** 2)
                testdnew = self.validerror - testvaliderror
                testeta = None
                if testdnew < 0.0 and dnew < 0.1:
                    nretareject += 1
                    addon = 'new eta rejected'
                else:
                    eta = neweta
                    nretareject = 0
                    addon = 'new eta = ' + str(round(eta, 2))
            if (self.debug > 0):
                fmt = '%3d  trainerr = %7.4f  validerr = %7.4f, ' + \
                      'dold = %8.4f, dnew = %8.4f %s'
                line = fmt % (self.stopcount, 100 * self.trainerror / lentrain, 
                              100 * self.validerror / lenval,
                              dold, dnew, addon)
                if self.lf == None:
                    print line
                else:
                    self.lf.write(line)
#            if self.validerror > old_val_error2:
            if dold <= 0.0 and dnew < 0.0:
                self = cp.deepcopy(oldnet)
                nretareject    = 0
                old_val_error1 = savoldvalerror1
                old_val_error2 = savoldvalerror2
                dold = old_val_error2 - old_val_error1
                dnew = old_val_error1 - self.validerror
                lastrestored   = self.stopcount
                if self.stopcount == steprestored:
                    mainbreak = False
                    break
                steprestored = self.stopcount
            if (nretareject > 20):
                mainbreak = False
                break

        if (mainbreak == True) and (dnew < 0.0) and (dold > 0.0):
            self = cp.deepcopy(oldnet)
            old_val_error1 = savoldvalerror1
            old_val_error2 = savoldvalerror2
            dold = old_val_error2 - old_val_error1
            dnew = old_val_error1 - self.validerror

        if ((self.writeweights == True) or (self.debug > 1)):
            fnhidden = '%s/hidden%d' % (self.subdir, self.stopcount)
            fnoutput = '%s/output%d' % (self.subdir, self.stopcount)
            savetxt(fnhidden, self.weights1, '%8.4f')
            savetxt(fnoutput, self.weights2, '%8.4f')

        fmt = '%3d  trainerr = %7.4f  validerr = %7.4f, ' + \
              'dold = %8.4f, dnew = %8.4f final'
        line = fmt % (self.stopcount, 100 * self.trainerror / lentrain, 
                      100 * self.validerror / lenval, dold, dnew)
        if self.lf == None:
            print line
        else:
            self.lf.write(line)
                
        return (self)



    def mlptrain(self, inputs, targets, eta, niterations):
        """ 
        Train the network without validation set 

        @param    inputs         Input values
        @param    targets        Target values (known classification for example)
        @param    eta            Learning rate
        @param    niterations    Number of iterations
        
        @return   error
        """
        # Add the inputs that match the bias node
        inputs = concatenate((inputs, -ones((self.ndata, 1))), axis = 1)
        change = range(self.ndata)

        updatew1 = zeros((shape(self.weights1)))
        updatew2 = zeros((shape(self.weights2)))

        error = -1.0
        self.niterations = niterations
        seterr(under = 'ignore')
        for n in xrange(niterations):

            self.outputs = self._mlpfwd(inputs)

            error = 0.5 * sum((targets - self.outputs) ** 2)
#            if (mod(n, 100) == 0):
#                print "Iteration: ", n, " Error: ", error

            # Different types of output neurons
            if self.outtype == 'linear':
                deltao = (targets - self.outputs) / self.ndata
            elif self.outtype == 'logistic':
                deltao = (targets - self.outputs) * \
                         self.outputs * (1.0 - self.outputs)
            elif self.outtype == 'softmax':
                #deltao = (targets - self.outputs) * self.outputs / self.ndata
                deltao = (targets - self.outputs) / self.ndata
            else:
                print "Error: illegal outtype"

            deltah = self.hidden * (1.0 - self.hidden) * \
                     (dot(deltao, transpose(self.weights2)))

            updatew1 = eta * (dot(transpose(inputs), deltah[:, :-1])) + \
                       self.momentum * updatew1
            updatew2 = eta * (dot(transpose(self.hidden), deltao)) + \
                       self.momentum * updatew2
            self.weights1 += updatew1
            self.weights2 += updatew2

            # Randomise order of inputs
            random.shuffle(change)
            inputs = inputs[change, :]
            targets = targets[change, :]
        
        return error



    def _mlpfwd(self, inputs):
        """ 
        Run the network forward (internal function)
        
        @param    inputs    Input values
        
        @return   output    Values of output layer  
        """

        self.hidden = dot(inputs, self.weights1);
        try:
            self.hidden = 1.0 / (1.0 + exp(-self.beta * self.hidden))
        except FloatingPointError as err:
            print 'hidden shape = ', self.hidden.shape
            maxpos = unravel_index(self.hidden.argmax(), self.hidden.shape)
            minpos = unravel_index(self.hidden.argmin(), self.hidden.shape)  
            print 'hidden max = ', self.hidden.max(), 'at', maxpos
            print 'hidden min = ', self.hidden.min(), 'at', minpos
            raise MlpError(minpos[0])
        self.hidden = concatenate((self.hidden, -ones((shape(inputs)[0], 1))), 
                                  axis = 1)

        outputs = dot(self.hidden, self.weights2);

        # Different types of output neurons
        if self.outtype == 'linear':
            return outputs
        elif self.outtype == 'logistic':
            try:
                res = 1.0 / (1.0 + exp(-self.beta * outputs))
            except FloatingPointError as err:
                print outputs
            return res
        elif self.outtype == 'softmax':
            normalisers = sum(exp(outputs), axis = 1) * \
                              ones((1, shape(outputs)[0]))
            return transpose(transpose(exp(outputs)) / normalisers)
        else:
            print "error: illegal outtype"



    def evaluate(self, inputs, normalize = True):
        '''
        Evaluate input values
        
        @param    inputs    Input values
        @param    normalize True (default) if inputs should be normalized
        
        @return   outputs   Values of output layer  
        '''
        
        # normalize inputs
        if ((normalize == True) and 
            (self.normsubtract != None) and (self.normdivide != None)):
            inputs = (inputs - self.normsubtract) / self.normdivide
            
        # add the bias nodes
        bias = -ones((shape(inputs)[0], 1))
        inputs = concatenate((inputs, bias), axis = 1)
        outputs = self._mlpfwd(inputs)
        return outputs



    def confmat(self, inputs, targets, makestats = True):
        """
        Build confusion matrix

        @param    inputs         Input values
        @param    targets        Target values (known classification f.e.)
        @param    makestats      True (default) if computing statistics for report
        
        @return:  cm             Confusion matrix
        """

        self.teststats = None
        if (makestats == True):
            self.teststats = targets.sum(axis = 0)
            
        # Add the inputs that match the bias node
        inputs = concatenate((inputs, -ones((shape(inputs)[0], 1))), axis = 1)
        outputs = self._mlpfwd(inputs)

        nclasses = shape(targets)[1]

        if nclasses == 1:
            nclasses = 2
            coutputs = where(outputs > 0.5, 1, 0)
            ctargets = targets
        else:
            if (self.multires == False):
                # 1-of-N encoding
                coutputs = argmax(outputs, 1)
                ctargets = argmax(targets, 1)
            else:
                coutputs = outputs
                ctargets = targets

        if (self.multires == False):
            self.cm = zeros((nclasses, nclasses), dtype = int)
            for i in range(nclasses):
                for j in range(nclasses):
                    # a = where(coutputs == i, 1, 0)
                    # b = where(ctargets == j, 1, 0)
                    # c = a * b
                    # elem = sum(c)
                    self.cm[i, j] = sum(where(coutputs == i, 1, 0) * 
                                    where(ctargets == j, 1, 0))
            self.allpercent = 1.0 * trace(self.cm) / sum(self.cm) * 100
        else:
            self.cm = zeros((2, nclasses), dtype = int)
            diff = abs(ctargets - coutputs)
            success = where(diff < self.mdelta, 1, 0)
            for i in xrange(nclasses):
                self.cm[0, i] = sum(success[:, i])
                self.cm[1, i] = sum(where(success[:, i] == 0, 1, 0))
            self.allpercent = 1.0 * sum(self.cm[0]) / \
                                    (nclasses * shape(targets)[0])
            
#        print "Confusion matrix is:"
#        print self.cm
#        print "Percentage Correct: ", 1.0 * trace(self.cm) / sum(self.cm) * 100

        return self.cm



    def _createreport(self, classes, titlefmt, intfmt, floatfmt, firstcolfmt,
                      fromeval, nrinputs):
        olines = []
        # nrclasses = len(classes)
        
        olines.append(self.comment)
        olines.append(self.select)
        olines.append('')
        olines.append('Input  nodes = %d' % self.nin)
        olines.append('Hidden nodes = %d' % self.nhidden)
        olines.append('Output nodes = %d, type = %s' % (self.nout, self.outtype))
        olines.append('')
        
        title = ''
        for i in xrange(len(classes)):
            title += titlefmt % classes[i]
        if ((self.trainstats != None) or (self.validstats != None) or
             (self.teststats != None)):
            olines.append('Exemplars  ' + title + '    Sum')

        nrtrain = 0
        if (self.trainstats != None) and (fromeval == False):
            oline = 'Training   '
            for i in xrange(len(self.trainstats)):
                oline += intfmt % self.trainstats[i]
            nrtrain = self.trainstats.sum()
            oline += intfmt % nrtrain
            olines.append(oline)
        
        nrvalid = -1
        if (self.validstats != None and (fromeval == False)):
            oline = 'Validation '
            for i in xrange(len(self.validstats)):
                oline += intfmt % self.validstats[i]
            nrvalid = self.validstats.sum()
            oline += intfmt % nrvalid
            olines.append(oline)

        nrtest = 0        
        if (self.teststats != None and (fromeval == False)):
            oline = 'Testing    '
            for i in xrange(len(self.teststats)):
                oline += intfmt % self.teststats[i]
            nrtest = self.teststats.sum()
            oline += intfmt % nrtest
            olines.append(oline)

        if (fromeval == False):
            nrinputs = nrtrain + nrvalid + nrtest
        olines.append('')
        oline = 'Exemplars    = %d  (%d training, %d validating, %d testing)' % \
                (nrinputs, nrtrain, nrvalid, nrtest)
        olines.append(oline)
        
        olines.append('')
        olines.append('momentum         = %f' % self.momentum)
        olines.append('beta             = %f' % self.beta)
        olines.append('learning rate    = %f' % self.eta)
        olines.append('nr iterations    = %d' % self.niterations)
        olines.append('nr repetitions   = %s' % self.stopcount)
        olines.append('training error   = %.4f = %8f per exemplar' % \
                      (self.trainerror, self.trainerror / self.ndata))
        olines.append('validation error = %.4f = %8f per exemplar' % \
                      (self.validerror, self.validerror / nrvalid))
        if (self.multires == True):
            olines.append('delta for class. = %.4f' % self.mdelta)
        olines.append('')
        
        if (self.multires == False):
            oline = firstcolfmt % "out/tar"
            olines.append(oline + title + titlefmt % "% FAP")
            for i in xrange(len(classes)):
                oline = firstcolfmt % classes[i]
                for j in xrange(len(classes)):
                    oline += intfmt % self.cm[i, j]
                try:
                    if (self.cm[i].sum() == 0.0):
                        oline += floatfmt % (0.0)
                    else:
                        oline += floatfmt % (100.0 - 100.0 * self.cm[i, i] / 
                                            self.cm[i].sum())
                except FloatingPointError as err:
                    print err, ' while printing diagonal element ', i
                    print floatfmt
                    print self.cm[i, i]
                    print self.cm[i].sum()
                olines.append(oline)
            tmp = self.cm.sum(axis = 0)
            olines.append('')
            oline = firstcolfmt % 'Sum'
            for i in xrange(len(tmp)):
                oline += intfmt % tmp[i]
            olines.append(oline)
            oline = firstcolfmt % '% corr'
            for i in xrange(shape(self.cm)[1]):
                try:
                    if (tmp[i] == 0.0):
                        oline += floatfmt % (0.0)
                    else:
                        oline += floatfmt % (100.0 * self.cm[i,i] / tmp[i])
                except FloatingPointError as err:
                    print err, ' while printing FAP ', i
                    print floatfmt
                    print self.cm[i, i]
                    print tmp[i]
            olines.append(oline)
        else:
            testcases = sum(self.cm)
            oline = firstcolfmt % 'classes'
            olines.append(oline + title + titlefmt % "  %  ")
            oline = firstcolfmt % '< delta'
            for i in xrange(len(classes)):
                oline += intfmt % self.cm[0, i]
            oline += floatfmt % (100.0 * sum(self.cm[0]) / testcases)
            olines.append(oline)
            oline = firstcolfmt % '> delta'
            for i in xrange(len(classes)):
                oline += intfmt % self.cm[1, i]
            oline += floatfmt % (100.0 * sum(self.cm[1]) / testcases)
            olines.append(oline)
            olines.append('')
            tmp = self.cm.sum(axis = 0)
            oline = firstcolfmt % 'Sum'
            for i in xrange(len(tmp)):
                oline += intfmt % tmp[i]
            olines.append(oline)
            oline = firstcolfmt % '% corr'
            for i in xrange(shape(self.cm)[1]):
                oline += floatfmt % (100.0 * self.cm[0,i] / tmp[i])
            olines.append(oline)
        
        olines.append('')
        oline = 'Number of stars = %4d' % self.cm.sum()
        olines.append(oline)
        # self.allpercent = 100.0 * trace(self.cm) / sum(self.cm)
        oline = "Percentage correct  = %6.2f" % (self.allpercent)
        olines.append(oline)

        return olines



    def report(self, titlefmt, intfmt, floatfmt, classes = None, ofname = None,
                firstcolfmt = '%7s ', fromeval = False, nrinputs = 0):
        '''
        Print or write report of training or evaluation of inputs
        
        @param titlefmt: Format string for class titles
        @param intfmt:   Format string for integer values
        @param floatfmt: Format string for floating point values
        @param classes:  string with class-names (None = default = use self.classes)
        @param ofname:   name of output file (default = None)
        @param firstcolfmt: Format for first columns (classes, default "%7s")
        '''
        
        if (classes != None):
            self.classes = classes
        olines = self._createreport(self.classes, titlefmt, intfmt, floatfmt,
                                    firstcolfmt, fromeval, nrinputs)
        
        if (ofname == None):
            for line in olines:
                print line
        else:
            of = open(self.subdir + '/' + ofname, 'w')
            for line in olines:
                of.write(line + '\n')
            of.close()
