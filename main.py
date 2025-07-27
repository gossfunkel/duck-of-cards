from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, NodePath, loadPrcFileData, BitMask32, Vec3, DirectionalLight
import simplepbr as spbr 

config_vars = """
win-size 1000 800
show-frame-rate-meter 1
hardware-animated-vertices true
basic-shaders-only false
threading-model Cull/Draw
"""

loadPrcFileData("", config_vars)

class DuckOfCards(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		spbr.__init__("Duck of Cards")

		render.setShaderAuto()

		self.set_background_color(0.1,0.4,0.2,1.)

		dirLight 	= DirectionalLight('dirLight')
		dirLight.setColorTemperature(6950)
		dirLight.setShadowCaster(True, 512, 512)
		dirLightNp  = render.attachNewNode(dirLight)
		dirLightNp.setHpr(0,-70,135)
		render.setLight(dirLightNp)

		self.tileModel = self.loader.loadModel("box")
		self.tileModel.setColor(0.,0.3,0.,1.)
		self.tileMap = self.render.attachNewNode("tile-map")
		self.createMap(10,10)

		self.cam.setPos(0.,0.,3.)
		self.cam.setHpr(-45,-45,0)
		#self.cam.setR(45) 			 # global 45deg roll
		#self.cam.setY(-45) 		 # global 45deg yaw
		#self.cam.setR(self.cam, 45) # local  45deg roll
		self.cam.setPos(self.cam, self.cam.getPos() + Vec3(0.,-8.,-4.))

		self.playerBase = self.loader.loadModel("box")
		self.playerBase.reparentTo(render)
		self.playerBase.setScale(1)
		self.playerBase.setPos(0.,0.,1.)
		self.playerBase.setColor(0.3,0.35,0.6,1.)

		self.enemyCount = 0
		self.enemies = []
		self.enemyModel = self.loader.loadModel("enemy1.gltf")
		self.enemyModelNd = self.render.attachNewNode("enemy-models")
		#self.enemyModel.reparentTo(render)
		self.enemyModel.setScale(0.1)
		self.enemyModel.setPos(0.5,0.,1.)
		self.enemyModel.setColor(1.,0.5,0.5,1.)

		self.spawnEnemy(Vec3(0.,5.,0.))

		self.taskMgr.add(self.update, "update", taskChain='default')

	def update(self, task):
		dt = globalClock.getDt()

		for enemy in self.enemies:
			#print(enemy)
			enemy.setPos(enemy.getPos()-Vec3(0.,0.1*dt,0.))
			#self.cam.lookAt(enemy)

		return task.cont

	def createMap(self, width, length):
		counter = 0
		for y in range(length-counter%length) :
			for x in range(width-counter%width):
				# generate tile
				tile = self.tileMap.attachNewNode("tile-" + str(counter))
				tile.setPos(width/2 - x,length/2 - y,0.)
				self.tileModel.instanceTo(tile)
				tile.find("**/box").node().setIntoCollideMask(BitMask32.bit(1))
				counter += 1

	def spawnEnemy(self, pos):
		newEnemy = self.enemyModelNd.attachNewNode("enemy " + str(self.enemyCount))
		newEnemy.setPos(pos)
		self.enemyModel.instanceTo(newEnemy)
		self.enemyCount += 1
		self.enemies.append(newEnemy)

app = DuckOfCards()
app.run()
