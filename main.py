from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, NodePath, loadPrcFileData, BitMask32, Vec3
from panda3d.core import DirectionalLight, TextNode, CollisionHandlerQueue, Material
from panda3d.core import CollisionTraverser, CollisionRay, CollisionNode, OrthographicLens
from panda3d.core import CollisionSphere, CollisionCapsule, Point3, TextureStage, TexGenAttrib
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
		self.castleTextNP.setScale(0.1)
		self.castleTextNP.setPos(-1.4,0., 0.85)

		self.waveDisplay = TextNode('wave number display')
		self.waveDisplay.setText("Wave: " + str(waveNum))
		self.waveDisplay.setFrameColor(1, 0, 1, 1)
		self.waveDisplay.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)
		self.waveDisplayNP = aspect2d.attachNewNode(self.waveDisplay)
		self.waveDisplayNP.setScale(0.05)
		self.waveDisplayNP.setPos(-0.9,0., 0.9)

		self.goldDisplay = TextNode('player gold display')
		self.goldDisplay.setText("GP: " + str(playerGold))
		self.goldDisplay.setFrameColor(1, 1, 0, 1)
		self.goldDisplay.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)
		self.goldDisplayNP = aspect2d.attachNewNode(self.goldDisplay)
		self.goldDisplayNP.setScale(0.05)
		self.goldDisplayNP.setPos(-0.9,0., 0.82)

		self.turretButt = DirectButton(text="place tower", scale=0.05, 
								pos=(-0.3, 0, 0.9), command=base.pickTower)

		# construct game over screen elements
		self.gameOverScreen = DirectDialog(frameSize = (-0.7, 0.7, -0.7, 0.7),
                                   fadeScreen = 0.4,
                                   relief = DGG.FLAT)
		self.gameOverScreen.hide()
		self.gameOverLabel = DirectLabel(text = "Game Over!", parent = self.gameOverScreen,
										scale = 0.1, pos = (0, 0, 0.2))
		restartBtn 	= DirectButton(text="Restart", command=base.startGame, pos=(-0.3, 0, -0.2),
								parent=self.gameOverScreen, scale=0.1)
		quitBtn 	= DirectButton(text="Quit", command=base.quit, pos=(0.3, 0, -0.2),
								parent=self.gameOverScreen, scale=0.1)

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

	# def showCooldown(self, pos, cooldown):
	# 	cd = TextNode('cooldown at ' + str(pos))
	# 	cd.setText(str(cooldown))
	# 	cd.setFrameColor(1, 1, 1, .6)
	# 	cdNP = aspect2d.attachNewNode(cd)
	# 	cdNP.setScale(0.05)
	# 	# TODO : BROKEN : THIS RECEIVES THE WORLD POSITION, BUT IT NEEDS THE SCREEN POSITION
	# 	cdNP.setPos(pos)

class PlayerCastle():
	def __init__(self, sb):
		self.model = sb.loader.loadModel("playerBase.gltf")
		self.model.reparentTo(render)
		self.model.setScale(0.2)
		self.model.setPos(0.,0.,1.)
		self.model.setColor(0.3,0.35,0.6,1.)

	def takeDmg(self):
		global castleHP
		# take damage
		castleHP -= 5.0
		# flash red for a moment
		Sequence(Func(self.model.setColor,1.,0.,0.,1.),
				Wait(0.1),
				Func(self.model.setColor,0.3,0.35,0.6,1.)).start()

