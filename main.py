from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, NodePath, loadPrcFileData, BitMask32, Vec3
from panda3d.core import DirectionalLight, TextNode, CollisionHandlerQueue, Material, Shader
from panda3d.core import CollisionTraverser, CollisionRay, CollisionNode, OrthographicLens
from panda3d.core import CollisionSphere, CollisionCapsule, Point3, TextureStage, TexGenAttrib
from panda3d.core import CollisionBox, TransparencyAttrib, CardMaker, Texture, SamplerState
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import LerpPosInterval
from enum import Enum
from direct.fsm.FSM import FSM
from random import randint
#import simplepbr as spbr 
#import complexpbr as cpbr 
import SpriteModel as spritem
import Buildings

config_vars = """
win-size 1200 800
show-frame-rate-meter 1
hardware-animated-vertices true
basic-shaders-only false
threading-model Cull/Draw
"""
#texture-scale 0.5
#"""

loadPrcFileData("", config_vars)

# GLOBAL VARIABLES

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
	# = BUGFIX: texture problems with paths and highlight not rendering correctly
	# = BUGFIX?: still having trouble with Func-setColor of Sequence in Enemy (!is_empty at 2030 of nodePath) MAYBE FIXED
	# = BUGFIX: highlighting tiles on mouseover when placing tower
	# = BUGFIX: arrows fly while paused / various animation cancels (fast spinning duck)
	# = dogs need flipped the right way when going y+
	# - procedurally generate paths- have enemies follow path?
	# - terminal-style output/dialogue at the bottom left
	# - improve card menu and add more options
	# - add pond and ducks
	# - add more enemies and bigger waves
	# - set up initial card offer
	# - add more card options
	# - confine mouse to window edges and trigger camera movement when it hits an edge
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

