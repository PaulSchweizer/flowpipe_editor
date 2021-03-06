from PySide2 import QtCore, QtGui, QtWidgets

class Ui_PlugEditor(object):
    def setupUi(self, PlugEditor):
        PlugEditor.setObjectName("PlugEditor")
        self.verticalLayout = QtWidgets.QVBoxLayout(PlugEditor)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(PlugEditor)
        self.widget.setObjectName("widget")
        self.formLayout = QtWidgets.QFormLayout(self.widget)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.name_label = QtWidgets.QLabel(self.widget)
        self.name_label.setObjectName("name_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.name_label)
        self.name_lineedit = QtWidgets.QLineEdit(self.widget)
        self.name_lineedit.setObjectName("name_lineedit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.name_lineedit)
        self.type_label = QtWidgets.QLabel(self.widget)
        self.type_label.setObjectName("type_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.type_label)
        self.type_combobox = QtWidgets.QComboBox(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.type_combobox.sizePolicy().hasHeightForWidth())
        self.type_combobox.setSizePolicy(sizePolicy)
        self.type_combobox.setObjectName("type_combobox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.type_combobox)
        self.tooltip_label = QtWidgets.QLabel(self.widget)
        self.tooltip_label.setObjectName("tooltip_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.tooltip_label)
        self.tooltip_lineedit = QtWidgets.QLineEdit(self.widget)
        self.tooltip_lineedit.setObjectName("tooltip_lineedit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.tooltip_lineedit)
        self.editable_label = QtWidgets.QLabel(self.widget)
        self.editable_label.setObjectName("editable_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.editable_label)
        self.editable_checkbox = QtWidgets.QCheckBox(self.widget)
        self.editable_checkbox.setText("")
        self.editable_checkbox.setChecked(True)
        self.editable_checkbox.setObjectName("editable_checkbox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.editable_checkbox)
        self.verticalLayout.addWidget(self.widget)
        self.buttons_widget = QtWidgets.QWidget(PlugEditor)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttons_widget.sizePolicy().hasHeightForWidth())
        self.buttons_widget.setSizePolicy(sizePolicy)
        self.buttons_widget.setObjectName("buttons_widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.buttons_widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(179, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.ok_button = QtWidgets.QPushButton(self.buttons_widget)
        self.ok_button.setObjectName("ok_button")
        self.horizontalLayout.addWidget(self.ok_button)
        self.cancel_button = QtWidgets.QPushButton(self.buttons_widget)
        self.cancel_button.setObjectName("cancel_button")
        self.horizontalLayout.addWidget(self.cancel_button)
        self.verticalLayout.addWidget(self.buttons_widget)

        self.retranslateUi(PlugEditor)
        QtCore.QMetaObject.connectSlotsByName(PlugEditor)

    def retranslateUi(self, PlugEditor):
        PlugEditor.setWindowTitle(QtWidgets.QApplication.translate("PlugEditor", "Plug Editor", None, -1))
        self.name_label.setText(QtWidgets.QApplication.translate("PlugEditor", "Name", None, -1))
        self.type_label.setText(QtWidgets.QApplication.translate("PlugEditor", "Type", None, -1))
        self.tooltip_label.setText(QtWidgets.QApplication.translate("PlugEditor", "Tooltip", None, -1))
        self.editable_label.setText(QtWidgets.QApplication.translate("PlugEditor", "Editable", None, -1))
        self.ok_button.setText(QtWidgets.QApplication.translate("PlugEditor", "Ok", None, -1))
        self.cancel_button.setText(QtWidgets.QApplication.translate("PlugEditor", "Cancel", None, -1))

