from floweditor.attributes import attribute_widgets
reload(attribute_widgets)

from Qt import QtWidgets, QtCore, QtGui


class AttributesWidget(QtWidgets.QWidget):

    right_clicked = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(AttributesWidget, self).__init__(parent)
        self.attributes = {}

        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.scrollarea = QtWidgets.QScrollArea(self)
        self.layout().addWidget(self.scrollarea)
        self.scrollarea.setWidgetResizable(True)
        self.attributes_widget = QtWidgets.QWidget()
        self.form = QtWidgets.QFormLayout(self.attributes_widget)
        self.scrollarea.setWidget(self.attributes_widget)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            child = self.childAt(event.pos())
            if child is not self.attributes_widget:
                row = (self.form.indexOf(child) / 2) * 2
                item = self.form.itemAt(row)
                if item is None:
                    self.right_clicked.emit(None)
                    return
                widget = self.attributes.get(item.widget().text())
                self.right_clicked.emit(widget)
            else:
                self.right_clicked.emit(None)
        event.accept()

    def initialize(self, schema, values=None, plugs=None):
        for index in range(self.form.count())[::-1]:
            i = self.form.takeAt(index)
            w = i.widget()
            w.setParent(None)
            del w
            del i

        values = values or {}
        plugs = plugs or {}
        self.attributes = {}
        for name, in_ in schema.items():
            type_ = in_.get("type")
            if name in values:
                value = values[name]
            else:
                value = in_.get("default")
            editable = in_.get("editable")
            tooltip = in_.get("tooltip")
            plug = plugs.get(name)
            cls = attribute_widgets.WIDGETS.get(type_)
            if cls is not None:
                widget = cls(self, value=value, editable=editable, tooltip=tooltip, plug=plug)
                self.form.addRow(name, widget)
                self.attributes[name] = widget

    def serialize(self):
        data = {}
        for name, widget in self.attributes.items():
            data[name] = widget.value()
        return data
