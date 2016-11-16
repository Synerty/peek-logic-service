'''
Created on 17/06/2013

@author: darkstar
'''

from rapui.site.ElementUtil import RapuiElement, addPageElement, removePageElement


@addPageElement('')
@addPageElement('setting')
@addPageElement('update')
@addPageElement('env')
class ContentElement(RapuiElement):
    xmlFileName = 'PeekAdmAppTemplate.xml'


def addPappAdminPage(pappName):
    addPageElement(pappName)(ContentElement)

def removePappAdminPage(pappName):
    removePageElement(pappName)

