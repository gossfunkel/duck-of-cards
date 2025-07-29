from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, NodePath, loadPrcFileData, BitMask32, Vec3
from panda3d.core import DirectionalLight, TextNode, CollisionHandlerQueue, Material
from panda3d.core import CollisionTraverser, CollisionRay, CollisionNode, OrthographicLens
from panda3d.core import CollisionSphere, CollisionCapsule
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import LerpPosInterval
from enum import Enum
import simplepbr as spbr 

config_vars = """
win-size 1200 800
show-frame-rate-meter 1
hardware-animated-vertices true
basic-shaders-only false
threading-model Cull/Draw
"""

loadPrcFileData("", config_vars)

castleHP = 100
playerGold = 0
waveNum = 0

class UI():
	def __init__(self):
		self.castleHPdisplay = TextNode('castle HP display')
		self.castleHPdisplay.setText(str(castleHP))
		self.castleHPdisplay.setFrameColor(0, 0, 1, 1)
		self.castleHPdisplay.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)
		self.castleTextNP = aspect2d.attachNewNode(self.castleHPdisplay)
		self.castleTextNP.setScale(0.08)
		self.castleTextNP.setPos(-1.2,0., 0.9)

		self.waveDisplay = TextNode('wave number display')
		self.waveDisplay.setText("Wave: " + str(waveNum))
		self.waveDisplay.setFrameColor(1, 0, 1, 1)
		self.waveDisplay.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)
		self.waveDisplayNP = aspect2d.attachNewNode(self.waveDisplay)
		self.waveDisplayNP.setScale(0.05)
		self.waveDisplayNP.setPos(-0.85,0., 0.9)

		self.goldDisplay = TextNode('player gold display')
		self.goldDisplay.setText("GP: " + str(playerGold))
		self.goldDisplay.setFrameColor(1, 1, 0, 1)
		self.goldDisplay.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)
		self.goldDisplayNP = aspect2d.attachNewNode(self.goldDisplay)
		self.goldDisplayNP.setScale(0.05)
		self.goldDisplayNP.setPos(-0.65,0., 0.9)

		#self.turretButt = DirectButton(text="spawn tower", scale=0.05, 
		#						pos=(-0.3, 0, 0.9), command=self.spawnTower, extraArgs=[(3.,5.,1.)])

	def update(self):
		# update hp display
		self.castleHPdisplay.setText(str(castleHP) + "hp")
		if castleHP < 25:
			self.castleHPdisplay.setFrameColor(1, 0, 0, 1)
			# update castle appearance
		# update wave display
		self.waveDisplay.setText("Wave: " + str(waveNum))
		# update player gold points display
		self.goldDisplay.setText("GP: " + str(playerGold))

	def spawnTower(self, pos):
		base.spawnTower(pos)
		return 0

	def showCooldown(self, pos, cooldown):
		cd = TextNode('cooldown at ' + str(pos))
		cd.setText(str(cooldown))
		cd.setFrameColor(1, 1, 1, .6)
		cdNP = aspect2d.attachNewNode(cd)
		cdNP.setScale(0.05)
		# TODO : BROKEN : THIS RECEIVES THE WORLD POSITION, BUT IT NEEDS THE SCREEN POSITION
		cdNP.setPos(pos)

class PlayerCastle():
	def __init__(self, sb):
		self.model = sb.loader.loadModel("playerBase.gltf")
		self.model.reparentTo(render)
		self.model.setScale(0.2)
		self.model.setPos(0.,0.,1.)
		self.model.setColor(0.3,0.35,0.6,1.)

class Enemy():
	def __init__(self, enemyNode, pos):
		self.node = enemyNode
		self.node.setPos(pos)
		self.node.setColor(1.,0.5,0.5,1.)
		self.hp = 20
		# CollisionCapsule(ax, ay, az, bx, by, bz, radius)
		self.hitSphere = CollisionCapsule(0.09, -0.1, 1.2,0.09, -0.1, 1.45, .12)
		self.hitNp = self.node.attachNewNode(CollisionNode('{}-cnode'.format(str(self.node))))
		self.hitNp.node().addSolid(self.hitSphere)
		#self.hitNp.show() 								# uncomment to show hitbox

		# testMaterial = Material()
		# testMaterial.setShininess(3.0) # Make this material shiny
		# testMaterial.setAmbient((0, 0, 1, 1)) # Make this material blue
		# testMaterial.setLocal(False)
		# self.node.getParent().setMaterial(testMaterial) # Apply material

		self.move = self.node.posInterval(10., Vec3(0,0,0), pos)
		self.despawnInt = Func(self.despawn)
		self.moveSeq = Sequence(
			self.move,
			self.despawnInt
		)
		#self.move = LerpPosInterval(self.node, 15, Vec3(0,0,0),
		#								startPos=pos, blendType='noBlend', fluid=1)
		#self.move.setDoneEvent(Interval(Func(self.despawn),0.))
		self.moveSeq.start()

	def despawn(self):
		global castleHP

		print(str(self.node) + " despawning")
		castleHP -= 5
		# and do a wee animation?

		self.node.removeNode() # clean up the node

