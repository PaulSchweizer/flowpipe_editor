from NodeGraphQt import NodeGraph, BaseNode


class FlowpipeNode(BaseNode):

    __identifier__ = 'flowpipe'

    NODE_NAME = 'FlowpipeNode'

    def __init__(self):
        super(FlowpipeNode, self).__init__()


QTGRAPH = NodeGraph()


try:
    QTGRAPH.register_node(FlowpipeNode)
except:
    pass
