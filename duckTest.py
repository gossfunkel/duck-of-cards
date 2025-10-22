from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData


config_vars = """
win-size 1200 800
show-frame-rate-meter 1
hardware-animated-vertices true
basic-shaders-only false
model-cache-dir
threading-model Cull/Draw
"""
loadPrcFileData("", config_vars)

class DuckBase(ShowBase):
	def __init__(self):		#			=========================
		ShowBase.__init__(self)
		self.model = loader.loadModel("assets/roundDuck.gltf")
		#self.model.setP(90)
		self.model.reparent_to(render)

		camera.set_pos(0,-5,0)

app = DuckBase()
app.run()