class Enemy():
	def __init__(self, enemyNode, pos, speed):
		self.node = enemyNode
		self.node.setPos(pos)
		self.node.setColor(1.,0.5,0.5,1.)
		#self.node.setH(-30)
		self.node.lookAt(base.castle.model)
		self.hp = 20.0
		self.speed = speed # allows slowing and rushing effects

						# CollisionCapsule(ax, ay, az, bx, by, bz, radius)
		self.hitSphere = CollisionCapsule(0.09, -0.1, 1.2,0.09, -0.1, 1.45, .12)
		hcnode = CollisionNode('{}-cnode'.format(str(self.node)))
		hcnode.setIntoCollideMask(BitMask32(0x02))
		self.hitNp = self.node.attachNewNode(hcnode)
		self.hitNp.node().addSolid(self.hitSphere)
		#self.hitNp.show() 								# uncomment to show hitbox

		self.move = self.node.posInterval(20./self.speed, Vec3(0,0,0), self.node.getPos())
		self.moveSeq = Sequence(
			self.move,
			Func(self.despawnAtk)
		)
		self.moveSeq.start()

		base.taskMgr.add(self.update, "update-"+str(self.node), taskChain='default')

	def update(self, task):
		if (self.hp <= 0.0): # die if health gets too low
			self.despawnDie()
			return task.done
		# otherwise, keep going :)
		return task.cont

	def despawnAtk(self):
		# damage the castle
		# and do a wee animation?
		base.castle.takeDmg()

		# clean up the node
		print(str(self.node) + " despawning")
		self.node.removeNode() 

	def despawnDie(self):
		global playerGold
		# do a wee animation?
		self.moveSeq.pause()
		playerGold += 5
		# clean up the node
		print(str(self.node) + " dying")
		self.node.removeNode() 

	def damage(self, dmg):
		# take the damage
		self.hp -= dmg
		# flash red for a moment
		if self.hp > 0:
			Sequence(Func(self.node.setColor,1.,0.,0.,1.),
					Wait(0.1),
					Func(self.node.setColor,1.,0.5,0.5,1.)).start()

class Arrow():
	def __init__(self, arrowNd, pos, enemyId):
		self.node = arrowNd
		self.enemy = base.enemies[int(enemyId)]
		self.damage = 10.0
		self.node.setPos(pos)
		self.node.lookAt(self.enemy.node.getPos())
		self.node.setP(30)
		#projectileNp = render.attachNewNode(ActorNode('projectile'))
		# self.cnode = CollisionNode('arrowColNode')
		# self.cnode.setFromCollideMask(BitMask32(0x00))
		# self.fromObject = self.node.attachNewNode(self.cnode)
		# self.fromObject.node().addSolid(CollisionSphere(0, 0, 0, .2))
		#self.fromObject.show()
		self.move = self.node.posInterval(.5, self.getTargetPos(), 
											self.node.getPos(), fluid=1, blendType='noBlend')

		# on arrival/despawn, do damage to enemy
		self.despawnInt = Func(self.despawn)
		self.moveSeq = Sequence(
			self.move,
			self.despawnInt
		).start()

	def getTargetPos(self):
		# get up-to-date position
		p = self.enemy.node.getPos()
		# adjust for visual accuracy
		p[0] += .55
		p[1] -= .3
		p[2] += 1.3
		return p

	def despawn(self):
		# do damage and remove
		self.enemy.damage(self.damage)
		self.node.removeNode()

