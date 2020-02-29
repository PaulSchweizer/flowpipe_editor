from Qt import QtWidgets, QtCore

import flowpipe.plug

from floweditor.attributes import attribute_widgets
from floweditor import plugeditor_ui


class AvailableNodesView(QtWidgets.QListView):

    selection_changed = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(AvailableNodesView, self).__init__(parent=parent)

    def selectionChanged(self, selected, deselected):
        indexes = self.selectedIndexes()
        if indexes:
            self.selection_changed.emit(indexes[0])
        else:
            self.selection_changed.emit(None)


class PlugEditor(QtWidgets.QDialog, plugeditor_ui.Ui_PlugEditor):

    def __init__(self, parent, fp_node, qt_node, plug_type=None, plug=None):
        super(PlugEditor, self).__init__(parent=parent)
        self.setupUi(self)

        self.fp_node = fp_node
        self.qt_node = qt_node
        self.plug_type = plug_type
        self.plug = plug

        self.type_combobox.addItems(attribute_widgets.WIDGETS.keys())
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        if self.plug is not None:
            self.plug_type = type(self.plug)
            self.name_lineedit.setText(self.plug.name)
            self.name_lineedit.setEnabled(False)
            if self.plug_type == flowpipe.plug.InputPlug:
                schema = self.fp_node.metadata.get("datatypes", {}).get("inputs", {}).get(self.plug.name, {})
                self.type_combobox.setCurrentIndex(self.type_combobox.findText(schema.get("type")))
                self.tooltip_lineedit.setText(schema.get("tooltip"))
                self.editable_checkbox.setChecked(QtCore.Qt.Checked if schema.get("editable") else QtCore.Qt.Unchecked)

    def accept(self):
        name = self.name_lineedit.text()

        if self.plug is None:
            self.plug = self.plug_type(name, node=self.fp_node)
            if self.plug_type == flowpipe.plug.InputPlug:
                self.qt_node.add_input(name)
            elif self.plug_type == flowpipe.plug.OutputPlug:
                self.qt_node.add_output(name)

        if self.plug_type == flowpipe.plug.InputPlug:
            type_ = "inputs"
        elif self.plug_type == flowpipe.plug.OutputPlug:
            type_ = "outputs"
        self.fp_node.metadata.setdefault("datatypes", {})
        self.fp_node.metadata["datatypes"].setdefault(type_, {})
        self.fp_node.metadata["datatypes"][type_].setdefault(name, {})
        self.fp_node.metadata["datatypes"][type_][name]["type"] = self.type_combobox.currentText()
        self.fp_node.metadata["datatypes"][type_][name]["editable"] = self.editable_checkbox.checkState() == QtCore.Qt.Checked
        self.fp_node.metadata["datatypes"][type_][name]["tooltip"] = self.tooltip_lineedit.text()

        super(PlugEditor, self).accept()
