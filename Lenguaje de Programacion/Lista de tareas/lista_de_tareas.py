#!/bin/python3
import sys, json, os, time, datetime
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

id_tarea_max = 0

def ahora():
    return int(time.time())

def cambiar_color(widget, rol, color):
    paleta = widget.palette()
    paleta.setColor(QPalette.ColorGroup.Active, rol, color)
    paleta.setColor(QPalette.ColorGroup.Inactive, rol, color)
    widget.setPalette(paleta)

class VistaListaTareas(QWidget):

    class ComponenteTarea(QFrame):

        CORRESPONDENCIA_DICT = [ ("id", "id"),
                                 ("description", "texto"),
                                 ("status", "estado"),
                                 ("createdAt", "creadoEn"),
                                 ("updatedAt", "actualizadoEn") ]


        def __init__(self, parent, texto = ""):
            super().__init__(parent)
            global id_tarea_max
            id_tarea_max += 1
            self.id = id_tarea_max
            self.creadoEn = self.actualizadoEn = ahora()

            self.disp_horiz = QHBoxLayout()
            self.marca_estado = QCheckBox()
            self.marca_estado.setTristate()
            self.etiq_tarea = QLabel(texto)
            self.etiq_tarea.setTextFormat(Qt.TextFormat.PlainText)
            self.etiq_tarea.setMinimumWidth(100)
            self.etiq_tarea.setWordWrap(True)
            self.boton_editar = QToolButton()
            self.boton_editar.setText("✏")
            self.boton_editar.setToolTip("Editar")
            self.boton_eliminar = QToolButton()
            self.boton_eliminar.setText("✕")
            self.boton_eliminar.setToolTip("Eliminar")

            # ------------------------------v  aquí va el faltante
            for widget in (self.marca_estado, self.boton_editar, self.boton_eliminar):
                self.disp_horiz.addWidget(widget, 0, Qt.AlignmentFlag.AlignTop)
            self.disp_horiz.insertWidget(1, self.etiq_tarea, 1, Qt.AlignmentFlag.AlignTop)
            self.setLayout(self.disp_horiz)

            self.boton_editar.clicked.connect(self.establecer_edicion)
            self.marca_estado.stateChanged.connect(
                lambda estado: self.etiq_tarea.setDisabled(estado == Qt.Checked) )

        @property
        def texto(self):
            return self.etiq_tarea.text()

        @texto.setter
        def texto(self, texto):
            self.actualizadoEn = ahora()
            self.etiq_tarea.setText(texto)

        @property
        def estado(self):
            return self.marca_estado.checkState()

        @estado.setter
        def estado(self, nuevo_estado):
            self.actualizadoEn = ahora()
            self.marca_estado.setCheckState(nuevo_estado)

        @pyqtSlot()
        def establecer_edicion(self, editando=True):
            if editando:
                self.boton_editar.setEnabled(False)
            else:
                self.boton_editar.setEnabled(True)

        def a_dict(self):
            return { "id": self.id, "description": self.texto, "status": self.estado,
                     "createdAt": self.creadoEn, "updatedAt": self.actualizadoEn }

        @classmethod
        def desde_dict(cls, fuente):
            global id_tarea_max
            tarea = cls(None)
            for clave, atributo in cls.CORRESPONDENCIA_DICT:
                if clave in fuente:
                    setattr(tarea, atributo, fuente[clave])
            if tarea.id > id_tarea_max:
                id_tarea_max = tarea.id
            return tarea

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
        self.boton_nueva_tarea.setToolTip("Añadir")
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

    def agregar_tarea(self, texto_o_dict):
        if isinstance(texto_o_dict, dict):
            nueva_tarea = self.ComponenteTarea.desde_dict(texto_o_dict)
        else:
            nueva_tarea = self.ComponenteTarea(None, texto_o_dict)
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
            self.agregar_tarea(tarea)

        self.modificado = False

    def guardar(self, ruta):
        tareas = self.a_lista()
        with open(ruta, "w") as archivo:
            json.dump(tareas, archivo, indent="\t")

        self.modificado = False

def carga_inicial(gestor):
    if os.path.isfile(ruta_archivo):
        try:
            gestor.cargar(ruta_archivo)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            print("No se pudo cargar la lista de tareas correctamente")
        except TypeError as e:
            print("El archivo '%s' de la lista de tareas está defectuoso." % ruta_archivo,
                  "Debe corregirlo o eliminarlo para continuar", sep="\n")
            return 1

    return 0

def main_gui():
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    ventana = VistaListaTareas()

    ret = carga_inicial(ventana)
    if ret:
        return ret
    try:
        ret = app.exec()
    except:
        ret = 1
    finally:
        if ventana.modificado:
            ventana.guardar(ruta_archivo)

    return ret

