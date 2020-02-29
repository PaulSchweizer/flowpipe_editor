import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), "NodeGraphQt-master"))
sys.path.append(os.path.join(os.path.dirname(__file__)))

from Qt import QtWidgets
from floweditor import editor


app = QtWidgets.QApplication(sys.argv)

w = editor.FlowEditor()
w.show()

sys.exit(app.exec_())
