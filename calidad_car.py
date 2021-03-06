# -*- coding: utf-8 -*-
"""Este módulo es el que articula toda la funcionalidad del plugin,
y esta compuesto por la clase CalidadCAR."""

from qgis.core import ( QGis,
                        QgsField,
                        QgsPoint,
                        QgsFeature,
                        QgsGeometry,
                        QgsVectorLayer,
                        QgsRasterLayer,
                        QgsMapLayerRegistry,
                        QgsCoordinateReferenceSystem,
                        QgsCoordinateReferenceSystem)

from PyQt4.QtCore import ( QVariant,
                           qVersion,
                           QSettings,
                           QFileInfo,
                           QTranslator,
                           QCoreApplication)

from PyQt4.QtGui import ( QIcon,
                          QColor,
                          QAction,
                          QMessageBox)


from src.actions import ( Modelling,
                          CSVAction,
                          LayerAction,
                          LayerNotFound,
                          DrawAxisAction,
                          ModellingAction,
                          AddSectionAction,
                          DrawPointsAction,
                          CreateInputFileAction,
                          ConcentrationPointsAction,
                          PreviousGeneratedLayerFound)

from dialogo_dibujar_vertices import (DrawDialog,
                                      NoSelectedOption, 
                                      NotLoadedPoints)
import time
import util
import copy
import os.path
import geometry
import resources
import numpy as np
import datetime as dtm

from dialogo_csv import CSVDialog
from src.modelling import calidad_car
from src import layer_manager as manager
from dialogo_variables import VarsDialog
from informacion import InformationDialog
from src.spreadsheets import Error, ErrorRow
from dialogo_parametros import SettingsDialog
from calidad_car_dialog import Ui_Dialog as CalidadCARDialog
from dialogo_arhivo_entrada import InputFileDialog, LoadInputFileDialog

