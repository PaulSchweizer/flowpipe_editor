import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), "NodeGraphQt-master"))
sys.path.append(os.path.join(os.path.dirname(__file__)))


from floweditor import editor


w = editor.FlowEditor()
w.show()
