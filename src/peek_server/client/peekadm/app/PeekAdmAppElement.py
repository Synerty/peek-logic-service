'''
Created on 17/06/2013

@author: darkstar
'''

from rapui.site.ElementUtil import RapuiElement, addPageElement


@addPageElement('peekadm')
@addPageElement('peekadm/setting')
@addPageElement('peekadm/update')
class ContentElement(RapuiElement):
    xmlFileName = 'PeekAdmAppTemplate.xml'
