import time

from flowpipe.node import INode, Node
from flowpipe.plug import InputPlug, OutputPlug


@Node(outputs=["result"],
      metadata={
          "datatypes": {
            "inputs": {
                "number_1": {
                    "type": "float",
                },
                "number_2": {
                    "type": "float"
                }
            },
            "outputs": {
                "result": {
                    "type": "float"
                }
            }
          }
      })
def Add(number_1, number_2):
    """Add the two given numbers."""
    r = number_1 + number_2
    time.sleep(0.5)
    return {
        "result": r
    }


@Node(outputs=["result"],
      metadata={
          "datatypes": {
            "inputs": {
                "number_1": {
                    "type": "float",
                },
                "number_2": {
                    "type": "float"
                }
            },
            "outputs": {
                "result": {
                    "type": "float"
                }
            }
          }
      })
def Multiply(number_1, number_2):
    """Multiply the two given values."""
    r = number_1 * number_2
    time.sleep(0.5)
    return {
        "result": r
    }


class DivideNode(INode):
    """A node as a standin for other nodes when prototyping"""

    def __init__(self, *args, **kwargs):
        super(DivideNode, self).__init__(*args, **kwargs)
        InputPlug('number_1', self, 0)
        InputPlug('number_2', self, 0)
        OutputPlug('result', self)
        self.metadata = {
              "datatypes": {
                "inputs": {
                    "number_1": {
                        "type": "float",
                    },
                    "number_2": {
                        "type": "float"
                    }
                },
                "outputs": {
                    "result": {
                        "type": "float"
                    }
                }
            }
        }

    def compute(self, number_1, number_2):
        r = number_1 / number_2
        time.sleep(0.5)
        return {
            "result": r
        }
