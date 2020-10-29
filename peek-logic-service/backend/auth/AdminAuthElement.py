
import logging
import os

from twisted.web._element import renderer, Element
from twisted.web.template import XMLFile
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class AdminAuthElement(Element):
    xmlFileName = 'AdminAuthTemplate.xml'
    loader = XMLFile(os.path.join(os.path.dirname(__file__), xmlFileName))

    def __init__(self, failed, failureMsg):
        self._failed = failed
        self._failureMsg = failureMsg

    @renderer
    @deferToThreadWrapWithLogger(logger)
    def loginTitle(self, request, tag):
        return tag(b"Login to Peek Admin")

    @renderer
    @deferToThreadWrapWithLogger(logger)
    def metaDescriptionContent(self, request, tag):
        return tag(content=b"...")

    @renderer
    def errorPanel(self, request, tag):
        if self._failed:
            if self._failureMsg:
                return tag(b"Failed to login : %s" % self._failureMsg.encode('utf-8'))
            return tag(b"Failed to login")
        return b""
