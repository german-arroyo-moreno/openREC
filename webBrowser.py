#!/usr/bin/python
# This code is from: https://pythonspot.com/pyqt5-webkit-browser/ 
"""
        OpenREC is an extendable framework for reconstruction of 3D models from
        photographs.
  
        Copyright (C) 2018  Germán Arroyo.

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <https://www.gnu.org/licenses/>.

        You can contact the author via email to <arroyo@ugr.es>,
        or in a more traditional way sending a letter to
        
        Germán Arroyo Moreno
        Departamento de Lenguajes y Sistemas Informáticos
        ETS Ingenierías Informática y de Telecomunicación,
        C/Periodista Daniel Saucedo Aranda, s/n · E-18071 GRANADA (Spain)
        Universidad de Granada.
"""
import PyQt5
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QDialog
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QPushButton
from PyQt5.QtWebKitWidgets import QWebView , QWebPage
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtNetwork import *
import sys
from optparse import OptionParser
 
 
class WebBrowser(QWebPage):
    ''' Settings for the browser.'''
 
    def userAgentForUrl(self, url):
        ''' Returns a User Agent that will be seen by the website. '''
        return "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
 
class Browser(QWebView):
    def __init__(self,parent=None):
        # QWebView
        self.view = QWebView.__init__(self,parent)
        #self.view.setPage(MyBrowser())
        self.setWindowTitle('Loading...')
        self.titleChanged.connect(self.adjustTitle)
        #super(Browser).connect(self.ui.webView,QtCore.SIGNAL("titleChanged (const QString&)"), self.adjustTitle)
        self.timer = None
        
    def load(self,url):  
        self.setUrl(QUrl(url)) 
 
    def adjustTitle(self):
        self.setWindowTitle(self.title())
 
    def disableJS(self):
        settings = QWebSettings.globalSettings()
        settings.setAttribute(QWebSettings.JavascriptEnabled, False)

    def timerReload(self, time):
        """ Reload thet page each time miliseconds """
        self.timer = QTimer(self);
        self.timer.timeout.connect(self.reload)
        self.timer.start(time)
 
class DialogBrowser(QDialog):
    ''' Create a window with one or more webpages '''
    def __init__(self,parent=None,title=""):
        super(DialogBrowser, self).__init__(parent)
        mainLayout = QVBoxLayout()
        self.setWindowTitle(title)
        self.panel = QTabWidget()
        self.panel.setMinimumWidth(600)
        self.panel.setMinimumHeight(400)
        self.panel.setMovable(True)
        mainLayout.addWidget(self.panel)
        
        closeButton = QPushButton("&Close")
        closeButton.clicked.connect(self.close_application)
        mainLayout.addWidget(closeButton)

        self.setLayout(mainLayout)

    def addUrl(self, url, text=""):
        t = Browser()
        self.panel.addTab(t, text)
        t.load(url) 
        t.timerReload(5000)

    def close_application(self):
        self.close()
