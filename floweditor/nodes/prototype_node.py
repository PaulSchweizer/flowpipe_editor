from flowpipe.node import INode
from flowpipe.plug import InputPlug, OutputPlug, SubInputPlug, SubOutputPlug


class PrototypeNode(INode):
    """A node as a standin for other nodes when prototyping"""

    def __init__(self, *args, **kwargs):
        super(PrototypeNode, self).__init__(*args, **kwargs)

    def compute(self, *args, **kwargs):
        return {
            output: kwargs.get(output, None) for output in self.outputs.keys()
        }

    def post_deserialize(self, data):
        """Perform more data operations after initial serialization."""
        self.name = data['name']
        self.identifier = data['identifier']
        self.metadata = data['metadata']
        self.file_location = data['file_location']
        for name, input_ in data['inputs'].items():
            if name not in self.inputs:
                InputPlug(name, self)
            self.inputs[name].value = input_['value']
        for name, output in data['outputs'].items():
            if name not in self.outputs:
                OutputPlug(name, self)
            self.outputs[name].value = output['value']
