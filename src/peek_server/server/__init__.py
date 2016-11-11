from rapui.Util import filterModules

for mod in filterModules(__file__):
    __import__(mod, locals(), globals())

import sw_update_from_ui
import sw_update_server
