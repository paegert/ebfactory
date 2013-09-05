# Makefile for lightcurve viewer, converts qt4 ui files in base classes for 
# python

all : lcviewui.py plotwindowui.py qplotloggui.py

lcviewui.py : lcview.ui
	pyuic4 lcview.ui -o lcviewui.py

plotwindowui.py : plotwindow.ui
	pyuic4 plotwindow.ui -o plotwindowui.py

qplotloggui.py : qplotloggui.ui
	pyuic4 qplotloggui.ui -o qplotloggui.py

