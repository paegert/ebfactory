'''
@package  ebf
@author   mpaegert
@version  \$Revision: 1.1 $
@date     \$Date: 2012/07/06 20:34:19 $

A simple muulti-layer perceptron, currently restricted to one hidden layer

$Log: mlp.py,v $
Revision 1.1  2012/07/06 20:34:19  paegerm
Initial revision

'''

from numpy import *


class mlp:
	""" A Multi-Layer Perceptron"""

	def __init__(self, inputs, targets, nhidden, 
				  beta = 1, momentum = 0.9, outtype = 'logistic',
				  multires = False, mdelta = 0.01):
		""" Constructor """
		
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
		self.traintstats = None
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
		self.normdevide   = None
		self.classes      = None

		# Initialise network
		self.weights1 = ((random.rand(self.nin + 1, self.nhidden) - 0.5) * 2 / 
						 sqrt(self.nin))
		self.weights2 = ((random.rand(self.nhidden + 1, self.nout) - 0.5) * 2 / 
						 sqrt(self.nhidden))



	def setnormvalues(self, subtract, devide):
		self.normsubtract = subtract
		self.normdevide   = devide
	
	
	
	def getnormvalues(self):
		return (self.normsubtract, self.normdevide)



	def setclasses(self, classes):
		self.classes = classes
	
	
	
	def getclasses(self):
		return self.classes
	


	def earlystopping(self, inputs, targets, valid, validtargets, eta, 
							  niterations = 100, makestats = True):

		# add the bias nodes
		valid = concatenate((valid, -ones((shape(valid)[0], 1))), axis = 1)
		
		self.eta = eta
		self.trainstats = None
		self.validstats = None
		if (makestats == True):
			self.trainstats = targets.sum(axis = 0)
			self.validstats = validtargets.sum(axis = 0)

		old_val_error1 = 100002
		old_val_error2 = 100001
		self.validerror  = 100000

		self.stopcount = 0
		if ((self.writeweights == True) or (self.debug > 0)):
			fnhidden = '%s/hidden%d' % (self.subdir, self.stopcount)
			fnoutput = '%s/output%d' % (self.subdir, self.stopcount)
			savetxt(fnhidden, self.weights1, '%8.4f')
			savetxt(fnoutput, self.weights2, '%8.4f')
			
		while (((old_val_error1 - self.validerror) > 0.001) or 
			   ((old_val_error2 - old_val_error1) > 0.001)):
			self.stopcount += 1
			self.trainerror = self.mlptrain(inputs, targets, eta, niterations)
			old_val_error2 = old_val_error1
			old_val_error1 = self.validerror
			validout = self.mlpfwd(valid)
			self.validerror = 0.5 * sum((validtargets - validout) ** 2)
			if (self.debug > 0):
				fmt = '%3d  trainerr = %7.3f  validerr = %7.3f, ' + \
				      'dold = %8.4f, dnew = %8.4f'
				print  fmt % (self.stopcount, self.trainerror, self.validerror,
							  old_val_error2 - old_val_error1,
							  old_val_error1 - self.validerror)

		if ((self.writeweights == True) or (self.debug > 0)):
			fnhidden = '%s/hidden%d' % (self.subdir, self.stopcount)
			fnoutput = '%s/output%d' % (self.subdir, self.stopcount)
			savetxt(fnhidden, self.weights1, '%8.4f')
			savetxt(fnoutput, self.weights2, '%8.4f')

		if (self.debug > 0):
			print "Stopped", self.validerror, old_val_error1, old_val_error2
			print old_val_error1 - self.validerror
			print old_val_error2 - old_val_error1
		return (self.validerror, self.trainerror)



	def mlptrain(self, inputs, targets, eta, niterations):
		""" Train the thing """
		# Add the inputs that match the bias node
		inputs = concatenate((inputs, -ones((self.ndata, 1))), axis = 1)
		change = range(self.ndata)

		updatew1 = zeros((shape(self.weights1)))
		updatew2 = zeros((shape(self.weights2)))

		error = -1.0
		self.niterations = niterations
		seterr(under='ignore')
		for n in xrange(niterations):

			self.outputs = self.mlpfwd(inputs)

			error = 0.5 * sum((targets - self.outputs) ** 2)
#			if (mod(n, 100) == 0):
#				print "Iteration: ", n, " Error: ", error

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
				print "error: illegal outtype"

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



	def mlpfwd(self, inputs):
		""" Run the network forward """

		self.hidden = dot(inputs, self.weights1);
		self.hidden = 1.0 / (1.0 + exp(-self.beta * self.hidden))
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



	def evaluate(self, inputs):
		# add the bias nodes
		bias = -ones((shape(inputs)[0], 1))
		inputs = concatenate((inputs, bias), axis = 1)
		outputs = self.mlpfwd(inputs)
		return outputs


	def confmat(self, inputs, targets, makestats = True):
		"""Confusion matrix"""

		self.teststats = None
		if (makestats == True):
			self.teststats = targets.sum(axis = 0)
			
		# Add the inputs that match the bias node
		inputs = concatenate((inputs, -ones((shape(inputs)[0], 1))), axis = 1)
		outputs = self.mlpfwd(inputs)

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
			
#		print "Confusion matrix is:"
#		print cm
#		print "Percentage Correct: ", 1.0 * trace(cm) / sum(cm) * 100

		return self.cm



	def _createreport(self, classes, titlefmt, intfmt, floatfmt, firstcolfmt):
		olines = []
		# nrclasses = len(classes)
		
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

		if (self.trainstats != None):
			oline = 'Training   '
			for i in xrange(len(self.trainstats)):
				oline += intfmt % self.trainstats[i]
			oline += intfmt % self.trainstats.sum()
			olines.append(oline)
		
		nrvalid = -1
		if (self.validstats != None):
			oline = 'Validation '
			for i in xrange(len(self.validstats)):
				oline += intfmt % self.validstats[i]
			nrvalid = self.validstats.sum()
			oline += intfmt % nrvalid
			olines.append(oline)
		
		if (self.teststats != None):
			oline = 'Testing    '
			for i in xrange(len(self.teststats)):
				oline += intfmt % self.teststats[i]
			oline += intfmt % self.teststats.sum()
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
		oline = 'Number of testcases = %4d' % self.cm.sum()
		olines.append(oline)
		# self.allpercent = 100.0 * trace(self.cm) / sum(self.cm)
		oline = "Percentage correct  = %6.2f" % (self.allpercent)
		olines.append(oline)

		return olines



	def report(self, titlefmt, intfmt, floatfmt, classes = None, ofname = None,
			    firstcolfmt = '%7s '):
		if (classes != None):
			self.classes = classes
		olines = self._createreport(self.classes, titlefmt, intfmt, floatfmt,
								    firstcolfmt)
		
		if (ofname == None):
			for line in olines:
				print line
		else:
			of = open(self.subdir + '/' + ofname, 'w')
			for line in olines:
				of.write(line + '\n')
			of.close()
