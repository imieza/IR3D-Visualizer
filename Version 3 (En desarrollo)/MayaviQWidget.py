import os
import warnings
warnings.filterwarnings('ignore')
os.environ['ETS_TOOLKIT'] = 'qt4'
os.environ['QT_API'] = 'pyqt'
import sip
sip.setapi('QString', 2)
import matplotlib.pyplot as plt
import numpy as np
from mayavi import mlab
from tvtk.api import tvtk
from traits.api import HasTraits, Instance, on_trait_change
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
    SceneEditor
from traitsui.api import View, Item

from PyQt4 import QtGui



class Visualization(HasTraits):
    scene = Instance(MlabSceneModel, ())

    @on_trait_change('scene.activated')
    def update_plot(self, Self):
        # This function is called when the view is opened. We don't
        # populate the scene when the view is not yet open, as some
        # VTK features require a GLContext.
        # We can do normal mlab calls on the embedded scene.
        self.generate_data_mayavi(Self)

    # the layout of the dialog screated
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                resizable=True  # We need this to resize with the parent widget
                )

    def _selection_change(self, old, new):
        self.trait_property_changed('current_selection', old, new)

    def image_data(self):
        data = np.random.random((5, 5, 5))
        i = tvtk.ImageData(spacing=(.5, .5, .5), origin=(-1, -1, -1))
        i.point_data.scalars = data.ravel()
        i.point_data.scalars.name = 'scalars'
        i.dimensions = data.shape

        return i

    def generate_data_mayavi(self, Self):

        if type(Self) is bool:
            return

        self.scene.mlab.clf()

        time = Self.calc["time"][Self.calc["peaks"]]
        grilla = False
        x, y, z = Self.calc['xyz']
        # Creo los valores del origen 0,0,0 para todos los vectores
        u = v = w = np.zeros(len(x))

        # Grilla
        if grilla:
            surf = self.scene.mlab.pipeline.surface(self.image_data(), opacity=0)
            obj3 = self.scene.mlab.pipeline.surface(mlab.pipeline.extract_edges(surf),
                                                    color=(.1, .1, .1), line_width=.001)

        # Grafico los vectores

        if len(x)>1:
            obj = self.scene.mlab.quiver3d(u, v, w, x, y,z,
                                           scalars=time,
                                           scale_mode="vector",
                                           mode="2ddash",
                                           line_width=2)
            obj.module_manager.scalar_lut_manager.reverse_lut = True
            obj.glyph.color_mode = 'color_by_scalar'

        obj2 = self.scene.mlab.quiver3d(u[0], v[0], w[0], x[0], y[0], z[0],
                                        scalars=time[0],
                                        scale_mode="vector",
                                        scale_factor=1,
                                        mode="2ddash",
                                        line_width=10)
        print "x[0]", x[0]
        obj2.module_manager.scalar_lut_manager.reverse_lut = True
        obj2.glyph.color_mode = 'color_by_scalar'

        self.snapshotFloorplan(Self)

        self.scene.background = (0, 0, 0)
        if len(x)>1:
            obj.module_manager.scalar_lut_manager.show_scalar_bar = True
            obj.module_manager.scalar_lut_manager.scalar_bar.orientation = 'vertical'
            obj.module_manager.scalar_lut_manager.scalar_bar.label_text_property.color = (1, 1, 1)
            obj.module_manager.scalar_lut_manager.scalar_bar.title_text_property.color = (0, 0, 0)
        # Agrego el colorbar, los ejes, y el cuadrado

        vista = self.scene.mlab.view(60, 60)
        self.scene.mlab.outline(obj) if len(x)>1 else None
        self.scene.mlab.axes()

    def snapshotFloorplan(self, Self):
        surf = self.scene.mlab.points3d([1, 0, -1, 0], [0, 1, 0, -1], [0, 0, 0, 0], scale_factor=.000000000001)

        self.scene.mlab.view(azimuth=0, elevation=180)
        mlab.show()

        imgmap = mlab.screenshot(mode='rgba', antialiased=False)

        newpath = os.getcwd() + '/images'
        if not os.path.exists(newpath):
            os.makedirs(newpath)

        i = Self.calc["name"]
        plt.imsave(arr=imgmap, fname="images/floorplan_" + i + ".png")


class MayaviQWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.visualization = Visualization()

        # If you want to debug, beware that you need to remove the Qt
        # input hook.
        # QtCore.pyqtRemoveInputHook()
        # import pdb ; pdb.set_trace()
        # QtCore.pyqtRestoreInputHook()

        # The edit_traits call will generate the widget to embed.
        self.ui = self.visualization.edit_traits(parent=self,
                                                 kind='subpanel').control

        layout.addWidget(self.ui)
        self.ui.setParent(self)

    def update_plot(self, Self):
        self.visualization.update_plot(Self)
