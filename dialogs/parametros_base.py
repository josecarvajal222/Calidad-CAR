# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/dialogo_parametros_base.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(460, 417)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 370, 421, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 40, 421, 69))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.comboVelocidad = QtWidgets.QComboBox(self.layoutWidget)
        self.comboVelocidad.setObjectName("comboVelocidad")
        self.verticalLayout.addWidget(self.comboVelocidad)
        self.layoutWidget1 = QtWidgets.QWidget(Dialog)
        self.layoutWidget1.setGeometry(QtCore.QRect(20, 140, 421, 69))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.comboConcentracion = QtWidgets.QComboBox(self.layoutWidget1)
        self.comboConcentracion.setObjectName("comboConcentracion")
        self.verticalLayout_2.addWidget(self.comboConcentracion)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(20, 220, 421, 141))
        self.groupBox.setObjectName("groupBox")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(10, 30, 401, 20))
        self.label_3.setObjectName("label_3")
        self.radioButtonTime = QtWidgets.QRadioButton(self.groupBox)
        self.radioButtonTime.setGeometry(QtCore.QRect(20, 60, 201, 26))
        self.radioButtonTime.setObjectName("radioButtonTime")
        self.radioButtonDist = QtWidgets.QRadioButton(self.groupBox)
        self.radioButtonDist.setGeometry(QtCore.QRect(20, 90, 201, 26))
        self.radioButtonDist.setObjectName("radioButtonDist")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Configurar parámetros"))
        self.label.setText(_translate("Dialog", "Selecciona la columna en la que se encuentra la información de la velocidad:"))
        self.label_2.setText(_translate("Dialog", "Selecciona la columna en la que se encuentra la información de los puntos de concentración:"))
        self.groupBox.setTitle(_translate("Dialog", "Salida"))
        self.label_3.setText(_translate("Dialog", "Selecciona la gráfica de concentración de que deseas ver:"))
        self.radioButtonTime.setText(_translate("Dialog", "Concentración / Tiempo"))
        self.radioButtonDist.setText(_translate("Dialog", "Concentración / Distancia"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

