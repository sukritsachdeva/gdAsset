# Copyright (c) 2012 The Foundry Visionmongers Ltd. All Rights Reserved.

from Katana import (QtCore, QtGui, QtWidgets, QT4FormWidgets, UI4, AssetAPI,
                    logging)
from UI4.Util import AssetWidgetDelegatePlugins
import os
import tempfile
import ConfigurationAPI_cmodule as Configuration

# Module Variables

# Set up a Katana logger
log = logging.getLogger("GDAssetWidgetDelegate")
#///////////////////////////////////////////////////////////////////////////////

def _logDebug(message):
    """
    Logs additional information for debug purposes.

    This can be turned on by setting the GD_DEBUG environment variable.
    """
    if os.environ.get("GD_DEBUG", False):
        log.info(message)


def _getBaseDir():
    """
    Returns the default root directory of the Google Drive asset database from the
    "GD_ASSET_DIR" environment variable. if left unimplemented, sets to "G:\Shared drives\Assets"
    """
    return os.environ.get("GD_ASSET_DIR", "G:\Shared drives\Assets")


def _listDirs(dir):
    """Returns an ordered list of directories inside a given folder"""
    dirs = []
    if not os.path.exists(dir):
        log.warning('Database directory not found: "%s"' % dir)
        return dirs
    
    children = os.listdir(dir)
    for child in children:
        path = os.path.join(dir, child)
        if os.path.isdir(path):
            dirs.append(child)

    return sorted(dirs)

def _listFiles(dir):
    """Returns an ordered list of files inside a given folder"""
    files = []
    if not os.path.exists(dir):
        log.warning('Database directory not found: "%s"' % dir)
        return files
    
    children = os.listdir(dir)
    for child in children:
        path = os.path.join(dir, child)
        if os.path.isfile(path):
            files.append(child)

    return sorted(files)


def _getShows():
    """Return a list of shows in the Google Drive database"""
    return _listDirs(_getBaseDir())


def _getShots(show=None):
    """Return a list of shots in the GD asset database"""
    if not show:
        return []
    showPath = os.path.join(_getBaseDir(), show)
    return _listDirs(showPath)


def _getAssets(show=None, shot=None):
    """Return a list of asset names in the GD asset database"""
    if not show or not shot:
        return []
    shotPath = os.path.join(_getBaseDir(), show, shot)
    return _listDirs(shotPath)


def _getVersions(show=None, shot=None, asset=None):                 ## This will need to be changed to '_getTasks'
    """Return a list of versions in the GD asset database"""
    if not show or not shot or not asset:
        return []
    assetPath = os.path.join(_getBaseDir(), show, shot, asset)
    return _listDirs(assetPath)

def _getVersions_(show=None, shot=None, asset=None):                 ## Testing this method for the combobox dialog
    """Return a list of versions in the GD asset database"""
    if not show or not shot or not asset:
        return []
    if shot == "Assets":
        assetPath = os.path.join(_getBaseDir(), show, shot, asset, "Lookdev")
        vers = []
        for file in _listFiles(assetPath):
            vers.append(file.split("_")[-1].split(".")[0])
    else:
        assetPath = os.path.join(_getBaseDir(), show, shot, asset, "Lighting")
        vers = []
        for file in _listFiles(assetPath):
            vers.append(file.split("_")[-1].split(".")[0])
    return vers

def _getFiles(show=None, shot=None, asset=None, version=None):          ## This method's a bit confusing, it returns dirs and files both, so creating a new one that returns ONLY files, below.
    """Return a list of files in the GD asset database"""
    if not show or not shot or not asset or not version:
        return []
    assetPath = os.path.join(_getBaseDir(), show, shot, asset, version)
    return _listDirs(assetPath)

def _getOnlyFiles(show=None, shot=None, asset=None, version=None):
    """Return a list of files in the GD asset database"""
    if not show or not shot or not asset or not version:
        return []
    assetPath = os.path.join(_getBaseDir(), show, shot, asset, version)
    return _listFiles(assetPath)


#///////////////////////////////////////////////////////////////////////////////

