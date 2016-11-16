'''
Created on 09/07/2014

@author: synerty
'''

from rapui.handler.ModelHandler import ModelHandler

modelSetListDataFilt = {
    "papp": "peek_server",
    "key": "nav.adm.papp.list"
}


class PeekModelSetListHandler(ModelHandler):
    def buildModel(self, payloadFilt, **kwargs):
        from peek_server.papp.PappServerLoader import pappServerLoader
        data = []
        for name, title, url in pappServerLoader.pappAdminTitleUrls():
            data.append({
                "templateUrl": '/%s/view/PappAdminRoot.html' % name,
                "title": title,
                "url": url})

        return data


peekModelSetListHandler = PeekModelSetListHandler(modelSetListDataFilt)
