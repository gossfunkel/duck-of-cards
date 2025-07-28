from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, NodePath, loadPrcFileData, BitMask32, Vec3, DirectionalLight
from direct.interval.IntervalGlobal import *
from direct.interval.LerpInterval import LerpPosInterval
from enum import Enum
import simplepbr as spbr 

config_vars = """
win-size 1000 800
show-frame-rate-meter 1
hardware-animated-vertices true
basic-shaders-only false
threading-model Cull/Draw
"""

loadPrcFileData("", config_vars)

class PlayerCastle():
	def __init__(self, sb):
		self.hp = 100;

		self.castleModel = sb.loader.loadModel("playerBase.gltf")
		self.castleModel.reparentTo(render)
		self.castleModel.setScale(0.2)
		self.castleModel.setPos(0.,0.,1.)
		self.castleModel.setColor(0.3,0.35,0.6,1.)

class DuckOfCards(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		spbr.__init__("Duck of Cards")

		render.setShaderAuto()

		self.spawner = {1: Vec3(0.,10.,0.), 2: Vec3(10.,0.,0.), 3: Vec3(0.,-10.,0.), 4: Vec3(-10.,0.,0.)}

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
		self.createMap(20,20)

		self.cam.setPos(0.,0.,3.)
		self.cam.setHpr(-45,-45,0)
		#self.cam.setR(45) 			 # global 45deg roll
		#self.cam.setY(-45) 		 # global 45deg yaw
		#self.cam.setR(self.cam, 45) # local  45deg roll
		self.cam.setPos(self.cam, self.cam.getPos() + Vec3(0.,-12.,-4.))

		self.castle = PlayerCastle(self)

		self.enemyCount = 0
		self.enemies = []
		self.enemyModel = self.loader.loadModel("enemy1.gltf")
		self.enemyModelNd = self.render.attachNewNode("enemy-models")
		#self.enemyModel.reparentTo(render)
		self.enemyModel.setScale(0.1)
		self.enemyModel.setPos(0.2,0.,1.)
		self.enemyModel.setColor(1.,0.5,0.5,1.)

		self.spawnEnemyWave(5,self.spawner[1])

		self.taskMgr.add(self.update, "update", taskChain='default')

	def update(self, task):
		dt = globalClock.getDt()

		#for enemy in self.enemies:
		#	#print(enemy)
		#	enemy.setPos(enemy.getPos()-Vec3(0.,0.1*dt,0.))
		#	#self.cam.lookAt(enemy)

		return task.cont

	def createMap(self, width, length):
		counter = 0
		for y in range(length) :
			for x in range(width):
				# generate tile
				tile = self.tileMap.attachNewNode("tile-" + str(counter))
				tile.setPos(width/2 - (width-x),length/2 - (length-y),0.)
				self.tileModel.instanceTo(tile)
				tile.find("**/box").node().setIntoCollideMask(BitMask32.bit(1))
				counter += 1

	def spawnEnemy(self, pos):
		newEnemy = self.enemyModelNd.attachNewNode("enemy " + str(self.enemyCount))
		newEnemy.setPos(pos)
		self.enemyModel.instanceTo(newEnemy)
		self.enemyCount += 1
		self.enemies.append(newEnemy)
		self.moveEnemy = LerpPosInterval(newEnemy,
                    15,
                    Vec3(0,0,0),
                    startPos=pos,
                    blendType='noBlend',
                    fluid=1)
		self.moveEnemy.start()

	def spawnEnemyWave(self, num, pos):
		self.spawnSeq = Sequence(Func(self.spawnEnemy,pos), Wait(2.5)) 
		for _ in range(num):
			self.spawnSeq.loop()

app = DuckOfCards()
app.run()
