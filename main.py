from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, NodePath, loadPrcFileData, BitMask32, Vec3
from panda3d.core import DirectionalLight, TextNode, CollisionHandlerQueue, Material
from panda3d.core import CollisionTraverser, CollisionRay, CollisionNode, OrthographicLens
from panda3d.core import CollisionSphere, CollisionCapsule, Point3, TextureStage, TexGenAttrib
from panda3d.core import CollisionBox, TransparencyAttrib, CardMaker, Texture
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import LerpPosInterval
from enum import Enum
from direct.fsm.FSM import FSM
from random import randint
#import simplepbr as spbr 
import complexpbr as cpbr 

config_vars = """
win-size 1200 800
show-frame-rate-meter 1
hardware-animated-vertices true
basic-shaders-only false
threading-model Cull/Draw
"""

loadPrcFileData("", config_vars)

castleHP = 100
playerGold = 10
waveNum = 0

# GAME OPENING / TUTORIAL
	#
	# <intro: darkened background, specific sprite art>
	# "QUACK! I mean QUICK! Invaders are at the gates! There's no time to explain- you, traveller!"
	# > ...
	# "Yes, you. What's your name?"
	# "Wait- there's no TIME! Take this; it is one of my fine and valuable magic cards."
	# "It will summon a magical tower to defend the innocent ducks of the pond wherever you place it."
	# "Place it carefully and fight back these merciless attackers who would make mincemeat of us!"
	# "BEGONE! BWAAACK- WACK wack..."
	# > ...okay?
	# <Enter PickTower; user places first tower>
	# "Bweeeell, you took care of them. Perhaps there will be a place for you in my fine little kingdom."
	# "The fine ducks of the pond have been set upon by dogs for months, since they found our new home."
	# "Of course, I keep all the kingdom safe with my mighty magic cards!"
	# "That is, here in the castle, where I won't be set upon by dogs..."
	# "So what do you say- are you going to abandon these poor townspeople to their fate, or 
	# face your duty to duke and for duck's sake? Will you take the cards out and help build our defenses?"
	# > i guess? Is there somewhere I can sleep?
	# "For now, you may join us in the Castle of Pond Duchy, our bastion in the quackmire."
	# "When these brutal invasion forces are pushed back, we can "
	# <Level 1 splash. Initial card offer. Timer for first wave starts as soon as card picked>

# TODO:
	# = BUGFIX: first arrow is invisible
	# = BUGFIX: tile highlighting for tower picker is broken
	# = BUGFIX: sometimes the game crashes because it tries to change the colour of a dead enemy
	# - procedurally generate paths- have enemies follow path?
	# - terminal-style output/dialogue at the bottom left
	# - cleanup and refactor code into a couple of files (enemies, buildings, friendlies, ui)
	# - improve card menu and add more options
	# - add pond and ducks
	# - add more enemies and bigger waves
	# - set up initial card offer
	# - add more card options
	# - give towers more prioritising options (furthest forward, closest, highest hp etc)
	# - update enemy, tower, and castle models
	# - add more terrain/some random plant sprites
	# - add tower models for other tower types (magic,fire,sniper,bomb,poison)
	# - add wandering duck models
	# - procedural spawning of walls and building models between towers and castle