class Tower():
	def __init__(self, towerNode, pos):
		self.node = towerNode
		self.node.setPos(pos)
		#self.node.setScale()
		self.rateOfFire = 1.0
		self.damage = 1.0
		self.cooldown = 0.0
		#self.projectilePusher = PhysicsCollisionHandler()
		self.rangeSphere = CollisionSphere(0, 0, 0, 4)
		self.rangeColliderNp = self.node.attachNewNode(CollisionNode(str(self.node) + '-range-cnode'))
		self.rangeColliderNp.node().addSolid(self.rangeSphere)
		#self.rangeColliderNp.show()
		self.enemyDetector = CollisionTraverser(str(self.node) + '-enemy-detector')
		self.detectorQueue = CollisionHandlerQueue()
		self.enemyDetector.addCollider(self.rangeColliderNp, self.detectorQueue)

		base.taskMgr.add(self.attackLoop, "{}_attackLoop".format(self.node), taskChain='default')

	def attackLoop(self, task):
		if (self.cooldown == 0):
			if (self.detectorQueue.entries != None):
				self.launchProjectiles()
			self.cooldown += 5./self.rateOfFire
			base.ui.showCooldown(self.node.getPos(), self.cooldown)
		else:
			base.ui.showCooldown(self.node.getPos(), self.cooldown)
			self.cooldown -= .05
		task.cont

	def launchProjectiles(self):
		target = self.detectorQueue.entries[0]
		projectileNp = render.attachNewNode(ActorNode('projectile'))
		fromObject = projectileNp.attachNewNode(CollisionNode('projectileColNode'))
		fromObject.node().addSolid(CollisionSphere(0, 0, 0, 1))
		self.projectilePusher.addCollider(fromObject, projectileNp)