class GDAssetControlWidget(AssetWidgetDelegatePlugins.BaseAssetControlWidget):
    """
    The asset control widget takes control of the display of any string
    parameters that have an asset id 'hint'.
    """

    def buildWidgets(self, hints):
        """Creates most of the UI widgets"""
        label = QtWidgets.QLabel("Google://", self)
        label.setProperty('smallFont', True)
        label.setProperty('boldFont', True)
        p = label.palette()
        p.setColor(QtGui.QPalette.WindowText, QtGui.QColor(200, 50, 100))
        p.setColor(QtGui.QPalette.Text, QtGui.QColor(200, 50, 100))
        label.setPalette(p)
        self.layout().addWidget(label)

        ##self.layout().addWidget(QtWidgets.QLabel("Google://"))
        self.__showEdit = QT4FormWidgets.InputWidgets.InputLineEdit(self)
        self.layout().addWidget(self.__showEdit)

        self.layout().addWidget(QtWidgets.QLabel("/"))
        self.__shotEdit = QT4FormWidgets.InputWidgets.InputLineEdit(self)
        self.layout().addWidget(self.__shotEdit)

        self.layout().addWidget(QtWidgets.QLabel("/"))
        self.__assetEdit = QT4FormWidgets.InputWidgets.InputLineEdit(self)
        self.layout().addWidget(self.__assetEdit)

        # self.layout().addWidget(QtWidgets.QLabel("/"))
        # self.__versionEdit = QT4FormWidgets.InputWidgets.InputLineEdit(self)                      ## disabling the input line to add a dropdown instead
        # self.layout().addWidget(self.__versionEdit)

        self.layout().addWidget(QtWidgets.QLabel("/"))
        self.__versionDropdown = QtWidgets.QComboBox(self)
        self.__versionDropdown.currentIndexChanged[str].connect(self.__versionChanged)
        self.layout().addWidget(self.__versionDropdown)                                             ##            

        self.__showEdit.lostFocus.connect(self.__lostFocus)
        self.__shotEdit.lostFocus.connect(self.__lostFocus)
        self.__assetEdit.lostFocus.connect(self.__lostFocus)
        ##self.__versionDropdown.currentIndexChanged.connect(self._setVersions)

    def __versionChanged(self, newVersion):
        """Triggered when the version dropdown is changed"""
        
        
        show = str(self.__showEdit.text())
        shot = str(self.__shotEdit.text())
        asset = str(self.__assetEdit.text())
        self.version = str(newVersion)
        file_name = _getOnlyFiles(show, shot="Assets", asset=shot, version=asset)[-1]
        if self.version == "":
            #pass
            assetFields = {"project" : show,
                       "entity" : shot,
                       "entity_type" : "Assets",            #hardcoded, need to be addressed
                       "pipe_step" : asset,
                       "name" : file_name}
        else:
            assetFields = {"project" : show,
                        "entity" : shot,
                        "entity_type" : "Assets",            #hardcoded, need to be addressed
                        "pipe_step" : asset,
                        "name" : file_name,
                        AssetAPI.kAssetFieldVersion : self.version}
        assetPlugin = AssetAPI.GetDefaultAssetPlugin()

        self.assetId = assetPlugin.buildAssetId(assetFields)

    def __lostFocus(self):
        """Triggered when the browser loses focus"""
        self.emitValueChanged()

    def setPalette(self, palette):
        self.__showEdit.setPalette(palette)
        self.__shotEdit.setPalette(palette)
        self.__assetEdit.setPalette(palette)
        self.__versionDropdown.setPalette(palette)

    def setReadOnly(self, readOnly):
        self.__showEdit.setEnabled(readOnly)
        self.__shotEdit.setEnabled(readOnly)
        self.__assetEdit.setEnabled(readOnly)
        self.__versionDropdown.setEnabled(not readOnly)

    def setValue(self, value):

        """Given an asset id. Set the Show, Shot, Asset and version in the UI."""

        assetPlugin = AssetAPI.GetDefaultAssetPlugin()
        if not assetPlugin.isAssetId(value):
            return

        assetFields = assetPlugin.getAssetFields(value, True)
        self.__showEdit.setText(assetFields["project"])
        self.__shotEdit.setText(assetFields["entity"])
        self.__assetEdit.setText(assetFields["pipe_step"])
        self._setVersions(value)

    def _setVersions(self, value):
        """
        Sets/Resets the versions
        """
        versions = []
        current_version = value.split("\\")[-1].split("_")[-1].split(".")[0]
        for file in _listFiles(os.path.dirname(value)):
            versions.append(file.split("_")[-1].split(".")[0])
        self.__versionDropdown.blockSignals(True)
        self.__versionDropdown.clear()
        self.__versionDropdown.addItems(versions)
        self.__versionDropdown.setCurrentText(current_version)
        self.__versionDropdown.blockSignals(False)                      # evaluate if another signal needs to be emitted

    # def _onVersionChange(self, new_version):
    #     """
    #     Triggers assetID update and file reload of the new selected version
    #     """
    #     print("VERSION CHANGED!", new_version)

    #     new_asset_id = self.getValue()



    def getValue(self):
        """Get the asset ID from this browser window"""

        # show = str(self.__showEdit.text())
        # shot = str(self.__shotEdit.text())
        # asset = str(self.__assetEdit.text())
        # version = str(self.__versionDropdown.currentText())

        # print "*m" * 10
        # print "I CAPTURE THIS VERSION FROM UI>>>>>>>>", version
        # print "*m" * 10
        # file_name = _getOnlyFiles(show, shot="Assets", asset=shot, version=asset)[-1]

        # if version == "":
        #     version = (file_name.split('.')[0]).split("_")[-1]
        # print "^^^^^^^^^^\n" * 10
        # print "THIS IS THE VERSION at getValue()", version
        # print "^^^^^^^^^^\n" * 10

        # assetFields = {"project" : show,
        #                "entity" : shot,
        #                "entity_type" : "Assets",            #hardcoded, need to be addressed
        #                "pipe_step" : asset,
        #                "file_name" : file_name,
        #                AssetAPI.kAssetFieldVersion : version}
        # assetPlugin = AssetAPI.GetDefaultAssetPlugin()

        # assetId = assetPlugin.buildAssetId(assetFields)
        return self.assetId