class UI():
	def __init__(self):
		# pass self to fsm
		base.fsm.ui = self

		# show remaining hit points
		self.castleHPdisplay = TextNode('castle HP display')
		self.castleHPdisplay.setText(str(castleHP))
		self.castleHPdisplay.setFrameColor(0, 0, 1, 1)
		self.castleHPdisplay.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)
		self.castleTextNP = aspect2d.attachNewNode(self.castleHPdisplay)
		self.castleTextNP.setScale(0.1)
		self.castleTextNP.setPos(-1.4,0., 0.85)

		# show current enemy wave
		self.waveDisplay = TextNode('wave number display')
		self.waveDisplay.setText("Wave: " + str(waveNum))
		self.waveDisplay.setFrameColor(1, 0, 1, 1)
		self.waveDisplay.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)
		self.waveDisplayNP = aspect2d.attachNewNode(self.waveDisplay)
		self.waveDisplayNP.setScale(0.05)
		self.waveDisplayNP.setPos(-0.9,0., 0.9)

		# show player gold
		self.goldDisplay = TextNode('player gold display')
		self.goldDisplay.setText("GP: " + str(playerGold))
		self.goldDisplay.setFrameColor(1, 1, 0, 1)
		self.goldDisplay.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)
		self.goldDisplayNP = aspect2d.attachNewNode(self.goldDisplay)
		self.goldDisplayNP.setScale(0.05)
		self.goldDisplayNP.setPos(-0.9,0., 0.82)

		#self.turretButt = DirectButton(text="", scale=0.05, 
		#						pos=(-0.3, 0, 0.9), command=base.pickTower)

		# construct 'game over' screen elements
		self.gameOverScreen = DirectDialog(frameSize = (-0.7, 0.7, -0.7, 0.7),
                                   			fadeScreen = 0.4, relief = DGG.FLAT)
		self.gameOverScreen.hide()
		self.gameOverLabel = DirectLabel(text = "Game Over!", parent = self.gameOverScreen,
										scale = 0.1, pos = (0, 0, 0.2))
		restartBtn 	= DirectButton(text="Restart", command=base.fsm.exitGameOver, pos=(-0.3, 0, -0.2),
								parent=self.gameOverScreen, scale=0.1)
		quitBtn 	= DirectButton(text="Quit", command=base.quit, pos=(0.3, 0, -0.2),
								parent=self.gameOverScreen, scale=0.1)
		
		# construct 'card menu' elements
		self.cardMenuScreen = DirectFrame(frameSize = (-1.2, 1.2, -.8, .8),
		#							items=[newTowerBtn], initialItem=0,
        #                           fadeScreen = 0.7,
                                   relief = DGG.FLAT)
		newTowerBtn	= DirectButton(text="10", command=base.buyTower,
										pos=(-0.3, 0, -0.3), parent=self.cardMenuScreen, scale=0.3)
		newTowerCM = CardMaker('newTowerCard')
		newTowerCM.setFrame(-0.5,0.,-0.605,0.)
		newTowerCard = aspect2d.attachNewNode(newTowerCM.generate())
		#newTowerCard.setScale(0.4)
		newTowerCard.reparentTo(self.cardMenuScreen)
		newTowerCTex = loader.loadTexture('assets/card-buildTower.png')
		newTowerCard.setTexture(newTowerCTex)

		self.cardMenuScreen.hide()
		self.cardMenuLabel = DirectLabel(text = "Welcome!\nWould you like to buy one of my fine cards?", 
								parent = self.cardMenuScreen, scale = 0.1, pos = (0, 0, 0.1))
		dukeImgObj = OnscreenImage(image='assets/theDuke-sprite_ready.png', pos=(0.8, 0.5, 0.6), 
										parent=self.cardMenuScreen, scale=0.4)
		dukeImgObj.setTransparency(TransparencyAttrib.MAlpha)
		self.duckButtonMaps = loader.loadModel('assets/duck-button_maps')
		self.duckbutt = DirectButton(geom=(self.duckButtonMaps.find('**/theDuke-sprite_ready'),
						self.duckButtonMaps.find('**/theDuke-sprite_click'),
						self.duckButtonMaps.find('**/theDuke-sprite_rollover'),
						self.duckButtonMaps.find('**/theDuke-sprite_disabled')), 
						command=base.fsm.request, extraArgs=['CardMenu'], 
						scale=0.35, pos=(1,0,0.75))
		self.pauseButtonMaps = loader.loadModel('assets/pause_maps')
		self.pauseButton = DirectButton(geom=(self.pauseButtonMaps.find('**/pause_ready'),
						self.pauseButtonMaps.find('**/pause_click'),
						self.pauseButtonMaps.find('**/pause_rollover'),
						self.pauseButtonMaps.find('**/pause_disabled')), 
						command=base.fsm.request, extraArgs=['Pause'], 
						scale=0.1, pos=(1.4,0,0.89))
		self.playButtonMaps = loader.loadModel('assets/play_maps')
		self.playButton = DirectButton(geom=(self.playButtonMaps.find('**/play_ready'),
						self.playButtonMaps.find('**/play_click'),
						self.playButtonMaps.find('**/play_rollover'),
						self.playButtonMaps.find('**/play_disabled')), 
						command=base.fsm.request, extraArgs=['Gameplay'], 
						scale=0.1, pos=(1.4,0,0.89))

		# exit button currently auto-resumes gameplay; should check state and return to pause 
		# 	if the game was paused before the card menu was opened
		self.exitButtonMaps = loader.loadModel('assets/exit_maps')
		self.exitButton = DirectButton(geom=(self.exitButtonMaps.find('**/exit_ready'),
						self.exitButtonMaps.find('**/exit_click'),
						self.exitButtonMaps.find('**/exit_rollover'),
						self.exitButtonMaps.find('**/exit_disabled')), 
						command=base.fsm.request, extraArgs=['Gameplay'], 
						scale=0.1, pos=(1.4,0,0.89))
		# quit the game from the pause screen
		quitBtn	= DirectButton(text="QUIT", command=base.quit,
										pos=(-0.5, 0, -2.), parent=self.playButton, scale=0.9)

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
		self.map = render.attachNewNode("castleMap")
		self.model.reparentTo(self.map)
		self.model.setScale(0.2)
		self.model.setPos(0.5,0.5,1.5)
		self.model.setColor(0.3,0.35,0.6,1.)
		self.model.setTag("castle", '1')
		self.model.node().setIntoCollideMask(BitMask32(0x04))

	def takeDmg(self):
		global castleHP
		# take damage
		castleHP -= 5.0
		# flash red for a moment
		Sequence(Func(self.model.setColor,1.2,0.1,0.1,1.),
				Wait(0.05),
				Func(self.model.setColor,0.3,0.35,0.6,1.)).start()