class DuckOfCards(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		# disable default mouse camera controls
		base.disableMouse()

		# initialise pbr for models, and shaders
		spbr.__init__("Duck of Cards")
		render.setShaderAuto()

		# enums-style dict of enemy spawn positions
		self.spawner = {1: Vec3(0.,10.,0.), 
						2: Vec3(10.,0.,0.), 
						3: Vec3(0.,-10.,0.), 
						4: Vec3(-10.,0.,0.)}

		# generate UI
		self.set_background_color(0.42,0.65,1.,1.)
		self.ui = UI()

		# create sunlight
		self.dirLight = DirectionalLight('dirLight')
		self.dirLight.setColorTemperature(6000)
		self.dirLight.setShadowCaster(True, 256, 256)
		#self.dirLight.setAttenuation(1,0,1)
		self.dirLightNp = render.attachNewNode(self.dirLight)
		self.dirLightNp.setHpr(-80,-50,20)
		render.setLight(self.dirLightNp)

		# initialise the dimetric camera (26.565deg for square pixels)
		self.cam.setPos(0.,0.,3.)
		self.cam.setHpr(-45,-26.565,0)
		#self.cam.setR(45) 			 # global 45deg roll
		#self.cam.setY(-45) 		 # global 45deg yaw
		#self.cam.setR(self.cam, 45) # local  45deg roll
		self.cam.setPos(self.cam, self.cam.getPos() + Vec3(0.,-12.,-4.))
		# orthographic lens to commit to isometric-style dimetric view
		self.lens = OrthographicLens()
		self.lens.setFilmSize(12, 8)  						# <--- update according to resolution
		self.lens.setNearFar(-40,40)
		self.cam.node().setLens(self.lens)

		# generate ground tile model and instance, creating node map
		self.tileModel = self.loader.loadModel("box")
		self.tileModel.setColor(0.,0.3,0.,1.)
		self.tileMap = self.render.attachNewNode("tileMap")
		self.createMap(20,20)

		# initialise the tile picker
		self.tilePicker = CollisionTraverser()
		self.tpQueue = CollisionHandlerQueue()
		tpNode = CollisionNode('tp-node')
		tpNode.setFromCollideMask(BitMask32.bit(1))
		tpNp = self.cam.attachNewNode(tpNode)
		self.pickerRay = CollisionRay()
		tpNode.addSolid(self.pickerRay)
		self.tilePicker.addCollider(tpNp, self.tpQueue)
		self.hitTile = False
		#self.tilePicker.showCollisions(render)

		# create a player castle object
		self.castle = PlayerCastle(self)

		# initialise tower models
		self.towerCount = 0
		self.towerModel = self.loader.loadModel("tower.gltf")
		self.towerModelNd = self.render.attachNewNode("tower-models")
		self.towerModel.setScale(0.2)

		# initialise enemy models & data
		self.enemyCount = 0
		self.enemies = []
		self.enemyModel = self.loader.loadModel("enemy2.gltf")
		self.enemyModelNd = self.render.attachNewNode("enemy-models")
		#self.enemyModel.reparentTo(render)
		self.enemyModel.setScale(0.1)
		self.enemyModel.setPos(0.2,0.,1.)

		#print(self.enemyModel.findAllMaterials())

		# spawn waves 								TODO - figure out spawning from both sides
		#													without incrementing waveNum twice:
		self.ui.spawnTower(Vec3(3.,5.,1.))
		self.waveSchedule = Sequence(
			Func(self.spawnEnemyWave, 5, self.spawner[1]),
			Wait(25.0),
			Func(self.spawnEnemyWave, 5, self.spawner[2]),
			Wait(25.0),
			Func(self.spawnEnemyWave, 5, self.spawner[3]),
			Func(self.spawnEnemyWave, 5, self.spawner[1])
		).start()

		# keyboard controls to move isometrically
		self.accept("arrow_left", self.move, ["left"])
		self.accept("arrow_right", self.move, ["right"])
		self.accept("arrow_up", self.move, ["fwd"])
		self.accept("arrow_down", self.move, ["back"])

		# run the mouse and update loops
		self.taskMgr.add(self.mouseTask, 'mouseTask', taskChain='default')
		self.taskMgr.add(self.update, "update", taskChain='default')

	def update(self, task):
		dt = globalClock.getDt()

		self.ui.update()

		return task.cont

	def move(self, direction):
		if direction == 'left':
			self.cam.setPos(self.cam.getPos() + Vec3(-1,1,0))
		elif direction == 'right':
			self.cam.setPos(self.cam.getPos() + Vec3(1,-1,0))
		elif direction == 'fwd':
			self.cam.setPos(self.cam.getPos() + Vec3(1,1,0))
		elif direction == 'back':
			self.cam.setPos(self.cam.getPos() + Vec3(-1,-1,0))

	def mouseTask(self, task):
		if self.hitTile is not False:
			#clean hightlighting
			self.tileMap.getChild(self.hitTile).setColor(0.3,0.9,0.4,1.)
			self.hitTile = False

		if (self.mouseWatcherNode.hasMouse()): # condition to protect from NaN
			mousePos = self.mouseWatcherNode.getMouse()
			self.pickerRay.setFromLens(self.camNode, mousePos.getX(), mousePos.getY())
			self.tilePicker.traverse(self.tileMap)

			if (self.tpQueue.getNumEntries() > 0): # when mouse ray collides with tiles:
				self.tpQueue.sortEntries() # sort by closest first
				tile = self.tpQueue.getEntry(0).getIntoNodePath().getNode(2)
				tileInd = int(tile.getName().split("-")[1]) # trim name to index
				#print("mouseover" + str(self.tileMap.getChild(tileInd)))
				self.tileMap.getChild(tileInd).setColor(0.9,1.,0.9,1.) # highlight
				self.hitTile = tileInd

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
		newEnNd = self.enemyModelNd.attachNewNode("enemy " + str(self.enemyCount))
		print(str(newEnNd) + " spawning")
		newEnemy = Enemy(newEnNd, pos)
		self.enemyModel.instanceTo(newEnemy.node)
		self.enemyCount += 1
		self.enemies.append(newEnemy)

	def spawnEnemyWave(self, num, pos):
		global waveNum
		waveNum += 1

		print("Spawning wave " + str(waveNum))
		self.spawnSeq = Sequence() 
		for _ in range(num):
			self.spawnSeq.append(Func(self.spawnEnemy,pos))
			self.spawnSeq.append(Wait(2.5))
		self.spawnSeq.start()

	def spawnTower(self, pos):
		print("Adding a tower at [" + str(pos[0]) + ", " + str(pos[1]) + ", " + str(pos[2]) + "]")
		newTowerNd = self.towerModelNd.attachNewNode("tower " + str(self.towerCount))
		newTower = Tower(newTowerNd, pos)
		self.towerModel.instanceTo(newTower.node)
		self.towerCount += 1
		return 0

app = DuckOfCards()
app.run()
