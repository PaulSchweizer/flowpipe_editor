from Qt import QtCore, QtWidgets


class IPlugWidget(QtWidgets.QWidget):

    def __init__(self, parent, value, editable=None, tooltip=None, plug=None):
        super(IPlugWidget, self).__init__(parent)
        self.editable = editable
        self.tooltip = tooltip
        self.plug = plug
        if editable is not None:
            self.setEnabled(editable)

    def set_plug_value(self):
        raise NotImplementedError

    def value(self):
        raise NotImplementedError


# -----------------------------------------------------------------------------
# Implementations
# -----------------------------------------------------------------------------


class StringWidget(IPlugWidget):

    def __init__(self, parent, value, *args, **kwargs):
        super(StringWidget, self).__init__(parent, value, *args, **kwargs)
        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.lineedit = QtWidgets.QLineEdit(value, self)
        self.layout().addWidget(self.lineedit)
        if self.plug is not None:
            self.lineedit.textChanged.connect(self.set_plug_value)

    def set_plug_value(self, text):
        self.plug.value = text

    def value(self):
        return self.lineedit.text()


class BoolWidget(IPlugWidget):

    def __init__(self, parent, value, *args, **kwargs):
        super(BoolWidget, self).__init__(parent, value, *args, **kwargs)
        self.setLayout(QtWidgets.QHBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.checkbox = QtWidgets.QCheckBox(self)
        self.checkbox.setCheckState(
            QtCore.Qt.Checked if value else QtCore.Qt.Unchecked)
        self.layout().addWidget(self.checkbox)
        if self.plug is not None:
            self.checkbox.stateChanged.connect(self.set_plug_value)

    def set_plug_value(self, state):
        self.plug.value = state == QtCore.Qt.Checked

    def value(self):
        return self.checkbox.checkState() == QtCore.Qt.Checked


class FloatWidget(IPlugWidget):

    def __init__(self, parent, value, *args, **kwargs):
        super(FloatWidget, self).__init__(parent, value, *args, **kwargs)
        self.setLayout(QtWidgets.QHBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.spinbox = QtWidgets.QDoubleSpinBox(self)
        self.spinbox.setMinimum(-16777215)
        self.spinbox.setMaximum(16777215)
        self.spinbox.setValue(value if value is not None else 0)
        self.layout().addWidget(self.spinbox)
        if self.plug is not None:
            self.spinbox.valueChanged.connect(self.set_plug_value)

    def set_plug_value(self, value):
        self.plug.value = value

    def value(self):
        return self.spinbox.value()


# -----------------------------------------------------------------------------
# Mapping
# -----------------------------------------------------------------------------


WIDGETS = {
    "string": StringWidget,
    "bool": BoolWidget,
    "float": FloatWidget
}