class CalidadCAR:
    """Implementación del plugin."""

    def __init__(self, iface):
        """Constructor.

        :param iface: Una instancia de la interfaz que será pasada a esta clase,
            la cual proveé una ligadura con la cual se podrá manipular la aplicación
            de QGIS en tiempo de ejecución.
        :type iface: QgsInterface
        """
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CalidadCAR_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Calidad CAR')
        self.toolbar = self.iface.addToolBar(u'CalidadCAR')
        self.toolbar.setObjectName(u'CalidadCAR')

        self.inputFile = None
        self.layers = []
        self.dlg = CalidadCARDialog()
        # self.csvDialog = CSVDialog()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CalidadCAR', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Agrega una acción la la barra de herramientas, y al menú del plugin.

        :param icon_path: Ruta del icono. Puede ser la ruta de un recurso recurso
            (ejemplo: ':/plugins/foo/bar.png') o una ruta normal del sistema de archivos
        :type icon_path: str

        :param text: Texto que será mostrado en el menu de opciones de plugin para esta accion.
        :type text: str

        :param callback: Función que será llamada cuando se hace click sobre la acción.
        :type callback: function

        :param enabled_flag: Una bandera que indica si la acción debería ser activada
            por defecto. Por defecto este valor esta en True.
        :type enabled_flag: bool

        :param add_to_menu: Una bandera indicando si la acción debería ser agregada
            al menú de opciones del plugin. Por defecto esta en True
        :type add_to_menu: bool

        :param add_to_toolbar: Una bandera indicando si la acción debería ser agregada
            a la barra de herramientas del plugin. Por defecto esta en True
        :type add_to_toolbar: bool

        :param status_tip: Texto opcional que aparecerá cuando el puntero del mouse
            se pocisione sobre la acción.
        :type status_tip: str

        :param parent: Widget padre de la nueva acción. Por defecto será None
        :type parent: QWidget

        :param whats_this: Texto opcional para mostrar en la barra de estatus,
            cuando el puntero del mouse se pocisione sobre la acción.

        :returns: La acción que fue creada. Notar que la acción también es
            agregada a self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Crea las entradas del menu, y las acciones de la barra de herramientas
            dentro de la interfaz de QGIS"""

        icon_path = ':/plugins/CalidadCAR/icons/layers-icon.png'
        self.addLayersAction = self.add_action(
            icon_path,
            text=self.tr(u'Cargar fondos'),
            callback=self.cargarCapas,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/CalidadCAR/icons/csv-join.png'
        self.addCsvAction = self.add_action(
            icon_path,
            text=self.tr(u'Crear archivo de entrada'),
            callback=self.createInputFile,
            parent=self.iface.mainWindow())

        # icon_path = ':/plugins/CalidadCAR/icons/add-section.png'
        # self.addSectionAction = self.add_action(
        #     icon_path,
        #     text=self.tr(u'Agregar sección'),
        #     callback=self.addSection,
        #     parent=self.iface.mainWindow())

        # icon_path = ':/plugins/CalidadCAR/icons/concentration-icon.png'
        # self.intersctionAction = self.add_action(
        #     icon_path,
        #     text=self.tr(u'Agregar puntos de concentración'),
        #     callback=self.concentrationPoints,
        #     parent=self.iface.mainWindow())

        # icon_path = ':/plugins/CalidadCAR/icons/start-icon.png'
        icon_path = ':/plugins/CalidadCAR/icons/execute.png'
        self.intersctionAction = self.add_action(
            icon_path,
            text=self.tr(u'Calcular'),
            callback=self.modeling,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/CalidadCAR/icons/erase-icon.png'
        self.intersctionAction = self.add_action(
            icon_path,
            text=self.tr(u'Limpiar'),
            callback=self.clean,
            parent=self.iface.mainWindow())        

        icon_path = ':/plugins/CalidadCAR/icons/vars-icon.png'
        self.intersctionAction = self.add_action(
            icon_path,
            text=self.tr(u'Configurar Variables'),
            callback=self.conf_vars,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/CalidadCAR/icons/add_section.png'
        self.intersctionAction = self.add_action(
            icon_path,
            text=self.tr(u'Agregar vértices'),
            callback=self.generate_secciones,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/CalidadCAR/icons/add_axis.png'
        self.intersctionAction = self.add_action(
            icon_path,
            text=self.tr(u'Generar eje'),
            callback=self.generate_axis,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/CalidadCAR/icons/info.png'
        self.intersctionAction = self.add_action(
            icon_path,
            text=self.tr(u'Acerca de'),
            callback=self.info,
            parent=self.iface.mainWindow())

        # self.intersctionAction.setEnabled(False)
        # self.addCsvAction.setEnabled(False)

    def generate_secciones(self):
        action = DrawPointsAction()
        dialog = DrawDialog()
        err = None

        try:
            action.pre()
            r = dialog.exec_()

            # En caso de que el usuario cancelo
            if not r: return

            dialog.validate()
            coords = None
            option = dialog.getOption()

            if not option:
                coords = dialog.getCoords()

            # print option, coords
            action.pro()
            action.pos(coords)
            # Actualiza el canvas
            self.iface.mapCanvas().refreshAllLayers() 

        # except ValueError:
        #     err = u"Asegurate que las coordenadas están en el formato correcto."
        except NoSelectedOption:
            err = u"Tienes que seleccionar una opción."
        except NotLoadedPoints:
            err = u"No subiste ninguna coordenada."
        except LayerNotFound:
            err = u"No se encontró la capa hidrografia, asegurate de cargarla con la acción\
            de cargar fondos."
        except PreviousGeneratedLayerFound:
            # TODO: Fix this
            err = u"Ya existe una capa de secciones, por favor eliminala antes de continuar"
        finally:
            if err:
                util.errorDialog(self, u'Error', err)

    def generate_axis(self):
        action = DrawAxisAction()
        err = None

        try:
            action.pre()
            action.pro()
            action.pos()

            # Actualiza el canvas
            self.iface.mapCanvas().refreshAllLayers() 

        except LayerNotFound:
            err = u"No se encontró la capa hidrografia, asegurate de cargarla con la acción\
            de cargar fondos."
        except PreviousGeneratedLayerFound:
            # TODO: Fix this
            err = u"Ya existe una capa de eje, por favor eliminala antes de continuar."
        finally:
            if err:
                util.errorDialog(self, u'Error', err)

    def createInputFile(self):
        action = CreateInputFileAction()
        if not action.pre():
            util.errorDialog(
                self, 
                u'No se encontraron algunas de las capas necesarias para realizar esta operación.', 
                u'Asegurate de agregar la capa del eje, y la capa de secciones en el diálogo de Cargar Fondos.')
            return

        dialog = InputFileDialog()
        r = dialog.exec_()
        if not r: return

        time = dialog.getT()
        if time == "":
            util.errorDialog(
                self, 
                u'No se ingreso el tiempo.', 
                u'El proceso solo se puede realizar si se ingresa un valor para el tiempo.')
            return

        if int(time) <= 0:
            util.errorDialog(
                self, 
                u'El tiempo tiene que ser un valor entero', 
                u'Y su valor tienen que ser mayor a cero.')
            return            

        coords, dis = action.pro()
        path = dialog.getFilePath()
        wd = dialog.getWD()
        sl = dialog.getSL()

        if action.pos(path, dis, int(time), wd, sl, coords):
            self.inputFile = path
            util.infoDialog(
                self,
                u'CalidadCAR',
                u'El archivo de entrada se ha creado con exito.',
                u'Ya puedes abrirlo para ingresar la información necesaria.')

    def info(self):
        dialog = InformationDialog()
        dialog.exec_()

    def conf_vars(self):
        dialog = VarsDialog()
        r = dialog.exec_()
        if not r: return

        contaminantes = dialog.getContaminantes()
        dialog.guargarContaminantes(contaminantes)

    def clean(self):
        """Recarga el plugin, limpiando todas las capas cargadas, excepto, las
           capas de salida de información."""
        eje = manager.get_layer('ejes')
        fondo = manager.get_layer('fondo')
        hidro = manager.get_layer('hidrografia')
        secciones = manager.get_layer('secciones')
        manager.remove_layers([eje, fondo, hidro, secciones])

        csv_layers = manager.get_all_layers("csv")
        manager.remove_layers(csv_layers)

        tempLayer = manager.get_layer("temp")
        if tempLayer is not None:
            tempLayer.commitChanges()
            manager.remove_layers([tempLayer])

        self.addCsvAction.setEnabled(True)
        self.layers = []

    def addSection(self):
        """Utiliza una capa llamada temp, para insertar las nuevas secciones,
           esta operación solo podrá ser realizada si existe la capa de secciones.

           En caso de que no exista la capa temp, se creara una nueva, con el crs
           de la capa de secciones.
        """
        if self.addCsvAction.isEnabled():
            title = u'Agregar sección transversal'
            detail = u'Una vez creada la capa de secciones no podrás unir más archivos CSV a la tabla de atributos de la capa de secciones.\n\n¿Deseas crear la capa de secciones?'

            if not util.questionDialog(self, title, detail):
                return

        action = AddSectionAction()

        if not action.pre():
            util.errorDialog(self, u'No se encontró la capa de secciones.',
            u'Asegurate de agregarla en el diálogo de cargar fondos.')
            return

        action.pro()
        action.pos(self.iface, self.addCsvAction)

    def concentrationPoints(self):
        """Este método se encarga de recopilar toda la información, para permitirle al usuario ingresar los puntos de concentración.

           Para que el usuario pueda realizar esta operación, necesariamente, tienen que estar cargadas la capa de ejes, y la capa de secciones transversales.
        """

        action = ConcentrationPointsAction()

        if not action.pre():
            util.errorDialog(self, u'No se encontraron algunas de las capas necesarias para realizar esta operación.',
                    u'Asegurate de agregar la capa de secciones, y la capa del eje en el diálogo de Cargar Fondos.')
            return

        action.pro()
        action.pos(self.iface)

    def modeling(self):
        dialog = LoadInputFileDialog()
        r = dialog.exec_()

        if not r: return

        path = dialog.getFilePath()
        if path == "":
            util.errorDialog(
                self, 
                u'No se selecciono ningún archivo.', 
                u'El proceso solo se puede realizar cuando se cargué el archivo de entrada.')
            return

        output_path = dialog.getOutputPath()
        if output_path == "":
            util.errorDialog(
                self, 
                u'No se selecciono la carpeta de salida.', 
                u'Por favor selecciona la carpeta de salida.')
            return

        variables = VarsDialog.leerVariables()
        for k, v in variables.iteritems():
            variables[k] = float(v)

        action = Modelling()
        try:
            action.pre(path)
        except Error as e:
            util.errorDialog(
                self,
                u'Se encontró un valor que no es númerico',
                u'Hoja: %s\nCelda: [%d, %d]' % (e.name, e.r, e.c))
            return
        except ErrorRow as e:
            util.errorDialog(
                self,
                u'La hoja %s no puede contener el valor %d en la fila %d' % (e.name, e.v, e.r),
                u'')
            return


        print "Se inicio el proceso..."
        action.pro(output_path, variables, dialog.getShowPlots(), dialog.getSavePlots())

    def intersection(self):
        """Se encarga de aplicar el modelo matemático a la información para determinar la calidad del agua.
        """

        action = ConcentrationPointsAction()

        if not action.pre():
            util.errorDialog(self, u'No se encontraron algunas de las capas necesarias para realizar esta operación.',
                    u'Asegurate de agregar la capa de secciones, y la capa del eje en el diálogo de Cargar Fondos.')
            return

        action.pro()
        action.pos(self.iface)

        action = ModellingAction()

        if not action.pre():
            util.errorDialog(self, u'No se encontraron algunas de las capas necesarias para realizar esta operación.', u'Asegurate de agregar los puntos de concentración, y la capa del eje en el diálogo de Cargar Fondos.')
            return

        field_names = action.pro()

        #Desplegar diálogo
        dialog = SettingsDialog(field_names)
        r = dialog.exec_()

        if not r: return

        vel_name = dialog.getVelocidad()
        conc_name = dialog.getConcentracion()
        flag = dialog.getFlag()

        try:
            action.pos(vel_name, conc_name, flag)
        except (TypeError, ValueError):
            util.errorDialog(self, u'Uno de los valores en la columna de velocidad o puntos de concentración es nulo',
            u'Asegurate de que no hay valores nulos en la tabla.')
            return

    def addCsv(self):
        """Crea una capa a partir de un archivo CSV, y une la información que
           contiene esta, con la tabla de atributos de la capa de secciones,
           la cual tendrá que existir, para que se pueda realizar esta operación.
        """

        action = CSVAction()

        shp = action.pre()

        if shp is None:
            util.errorDialog(self, u'No se encontró la capa de secciones.',
            u'Asegurate de agregarla en el diálogo de Cargar fondos.')
            return

        field_names = action.pro()

        csvDialog = CSVDialog(field_names)
        result = csvDialog.exec_()

        if result and csvDialog.getLayer():

            action.pos( csvDialog.getLayer(),
                        csvDialog.getSelectedColumns(),
                        csvDialog.getJoinField(),
                        field_names,
                        csvDialog.getJoinFieldTarget())

    def unload(self):
        """Remueve el menú del plugin, y las acciones de la barra de herramientas
           de la interfaz de QGIS."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Calidad CAR'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def cargarCapas(self):
        """Función que se ejecuta cuando el usuario hace click en la acción de Cargar Fondos"""
        self.dlg.show()
        result = self.dlg.exec_()

        if result:
            action = LayerAction()
            action.pre()
            action.pro(self.dlg.getFilePaths())
            self.layers = action.pos()
