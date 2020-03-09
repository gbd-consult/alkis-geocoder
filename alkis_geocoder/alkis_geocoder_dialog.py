# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GWSAlkisGeocoderDialog
                                 A QGIS plugin
 Adress Geocoding using GBD WebSuite and ALKIS database
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-06-26
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Geoinformatikbüro Dassau GmbH
        email                : info@gbd-consult.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.utils import iface
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QSettings, QVariant, Qt, QCoreApplication
from qgis.core import QgsDataSourceUri, QgsField, QgsProject, QgsVectorLayer, QgsGeometry, QgsPointXY
import requests as r

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'alkis_geocoder_dialog_base.ui'))


class AlkisGeocoderDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(AlkisGeocoderDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # Populate hostname
        if os.path.isfile(os.path.join(os.path.dirname(__file__), 'hostname')):
            with open(os.path.join(os.path.dirname(__file__), 'hostname')) as f:
                self.hostnameLineEdit.insert(f.read())

        # Populate help window
        with open(os.path.join(os.path.dirname(__file__), 'help.html')) as html:
            self.textBrowser.setHtml(html.read())

        # Only show delimitedtext layers
        self.setLayerExceptions()

        self.onLayerChange(self.tableLayer.currentLayer())
        self.tableLayer.layerChanged.connect(self.onLayerChange)


        self.generateLayerButton.clicked.connect(self.generateLayer)

        self.generateLayerButton.setEnabled(False)

        if not self.tableLayer.currentLayer():
            self.attributeBox.setEnabled(False)


        QgsProject.instance().layerWasAdded.connect(lambda x: self.setLayerExceptions())
        QgsProject.instance().layerRemoved.connect(lambda x:self.setLayerExceptions())

        self.hostnameLineEdit.textEdited.connect(lambda x: self.checkInputFields())
        self.passwordLineEdit.textEdited.connect(lambda x: self.checkInputFields())
        self.userLineEdit.textEdited.connect(lambda x: self.checkInputFields())
        self.hausnummerField.fieldChanged.connect(lambda x: self.checkInputFields())
        self.strasseField.fieldChanged.connect(lambda x: self.checkInputFields())
        self.gemarkungField.fieldChanged.connect(lambda x: self.checkInputFields())


    def setLayerExceptions(self):
        """ only show delimeted text layers in the layer selector. """
        excepted = []
        for layer in QgsProject.instance().mapLayers().values():
            if hasattr(layer, 'providerType') and layer.providerType() not in ('delimitedtext', 'ogr'):
                excepted.append(layer)
            elif layer.geometryType() != 4:
                excepted.append(layer)
        self.tableLayer.setExceptedLayerList(excepted) 

    
    def checkInputFields(self):
        """ Checks all required input fields of the form. """
        if not (self.hostnameLineEdit.text() and self.userLineEdit.text() \
                and self.passwordLineEdit.text() and self.tableLayer.currentLayer() \
                and self.strasseField.currentField() and self.gemarkungField.currentField() \
                and self.hausnummerField.currentField()):
            self.generateLayerButton.setEnabled(False)
        else:
            self.generateLayerButton.setEnabled(True)


            
    def onLayerChange(self,layer):
        """ gets run, when the active layer of the QgsMapLayerCombobox changes."""
        if self.tableLayer.currentLayer():
            self.generateLayerButton.setEnabled(True)
            self.attributeBox.setEnabled(True)

        self.strasseField.setLayer(layer)
        self.hausnummerField.setLayer(layer)
        self.gemarkungField.setLayer(layer)

        self.checkInputFields()



    def generateLayer(self):
        """ The main function, that does all the geocoding work. """

        # disable the Button while generating
        self.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QCoreApplication.processEvents()

        try:
            hostname = self.hostnameLineEdit.text()
            # FIXME: We need a better test for connectivity.
            with open(os.path.join(os.path.dirname(__file__), 'hostname'), 'w') as f:
                f.write(hostname)
            # try to authenticate with GWS
            username = self.userLineEdit.text()
            password = self.passwordLineEdit.text()
            response = r.post(hostname, json={
                'cmd': 'authLogin',
                'params': {
                    'username': username,
                    'password': password
                }
            })
            if response.status_code != 200:
                iface.messageBar().pushCritical('Authentifizierung fehlgeschlagen', 'Falsche Logindaten!')
                self.setEnabled(True)
                QApplication.restoreOverrideCursor()
                return False
        except:
            self.setEnabled(True)
            QApplication.restoreOverrideCursor()
            iface.messageBar().pushCritical('GWS Fehler!', 'Konnte keine Verbindung zum Server herstellen.')
            return False

        # create new memory layer
        layer = self.tableLayer.currentLayer()
        features = [f for f in layer.getFeatures()]
        mem_layer = QgsVectorLayer('Point?crs=epsg:25832', '%s_geocoded' % layer.name(), 'memory')
        mem_layer_data = mem_layer.dataProvider()
        attr = layer.dataProvider().fields().toList()
        mem_layer_data.addAttributes(attr + [QgsField('lat', QVariant.Double), QgsField('lon', QVariant.Double)])
        mem_layer.updateFields()
        mem_layer_data.addFeatures(features)
        mem_layer.startEditing()

        addr_list = []
        fid_list = []
        for feature in mem_layer.getFeatures():
            gemarkung = feature[self.gemarkungField.currentField()]
            strasse = feature[self.strasseField.currentField()]
            hausnummer = feature[self.hausnummerField.currentField()]
            if gemarkung and strasse and hausnummer:
                addr_list.append({ 
                    'gemarkung' : gemarkung,
                    'strasse' : strasse,
                    'hausnummer' : str(hausnummer)
                })
                fid_list.append(feature.id())
                addr_list.append({
                    'gemeinde' : gemarkung,
                    'strasse' : strasse,
                    'hausnummer' : str(hausnummer)

                })
                fid_list.append(feature.id())

        response = r.post(hostname, json={
            "cmd": "alkisgeocoderDecode",
            "params": {
                "crs": "EPSG:25832",
                "adressen": addr_list
            }
        })
        coordinates = response.json().get('coordinates')
        if not coordinates:
            iface.messageBar().pushCritical('GWS Fehler!', 'GWS unterstützt kein AlkisGeocoder!')
            self.setEnabled(True)
            QApplication.restoreOverrideCursor()
            return False

        for (fid,coords) in zip(fid_list, coordinates):
            if coords:
                feature = mem_layer.getFeature(fid)
                x = coords[0]
                y = coords[1]
                feature.setAttribute('lat', x)
                feature.setAttribute('lon', y)
                geom = QgsPointXY(x, y)
                feature.setGeometry(QgsGeometry.fromPointXY(geom))
                mem_layer.updateFeature(feature)

        geom_features = len(list(filter(lambda x: x.hasGeometry(),[f for f in mem_layer.getFeatures()])))
        if geom_features > 0:
            iface.messageBar().pushSuccess('Geocodierung abgeschlossen', '%s von %s Features konnten geocodiert werden' % (geom_features, layer.featureCount()))
            mem_layer.commitChanges()
            QgsProject.instance().addMapLayer(mem_layer)
        else:
            del(mem_layer)
            iface.messageBar().pushCritical('Geocodierung fehlgeschlagen', 'Es konnten keine Features geocodiert werden.')


        self.setEnabled(True)
        QApplication.restoreOverrideCursor()
