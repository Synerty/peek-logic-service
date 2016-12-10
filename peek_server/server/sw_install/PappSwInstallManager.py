from peek_platform.sw_install.PappSwInstallManagerBase import PappSwInstallManagerBase
from peek_server.papp.PappServerLoader import pappServerLoader


class PappSwInstallManager(PappSwInstallManagerBase):
    def notifyOfPappVersionUpdate(self, pappName, targetVersion):
        pappServerLoader.loadPapp(pappName)
        pappServerLoader.buildFrontend(self)


pappSwInstallManager = PappSwInstallManager()