class GestorTareas:

    MSG_NO_ID = "No hay una tarea con ID '%d'"
    TABLA_ESTADOS = { Qt.Unchecked: "pendiente",
                      Qt.PartiallyChecked: "en-progreso",
                      Qt.Checked: "terminado" }

    def __init__(self):
        self.lista_tareas = []
        self.modificado = False

    def enumerar_tareas(self, estado_buscado=None):
        for tarea in self.lista_tareas:
            estado = tarea["status"]
            if estado_buscado is not None and estado != estado_buscado:
                continue
            estado = self.TABLA_ESTADOS[estado]
            creadoEn, actualizadoEn = map(
                lambda hora: datetime.datetime.fromtimestamp(hora),
                (tarea["createdAt"], tarea["updatedAt"]) )
            creadoEn = creadoEn.isoformat(" ", "seconds")
            actualizadoEn = actualizadoEn.isoformat(" ", "seconds")
            yield ("{id:3} [{estado}] {description}\n"
                   "\tCreada el {creadoEn}  Actualizada el {actualizadoEn}").format(
                       **tarea, estado=estado, creadoEn=creadoEn, actualizadoEn=actualizadoEn)

    def buscar_tarea_por_id(self, id_tarea):
        for indice, tarea in enumerate(self.lista_tareas):
            if tarea["id"] == id_tarea:
                return indice, tarea
        raise KeyError(self.MSG_NO_ID % id_tarea)

    def agregar_tarea(self, texto):
        global id_tarea_max
        id_tarea_max += 1
        hora = ahora()
        self.lista_tareas.append(
            { "id": id_tarea_max, "description": texto, "status": Qt.Unchecked,
              "createdAt": hora, "updatedAt": hora } )
        self.modificado = True

    def editar_tarea(self, id_tarea, texto):
        tarea = self.buscar_tarea_por_id(id_tarea)[1]
        tarea["description"] = texto
        tarea["updatedAt"] = ahora()
        self.modificado = True

    def eliminar_tarea(self, id_tarea):
        indice, tarea = self.buscar_tarea_por_id(id_tarea)
        del self.lista_tareas[indice]
        self.modificado = True

    def marcar_tarea(self, id_tarea, estado):
        if estado not in self.TABLA_ESTADOS:
            raise ValueError("Estado de tarea inválido")

        tarea = self.buscar_tarea_por_id(id_tarea)[1]
        tarea["status"] = estado
        tarea["updatedAt"] = ahora()
        self.modificado = True

    def cargar(self, ruta):
        with open(ruta, "r") as archivo:
            self.lista_tareas = json.load(archivo)

        for tarea in self.lista_tareas:
            if not isinstance(tarea, dict) \
              or set(tarea) != {"id", "description", "status", "createdAt", "updatedAt"}:
                self.lista_tareas = []
                raise TypeError("El archivo '%s' de la lista de tareas está defectuoso." % ruta)

        global id_tarea_max
        id_tarea_max = max(tarea["id"] for tarea in self.lista_tareas)
        self.modificado = False

    def guardar(self, ruta):
        with open(ruta, "w") as archivo:
            json.dump(self.lista_tareas, archivo, indent="\t")

        self.modificado = False

