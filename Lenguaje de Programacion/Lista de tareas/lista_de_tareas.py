#!/bin/python3
import sys, json, os
from PyQt5.QtCore import (Qt, pyqtSlot)
from PyQt5.QtGui import (QPalette, QColor)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPlainTextEdit, QToolButton,
    QCheckBox, QScrollArea, QFrame, QHBoxLayout, QVBoxLayout)

style_sheet = """
QToolButton {
    padding: 0px;
    font-size: 15pt;
}

ComponenteTarea {
    border: 0px;
    border-bottom: 1px solid lightgray;
}
"""

ruta_archivo = "tareas.json"

def cambiar_color(widget, rol, color):
    paleta = widget.palette()
    paleta.setColor(QPalette.ColorGroup.Active, rol, color)
    paleta.setColor(QPalette.ColorGroup.Inactive, rol, color)
    widget.setPalette(paleta)

class VistaListaTareas(QWidget):

    class ComponenteTarea(QFrame):

        def __init__(self, parent, texto = ""):
            super().__init__(parent)

            self.disp_horiz = QHBoxLayout()
            self.marca_listo = QCheckBox()
            self.etiq_tarea = QLabel(texto)
            self.etiq_tarea.setTextFormat(Qt.TextFormat.PlainText)
            self.etiq_tarea.setMinimumWidth(100)
            self.etiq_tarea.setWordWrap(True)
            self.boton_editar = QToolButton()
            self.boton_editar.setText("✏")
            self.boton_eliminar = QToolButton()
            self.boton_eliminar.setText("✕")

            # ------------------------------v  aquí va el faltante
            for widget in (self.marca_listo, self.boton_editar, self.boton_eliminar):
                self.disp_horiz.addWidget(widget, 0, Qt.AlignmentFlag.AlignTop)
            self.disp_horiz.insertWidget(1, self.etiq_tarea, 1, Qt.AlignmentFlag.AlignTop)
            self.setLayout(self.disp_horiz)

            self.boton_editar.clicked.connect(self.establecer_edicion)
            self.marca_listo.toggled.connect(self.etiq_tarea.setDisabled)

        @property
        def texto(self):
            return self.etiq_tarea.text()

        @texto.setter
        def texto(self, texto):
            self.etiq_tarea.setText(texto)

        @property
        def listo(self):
            return self.marca_listo.isChecked()

        @listo.setter
        def listo(self, terminado):
            self.marca_listo.setChecked(terminado)

        @pyqtSlot()
        def establecer_edicion(self, editando=True):
            if editando:
                self.boton_editar.setEnabled(False)
            else:
                self.boton_editar.setEnabled(True)

        def a_dict(self):
            return {"listo": self.listo, "texto": self.texto}

    def __init__(self):
        super().__init__(None)
        self.setWindowTitle("Lista de Tareas")
        self.resize(400, 400)
        self.tarea_editada = None
        self.modificado = False

        self.panel_inferior = QWidget()
        self.despl_inferior = QScrollArea()
        self.disp_principal = QVBoxLayout(self)
        self.disp_superior = QHBoxLayout()
        self.disp_inferior = QVBoxLayout()

        self.disp_principal.addLayout(self.disp_superior)
        self.disp_principal.addWidget(self.despl_inferior)

        self.etiq_nueva_tarea = QLabel("Nueva tarea: ")
        self.areatexto_nueva_tarea = QPlainTextEdit()
        self.areatexto_nueva_tarea.setMaximumHeight(50)
        self.boton_nueva_tarea = QToolButton()
        self.boton_nueva_tarea.setText("+")
        self.disp_superior.addWidget(self.etiq_nueva_tarea, 0, Qt.AlignmentFlag.AlignTop)
        self.disp_superior.addWidget(self.areatexto_nueva_tarea, 1)
        self.disp_superior.addWidget(self.boton_nueva_tarea)

        self.lista_tareas = []
        self.disp_inferior.addStretch(1)
        self.panel_inferior.setLayout(self.disp_inferior)
        self.despl_inferior.setWidget(self.panel_inferior)
        self.despl_inferior.setWidgetResizable(True)
        self.despl_inferior.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.boton_nueva_tarea.clicked.connect(self.procesar_tarea)

        self.show()

    @pyqtSlot()
    def procesar_tarea(self):
        texto = self.areatexto_nueva_tarea.toPlainText()

        if self.tarea_editada is None:
            if texto == "":
                self.areatexto_nueva_tarea.setFocus(Qt.FocusReason.OtherFocusReason)
                return
            self.agregar_tarea(texto)
            self.areatexto_nueva_tarea.setPlainText("")
        else:
            if texto != "" and self.tarea_editada.texto != texto:
                self.tarea_editada.texto = texto
                self.modificado = True
            self.terminar_edicion_tarea()

    def agregar_tarea(self, texto, listo=False):
        nueva_tarea = self.ComponenteTarea(None, texto)
        if listo:
            nueva_tarea.listo = listo
        nueva_tarea.boton_eliminar.clicked.connect(self.eliminar_tarea)
        nueva_tarea.boton_editar.clicked.connect(self.editar_tarea)
        self.disp_inferior.insertWidget(self.disp_inferior.count() - 1, nueva_tarea)
        self.lista_tareas.append(nueva_tarea)
        self.modificado = True

    @pyqtSlot()
    def editar_tarea(self, tarea=None):
        if tarea is None:
            tarea = self.sender().parent()
        self.areatexto_nueva_tarea.setPlainText(tarea.texto)
        if self.tarea_editada is not None:
            self.tarea_editada.establecer_edicion(False)
        self.tarea_editada = tarea
        self.boton_nueva_tarea.setText("✓")

    def terminar_edicion_tarea(self):
        tarea, self.tarea_editada = self.tarea_editada, None
        tarea.establecer_edicion(False)
        self.boton_nueva_tarea.setText("+")
        self.areatexto_nueva_tarea.setPlainText("")

    @pyqtSlot()
    def eliminar_tarea(self, tarea=None):
        if tarea is None:
            tarea = self.sender().parent()
        if tarea is self.tarea_editada:
            self.terminar_edicion_tarea()
        self.disp_inferior.removeWidget(tarea)
        self.lista_tareas.remove(tarea)
        self.modificado = True
        tarea.deleteLater()

    def a_lista(self):
        return [tarea.a_dict() for tarea in self.lista_tareas]

    def cargar(self, ruta):
        with open(ruta, "r") as archivo:
            tareas = json.load(archivo)
        for tarea in self.lista_tareas:
            self.eliminar_tarea(tarea)
        for tarea in tareas:
            self.agregar_tarea(tarea["texto"], tarea["listo"])

        self.modificado = False

    def guardar(self, ruta):
        tareas = self.a_lista()
        with open(ruta, "w") as archivo:
            json.dump(tareas, archivo, indent="\t")

def main():
    app = QApplication([])
    app.setStyleSheet(style_sheet)
    ventana = VistaListaTareas()

    if os.path.isfile(ruta_archivo):
        try:
            ventana.cargar(ruta_archivo)
        except OSError, UnicodeDecodeError, json.JSONDecodeError:
            print("No se pudo cargar la lista de tareas correctamente")
    try:
        ret = app.exec()
    except:
        ret = 1
    finally:
        if ventana.modificado:
            ventana.guardar(ruta_archivo)

    return ret

if __name__ == "__main__":
    sys.exit(main())