class Enemy(FSM):
	def __init__(self, enemyNode, pos, speed):
		FSM.__init__(self, (str(enemyNode) + 'FSM')) # must be called when overloading

		self.node = enemyNode
		self.node.setPos(pos)
		self.node.setColor(1.,0.5,0.5,1.)
		#self.node.setH(-30)
		# modified target vector to prevent enemies flying into the air as they approach castle
		self.targetPos = base.castle.model.getPos() - Vec3(0.,0.,1.)
		
		# make them look where they're going
		#self.node.lookAt(self.targetPos)
		if (self.targetPos.getX() - pos.getX() > 1 or self.targetPos.getX() - pos.getX() < -1):
			# entity and target x are more than 1 unit apart
			if (self.targetPos.getX() > pos.getX()): # target is further 'up' x relative to entity
				self.demand('X')
				print(str(self.node)+" facing X")
			else: 								# target is lower down x-axis relative to entity
				self.demand('Xneg')
				print(str(self.node)+" facing Xneg")
		else: # entity and target x are less than 1 unit apart (aligned on x axis)
			if (self.targetPos.getY() > pos.getY()): # target is further 'up' y relative to entity
				self.demand('Y')
				print(str(self.node)+" facing Y")
			else: 								# target is lower down y-axis relative to entity
				self.demand('Yneg')
				print(str(self.node)+" facing Yneg")

		self.hp = 20.0
		self.speed = speed # allows slowing and rushing effects

						# CollisionCapsule(ax, ay, az, bx, by, bz, radius)
		self.hitSphere = CollisionCapsule(0.09, -0.1, 1.2,0.09, -0.1, 1.45, .12)
		hcnode = CollisionNode('{}-cnode'.format(str(self.node)))
		hcnode.setIntoCollideMask(BitMask32(0x02))
		self.hitNp = self.node.attachNewNode(hcnode)
		self.hitNp.node().addSolid(self.hitSphere)
		#self.hitNp.show() 								# uncomment to show hitbox

		self.move = self.node.posInterval(20./self.speed, self.targetPos, self.node.getPos())
		self.moveSeq = Sequence(
			self.move,
			Func(self.despawnAtk)
		)
		self.moveSeq.start()

		base.taskMgr.add(self.update, "update-"+str(self.node), taskChain='default')

	def enterX(self):
		# TODO lerp round
		self.node.lookAt(self.node.getX()+1, self.node.getY(), self.node.getZ())

	def filterX(self, request, args): # process input while facing +x
		if (request == 'Left'):
			return 'Yneg'
		elif (request == 'Right'):
			return 'Y'
		elif (request == 'Flip'):
			return 'Xneg'
		else:
			return None

	def enterY(self):
		# TODO lerp round
		self.node.lookAt(self.node.getX(), self.node.getY()+1,self.node.getZ())

	def filterY(self, request, args): # process input while facing +x
		if (request == 'Left'):
			return 'X'
		elif (request == 'Right'):
			return 'Xneg'
		elif (request == 'Flip'):
			return 'Yneg'
		else:
			return None

	def enterXneg(self):
		# TODO lerp round
		self.node.lookAt(self.node.getX()-1, self.node.getY(),self.node.getZ())

	def filterXneg(self, request, args): # process input while facing +x
		if (request == 'Left'):
			return 'Y'
		elif (request == 'Right'):
			return 'Yneg'
		elif (request == 'Flip'):
			return 'X'
		else:
			return None

	def enterYneg(self):
		# TODO lerp round
		self.node.lookAt(self.node.getX(), self.node.getY()-1,self.node.getZ())

	def filterYneg(self, request, args): # process input while facing +x
		if (request == 'Left'):
			return 'Xneg'
		elif (request == 'Right'):
			return 'X'
		elif (request == 'Flip'):
			return 'Yneg'
		else:
			return None

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
		# stop moving and don't damage the castle!
		self.moveSeq.clearIntervals()
		# remove update task from taskMgr
		if (base.taskMgr.getTasksNamed(str(self.node)+"_update") != None):
			base.taskMgr.remove(base.taskMgr.getTasksNamed(str(self.node)+"_update"))
		# do a wee animation?
		# give player gold
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
		#if (self.hp <= 0.0): # die if health gets too low
		#else: 
		#	self.despawnDie()
		# this seems to cause despawnDie to run twice, somehow. I should do proper garbage collection
		# on these objects, and remove the enemies as well as their nodes

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
		self.scanSeq = Sequence(Func(self.update))
		self.scanSeq.loop()

		#base.taskMgr.add(self.update, str(self.node)+"_update", taskChain='default')
		# task replaced with sequence for pausability

	def update(self):
		if not self.onCD: self.attackScan()

	#def update(self, task):
		#	# scan for enemies if not on cooldown
		#	if not self.onCD: self.attackScan()
		#	return task.cont
		#def pause(self):
		#	base.taskMgr.getTasksNamed(str(self.node)+"_update").pause() 
		#   ^ this pause method isn't a thing. using a sequence instead of the task

	def cdOFF(self):
		if not self.onCD: return 1
		else: 
			self.onCD = False
			return 0

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

