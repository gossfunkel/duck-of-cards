from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, DirectionalLight

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
		dirLight = DirectionalLight('dirLight')
		dirLight.setColorTemperature(6000)
		dirLight.setShadowCaster(True, 512, 512)
		dirLightNp = render.attachNewNode(dirLight)
		dirLightNp.setHpr(-20,-40,20)
		render.setLight(dirLightNp)
		#self.model.setP(90)
		self.model.reparent_to(render)

		camera.set_pos(0,-15,0)

		self.taskMgr.add(self.update, "update", taskChain='default')

	def update(self, task):
		self.model.setH(self.model.getH() + 1)
		return task.cont


app = DuckBase()
app.run()