#///////////////////////////////////////////////////////////////////////////////

class GDAssetRenderWidget(AssetWidgetDelegatePlugins.BaseAssetRenderWidget):

    def buildWidgets(self, hints):
        """
        This will construct the UI for the render widget for the asset
        management system.
        """
        label = QtWidgets.QLabel(" (Google Drive)", self)
        label.setProperty('smallFont', True)
        label.setProperty('boldFont', True)
        p = label.palette()
        p.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 200, 0))
        p.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 200, 0))
        label.setPalette(p)
        self.layout().addWidget(label)

        assetIdWidget = QtWidgets.QWidget(self)
        assetIdHBox = QtWidgets.QHBoxLayout(assetIdWidget)
        assetIdLabel = QtWidgets.QLabel("Output Asset:", assetIdWidget)
        assetIdLabel.setEnabled(False)
        assetIdHBox.addWidget(assetIdLabel, 0)
        self.__assetIdLabel = QtWidgets.QLineEdit("", assetIdWidget)
        self.__assetIdLabel.setReadOnly(True)
        assetIdHBox.addWidget(self.__assetIdLabel, 0)
        self.layout().addWidget(assetIdWidget)

        self.updateWidgets()

    def updateWidgets(self):
        """Update the UI to reflect internals"""
        assetId = self.getOutputInfo()["outputLocation"]
        if not assetId:
            assetId = "No output defined..."

        self.__assetIdLabel.setText(assetId)

#///////////////////////////////////////////////////////////////////////////////