class GamestateFSM(FSM):
	def __init__(self): 
		FSM.__init__(self, 'GamestateFSM') # must be called when overloading

		# enums-style dict of enemy spawn positions
		self.spawner = {1: Vec3(0.5,9.5,0.5), 
						2: Vec3(9.5,0.5,0.5), 
						3: Vec3(0.5,-9.5,0.5), 
						4: Vec3(-9.5,0.5,0.5)}

		# empty object to be filled with ui
		self.ui = None

		#self.choosingTile = False
		# spawn waves 								TODO - figure out spawning from both sides
		#													without incrementing waveNum twice:
		self.waveSchedule = Sequence(
			Wait(5.0),
			Func(base.spawnEnemyWave, 5, self.spawner[1]),
			Wait(25.0),
			Func(base.spawnEnemyWave, 5, self.spawner[2]),
			Wait(25.0),
			Func(base.spawnEnemyWave, 5, self.spawner[3]),
			Wait(25.0),
			Func(base.spawnEnemyWave, 10, self.spawner[1]),
			Wait(25.0),
			Func(base.spawnEnemyWave, 10, self.spawner[4])
		)
		self.waveSchedule.start()

	def enterGameplay(self):
		# resume sequences 
		self.waveSchedule.resume()
		if (base.spawnSeq != None):
			base.spawnSeq.resume()
		for enemy in base.enemies:
			enemy.moveSeq.resume()
		for tower in base.towers:
			tower.scanSeq.resume()

		self.ui.pauseButton.show()
		self.ui.playButton.hide()
		self.ui.exitButton.hide()

	def enterPause(self):
		# pause sequences
		self.waveSchedule.pause()
		if (base.spawnSeq != None):
			base.spawnSeq.pause()
		for enemy in base.enemies:
			enemy.moveSeq.pause()
		for tower in base.towers:
			tower.scanSeq.pause()
		# show pause state with dimmed screen and changing pause icon
		self.ui.pauseButton.hide()
		self.ui.playButton.show()
		# show pause menu

	def exitPause(self):
		# force hide pause menu
		self.ui.pauseButton.show()
		self.ui.playButton.hide()
		self.ui.exitButton.hide()
		# return pause icon and screen to normal state
		# don't resume schedules here; this allows Gameplay to resume so that things don't
		# 	resume when opening the menu while paused
		#self.waveSchedule.resume()
		#if (base.spawnSeq != None):
		#	base.spawnSeq.resume()
		#for enemy in base.enemies:
		#	enemy.moveSeq.resume()
		#pass

	def enterCardMenu(self):
		# pause sequences
		self.waveSchedule.pause()
		if (base.spawnSeq != None):
			base.spawnSeq.pause()
		for enemy in base.enemies:
			enemy.moveSeq.pause()
		for tower in base.towers:
			tower.scanSeq.pause()
		# arrows still don't pause in-flight; is another for loop the right answer, or can
		# 	i have the sequences all checking if the fsm.state == 'Gameplay' before continuing,
		# 	and suspend until it reaches that state. Sequences can't unpause themselves tho:/
		if self.ui.cardMenuScreen.isHidden():
			self.ui.cardMenuScreen.show()
		# update buttons
		self.ui.duckbutt.hide()
		self.ui.exitButton.show()

	def exitCardMenu(self):
		if not self.ui.cardMenuScreen.isHidden():
			self.ui.cardMenuScreen.hide()
		self.ui.duckbutt.show()
		self.ui.exitButton.hide()
		# n.b. what to do if leaving card menu while paused?

	def enterPickTower(self): 
		# enable toggle to tell updates to listen for clicks and run mouseray collider
		# maybe start a task for the tower picker?
		pass

	def exitPickTower(self):
		#self.choosingTile = False
		pass

	def enterGameOver(self):
		# pause sequences
		self.waveSchedule.pause()
		for enemy in base.enemies:
			enemy.move.pause()
		if self.ui.gameOverScreen.isHidden():
			self.ui.gameOverScreen.show()

	def exitGameOver(self):
		# reset the game
		pass

