'''
Created on 17/06/2013

@author: Jarrod Chesney
'''
import os

from twisted.web._element import renderer, Element
from twisted.web.template import XMLFile

import txhttputil
from peek_server.storage.Setting import globalSetting, SYSTEM_DESCRIPTION


class BuildLoginElement(Element):
    xmlFileName = 'LoginTemplate.xml'
    loader = XMLFile(os.path.join(os.path.dirname(__file__), xmlFileName))
    rapuiPath = os.path.dirname(txhttputil.__file__)
    stylePath = os.path.join(rapuiPath, 'style')
    javascriptPath = os.path.join(rapuiPath, 'javascript', 'server')

    def __init__(self, failed):
        self._failed = failed

    @renderer
    def loginTitle(self, request, tag):
        tag("Login to %s" % globalSetting()[SYSTEM_DESCRIPTION])
        return tag

    @renderer
    def metaDescriptionContent(self, request, tag):
        tag(content="%s" % globalSetting()[SYSTEM_DESCRIPTION])
        return tag

    @renderer
    def errorPanel(self, request, tag):
        if self._failed:
            return tag("Failed to login_page")
        return ""