class GDAssetListsWidget(QtWidgets.QFrame):
    """
    Asset browser using lists. This is used for asset selection when loading
    assets.
    """

    def __init__(self):
        QtWidgets.QFrame.__init__(self)

        self.ll = QtWidgets.QHBoxLayout(self)
        self.__showList = self.__buildListWidget("Project", self.ll)
        self.__shotList = self.__buildListWidget("Entity", self.ll)
        self.__nameList = self.__buildListWidget("",self.ll)
        self.__versionList = self.__buildListWidget("Task", self.ll)

        self.__showList.itemSelectionChanged.connect(self.__updateShow)
        self.__shotList.itemSelectionChanged.connect(self.__updateShot)
        self.__nameList.itemSelectionChanged.connect(self.__updateAsset)
        self.__versionList.itemSelectionChanged.connect(self.__updateVersion)

        self.__widgetsDict = {
            "project": self.__showList,
            "entity_type": self.__shotList,
            "entity": self.__nameList,
            "pipe_step": self.__versionList,
        }

        self.__showList.clear()
        self.__showList.addItems(_getShows())


    def __buildListWidget(self, name, parentLayout):

        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel(name)
        layout.addWidget(self.label)
        listWidget = QtWidgets.QListWidget()
        listWidget.setAlternatingRowColors(True)
        layout.addWidget(listWidget)

        parentLayout.addLayout(layout)

        return listWidget

    def __updateShow(self):
        show = self.__getListSelectionText("project")
        self.__shotList.clear()
        
        self.__shotList.addItems(_getShots(show))

    def __updateShot(self):
        show = self.__getListSelectionText("project")
        shot = self.__getListSelectionText("entity_type")
        labels = self.findChildren(QtWidgets.QLabel)
        labels[2].setText(shot)         # Asset/Sequence switch
        self.__nameList.clear()
        self.__nameList.addItems(_getAssets(show, shot))

    def __updateAsset(self):
        show = self.__getListSelectionText("project")
        shot = self.__getListSelectionText("entity_type")
        name = self.__getListSelectionText("entity")
        self.__versionList.clear()
        self.__versionList.addItems(_getVersions(show, shot, name))

    def __updateVersion(self):
        show = self.__getListSelectionText("project")
        shot = self.__getListSelectionText("entity_type")
        name = self.__getListSelectionText("entity")
        version = self.__getListSelectionText("pipe_step")
        #self.__versionList.clear()
        #self.__versionList.addItems(_getOnlyFiles(show, shot, name, version))
                                                                                

    def __getListSelectionText(self, name):
        currSel = ""
        w = self.__widgetsDict.get(name, None)
        if w:
            sel = w.selectedItems()
            currSel = sel[0].text() if sel else ""

        return str(currSel)

    def __selectItem(self, listName, itemName):
        w = self.__widgetsDict.get(listName, None)
        if w:
            items = w.findItems(itemName, QtCore.Qt.MatchExactly)

            if items and items[0]:
                w.setCurrentItem(items[0], QtCore.QItemSelectionModel.Select)

    def setAssetId(self, assetId):
        """
        Given an asset id decomposes in to a show, shot, name and
        version fields and updates the UI to reflect that
        """
        assetPlugin = AssetAPI.GetDefaultAssetPlugin()
        if not assetPlugin.isAssetId(assetId):
            return

        assetFields = assetPlugin.getAssetFields(assetId, True)
        for k in ("project", "entity_type", "entity",  "pipe_step"):
            self.__selectItem(k, assetFields[k])

    def getAssetFields(self):
        fields = {}
        for k in ("project", "entity_type", "entity", "pipe_step"):
            fields[k] = self.__getListSelectionText(k)
        
        fields['name'] = _getOnlyFiles(show=fields["project"], shot=fields["entity_type"], asset=fields["entity"], version=fields["pipe_step"])[-1]

        return fields

#///////////////////////////////////////////////////////////////////////////////