class GamestateFSM(FSM):
	def __init__(self): 
		FSM.__init__(self, 'GamestateFSM') # must be called when overloading

		# enums-style dict of enemy spawn positions
		self.spawner = {1: Vec3(0.,18.,0.),  # Y position (top left)
						2: Vec3(18.,0.,0.),  # X position (top right)
						3: Vec3(0.,-18.,0.), # Yneg position (bottom right)
						4: Vec3(-18.,0.,0.)} # Xneg position (bottomg left)

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

		# disable default panda3d mouse camera controls
		base.disableMouse()

		# initialise pbr for models, and shaders
		#spbr.__init__("Duck of Cards")
		#cpbr.apply_shader(self.render)
		#cpbr.screenspace_init()
		render.setShaderAuto()
		#cpbr.set_cubebuff_active()
		#cpbr.set_cubebuff_inactive()
		#base.complexpbr_z_tracking = True

		# example of how to set up bloom -- complexpbr.screenspace_init() must have been called first
		#screen_quad = base.screen_quad
		#screen_quad.set_shader_input("bloom_intensity", 0.25)
		#screen_quad.set_shader_input("bloom_threshold", 0.3)
		#screen_quad.set_shader_input("bloom_blur_width", 20)
		#screen_quad.set_shader_input("bloom_samples", 4)

		# Make dark background 
		#self.set_background_color(0.42,0.65,1.,1.)
		self.set_background_color(0.02,0.,0.05,1.)

		# create sunlight
		self.dirLight = DirectionalLight('dirLight')
		self.dirLight.setColorTemperature(6000)
		self.dirLight.setShadowCaster(True, 512, 512)
		#self.dirLight.setAttenuation(1,0,1)
		self.dirLightNp = render.attachNewNode(self.dirLight)
		self.dirLightNp.setHpr(-70,-40,20)
		render.setLight(self.dirLightNp)

		# initialise the camera - isometric angle (35.264deg)
		self.cam.setPos(0.,0.,3.)
		self.cam.setHpr(-45,-35.264,0)
		#self.cam.setHpr(-45,-26.565,0) # dimetric angle - 26.565deg for square pixels
		self.cam.setPos(self.cam, self.cam.getPos() + Vec3(0.,-12.,-4.))
		# orthographic lens to commit to isometric view
		self.lens = OrthographicLens()
		self.lens.setFilmSize(12, 8)  						# <--- update according to resolution
		self.lens.setNearFar(-40,40)
		self.cam.node().setLens(self.lens)

		# generate ground tile model and instance, creating node map
		self.tileMap = self.render.attachNewNode("tileMap")
		self.tileModel = self.loader.loadModel("assets/groundTile.egg")
		self.lakeTiles = self.render.attachNewNode("lakeTiles")
		self.lakeTileModel = self.loader.loadModel("assets/lakeTile.egg")

		self.tileTS = TextureStage('tileTS')
		self.tileTS.setMode(TextureStage.M_add)
		self.tileTS.setTexcoordName('UVMap')
		self.tileHighlight = self.loader.loadTexture("assets/highlight-tile.png")
		self.groundTex = self.loader.loadTexture("assets/ground-tile.png")
		self.createMap(20,20)

		#self.tileModel.ls()

		# generate path textures and apply to tiles
		self.pathTex = loader.loadTexture("assets/road-tile.png")
		#self.pathTex.set_format(Texture.F_rgba32)
		self.pathTS = TextureStage('path-textureStage')
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
		self.hitTile = None
		# UNCOMMENT FOR DEBUG 
		#self.tilePicker.showCollisions(render)
		#tpNp.show()

		# create a player castle object
		self.castle = Buildings.PlayerCastle()
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
		self.enemyModel = self.loader.loadModel("assets/dogboard1.gltf")
		self.enemyModel.setH(90)
		self.enemyModelNd = self.render.attachNewNode("enemy-models")
		#self.enemyModel.reparentTo(render)
		self.enemyModel.setScale(0.1)
		self.enemyModel.setPos(0.,0.,.8)
		#print(self.enemyModel.findAllMaterials())

		# load a random duck as a placeholder for civilian ducks
		self.duckModel = self.loader.loadModel("assets/duckboard1.gltf")
		self.duckNp = self.render.attachNewNode("duck-models")
		self.duckModel.setScale(0.05)
		self.duckModel.setH(-90)
		self.randomDuck = spritem.NormalInnocentDuck("an-innocent-duck", Vec3(-2.,-2.,2.), 1.)

		# initialise the finite-state machine
		self.fsm = GamestateFSM()

		# initialise the UI manager
		self.ui = UI()

		# keyboard controls to move isometrically
		self.accept("arrow_left", self.move, ["left"])
		self.accept("arrow_right", self.move, ["right"])
		self.accept("arrow_up", self.move, ["fwd"])
		self.accept("arrow_down", self.move, ["back"])
		self.accept("page_up", self.move, ["zoomIn"])
		self.accept("page_down", self.move, ["zoomOut"])

		# listen for left-clicks
		self.accept("mouse1", self.onMouse)

		# run the mouse and update loops
		self.taskMgr.add(self.towerPlaceTask, 'towerPlaceTask', taskChain='default')
		self.taskMgr.add(self.update, "update", taskChain='default')

		self.fsm.demand('Gameplay')

	def update(self, task):
		dt = globalClock.getDt()

		if not (castleHP > 0):
			self.fsm.demand('GameOver')

		self.ui.update()

		return task.cont

	# respond to left mouseclick (from Gameplay state)
	def onMouse(self):
		if (self.fsm.state == 'PickTower' and self.hitTile != None): # in tower tile picker state; place tower and exit tile picker state
			self.spawnTower(self.hitTile.getPos() + Vec3(0.,0,1.))
			self.hitTile.set_texture(self.tileTS, self.groundTex, 1)
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

	def giveGold(self, amount):
		global playerGold
		playerGold += int(amount)
		return playerGold

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
		elif direction == 'zoomIn':
			self.cam.setScale(self.cam.getScale()*0.8)
		elif direction == 'zoomOut':
			self.cam.setScale(self.cam.getScale()*1.2)

	# ray-based tile picker for placing down towers
	def towerPlaceTask(self, task):
		#self.fsm.demand('PickTower')

		if (self.fsm.state == 'PickTower'): # if the tower placer is on
			if self.hitTile != None: 			# clear hightlighting on non-hovered tiles
				for tile in self.tileMap.getChildren():
					#if tile != self.hitTile:
					tile.set_texture(self.tileTS, self.groundTex, 1)
				self.hitTile = None

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
					tileInd = int(tileColl.getName().split("-")[1]) # trim name to index
					# highlight on mouseover
					self.hitTile = self.tileMap.getChild(tileInd)
					print("highlighting: " + str(self.hitTile))
					self.hitTile.set_texture(self.tileTS, self.tileHighlight, 1)
					#print(tileInd)

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
					tile = self.lakeTiles.attachNewNode("origin-laketile")
					#tile.setPos(width/2 - (width-x),length/2 - (length-y),1.)
					tile.setPos(width - (2*width-x*2),length - (2*length-y*2),-0.5)
					self.lakeTileModel.instanceTo(tile)
					tile.setTag("tile-lake-",'0')					
					# elseif (place terrain at x,y)
					# 	self.terrainTileModel.instanceTo(tile)
					# 	tile.setTag("tile-terrain-" + str(counter),str(counter))
					# 	createTerrainCollider(tile)
				else: 						# place a regular grass tile
					tile = self.tileMap.attachNewNode("tile-" + str(counter))
					#tile.setPos(width/2 - (width-x),length/2 - (length-y),1.)
					tile.setPos(width - (2*width-x*2),length - (2*length-y*2),-0.5)
					#tileHitbox = CollisionBox(tile.getPos()/100,.46, .46, .5)
					tileHitbox = CollisionBox(tile.getPos()/50,.92, .92, .5)
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
				#tile.setTexPos(TextureStage.getDefault(), 1., 1., 0.)
		# apply decal

	def spawnEnemy(self, pos): 				# spawn an individual creep
		newEnemy = spritem.Enemy("enemy-" + str(self.enemyCount), pos, 1.)
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
		newTower = Buildings.Tower(newTowerNd, pos)
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