class DuckOfCards(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		# temporary integer ticker to rotate the random duck
		self.t = 0

		# disable default panda3d mouse camera controls
		base.disableMouse()

		# initialise pbr for models, and shaders
		#spbr.__init__("Duck of Cards")
		cpbr.apply_shader(self.render)
		#cpbr.screenspace_init()
		render.setShaderAuto()

		# generate UI
		#self.set_background_color(0.42,0.65,1.,1.)
		self.set_background_color(0.,0.,0.,1.)

		# create sunlight
		self.dirLight = DirectionalLight('dirLight')
		self.dirLight.setColorTemperature(6000)
		self.dirLight.setShadowCaster(True, 512, 512)
		#self.dirLight.setAttenuation(1,0,1)
		self.dirLightNp = render.attachNewNode(self.dirLight)
		self.dirLightNp.setHpr(-70,-40,20)
		render.setLight(self.dirLightNp)

		# initialise the dimetric camera (26.565deg for square pixels)
		self.cam.setPos(0.,0.,3.)
		#self.cam.setHpr(-45,-26.565,0)
		# isometric angle! 35.264deg
		self.cam.setHpr(-45,-35.264,0)
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
		#self.tileStage = TextureStage('tileStage')
		self.tileMap = self.render.attachNewNode("tileMap")
		self.lakeTiles = self.render.attachNewNode("lakeTiles")
		self.tileModel = self.loader.loadModel("assets/groundTile.gltf")
		self.lakeTileModel = self.loader.loadModel("assets/lakeTile.gltf")
		#self.tileModel.clearTexture()
		self.tileModel.setScale(0.5)
		self.lakeTileModel.setScale(0.5)
		#self.tileTS = TextureStage('grountTile-texturestage')
		#self.tileTS.setMode(TextureStage.MReplace)
		self.groundTex = loader.loadCubeMap("assets/ground-tile_#.png")
		self.groundTex.set_format(Texture.F_rgba32)
		#self.groundTex.setWrapU(Texture.WM_clamp)
		#self.groundTex.setWrapV(Texture.WM_clamp)
		self.createMap(20,20)
		#self.tileHighlight = loader.loadCubeMap("assets/ground-tile-highlight_#.png")
		#self.tileHighlight.set_format(Texture.F_rgba32)

		# generate path textures and apply to tiles
		self.pathTex = loader.loadTexture("assets/road1.png")
		self.pathTex.set_format(Texture.F_rgba32)
		self.pathTS = TextureStage('path-texturestage')
		self.pathTS.setMode(TextureStage.MDecal)
		self.placePaths()

		# initialise the tile picker
		self.tPickerRay = CollisionRay()
		self.tilePicker = CollisionTraverser()
		self.tpQueue = CollisionHandlerQueue()
		tpNode = CollisionNode('tp-node')
		tpNode.setFromCollideMask(BitMask32(0x01))
		tpNp = self.cam.attachNewNode(tpNode)
		tpNode.addSolid(self.tPickerRay)
		self.tilePicker.addCollider(tpNp, self.tpQueue)
		self.hitTile = 0
		# UNCOMMENT FOR DEBUG 
		#self.tilePicker.showCollisions(render)
		#tpNp.show()

		# create a player castle object
		self.castle = PlayerCastle(self)
		# self.cPickerRay = CollisionRay()
		# self.castlePicker = CollisionTraverser()
		# self.castleQueue = CollisionHandlerQueue()
		# cscNode = CollisionNode('csc-node')
		# cscNode.setFromCollideMask(BitMask32(0x04))
		# cscNp = self.cam.attachNewNode(cscNode)
		# cscNode.addSolid(self.cPickerRay)
		# self.castlePicker.addCollider(cscNp, self.castleQueue)

		# initialise projectile models
		self.arrowModel = self.loader.loadModel("assets/arrow2.gltf")
		self.arrowModelNd = self.render.attachNewNode("arrow-models")
		self.arrowModel.setScale(0.1)

		# initialise tower models
		self.towerCount = 0
		self.towers = []
		self.towerModel = self.loader.loadModel("tower.gltf")
		self.towerModelNd = self.render.attachNewNode("tower-models")
		self.towerModel.setScale(0.2)

		# initialise enemy models & data
		self.enemyCount = 0
		self.enemies = []
		self.spawnSeq = None
		self.enemyModel = self.loader.loadModel("assets/enemy1.gltf")
		self.enemyModelNd = self.render.attachNewNode("enemy-models")
		#self.enemyModel.reparentTo(render)
		self.enemyModel.setScale(0.1)
		self.enemyModel.setPos(0.,0.,1.)
		#print(self.enemyModel.findAllMaterials())

		# load a random duck as a placeholder for civilian ducks
		self.randomDuck = self.loader.loadModel("assets/duckboard1.gltf")
		self.randomDuck.reparentTo(self.render)
		self.randomDuck.setScale(0.05)
		self.randomDuck.setPos(-2.,-2.,2.)
		self.randomDuck.setH(-90)

		# initialise the finite-state machine
		self.fsm = GamestateFSM()

		# initialise the UI manager
		self.ui = UI()

		# keyboard controls to move isometrically
		self.accept("arrow_left", self.move, ["left"])
		self.accept("arrow_right", self.move, ["right"])
		self.accept("arrow_up", self.move, ["fwd"])
		self.accept("arrow_down", self.move, ["back"])

		# listen for left-clicks
		self.accept("mouse1", self.onMouse)

		# run the mouse and update loops
		self.taskMgr.add(self.towerPlaceTask, 'towerPlaceTask', taskChain='default')
		self.taskMgr.add(self.update, "update", taskChain='default')

		self.fsm.demand('Gameplay')

	def update(self, task):
		dt = globalClock.getDt()

		if self.fsm.state == 'Gameplay':
			self.t += 1
		
		self.randomDuck.setH(self.t%360)

		if not (castleHP > 0):
			self.fsm.demand('GameOver')

		self.ui.update()

		return task.cont

	# respond to left mouseclick (from Gameplay state)
	def onMouse(self):
		if (self.fsm.state == 'PickTower'): # in tower tile picker state; place tower and exit tile picker state
			self.spawnTower(self.tileMap.getChild(self.hitTile).getPos() + Vec3(-0.5,-0.5,1.))
			self.fsm.demand('Gameplay')
		# else: 
		# 	if not (self.fsm.state == 'CardMenu'): # if the menu isn't open
		# 		if self.mouseWatcherNode.hasMouse():
		# 			mousePos = self.mouseWatcherNode.getMouse()
		# 			self.cPickerRay.setFromLens(self.camNode, mousePos.getX(), mousePos.getY())
		# 			self.castlePicker.traverse(self.castle.map)
		# 			print("mouse click " + str(mousePos))

		# 			if (self.castleQueue.getNumEntries() > 0): 	# when mouse ray collides with castle:
		# 				self.castleQueue.sortEntries()
		# 				pickedObj = self.castleQueue.getEntry(0).getIntoNodePath()
		# 				pickedObj = pickedObj.findNetTag('castle')
		# 				print("queue entry " + str(pickedObj))
		# 				if pickedObj == self.castle.model:
		# 					print("castle clicked")
		# 					self.fsm.request('CardMenu')
		elif (self.fsm.state == 'CardMenu'):
			mousePos = self.mouseWatcherNode.getMouse()
			print(mousePos)
			if ((mousePos[0] > 1.2 or mousePos[0] < -1.2) or (mousePos[1] > 0.8 or mousePos[1] < -0.8)):
				self.fsm.demand('Gameplay')

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
	def towerPlaceTask(self, task):
		#self.fsm.demand('PickTower')

		if self.hitTile != 0:
			#clear hightlighting
			self.tileMap.getChild(self.hitTile).setColor(1.0,1.0,1.0,1.0)
			#self.tileMap.getChild(self.hitTile).setTexture(self.groundTex, 1)
			self.hitTile = 0

		if (self.fsm.state == 'PickTower'): # if the tower placer is on
			if (self.mouseWatcherNode.hasMouse()): # condition to protect from NaN when offscreen
				# get mouse position and traverse tileMap with the pickerRay
				mousePos = self.mouseWatcherNode.getMouse()
				self.tPickerRay.setFromLens(self.camNode, mousePos.getX(), mousePos.getY())
				self.tilePicker.traverse(self.tileMap)

				if (self.tpQueue.getNumEntries() > 0): 	# when mouse ray collides with tiles:
					# sort by closest first
					self.tpQueue.sortEntries() 			
					# find tile node and get tile index
					tileColl = self.tpQueue.getEntry(0).getIntoNodePath().getNode(1)
					#print(tileColl)
					#tileInd = tileColl.getName().split("-")[1] # trim name 
					tileInd = int(tileColl.getName().split("-")[1]) # trim name to index
					#print("mouseover: " + str(self.tileMap.getChild(tileInd)))
					# highlight on mouseover
					#self.tileMap.getChild(tileInd).setTexture(TextureStage.getDefault(), self.tileHighlight, 1)
					self.tileMap.getChild(tileInd).setColor(1.5,1.5,1.4,1.0)
					# save index of hit tile
					self.hitTile = tileInd
					#print(tileInd)
					# TODO : FIX BUG : CURRENTLY RETURNING [-9,-9,0] REGARDLESS OF CLICK

		return task.cont

	def createMap(self, width, length): 	# generate pickable tiles to place towers on
		counter = 0
		lakeSpawnPoint = [randint(2,int(width)-2), randint(2,int(length)-2)]
		print("lake spawn generation: " + str(lakeSpawnPoint))
		for y in range(length) :
			for x in range(width):
				# generate tile, starting at -(width/2),-(height/2) and ending at width/2,height/2
				# 	e.g. for width & height 10, creates a grid from -5,-5 to 5,5
				# Im choosing to have regular tiles to make user selections more reliable.
				# 	This allows for relatively simple procedural modeling by definite units, 
				# 	rather than freeform user selections, or something even more complex.
				# The actual pond generation will happen in a vertex shader, but it will
				# 	need a texture tag or application to specific objects to work.
				if (x==lakeSpawnPoint[0] and y==lakeSpawnPoint[1]):
					tile = self.lakeTiles.attachNewNode("laketile-" + str(counter))
					tile.setPos(width/2 - (width-x),length/2 - (length-y),1.)
					self.lakeTileModel.instanceTo(tile)
					tile.setTag("tile-lake-" + str(counter),str(counter))					
					# elseif (place terrain at x,y)
					# 	self.terrainTileModel.instanceTo(tile)
					# 	tile.setTag("tile-terrain-" + str(counter),str(counter))
					# 	createTerrainCollider(tile)
				else: 						# place a regular grass tile
					tile = self.tileMap.attachNewNode("tile-" + str(counter))
					tile.setPos(width/2 - (width-x),length/2 - (length-y),1.)
					tileHitbox = CollisionBox(tile.getPos()/100,.45, .45, .5)
					tileColl = CollisionNode(str(tile)+'-cnode')
					tileColl.setIntoCollideMask(BitMask32(0x01))
					tileNp = tile.attachNewNode(tileColl)
					tileNp.node().addSolid(tileHitbox)
					self.tileModel.instanceTo(tile)
					tile.setTag("tile-" + str(counter), str(counter))
					#tileNp.show() 					# uncomment to show hitboxes
				counter += 1
		# then apply decals like paths, decor/flora&fauna, obstacles etc

	def placePaths(self):
		# find appropriate tile to decal
		# TODO replace this with a wee path budget to spend and a random walk algorithm to spend it
		for tile in self.tileMap.children: # currently covers the cardinal directions
			if ((tile.getX() == 0 and tile.getY() != 0) or (tile.getY() == 0 and tile.getX() != 0)):
				tile.setTexture(self.pathTS, self.pathTex)
				#tile.setTexPos(TextureStage.getDefault(), 1., 0., 0.)
		#tile = self.tileMap.getChild(1)
		# apply decal

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
		self.spawnSeq.append(Func(self.resetSpawnSeq))
		self.spawnSeq.start()

	def resetSpawnSeq(self):
		# this method protects against rushing waves by spamming pause and resuming 
		# 	this sequence when it persists after spawning the wave
		self.spawnSeq = None

	def spawnTower(self, pos):
		#pos = pos - Vec3(1.5,1.5,0)
		print("Adding a tower at [" + str(pos[0]) + ", " + str(pos[1]) + ", " + str(pos[2]) + "]")
		newTowerNd = self.towerModelNd.attachNewNode("tower " + str(self.towerCount))
		newTower = Tower(newTowerNd, pos)
		self.towers.append(newTower)
		self.towerModel.instanceTo(newTower.node)
		self.towerCount += 1
		return 0

	def buyTower(self):
		global playerGold
		if playerGold >= 10:
			playerGold -= 10
			self.fsm.demand('PickTower')
		else:
			# show "can't afford" splash
			print("broke bitch")
			pass

	def startGame(self): 	# remove all towers, enemies etc and prepare the game start-state
		global waveNum, playerGold, castleHP
		
		waveNum = 0
		playerGold = 0
		castleHP = 100

	def quit(self): 		# exit the game in a reasonable fashion
		self.fsm.cleanup()
		base.userExit()

app = DuckOfCards()
app.run()