class GDAssetCombosWidget(QtWidgets.QFrame):
    """
    Asset browser using combo boxes. This is used for asset selection when
    saving.
    """

    def __init__(self):
        """
        Builds the initial combobox UI.
        """
        QtWidgets.QFrame.__init__(self)

        QtWidgets.QHBoxLayout(self)

        self.layout().addWidget(QtWidgets.QLabel("show:"))
        self.__showCombobox = QtWidgets.QComboBox()
        self.layout().addWidget(self.__showCombobox)

        self.layout().addWidget(QtWidgets.QLabel("shot:"))
        self.__shotCombobox = QtWidgets.QComboBox()
        self.layout().addWidget(self.__shotCombobox)

        self.layout().addWidget(QtWidgets.QLabel("asset:"))
        self.__assetCombobox = QtWidgets.QComboBox()
        self.layout().addWidget(self.__assetCombobox)

        self.layout().addWidget(QtWidgets.QLabel("version:"))
        self.__versionCombobox = QtWidgets.QComboBox()
        self.layout().addWidget(self.__versionCombobox)

        self.__versionUp = False
        self.__versionUpCheckBox = QtWidgets.QCheckBox('Version Up')
        self.__versionUpCheckBox.setChecked(self.__versionUp)
        self.layout().addWidget(self.__versionUpCheckBox)

        self.__showCombobox.currentIndexChanged.connect(self.__updateShow)
        self.__shotCombobox.currentIndexChanged.connect(self.__updateShot)
        self.__assetCombobox.currentIndexChanged.connect(self.__updateAsset)
        self.__versionCombobox.currentIndexChanged.connect(self.__updateVersion)
        self.__versionUpCheckBox.stateChanged.connect(self.__on_versionUpCheckBox_stateChanged)

        # Modify the integrated QListViews to lay out the items every time the
        # view is resized, so that changes in the application font preferences
        # are correctly reflected
        for combobox in (self.__showCombobox, self.__shotCombobox,
                         self.__assetCombobox, self.__versionCombobox):
            combobox.view().setResizeMode(QtWidgets.QListView.Adjust)

        self.__showCombobox.addItems(_getShows())

    def __updateShow(self):
        """Updates the value in the 'show' combo box UI"""

        show = str(self.__showCombobox.currentText())
        self.__shotCombobox.clear()
        self.__shotCombobox.addItems(_getShots(show))

    def __updateShot(self):
        """Updates the value in the 'shot' combo box UI"""
        show = str(self.__showCombobox.currentText())
        shot = str(self.__shotCombobox.currentText())
        self.__assetCombobox.clear()
        self.__assetCombobox.addItems(_getAssets(show, shot))

    def __updateAsset(self):
        """Updates the value in the 'asset' combo box UI"""
        show = str(self.__showCombobox.currentText())
        shot = str(self.__shotCombobox.currentText())
        asset = str(self.__assetCombobox.currentText())
        self.__versionCombobox.clear()
        self.__versionCombobox.addItems(_getVersions_(show, shot, asset))

    def __updateVersion(self):
        """Updates the value in the 'versions' combo box UI"""
        pass

    def __on_versionUpCheckBox_stateChanged(self, state):
        self.__versionUp = bool(state)

    def isVersionUpChecked(self):
        return self.__versionUp

    def setEditable(self, editable):
        """Propagate editability down to child widgets"""
        self.__showCombobox.setEditable(editable)
        self.__shotCombobox.setEditable(editable)
        self.__assetCombobox.setEditable(editable)
        self.__versionCombobox.setEditable(editable)

    def setAssetId(self, assetId):
        """Given an asset ID, decompose in to a show, shot, asset name
        and asset version and update the UI to reflect that.
        """

        assetPlugin = AssetAPI.GetDefaultAssetPlugin()
        if not assetPlugin.isAssetId(assetId):
            return

        assetFields = assetPlugin.getAssetFields(assetId, True)
        self.__showCombobox.setEditText(assetFields["show"])
        self.__shotCombobox.setEditText(assetFields["shot"])
        self.__assetCombobox.setEditText(assetFields[AssetAPI.kAssetFieldName])
        self.__versionCombobox.setEditText(assetFields.get(AssetAPI.kAssetFieldVersion,""))

    def getAssetFields(self):
        """Get hold of the individual asset fields from the UI"""
        show = str(self.__showCombobox.currentText())
        shot = str(self.__shotCombobox.currentText())
        asset = str(self.__assetCombobox.currentText())
        version = str(self.__versionCombobox.currentText())
        if version == "":
            version = "v00"
        if shot == "Assets":
            file_name = asset + "_" + "ldv" + "_" + version
            pipe_step = "Lookdev"
        else:
            file_name = asset + "_" + "lgt" + "_" + version
            pipe_step = "Lighting"

        return {"project" : show,
                "entity_type" : shot,
                "entity" : asset,
                "version": version,
                "name" : file_name,
                "pipe_step" : pipe_step}

#///////////////////////////////////////////////////////////////////////////////

