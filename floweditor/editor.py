import logging
import inspect
import json
import os
import re
import sys
import traceback
import webbrowser
from Qt import QtWidgets, QtCore, QtGui

from floweditor import widgets
from floweditor import floweditor_ui
from floweditor import utils
from floweditor import QTGRAPH
import floweditor.nodes.prototype_node
import floweditor.nodes.nodes
import flowpipe.plug
import flowpipe.node
import flowpipe.event
from flowpipe.graph import Graph
from flowpipe.node import FunctionNode


flowpipe.event.log.setLevel(logging.INFO)

log = logging.getLogger(__name__)

COLORS = {
    "idle": (180, 180, 180),
    "scheduled": (80, 80, 120),
    "evaluating": (50, 50, 220),
    "success": (70, 120, 70),
    "error": (180, 70, 70)
}

NODE_DETAILS = """
<b>{name}</b>
<br>
<p style="white-space: pre-wrap;">
{doc}
</p>
<b>File:</b> <a href="file://{file}.py">{file}.py</a>
<br>
<b>Module:</b> {module}
<br>
<b>Class:</b> {cls}"""


class AvailableNodesModel(QtGui.QStandardItemModel):

    def mimeData(self, indexes):
        data = QtCore.QMimeData()
        data.setText(indexes[0].data(QtCore.Qt.ToolTipRole))
        return data


