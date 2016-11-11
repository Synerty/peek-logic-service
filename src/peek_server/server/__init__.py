from rapui.Util import filterModules

for mod in filterModules(__file__):
    __import__(mod, locals(), globals())

import sw_download
import sw_install
import sw_upload
import sw_version