class GDBrowser(QtWidgets.QFrame):
    """
    The GD asset browser class. This is added to the browser as a tab in the
    configureAssetBrowser function of the GDAssetWidgetDelegate.

    The GD browser uses two different UIs depending on the save mode. For
    saving, the asset ID is specified using combo boxes. For loading assets,
    assets are chosen from a list view (see GDAssetCombosWidget and
    GDAssetListsWidget respectively).
    """

    def __init__( self , *args , **kargs ) :
        QtWidgets.QFrame.__init__( self , *args )

        QtWidgets.QVBoxLayout(self)

        self.__assetIdLayout = QtWidgets.QHBoxLayout()
        self.__widget = None
        self.__saveMode = False
        self.__context = ""
        self.__requestedLocation = ""

    def showEvent(self, event):
        if not self.__widget:
            if self.__saveMode:
                self.__widget = GDAssetCombosWidget()
                self.__widget.setEditable(True)
            else:
                self.__widget = GDAssetListsWidget()
            self.layout().addWidget(self.__widget)

        if self.__requestedLocation and self.__widget:
            self.__widget.setAssetId(self.__requestedLocation)

    def setContext(self, context):
        self.__context = context

    def getExtraOptions(self):
        result = {"context": self.__context}
        if self.__saveMode:
            result["versionUp"] = str(self.__widget.isVersionUpChecked())

        return result

    def setSaveMode(self, saveMode):
        self.__saveMode = saveMode

    def setLocation(self, assetId):
        self.__requestedLocation = assetId

    def selectionValid(self):
        return True

    def getResult(self):
        assetFields = self.__widget.getAssetFields()
        assetPlugin = AssetAPI.GetDefaultAssetPlugin()
        return assetPlugin.buildAssetId(assetFields)

#///////////////////////////////////////////////////////////////////////////////

class GDAssetWidgetDelegate(AssetWidgetDelegatePlugins.BaseAssetWidgetDelegate):
    """
    The widget delegate class that implements BaseAssetWidgetDelegate.

    This class is registered to be associated with GDAsset and represents
    the entry point for configuring the render widget, control widget and
    asset browser.
    """

    def createAssetControlWidget(self, parent):
        """The hook in to katana that creates the asset control widget"""
        w = GDAssetControlWidget(parent, self.getWidgetHints())
        parent.layout().addWidget(w)
        return w

    def createAssetRenderWidget(self, parent, outputInfo):
        """The hook in to katana that creates the asset render control widget"""

        w = GDAssetRenderWidget(parent, self.getWidgetHints(), outputInfo)
        parent.layout().addWidget(w)
        return w

    def configureAssetBrowser(self, browser):
        """
        Configure the asset browser.

        For example, to disable an asset browser for shader lookups on the
        Material node, check for a specific context and return early:

         if context == AssetAPI.kAssetContextShader:
             _logDebug("Do not show asset browser for shaders.")
             return
        """
        AssetWidgetDelegatePlugins.BaseAssetWidgetDelegate.\
            configureAssetBrowser(self, browser)
        valuePolicy = self.getValuePolicy()
        hints = valuePolicy.getWidgetHints()
        context = hints.get("context")

        _logDebug("configureAssetBrowser hints: %s" % hints)

        index = browser.addBrowserTab(GDBrowser, "GoogleDrive")
        inputPath = str(valuePolicy.getValue())
        if inputPath.startswith("mock://") or not inputPath:
            browser.setCurrentIndex(index)
            browser.getBrowser(index).setLocation(inputPath)
            browser.getBrowser(index).setContext(context)

    def shouldAddFileTabToAssetBrowser(self):
        """Yes we want to keep the file tab in the asset browser"""
        return True

    def shouldAddStandardMenuItems(self):
        """Yes we want asset ids to have a standard dropdown menu"""
        return True

    def getQuickLinkPathsForContext(self, context):
        return AssetWidgetDelegatePlugins.BaseAssetWidgetDelegate.\
            getQuickLinkPathsForContext(self, context)


#///////////////////////////////////////////////////////////////////////////////

# Register the widget delegate to be associated with GDAsset
PluginRegistry = [
    ("AssetWidgetDelegate", 1, "Google", GDAssetWidgetDelegate),
]