class Tower():
	def __init__(self, towerNode, pos):
		self.node = towerNode
		self.node.setPos(pos)
		#self.node.setScale()
		self.rateOfFire = 1.0
		self.damage = 1.0
		self.cooldown = 3.0
		self.onCD = False

		# initialise detection of enemies in range
		self.rangeSphere = CollisionSphere(0, 0, 0, 4)
		rcnode = CollisionNode(str(self.node) + '-range-cnode')
		rcnode.setFromCollideMask(BitMask32(0x02))
		self.rangeColliderNp = self.node.attachNewNode(rcnode)
		self.rangeColliderNp.node().addSolid(self.rangeSphere)
		#self.rangeColliderNp.show()

		self.enemyDetector = CollisionTraverser(str(self.node) + '-enemy-detector')
		self.detectorQueue = CollisionHandlerQueue()
		self.enemyDetector.addCollider(self.rangeColliderNp, self.detectorQueue)
		#self.enemyDetector.showCollisions(base.enemyModelNd)

		self.cdInt = Wait(self.cooldown/self.rateOfFire)
		self.cdSeq = Sequence(self.cdInt,Func(self.cdOFF))
		
		base.taskMgr.add(self.update, str(self.node)+"_update", taskChain='default')

	def update(self, task):
		# scan for enemies if not on cooldown
		if not self.onCD: self.attackScan()

		return task.cont

	def cdOFF(self):
		self.onCD = False

	def attackScan(self):
		# check for intersecting collisionsolids
		self.enemyDetector.traverse(base.enemyModelNd)
		#print("scanning...")

		if (self.detectorQueue.getNumEntries() > 0):
			#print("enemy detected!")
			# sort queue of detected solids by closest (n.b. edit here for priority options)
			self.detectorQueue.sortEntries()

			# find nodePoint and ID of detected enemy
			enemyNp = self.detectorQueue.entries[0].getIntoNodePath()
			#target = self.detectorQueue.entries[0].getSurfacePoint(enemyNp)
			enemyId = enemyNp.getName()[26:len(enemyNp.getName())-6] #print(enemyId)
			# FIRE
			self.launchProjectiles(enemyId)

			# put self on cooldown
			self.onCD = True
			self.cdSeq.start()

	def launchProjectiles(self, enemy):
		print("firing at " + enemy)
		arrowNd = base.arrowModelNd.attachNewNode("arrow")
		newArrow = Arrow(arrowNd, self.node.getPos(), enemy)
		base.arrowModel.instanceTo(arrowNd)

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
		self.tileStage = TextureStage('tileStage')
		self.tileModel = self.loader.loadModel("box")
		self.tileModel.clearTexture()
		self.groundTex = loader.load3DTexture("assets/ground-tile_#.png")
		self.tileModel.setTexture(self.groundTex, 1)
		self.tileMap = self.render.attachNewNode("tileMap")
		self.createMap(20,20)

		# initialise the tile picker
		self.tilePicker = CollisionTraverser()
		self.tpQueue = CollisionHandlerQueue()
		tpNode = CollisionNode('tp-node')
		tpNode.setFromCollideMask(BitMask32(0x01))
		tpNp = self.cam.attachNewNode(tpNode)
		self.pickerRay = CollisionRay()
		tpNode.addSolid(self.pickerRay)
		self.tilePicker.addCollider(tpNp, self.tpQueue)
		self.hitTile = False
		self.choosingTile = False
		#self.tilePicker.showCollisions(render)

		# create a player castle object
		self.castle = PlayerCastle(self)

		# initialise projectile models
		self.arrowModel = self.loader.loadModel("assets/arrow2.gltf")
		self.arrowModelNd = self.render.attachNewNode("arrow-models")
		self.arrowModel.setScale(0.1)

		# initialise tower models
		self.towerCount = 0
		self.towerModel = self.loader.loadModel("tower.gltf")
		self.towerModelNd = self.render.attachNewNode("tower-models")
		self.towerModel.setScale(0.2)

		# initialise enemy models & data
		self.enemyCount = 0
		self.enemies = []
		self.enemyModel = self.loader.loadModel("assets/enemy1.gltf")
		self.enemyModelNd = self.render.attachNewNode("enemy-models")
		#self.enemyModel.reparentTo(render)
		self.enemyModel.setScale(0.1)
		self.enemyModel.setPos(0.,0.,1.)

		#print(self.enemyModel.findAllMaterials())

		# spawn waves 								TODO - figure out spawning from both sides
		#													without incrementing waveNum twice:
		#self.ui.spawnTower(Vec3(3.,5.,1.))
		self.waveSchedule = Sequence(
			Func(self.spawnEnemyWave, 5, self.spawner[1]),
			Wait(25.0),
			Func(self.spawnEnemyWave, 5, self.spawner[2]),
			Wait(25.0),
			Func(self.spawnEnemyWave, 5, self.spawner[3]),
			Wait(25.0),
			Func(self.spawnEnemyWave, 10, self.spawner[1]),
			Wait(25.0),
			Func(self.spawnEnemyWave, 10, self.spawner[4])
		).start()

		# keyboard controls to move isometrically
		self.accept("arrow_left", self.move, ["left"])
		self.accept("arrow_right", self.move, ["right"])
		self.accept("arrow_up", self.move, ["fwd"])
		self.accept("arrow_down", self.move, ["back"])

		self.accept("mouse1", self.onMouse)

		# run the mouse and update loops
		self.taskMgr.add(self.mouseTask, 'mouseTask', taskChain='default')
		self.taskMgr.add(self.update, "update", taskChain='default')

	def update(self, task):
		dt = globalClock.getDt()

		if not (castleHP > 0):
			if self.ui.gameOverScreen.isHidden():
				self.ui.gameOverScreen.show()

		self.ui.update()

		return task.cont

	# respond to mouseclick
	def onMouse(self):
		if self.choosingTile:
			self.spawnTower(self.tileMap.getChild(self.hitTile).getPos() + Vec3(0.5,0.5,1))
			self.choosingTile = False

	# camera movement function (step around by blocks of 1x1)
	def move(self, direction):
		if direction == 'left':
			self.cam.setPos(self.cam.getPos() + Vec3(-1,1,0))
		elif direction == 'right':
			self.cam.setPos(self.cam.getPos() + Vec3(1,-1,0))
		elif direction == 'fwd':
			self.cam.setPos(self.cam.getPos() + Vec3(1,1,0))
		elif direction == 'back':
			self.cam.setPos(self.cam.getPos() + Vec3(-1,-1,0))

	# ray-based tile picker for placing down towers
	def mouseTask(self, task):
		if self.hitTile is not False:
			#clear hightlighting
			self.tileMap.getChild(self.hitTile).setColor(1.0,1.0,1.0,1.0)
			self.hitTile = False

		if (self.choosingTile): # if the tower placer is on
			if (self.mouseWatcherNode.hasMouse()): # condition to protect from NaN when offscreen
				# get mouse position and traverse tileMap with the pickerRay
				mousePos = self.mouseWatcherNode.getMouse()
				self.pickerRay.setFromLens(self.camNode, mousePos.getX(), mousePos.getY())
				self.tilePicker.traverse(self.tileMap)

				if (self.tpQueue.getNumEntries() > 0): 	# when mouse ray collides with tiles:
					# sort by closest first
					self.tpQueue.sortEntries() 			
					# find tile node and get tile index
					tile = self.tpQueue.getEntry(0).getIntoNodePath().getNode(2)
					tileInd = int(tile.getName().split("-")[1]) # trim name to index
					#print("mouseover" + str(self.tileMap.getChild(tileInd)))
					# highlight on mouseover
					self.tileMap.getChild(tileInd).setColor(1.2,1.2,1.2,1.0)
					# save index of hit tile
					self.hitTile = tileInd

		return task.cont

	def createMap(self, width, length): 	# generate pickable tiles to place towers on
		counter = 0
				
		for y in range(length) :
			for x in range(width):
				# generate tile
				tile = self.tileMap.attachNewNode("tile-" + str(counter))
				tile.setPos(width/2 - (width-x),length/2 - (length-y),0.)
				self.tileModel.instanceTo(tile)
				tile.setTag("tile-" + str(counter), str(counter))

				tile.find("**/box").node().setIntoCollideMask(BitMask32(0x01))
				counter += 1

	def spawnEnemy(self, pos): 				# spawn an individual creep
		newEnNd = self.enemyModelNd.attachNewNode("enemy " + str(self.enemyCount))
		print(str(newEnNd) + " spawning")
		newEnemy = Enemy(newEnNd, pos, 1.)
		self.enemyModel.instanceTo(newEnemy.node)
		self.enemyCount += 1
		self.enemies.append(newEnemy)

	def spawnEnemyWave(self, num, pos): 	# spawn a wave of creeps
		global waveNum
		waveNum += 1

		print("Spawning wave " + str(waveNum))
		self.spawnSeq = Sequence() 
		for _ in range(num):
			self.spawnSeq.append(Func(self.spawnEnemy,pos))
			self.spawnSeq.append(Wait(2.5))
		self.spawnSeq.start()

	def pickTower(self): 	# TODO: I should probably use an FSM for this, the card shop menu, 
							# 		a pause screen/button, and the 'game over' screen
		self.choosingTile = True

	def spawnTower(self, pos):
		print("Adding a tower at [" + str(pos[0]) + ", " + str(pos[1]) + ", " + str(pos[2]) + "]")
		newTowerNd = self.towerModelNd.attachNewNode("tower " + str(self.towerCount))
		newTower = Tower(newTowerNd, pos)
		self.towerModel.instanceTo(newTower.node)
		self.towerCount += 1
		return 0

	def startGame(self): 	# remove all towers, enemies etc and prepare the game start-state
		global waveNum, playerGold, castleHP
		
		waveNum = 0
		playerGold = 0
		castleHP = 100

	def quit(self): 		# exit the game in a reasonable fashion
		base.userExit()

app = DuckOfCards()
app.run()