class FlowEditor(QtWidgets.QMainWindow, floweditor_ui.Ui_FlowEditorWindow):

    def __init__(self, parent=None):
        super(FlowEditor, self).__init__(parent=parent)
        self.setupUi(self)

        self.statusBar().addPermanentWidget(self.bottom_widget, 1)
        style = QtWidgets.QApplication.instance().style()
        qstyle = QtWidgets.QStyle

        toolbar = QtWidgets.QToolBar("Evaluation", self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, toolbar)
        self.addToolBar(QtCore.Qt.TopToolBarArea, toolbar)
        self.evaluate_locally_action.setIcon(style.standardIcon(qstyle.SP_ComputerIcon))
        self.evaluate_locally_action.triggered.connect(self.evaluate_locally)
        toolbar.addAction(self.evaluate_locally_action)

        self.fp_nodes_map = {}
        self.qt_nodes_map = {}
        self.logs = {}
        self.graph = None
        self.selected_fp_node = None

        # Graph View
        #
        self.graph_viewer = QTGRAPH.viewer()
        self.graph_widget.layout().addWidget(self.graph_viewer)
        QTGRAPH.nodes_deleted.connect(self.nodes_deleted)
        self.graph_viewer.data_dropped.connect(self.node_dropped)
        self.graph_viewer.connection_changed.connect(self.connection_changed)

        # graph_menu = QTGRAPH._viewer.context_menu()
        # graph_menu.clear()
        # self.delete_action = graph_menu.addAction(
        #     'Delete', self.delete_nodes, QtGui.QKeySequence.Delete)

        nodes = utils.discover_nodes()

        # ---------------------------------------------------------------------
        # Available Nodes - View
        #
        self.node_model = AvailableNodesModel()
        for node in nodes:
            item = QtGui.QStandardItem()
            item.setData(node["name"], QtCore.Qt.DisplayRole)
            item.setData("{0}.{1}".format(node["file"], node["name"]), QtCore.Qt.ToolTipRole)
            item.setData(node["node"], QtCore.Qt.UserRole)
            self.node_model.appendRow([item])
        self.available_nodes_view.setModel(self.node_model)

        # Available Nodes - Actions
        #
        self.create_action = QtWidgets.QAction("Create", self.available_nodes_view)
        self.create_action.triggered.connect(self.create_node)
        self.available_nodes_view.addAction(self.create_action)
        self.available_nodes_view.doubleClicked.connect(self.create_node)

        # Available Nodes - Details
        #
        self.available_nodes_view.selection_changed.connect(self.show_node_details)

        # ---------------------------------------------------------------------
        # Selected Node - Attributes
        #
        self.name_lineedit.textChanged.connect(self.edit_node_name)
        self.open_code_button.clicked.connect(self.open_code)
        self.graph_viewer.node_selection_changed.connect(self.node_selection_changed)
        # self.graph_viewer.node_selected.connect(self.node_selection_changed)

        # Logs
        #
        self.clear_log_button.clicked.connect(self.log_textedit.clear)

        # Main Menu
        #
        self.actionNew.triggered.connect(self.new)
        self.actionOpen.triggered.connect(self.open)
        self.actionSave_As.triggered.connect(self.save_as)
        self.actionQuit.triggered.connect(self.close)

        # Prototyping options
        #
        self.node_inputs_widget.right_clicked.connect(self.inputs_right_clicked)
        self.node_outputs_widget.right_clicked.connect(self.outputs_right_clicked)

        self.new()

    # -------------------------------------------------------------------------
    # Events
    # -------------------------------------------------------------------------

    def closeEvent(self, event):
        self.graph_viewer.data_dropped.disconnect(self.node_dropped)
        self.graph_viewer.node_selection_changed.disconnect(self.node_selection_changed)
        QTGRAPH.nodes_deleted.disconnect(self.nodes_deleted)
        return event.accept()

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def new(self):
        self.fp_nodes_map = {}
        self.qt_nodes_map = {}
        self.graph = Graph()
        QTGRAPH.clear_session()
        self.node_deselected()

    def open(self):
        json_file = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open JSON graph file", "",
            "JSON Files (*.json)")[0]
        if not json_file:
            return
        json_data = None
        with open(json_file, "r") as f:
            json_data = json.load(f)
        graph = Graph.deserialize(json_data)
        w.load_graph(graph)

    def save_as(self):
        save_file, file_type = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save graph to JSON file", os.path.expanduser("~"),
            "JSON Files (*.json)")
        if not save_file:
            return

        if file_type == "JSON Files (*.json)":
            if not save_file.lower().endswith(".json"):
                save_file = "{0}.json".format(save_file)
            with open(save_file, "w") as f:
                json.dump(self.graph.serialize(), f, indent=2)
                print("Saved to", save_file)

    def open_code(self):
        if self.selected_fp_node is not None:
            webbrowser.open(self.selected_fp_node.file_location)

    # -------------------------------------------------------------------------
    # Internals
    # -------------------------------------------------------------------------

    def create_node(self):
        for index in self.available_nodes_view.selectedIndexes():
            self.add_node(index.data(QtCore.Qt.UserRole), QtCore.QPoint())

    def node_dropped(self, data, point):
        for row in range(self.node_model.rowCount()):
            item = self.node_model.item(row)
            if item.data(QtCore.Qt.ToolTipRole) == data.text():
                self.add_node(item.data(QtCore.Qt.UserRole), point)
                return

    def nodes_deleted(self, nodes):
        for node_id in nodes:
            node = self.fp_nodes_map.get(node_id)
            self.graph.delete_node(node)
            del self.qt_nodes_map[node_id]
            del self.fp_nodes_map[node_id]

    def add_node(self, node_cls, point):
        # Check if the name is already taken
        name = getattr(node_cls, "__name__", None) or node_cls.name
        index = -1
        for node in self.graph.nodes:
            if node.name.startswith(name):
                numbers = re.findall(r"(\d+$)", node.name)
                if numbers:
                    if int(numbers[0]) + 1 > index:
                        index = int(numbers[0]) + 1
                else:
                    index = 0
        if index > -1:
            name = "{name}{index}".format(name=name, index=index)

        fp_node = node_cls(graph=self.graph, name=name)
        return self._add_node(fp_node, point)

    def _add_node(self, fp_node, point):
        qt_node = QTGRAPH.create_node(
            'flowpipe.FlowpipeNode',
            name=fp_node.name,
            pos=[point.x(), point.y()]
        )
        for input_ in fp_node.all_inputs().values():
            qt_node.add_input(input_.name)
        for output in fp_node.all_outputs().values():
            qt_node.add_output(output.name)
        self.fp_nodes_map[qt_node.id] = fp_node
        self.qt_nodes_map[qt_node.id] = qt_node
        QTGRAPH.clear_selection()
        return qt_node

    def show_node_details(self, index):
        if index is None:
            self.nodes_details_text.setPlainText("")
        else:
            text = NODE_DETAILS.format(
                name=index.data(QtCore.Qt.DisplayRole),
                doc=utils.dedent_doc(index.data(QtCore.Qt.UserRole).__doc__),
                file=index.data(QtCore.Qt.ToolTipRole).split(".")[0],
                module=index.data(QtCore.Qt.ToolTipRole).split(".")[0],
                cls=index.data(QtCore.Qt.DisplayRole))
            self.nodes_details_text.setText(text)

    def node_selection_changed(self, selected, deselected):
        selection = self.graph_viewer.selected_nodes()
        if len(selection) == 1:
            self.node_selected(selection[0].id)
        else:
            self.node_deselected()

    def node_selected(self, qt_node_id):
        fp_node = self.fp_nodes_map[qt_node_id]
        self.selected_fp_node = fp_node
        self.refresh_node_attributes()

    def refresh_node_attributes(self):
        if self.selected_fp_node is None:
            self.node_deselected()
            return

        self.node_name_widget.setEnabled(True)
        self.node_inputs_widget.setEnabled(True)
        self.node_outputs_widget.setEnabled(True)
        self.code_widget.setEnabled(True)
        self.errors_widget.setEnabled(True)

        self.node_state_label.setText(
            '<span style="color: #ff9999">Dirty</span>' if self.selected_fp_node.is_dirty
            else '<span style="color: #99ff99">Clean</span>')
        self.name_lineedit.setText(self.selected_fp_node.name)
        self.node_type_label.setText(self.selected_fp_node.__class__.__name__)
        self.description_textedit.setPlainText(utils.dedent_doc(self.selected_fp_node.__doc__))

        inputs = {}
        for name, in_ in self.selected_fp_node.inputs.items():
            if in_._sub_plugs:
                inputs[name] = {}
                for sub_name, sub_plug in in_._sub_plugs.items():
                    inputs[name][sub_name] = sub_plug
            else:
                inputs[name] = in_

        outputs = {}
        for name, out in self.selected_fp_node.outputs.items():
            if out._sub_plugs:
                outputs[name] = {}
                for sub_name, sub_plug in out._sub_plugs.items():
                    outputs[name][sub_name] = sub_plug
            else:
                outputs[name] = out

        # Code
        #
        if isinstance(self.selected_fp_node, FunctionNode):
            self.code_view.setPlainText(inspect.getsource(self.selected_fp_node.func))
        elif self.selected_fp_node.__class__.__name__ == "PrototypeNode":
            self.code_view.setPlainText("")
        else:
            self.code_view.setPlainText(inspect.getsource(self.selected_fp_node.compute))

        # Errors
        #
        self.errors_textedit.setHtml(self.logs.get(self.selected_fp_node, ""))

        # Disable/Enable certain fields
        #
        if isinstance(self.selected_fp_node, floweditor.nodes.prototype_node.PrototypeNode):
            self.description_textedit.setStyleSheet("")
            self.description_textedit.setTextInteractionFlags(
                QtCore.Qt.TextEditable | QtCore.Qt.TextSelectableByMouse |
                QtCore.Qt.TextSelectableByKeyboard)
        else:
            self.description_textedit.setStyleSheet("background-color: palette(window)")
            self.description_textedit.setTextInteractionFlags(
                QtCore.Qt.NoTextInteraction)

        # Plugs
        #
        schema = self.selected_fp_node.metadata.get("datatypes", {}).get("inputs", {})
        display_schema = {}
        for plug in self.selected_fp_node.inputs.values():
            s = schema.get(plug.name, {})
            display_schema[plug.name] = {
                "type": s.get("type", "string"),
                "tooltip": s.get("tooltip"),
                "editable": s.get("editable")
            }
        plugs = {p.name: p for p in self.selected_fp_node.inputs.values()}
        values = {p.name: p.value for p in plugs.values()}
        self.node_inputs_widget.initialize(display_schema, values=values, plugs=plugs)

        schema = self.selected_fp_node.metadata.get("datatypes", {}).get("outputs", {})
        display_schema = {}
        for plug in self.selected_fp_node.outputs.values():
            s = schema.get(plug.name, {})
            display_schema[plug.name] = {
                "type": s.get("type", "string"),
                "tooltip": s.get("tooltip"),
                "editable": False
            }
        plugs = {p.name: p for p in self.selected_fp_node.outputs.values()}
        values = {p.name: p.value for p in plugs.values()}
        self.node_outputs_widget.initialize(display_schema, values=values, plugs=plugs)

    def node_deselected(self):
        self.selected_fp_node = None
        self.node_state_label.clear()
        self.name_lineedit.clear()
        self.node_type_label.clear()
        self.description_textedit.clear()
        self.code_view.clear()
        self.errors_textedit.clear()
        self.node_inputs_widget.initialize({}, values={})
        self.node_outputs_widget.initialize({}, values={})
        self.node_name_widget.setEnabled(False)
        self.node_inputs_widget.setEnabled(False)
        self.node_outputs_widget.setEnabled(False)
        self.code_widget.setEnabled(False)
        self.errors_widget.setEnabled(False)

    def edit_node_name(self):
        if len(self.graph_viewer.selected_nodes()) == 1:
            if self.name_lineedit.text() not in [n.name for n in self.graph.nodes]:
                self.graph_viewer.selected_nodes()[0].name = self.name_lineedit.text()
                fp_node = self.fp_nodes_map[self.graph_viewer.selected_nodes()[0].id]
                fp_node.name = self.name_lineedit.text()

    def connection_changed(self, disconnected, connected):
        for connection in connected:
            start_plug = connection[0]
            end_plug = connection[1]
            start_fp_node = self.fp_nodes_map[start_plug.node.id]
            end_fp_node = self.fp_nodes_map[end_plug.node.id]
            start_fp_node.all_outputs()[start_plug.name].connect(
                end_fp_node.all_inputs()[end_plug.name])

        for connection in disconnected:
            start_plug = connection[0]
            end_plug = connection[1]
            start_fp_node = self.fp_nodes_map[start_plug.node.id]
            end_fp_node = self.fp_nodes_map[end_plug.node.id]
            start_fp_node.all_outputs()[start_plug.name].disconnect(
                end_fp_node.all_inputs()[end_plug.name])

    def evaluate_locally(self):
        print self.graph
        self.index = 0.0
        self.progressbar.setValue(0)
        self.current_node = None
        for qt_node in self.qt_nodes_map.values():
            qt_node.set_color(*COLORS["scheduled"])

        flowpipe.node.INode.EVENTS["evaluation-started"].register(self.node_evaluation_started)
        flowpipe.node.INode.EVENTS["evaluation-finished"].register(self.node_evaluation_finished)

        try:
            self.graph.evaluate()
            self.progress_label.setText("Evaluation successful")
        except Exception as error:
            qt_node = QTGRAPH.get_node_by_name(self.current_node.name)
            qt_node.set_color(*COLORS["error"])
            self.progress_label.setText("Evaluation failed!")
            tb = ''.join(traceback.format_exception(*sys.exc_info()))
            self.logs[self.current_node] = (
                '<span style="white-space: pre-wrap; color: #ff9999;">{0}'
                '</span>'.format(tb))
            log.exception(error)
            self.update_logs(tb)

        flowpipe.node.INode.EVENTS["evaluation-started"].deregister(self.node_evaluation_started)
        flowpipe.node.INode.EVENTS["evaluation-finished"].deregister(self.node_evaluation_finished)

        self.refresh_node_attributes()

    def node_evaluation_started(self, node):
        qt_node = QTGRAPH.get_node_by_name(node.name)
        self.current_node = node
        qt_node.set_color(*COLORS["evaluating"])
        self.progress_label.setText(node.name)
        QtWidgets.QApplication.instance().processEvents()

    def node_evaluation_finished(self, node, error=False):
        qt_node = QTGRAPH.get_node_by_name(node.name)
        self.index += 1.0
        self.progressbar.setValue((self.index / len(self.graph.nodes)) * 100)
        qt_node.set_color(*COLORS["success"])
        QtWidgets.QApplication.instance().processEvents()
        self.update_logs("Evaluated: {0}".format(node.name))

    def update_logs(self, message):
        self.log_textedit.append(message)

    def load_graph(self, graph):
        self.new()
        self.graph = graph
        self.graph_name_lineedit.setText(graph.name)
        x = 0
        for row in graph.evaluation_matrix:
            y = 0
            x_diff = 250
            for fp_node in row:
                self._add_node(fp_node, QtCore.QPoint(x, y))
                y += 150
            x += x_diff
        for fp_node in graph.nodes:
            for i, output in enumerate(fp_node.all_outputs().values()):
                for c in output.connections:
                    in_index = c.node.all_inputs().values().index(c)
                    QTGRAPH.get_node_by_name(fp_node.name).set_output(
                        i, QTGRAPH.get_node_by_name(c.node.name).input(in_index))

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def add_input_plug(self):
        selection = self.graph_viewer.selected_nodes()
        if len(selection) != 1:
            return
        fp_node = self.fp_nodes_map[selection[0].id]
        qt_node = self.qt_nodes_map[selection[0].id]
        editor = widgets.PlugEditor(
            self, fp_node=fp_node, qt_node=qt_node,
            plug_type=flowpipe.plug.InputPlug, plug=None)
        if editor.exec_():
            self.node_selected(selection[0].id)

    def add_output_plug(self):
        selection = self.graph_viewer.selected_nodes()
        if len(selection) != 1:
            return
        fp_node = self.fp_nodes_map[selection[0].id]
        qt_node = self.qt_nodes_map[selection[0].id]
        editor = widgets.PlugEditor(
            self, fp_node=fp_node, qt_node=qt_node,
            plug_type=flowpipe.plug.OutputPlug, plug=None)
        if editor.exec_():
            self.node_selected(selection[0].id)

    def delete_nodes(self):
        for qt_node in QTGRAPH.selected_nodes():
            self.graph.delete_node(self.fp_nodes_map[qt_node.id])
        QTGRAPH.delete_nodes(QTGRAPH.selected_nodes())
        self.node_deselected()

    def inputs_right_clicked(self, attribute_widget):
        selection = self.graph_viewer.selected_nodes()
        if len(selection) != 1:
            return
        fp_node = self.fp_nodes_map[selection[0].id]

        menu = QtWidgets.QMenu(self.node_inputs_widget)

        if fp_node.__class__.__name__ == "PrototypeNode":
            add_action = QtWidgets.QAction(menu)
            add_action.setText("Add Input Plug")
            add_action.triggered.connect(self.add_input_plug)
            menu.addAction(add_action)

        menu.exec_(QtGui.QCursor.pos())

    def outputs_right_clicked(self, attribute_widget):
        selection = self.graph_viewer.selected_nodes()
        if len(selection) != 1:
            return
        fp_node = self.fp_nodes_map[selection[0].id]

        menu = QtWidgets.QMenu(self.node_inputs_widget)

        if fp_node.__class__.__name__ == "PrototypeNode":
            add_action = QtWidgets.QAction(menu)
            add_action.setText("Add Output Plug")
            add_action.triggered.connect(self.add_output_plug)
            menu.addAction(add_action)

        menu.exec_(QtGui.QCursor.pos())


if __name__ == "__main__":
    w = FlowEditor()
    w.show()