class TareasCli:

    TABLA_ESTADOS = {}
    MSG_MUCHOS_ARG = "El comando '{comando}' tiene solo {numero} argumento(s){opcional}"
    MSG_ID_NO_ENTERO = "El ID de tarea no es un número: "

    @classmethod
    def inicializar_clase(cls):
        for codigo, nombre in GestorTareas.TABLA_ESTADOS.items():
            cls.TABLA_ESTADOS[nombre] = codigo

    def __init__(self):
        self.gestor = GestorTareas()
        if carga_inicial(self.gestor) > 0:
            raise TypeError()

        self.comandos = { "enumerar": self.enumerar,
                          "agregar": self.agregar,
                          "editar": self.editar,
                          "marcar-pendiente": self.marcar,
                          "marcar-en-progreso": self.marcar,
                          "marcar-terminado": self.marcar,
                          "eliminar": self.eliminar }

    def inicio(self):
        if sys.argv[1] == "cli":
            if len(sys.argv) > 2:
                print("El comando 'cli' no lleva argumentos", file=sys.stderr)
                raise ValueError()
            self.consola()
        else:
            self.consola(una_vez=True)

    def consola(self, una_vez=False):
        if una_vez:
            linea_comando = sys.argv[1:]
            self._consola_aux(linea_comando)
        else:
            print("Nota: en este modo no se requieren comillas"
                  " para el texto de las tareas")

            linea_comando = input(">> ")
            while linea_comando != "salir":
                if linea_comando.startswith("agregar "):
                    limite = 1
                elif linea_comando.startswith("editar "):
                    limite = 2
                else:
                    limite = -1

                linea_comando = linea_comando.split(None, limite)
                self._consola_aux(linea_comando)
                linea_comando = input(">> ")

    def _consola_aux(self, linea_comando):
        if linea_comando[0] in ("ayuda", "help", "--help", "-h", "-?"):
            if len(linea_comando) > 1:
                print("El comando 'ayuda' no lleva argumentos", file=sys.stderr)
                raise ValueError()
            else:
                print("Comandos disponibles:",
                      *("\t" + comando for comando in self.comandos),
                      "\tayuda",
                      "\tsalir (solo disponible en el modo consola)",
                      "\tcli (consola, solo disponible fuera del modo consola)",
                      sep="\n")
            return

        try:
            comando = self.comandos[linea_comando[0]]
        except KeyError:
            print("El comando '%s' no existe" % linea_comando[0], file=sys.stderr)
            return
        try:
            if linea_comando[0].startswith("marcar-"):
                comando(linea_comando)
            else:
                comando(linea_comando[1:])
        except (KeyError, ValueError) as e:
            mensaje = e.args[0] if len(e.args) > 0 else ""
            if len(mensaje) > 0:
                print(mensaje, file=sys.stderr)
            raise

    def enumerar(self, linea_comando):
        if len(linea_comando) > 1:
            print(self.MSG_MUCHOS_ARG.format(comando="enumerar", numero="un", opcional=" opcional"),
                  file=sys.stderr)
            raise ValueError()
        elif len(linea_comando) == 1:
            estado = linea_comando[0]
            if estado not in self.TABLA_ESTADOS:
                print("'%s' no es un estado válido" % estado, file=sys.stderr)
                raise ValueError()
            estado = self.TABLA_ESTADOS[estado]
        else:
            estado = None

        for salida in self.gestor.enumerar_tareas(estado):
            print(salida, end="\n\n")

    def agregar(self, linea_comando):
        if len(linea_comando) != 1:
            print(self.MSG_MUCHOS_ARG.format(comando="agregar", numero="un", opcional=""),
                  file=sys.stderr)
            raise ValueError()

        texto = linea_comando[0]
        self.gestor.agregar_tarea(texto)

    def _obtener_id_tarea(self, linea_comando):
        try:
            id_tarea = int(linea_comando[0])
        except ValueError:
            print(self.MSG_ID_NO_ENTERO + linea_comando[0],
                  file=sys.stderr)
            raise ValueError()
        return id_tarea

    def editar(self, linea_comando):
        if len(linea_comando) != 2:
            print(self.MSG_MUCHOS_ARG.format(comando="editar", numero="dos", opcional=""),
                  file=sys.stderr)
            raise ValueError()

        id_tarea = self._obtener_id_tarea(linea_comando)
        texto = linea_comando[1]
        self.gestor.editar_tarea(id_tarea, texto)

    def eliminar(self, linea_comando):
        if len(linea_comando) != 1:
            print(self.MSG_MUCHOS_ARG.format(comando="eliminar", numero="un", opcional=""),
                  file=sys.stderr)
            raise ValueError()

        id_tarea = self._obtener_id_tarea(linea_comando)
        self.gestor.eliminar_tarea(id_tarea)

    def marcar(self, linea_comando):
        # marcar recibe el nombre de comando como argumento extra
        if len(linea_comando) != 2:
            print(self.MSG_MUCHOS_ARG.format(comando=linea_comando[0], numero="un", opcional=""),
                  file=sys.stderr)
            raise ValueError()
        comando = linea_comando[0]
        if not comando.startswith("marcar-"):
            raise ValueError("", "Nombre de comando inválido: " + comando)

        estado = comando[7:]
        if estado not in self.TABLA_ESTADOS:
            print("'%s' no es un estado válido" % estado, file=sys.stderr)
            raise ValueError()

        estado = self.TABLA_ESTADOS[estado]
        id_tarea = self._obtener_id_tarea(linea_comando[1:])
        self.gestor.marcar_tarea(id_tarea, estado)

TareasCli.inicializar_clase()

def main_cli():
    try:
        cli = TareasCli()
    except TypeError:
        return 1

    ret = 0
    try:
        cli.inicio()
    except (KeyError, TypeError, ValueError):
        #raise
        ret = 1
    except KeyboardInterrupt:
        ret = 2
    finally:
        if cli.gestor.modificado and ret != 2:
            cli.gestor.guardar(ruta_archivo)

    return 0

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit(main_gui())
    else:
        sys.exit(main_cli())
