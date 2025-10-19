from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, NodePath, loadPrcFileData, BitMask32, Vec3
from panda3d.core import DirectionalLight, TextNode, CollisionHandlerQueue, Material, Shader
from panda3d.core import CollisionTraverser, CollisionRay, CollisionNode, OrthographicLens
from panda3d.core import CollisionSphere, CollisionCapsule, Point3, TextureStage, TexGenAttrib
from panda3d.core import CollisionBox, TransparencyAttrib, CardMaker, Texture, SamplerState
from panda3d.core import PNMImage, ShaderInput
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import LerpPosInterval
from enum import Enum
from direct.fsm.FSM import FSM
from random import randint
from math import sqrt
import SpriteModel as spritem
import Buildings

config_vars = """
win-size 1200 800
show-frame-rate-meter 1
//hardware-animated-vertices true
//basic-shaders-only false
model-cache-dir
//threading-model Cull/Draw
hardware-animated-vertices true
model-cache-dir
basic-shaders-only false
threading-model Cull/Draw
"""

loadPrcFileData("", config_vars)

# GLOBAL VARIABLES

castleHP = 100
playerGold = 10
waveNum = 0
testing = True

# GAME OPENING / TUTORIAL
	#
	# <intro dialogue sequence>
	# <Enter PickTower; user places first tower>
	# dialogue sequence 2:
	# "Bweeeell, you took care of them. Perhaps there will be a place for you in my fine little fiefdom."
	# "The fine ducks of the pond have been set upon by dogs for months, since they found our new home."
	# "Of course, I keep all the fiefdom safe with my mighty magic cards!"
	# "That is, here in the castle, where I won't be set upon by dogs..."
	# "So what do you say- are you going to abandon these poor townspeople to their fate, or 
	# face your duty to duke and for duck's sake? Will you take the cards out and help build our defenses?"
	# > i guess? Is there somewhere I can sleep?
	# "For now, you may join us in the Castle of Pond Duchy, our bastion in the quackmire."
	# "When these brutal invasion forces are pushed back, we can "
	# <Level 1 splash. Initial card offer. Timer for first wave starts as soon as card picked>

# CLIMAX CUTSCENE
	# 
	# > There isn't even such a think as a Duke of Cards! There's the King, the Queen, and the Ja-
	# "SILENCE! You have betrayed my trust, traveller, and now it is time for you to travel on."
	# > What if I don't want to?
	# "Don't- SQUAAAH the insolence! You walk into my fiefdom, use my magic, and now you spurn and insult me."
	# "I see this fiefdom requires a firmer hand than I have carried so far."
	# "Very well- if you won't accept the power I offer, I shall hold it myself..."
	# [Duke casts the card and things go dark]
	# > ...
	# > Um... duke?
	# > ...
	# > Hello?
	# // YOU HAVE PLAYED WITH POWERS YOU DO NOT UNDERSTAND // [screenshake]
	# > Who sai-
	# // YOU WILL COME TO KNOW WHY THE LIKES OF YOU AND YOUR FEEBLE FEATHERED FRIEND 
	# 		DO NOT RECOGNISE WHAT YOU TOYED WITH //
	# > He's not my friend
	# // THROUGH HIM YOU KNOW MORE FELLOWSHIP THAN YOU HAVE WITH ANYTHING YOU WILL SEE FROM NOW //
	# // WELCOME TO THE DAWN OF YOUR WORLD'S UNMAKING //
	# [screen brightens and lighting is changed for purple, after a moment there's a rumble]
	# [the castle erupts and a portal tears open in its place]
	# > ...
	# [Duke [Evil] sprite appears]
	# > You! What did you do?!
	# // THE TIME FOR NEGOTIATION IS PAST // WE CAN SEE YOU WILL BE NO HINDRANCE //
	# > What are you?
	# // WE ARE THE RAW VIOLENCE THAT YEARNS WITHIN EVERY FIBRE TO ESCAPE FROM ITS FICKLE CAGE //
	# // WE ARE THE FIRE THAT YOU HOLD TO YOUR ENEMIES FACE, THE FIRE THAT PROMISES YOUR WORLD TO THE ASHES //
	# // YOU WILL TASTE THE PRICE OF POWER //
	# [Next round begins; current defenses should hold]
	# [after that round, ally appears]
	# "Traveller! What's going on? What happened to the castle??"
	# > The Duke used some kind of powerful card, but I think he was tricked into releasing some kind of... demons.
	# "DEMONS?!? You mean, those things that just attacked us?"
	# > They came from the portal. I think there will be more. Perhaps much more.
	# "Wh- what do we do?!"
	# > Do we have any more cards? Or anything else we can use?
	# "More cards... I'll see what I can find! In the mean time, I suppose I can ask the other townspeople to help 
	# 	put up some barricades?"
	# > Thank you. I'll do what I can to hold off the hordes.
	# "G- godspeed!" [scurries off. Barricades interface appears. After placing, the next round begins]
	# [cards are thereafter awarded randomly from the Wild Townspeople set. Then the 'closing the portal' mission begins]

# TODO:
	# = BUGFIX: tower picker broke again:(
	# = BUGFIX: texture problems with paths and highlight not rendering correctly
	# = BUGFIX: problems with orientation of models and model recolouring between different systems
				# => turret orientation, colour
				# => arrow orientation
				# => castle colour
	# = BUGFIX?: still having trouble with Func-setColor of Sequence in Enemy (!is_empty at 2030 of nodePath) MAYBE FIXED
	# = BUGFIX: highlighting tiles on mouseover when placing tower
	# = BUGFIX: arrows fly while paused / various animation cancels (fast spinning duck). n.b.
		# pausing at the wrong time causes hundreds of dogs to spawn (!!)
	# --- PHASE 1) Basic game mechanics
	# = finish spritemodel directional system (models facing the right way, animate turn)
	# - procedurally generate paths- have enemies follow path? pathfinding
	# - terminal-style output/dialogue at the bottom left
	# - improve card menu and add more cards
	# - add more enemies and bigger waves
	# - set up initial card offer
	# - add more card options and do nicer card art 
	# - add tower models for other tower types (magic,fire,sniper,bomb,poison)
	# - make enemies 'pop' (coin scatter animation?) and improve tile placement (animation, sfx)
	# - confine mouse to window edges and trigger camera movement when it hits an edge
	# --- PHASE 2) Story & progression
	# - add in all dialogue & character sprites
	# - make pause menu and save/load functionality	
	# - make and add some music!
	# - implement missions (only a few, for the main story sections)
	# - improve progression display and splashes/notifiers for mission/wave progress
	# - add more terrain/some random plant sprites
	# - give towers more prioritising options (furthest forward, closest, highest hp etc)
	# - update enemy, tower, and castle models
	# - add pond and wandering ducks
	# --- PHASE 3) Ending & finishing touches
	# - procedural spawning of walls and building models between towers and castle
	# - 'evil mode' game state transition, general colour management and filtering shaders
	# - game menu, splash screen, and loading screens
	# - fill out assets:
		# -> enemies
		# -> allies
		# -> buildings
		# -> music
		# -> sfx
		# -> fx/animations/effect shaders
		# -> set dressing / props
		# -> card art
	# - distribution build

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
		restartBtn 	= DirectButton(text = "Restart", command = base.fsm.exitGameOver, pos = (-0.3, 0, -0.2),
								parent = self.gameOverScreen, scale = 0.1)
		quitBtn 	= DirectButton(text = "Quit", command = base.quit, pos = (0.3, 0, -0.2),
								parent = self.gameOverScreen, scale = 0.1)
		
		# construct 'card menu' elements
		self.cardMenuScreen = DirectFrame(frameSize = (-1.2, 1.2, -.8, .8),
		#							items = [newTowerBtn], initialItem = 0,
        #                           fadeScreen = 0.7,
                                   relief = DGG.FLAT)
		newTowerBtn	= DirectButton(text = "10", command = base.buyTower,
										pos = (-0.3, 0, -0.3), parent = self.cardMenuScreen, scale = 0.3)
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

class DialogueState():
	def __init__(self, step, seqs):
		assert isinstance(seqs, Sequence), f'Dialogue state not passed list at construction as required!'
		self.stateSequence = seqs
		self.step = step

class GamestateFSM(FSM):
	def __init__(self): 
		FSM.__init__(self, 'GamestateFSM') # must be called when overloading

		# enums-style dict of enemy spawn positions
		# n.b. the directions are named for which way the model is *facing*
		self.spawner = {1: Vec3(-18.,18.,0.),  	# (top left)
						2: Vec3(18.,18.,0.),  	# (top right)
						3: Vec3(18.,-18.,0.), 	# (bottom right)
						4: Vec3(-18.,-18.,0.)} 	# (bottom left)

		# empty object to be filled with ui
		self.ui = None

		# setup dialogue
		self.inDialogue = False
		self.clickWaiting = False

		#self.choosingTile = False
		# spawn waves 								TODO - figure out spawning from both sides
		#													without incrementing waveNum twice:
		if testing:
			self.waveSchedule = Sequence(
				Wait(5.0),
				Func(base.spawnEnemyWave, 1, self.spawner[1]),
				Wait(4.0),
				Func(base.spawnEnemyWave, 1, self.spawner[2]),
				Wait(6.0),
				Func(base.spawnEnemyWave, 1, self.spawner[3]),
				Wait(4.0),
				Func(base.spawnEnemyWave, 5, self.spawner[4]),
				Wait(6.0),
				Func(base.spawnEnemyWave, 10, self.spawner[1]),
				#Func(base.spawnEnemyWave, 10, self.spawner[3]),
				Wait(10.0),
				Func(base.spawnEnemyWave, 10, self.spawner[2]),
				Func(base.spawnEnemyWave, 10, self.spawner[4]),
			)
		else:
			self.waveSchedule = Sequence(
				Wait(5.0),
				Func(base.spawnEnemyWave, 5, self.spawner[1]),
				Wait(25.0),
				Func(base.spawnEnemyWave, 5, self.spawner[2]),
				Wait(25.0),
				Func(base.spawnEnemyWave, 5, self.spawner[3]),
				Wait(25.0),
				Func(base.spawnEnemyWave, 10, self.spawner[4]),
				Wait(25.0),
				Func(base.spawnEnemyWave, 10, self.spawner[2])
			)	
		self.waveSchedule.start()

	# main Gameplay state	

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

	# Pause menu

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

	# Card Menu

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

	# Pick Tower

	def enterPickTower(self): 
		# enable toggle to tell updates to listen for clicks and run mouseray collider
		# maybe start a task for the tower picker?
		self.waveSchedule.pause()
		if (base.spawnSeq != None):
			base.spawnSeq.pause()
		for enemy in base.enemies:
			enemy.moveSeq.pause()
		for tower in base.towers:
			tower.scanSeq.pause()

	def exitPickTower(self):
		#self.choosingTile = False
		pass

	# Game Over

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

	# Dialogue

	def enterDialogue(self):
		# pause sequences
		self.waveSchedule.pause()
		if (base.spawnSeq != None):
			base.spawnSeq.pause()
		for enemy in base.enemies:
			enemy.moveSeq.pause()
		for tower in base.towers:
			tower.scanSeq.pause()

		#TODO: DON'T ENTER DIALOGUE UNLESS THE CORRECT DIALOGUE HAS BEEN LOADED!
		# 		It needs to progress through the game linearly, and not get stuck in this state

		# generate a black fade from the bottom of the screen for the character background
		base.textCardMaker.setFrameFullscreenQuad()
		self.fadeBoxBack = render2d.attachNewNode(base.textCardMaker.generate())
		self.fadeBoxBack.setTransparency(1)
		fadeShader = Shader.load(Shader.SL_GLSL,
					 vertex="default.vert",
                     fragment="darkFade.frag")
		self.fadeBoxBack.setShader(fadeShader)
		self.fadeBoxBack.setShaderInput(ShaderInput('range',0.8))

		# display the sprite of the character addressing the player
		base.textCardMaker.setFrame(-0.1,1.,-1.,0.65)
		self.characterSprite = render2d.attachNewNode(base.textCardMaker.generate())
		self.characterSprite.setTransparency(1)
		self.characterSprite.setTexture(loader.loadTexture("assets/theDuke-sprite_ready.png"))

		# generate a black fade from the bottom of the screen for the text background
		base.textCardMaker.setFrameFullscreenQuad()
		self.fadeBoxFront = render2d.attachNewNode(base.textCardMaker.generate())
		self.fadeBoxFront.setTransparency(1)
		fadeShader = Shader.load(Shader.SL_GLSL,
					 vertex="default.vert",
                     fragment="darkFade.frag")
		self.fadeBoxFront.setShader(fadeShader)
		self.fadeBoxFront.setShaderInput(ShaderInput('range',1.4))

		self.inDialogue = True
		self.dialogueStep = 0
		
		self.dialogueTextNP = base.drawText(base.dialogue[self.dialogueStep])
		#wait for user to click
		self.clickWaiting = True

	def exitDialogue(self):
		# remove the dialogue box
		self.dialogueTextNP.removeNode()
		self.fadeBoxBack.removeNode()
		self.characterSprite.removeNode()
		self.fadeBoxFront.removeNode()

		self.inDialogue = False
		self.clickWaiting = False

	def setClickWaitingFalse(self):
		self.clickWaiting = False

	def stepDialogue(self):
		self.dialogueTextNP.node().setText(base.dialogue[self.dialogueStep])

class DuckOfCards(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		# disable default panda3d mouse camera controls
		base.disableMouse()
		#render.setShaderAuto()

		# Make background 
		#self.set_background_color(0.42,0.65,1.,1.)
		self.set_background_color(0.5,0.6,0.85,1.)

		# create sunlight
		# self.dirLight = DirectionalLight('dirLight')
		# self.dirLight.setColorTemperature(6000)
		# self.dirLight.setShadowCaster(True, 512, 512)
		# #self.dirLight.setAttenuation(1,0,1)
		# self.dirLightNp = render.attachNewNode(self.dirLight)
		# self.dirLightNp.setHpr(-70,-40,20)
		# render.setLight(self.dirLightNp)

		# initialise the camera - isometric angle (35.264deg)
		self.camera.setPos(0.,-10.,7.5) 
		self.camera.setHpr(0,-35.264,0)
		#self.camera.setHpr(-45,-26.565,0) # dimetric angle - 26.565deg for square pixels

		# orthographic lens to commit to isometric view
		#self.lens = OrthographicLens()
		#self.lens.setFilmSize(12, 8)  						# <--- update according to resolution
		#self.lens.setNearFar(-40,40)
		#self.camera.node().setLens(self.lens)

		self.createMap(40,40)

		#self.tileMap.ls()

		# n.b. this is part of the opening cutscene as a placeholder for the final dialogue data
		self.dialogue = ["QUACK! I mean QUICK! Attackers are at the gates!\nThere's no time to explain- you, traveller!",
							"> ...", "Yes, you! What's your name?", 
							"Wait- there's no TIME! Take this;\nit is one of my fine and valuable magic cards.",
							"It will summon a magical tower to defend\nthe innocent ducks of the pond\nwherever you place it.",
							"Place it carefully and fight back these\nmerciless attackers who would make\nMINCEMEAT of us!",
							"What are you waiting for?!\nBEGONE! BWAAACK- WACK wack..."]
		self.dialogueStates = [DialogueState(3,Sequence(Func(self.offerCard))),
								DialogueState(4,Sequence(Func(self.takeOfferedCard)))]
		self.textCardMaker = CardMaker('textScreen')
		self.textCardMaker.setHasUvs(1)
		self.textCardMaker.clearColor()

		# generate path textures and apply to tiles
		self.pathTex = loader.loadTexture("assets/road-tile.png")
		#self.pathTex.set_format(Texture.F_rgba32)
		self.pathTS = TextureStage('path-textureStage')
		self.pathTS.setMode(TextureStage.MDecal)
		self.pathTS.setTexcoordName('UVMap')
		self.placePaths()

		# initialise the tile picker
		self.tilePicker = CollisionTraverser()
		self.tpQueue = CollisionHandlerQueue()
		tilePickerNode = CollisionNode('tilePicker-node')
		tilePickerNP = camera.attachNewNode(tilePickerNode)
		tilePickerNode.setFromCollideMask(BitMask32(0x01))
		self.tilePickerRay = CollisionRay()
		tilePickerNode.addSolid(self.tilePickerRay)
		self.tilePicker.addCollider(tilePickerNP, self.tpQueue)
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

		# initialise tower tracking
		self.towerCount = 0
		self.towers = []

		# initialise enemy models & data
		self.enemyCount = 0
		self.enemies = []
		self.spawnSeq = None
		self.enemyModelNd = render.attachNewNode("enemy-models")
		#self.enemyModel.reparentTo(render)
		#print(self.enemyModel.findAllMaterials())

		# load a random duck as a placeholder for civilian ducks
		#self.duckNp = self.render.attachNewNode("duck_models")
		# temporary integer ticker to rotate the random duck
		self.t = 0
		randomDuck = spritem.NormalInnocentDuck("an_innocent_duck", Vec3(-2.,-2.,0.), .5)

		#self.sphere = self.loader.loadModel("smiley")
		#self.sphere.setPos(0,0,3)
		#self.sphere.reparentTo(render)

		# initialise the finite-state machine
		self.fsm = GamestateFSM()

		# initialise the UI manager
		self.ui = UI()

		# keyboard controls to move isometrically
		self.accept("arrow_left", self.move, ["left"])
		self.accept("a", self.move, ["left"])
		self.accept("arrow_right", self.move, ["right"])
		self.accept("d", self.move, ["right"])
		self.accept("arrow_up", self.move, ["fwd"])
		self.accept("w", self.move, ["fwd"])
		self.accept("arrow_down", self.move, ["back"])
		self.accept("s", self.move, ["back"])
		self.accept("page_down", self.move, ["down"])
		self.accept("z", self.move, ["down"])
		self.accept("page_up", self.move, ["up"])
		self.accept("x", self.move, ["up"])
		self.accept("f", self.move, ["zoomOut"])
		self.accept("r", self.move, ["zoomIn"])

		# listen for left-clicks
		self.accept("mouse1", self.onMouse)

		# run the mouse and update loops
		self.taskMgr.add(self.towerPlaceTask, 'towerPlaceTask', taskChain='default')
		self.taskMgr.add(self.update, "update", taskChain='default')

		if not testing:
			self.fsm.demand('Dialogue')
		else:
			self.fsm.demand('Gameplay')

	# LOAD-IN
	def createMap(self, width, length): 	# generate pickable tiles to place towers on
		# generate ground tile model and instance, creating node map
		self.tileMap = render.attachNewNode("tileMap")
		# self.tileModel = self.loader.loadModel("assets/groundTile.egg")
		# self.lakeTiles = self.render.attachNewNode("lakeTiles")
		# self.lakeTileModel = self.loader.loadModel("assets/lakeTile.egg")

		self.tileTS = TextureStage('tileTS')
		self.tileTS.setMode(TextureStage.M_replace)
		self.tileTS.setTexcoordName('UVMap')

		# each tile is assigned a unique index, locally referred to as tileIndex:
		tileIndex = 0
		# a random spawn point for the duck pond is generated:
		pondSpawnPoint = [randint(2,int(width)-2), randint(2,int(length)-2)]
		print("pond spawn generation: " + str(pondSpawnPoint))

		self.tile_maker = CardMaker('tile-')
		#tile_maker.setColor(1.,1.,1.,1.)
		self.tileScaleFactor = sqrt(2) # pythagoras; turning squares sideways makes triangles maybe?
		self.tile_maker.setFrame(0.,self.tileScaleFactor,0.,self.tileScaleFactor)
		self.tile_maker.setHasUvs(1)
		self.tile_maker.clearColor()

		self.groundTex = loader.loadTexture("../duck-of-cards/assets/ground-tile_4.png")
		self.groundTex.setWrapU(Texture.WM_clamp)
		self.groundTex.setWrapV(Texture.WM_clamp)
		self.groundTex.setMagfilter(SamplerState.FT_nearest)
		self.groundTex.setMinfilter(SamplerState.FT_nearest)

		self.pondTex = loader.loadTexture("../duck-of-cards/assets/lake-tile_4.png")
		self.pondTex.setWrapU(Texture.WM_clamp)
		self.pondTex.setWrapV(Texture.WM_clamp)
		self.pondTex.setMagfilter(SamplerState.FT_nearest)
		self.pondTex.setMinfilter(SamplerState.FT_nearest)

		# self.hilightCard = self.render.attachNewNode(card_maker.generate())
		# self.hilightCard.setPos(0.,0.,-10.)
		# self.hilightCard.setHpr(0., -90., 45.)
		self.highlightTex = loader.loadTexture("../duck-of-cards/assets/ground-tile-highlight_4.png")
		self.highlightTex.setWrapU(Texture.WM_clamp)
		self.highlightTex.setWrapV(Texture.WM_clamp)
		self.highlightTex.setMagfilter(SamplerState.FT_nearest)
		self.highlightTex.setMinfilter(SamplerState.FT_nearest)

		for x in range(width) :
			for y in range(length):
				# Im choosing to have regular tiles to make user selections more reliable.
				# 	This gives us discrete units for procedurally modelling the duck pond, 
				# 	rather than modelling freeform user selections (!!)
				# The pond generation will happen in a shader
				tileIndex += 1
				tile = self.tileMap.attachNewNode(self.tile_maker.generate())#"tileGRASS"+str(x)+":"+str(y)+"-"+str(tileInd)
				tile.setName("tile-"+str(tileIndex))
				tile.setPos(x-y,x+y-length,0.)
				tile.setHpr(0., -90., 45.)
				tile.setTransparency(1)

				tileHitbox = CollisionBox(Point3(0, 0, -0.1),Point3(1.39, 1.39, 0.001))
				tileColl = CollisionNode('cnode_'+str(tile))
				tileColl.setIntoCollideMask(BitMask32(0x01))
				colliderNp = tile.attachNewNode(tileColl)
				colliderNp.setHpr(0., 90., 0.)
				colliderNp.node().addSolid(tileHitbox)
				#colliderNp.show()
				if (x==pondSpawnPoint[0] and y==pondSpawnPoint[1]):
					tile.setTexture(self.tileTS, self.pondTex)
					tile.setTag("TILEpond-"+str(tileIndex),str(tileIndex))
					#tile.setColor(0,1,0,1)
				else: 						# place a regular grass tile
					tile.setTexture(self.tileTS, self.groundTex)
					tile.setTag("TILEground-"+str(tileIndex),str(tileIndex))
				
		# then apply decals like paths, decor/flora&fauna, obstacles etc

	def placePaths(self):
		# find appropriate tile to decal
		# TODO replace this with a wee path budget to spend and a random walk algorithm to spend it
		for tile in self.tileMap.children: # currently covers the cardinal directions
			if (tile.getX() == 0 and tile.getY() != 0):
				tile.setTexture(self.pathTS, self.pathTex)
				#tile.setTexHpr(self.pathTS, 90,0,0)
				#tile.setTexScale(self.pathTS, 1.1,1.1,1)
				tile.setTexPos(self.pathTS, -.1, .1, 0.)
			if (tile.getY() == 0 and tile.getX() != 0):
				tile.setTexture(self.pathTS, self.pathTex)
		# apply decal

	# TASK FUNCTIONS
	def update(self, task):
		dt = globalClock.getDt()

		#if testing: self.sphere.setPos(self.sphere.getPos()[0] + 0.01,0,3)

		if not (castleHP > 0):
			self.fsm.demand('GameOver')

		self.ui.update()

		return Task.cont

	# respond to left mouseclick (from Gameplay state)
	def onMouse(self):
		if (self.fsm.state == 'PickTower' and self.hitTile != None): # in tower tile picker state; place tower and exit tile picker state
			# todo: sequence for animating tower placement - clunk
			print("ONMOUSE HIT " + str(self.hitTile))
			self.spawnTower(self.hitTile.getPos() + Vec3(0.,0,1.))
			self.hitTile.set_texture(self.tileTS, self.groundTex, 1)
			self.hitTile.set_color(1,0,0,1)
			self.hitTile = None
			#self.hitTile.setColor(1.,1.,1.,1.)
			#self.hitTile.findTexture(self.tileTS).load(self.groundPNM)
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
		elif (self.fsm.state == 'Dialogue'):
			# in dialogue, we check if we're waiting for a click
			if (self.fsm.clickWaiting):
				# we then step forward the dialogue counter
				self.fsm.dialogueStep += 1
				# and check if the dialogue is at the end of the array (completed)
				if (self.fsm.dialogueStep < len(self.dialogue)): 
					# procede to next step of dialogue 
					self.fsm.stepDialogue()
					for ds in self.dialogueStates:
						if (self.fsm.dialogueStep == ds.step):
							# execute functions (stored in Sequence) for current step
							ds.stateSequence.start()
							break
					Wait(2) # avoid accidentally skipping dialogue
				else:
					# exit dialogue if we reach the end of the array
					self.fsm.demand('Gameplay')
					self.fsm.setClickWaitingFalse()

	def giveGold(self, amount):
		global playerGold
		playerGold += int(amount)
		return playerGold

	# camera movement function (step around by blocks of 1x1)
	def move(self, direction):
		assert self.camera.getPos() != None, f"base.camera doesn't return a position when queried"
		if direction == 'left':
			self.camera.setPos(self.camera.getPos() + Vec3(-1,0,0))
		elif direction == 'right':
			self.camera.setPos(self.camera.getPos() + Vec3(1,0,0))
		elif direction == 'fwd':
			self.camera.setPos(self.camera.getPos() + Vec3(0,1,0))
		elif direction == 'back':
			self.camera.setPos(self.camera.getPos() + Vec3(0,-1,0))
		elif direction == 'down':
			self.camera.setPos(self.camera.getPos() + Vec3(0,0,-1))
		elif direction == 'up':
			self.camera.setPos(self.camera.getPos() + Vec3(0,0,1))
		elif direction == 'zoomIn':
			#self.camera.setScale(self.camera.getScale()*0.8)
			self.camera.setPos(self.camera.getPos() + Vec3(0,1,-1))
		elif direction == 'zoomOut':
			#self.camera.setScale(self.camera.getScale()*1.2)
			self.camera.setPos(self.camera.getPos() + Vec3(0,-1,1))

	# ray-based tile picker for placing down towers
	def towerPlaceTask(self, task):
		if (self.fsm.state == 'PickTower'): # if the tower placer is on
			if self.hitTile != None: 			# clear highlighting on non-hovered tiles
				for tile in self.tileMap.getChildren():
					if tile != self.hitTile:
						#tile.findTexture(self.tileTS).load(self.groundPNM)
						tile.setTexture(self.tileTS, self.groundTex, 1)
					#tile.setColor(1.,1.,1.,1.)
					#print(tile.ls())
				#self.hitTile = None

			if (self.mouseWatcherNode.hasMouse()): # condition to protect from NaN when offscreen
				# get mouse position and traverse tileMap with the pickerRay
				mousePos = base.mouseWatcherNode.getMouse()
				self.tilePickerRay.setFromLens(base.camNode, mousePos.x, mousePos.y)
				self.tilePicker.traverse(self.tileMap)

				if (self.tpQueue.getNumEntries() > 0): 	# when mouse ray collides with tiles:
					# sort by closest first
					self.tpQueue.sortEntries() 
					# # find tile node and get tile index
					tileColl = self.tpQueue.getEntry(0).getIntoNodePath()
					#self.hitTile = tileColl.getNode(1)
					print(tileColl)
					if (tileColl.getTag("TILEground") != ""):
						# highlight on mouseover
						tileInd = int(tileColl.getTag("TILEground"))
						self.hitTile = self.tileMap.getChild(tileInd)
						self.hitTile.setTexture(self.tileTS, self.highlightTex, 1)
					# tileColl = self.tpQueue.getEntry(0).getIntoNodePath().getNode(1)
					# tileInd = int(tileColl.getName().split("-")[1]) # trim name to index
					# # highlight on mouseover
					# self.hitTile = self.tileMap.getChild(tileInd)
					# print("highlighting: " + str(self.hitTile))
					# #self.hitTile.set_texture(self.tileTS, self.tileHighlight, 1)
					# self.hitTile.setColor(1.2,1.2,1.2,1.)
					#self.hitTile.findTexture(self.tileTS).load(self.tileHighlight)
					#print(tileInd)

		return Task.cont
	
	def spawnEnemy(self, pos, facing): 				# spawn an individual creep
		newEnemy = spritem.Enemy("enemy-" + str(self.enemyCount), pos, facing, 1.)
		self.enemyCount += 1
		self.enemies.append(newEnemy)

	def spawnEnemyWave(self, num, pos): 	# spawn a wave of creeps
		global waveNum
		waveNum += 1

		print("Spawning wave " + str(waveNum))
		self.spawnSeq = Sequence() 
		if pos == self.fsm.spawner[1]: facing = 'BottomLeft'
		elif pos == self.fsm.spawner[2]: facing = 'BottomRight'
		elif pos == self.fsm.spawner[3]: facing = 'TopRight'
		elif pos == self.fsm.spawner[4]: facing = 'TopLeft'
		else: raise ValueError('Enemies spawning in an unapproved location [base.spawnEnemyWave]')
		for _ in range(num):
			self.spawnSeq.append(Func(self.spawnEnemy,pos,facing))
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
		newTower = Buildings.Tower(pos)
		# add to list to allow pausing of sequences
		self.towers.append(newTower)
		return newTower

	def buyTower(self):
		global playerGold
		if playerGold >= 10:
			playerGold -= 10
			self.fsm.demand('PickTower')
		else:
			# TODO: show hoverover tip that you can't afford this card
			self.popupText("broke bitch",2)
			pass

	def offerCard(self):
		#self.fsm.setClickWaitingFalse()
		newTowerCM = CardMaker('newTowerCard')
		newTowerCM.setFrame(-0.5,0.,-0.605,0.)
		self.newTowerCard = aspect2d.attachNewNode(newTowerCM.generate())
		self.newTowerCard.setPos(-0.2,0.,0.5)
		self.newTowerCard.setScale(1.4)
		#self.newTowerCard.reparentTo(aspect2d)
		newTowerCTex = loader.loadTexture('assets/card-buildTower.png')
		self.newTowerCard.setTexture(newTowerCTex)

	def takeOfferedCard(self):
		# TODO: add a sexy, sparkly animation for taking the card
		self.newTowerCard.removeNode()

	def startGame(self): 	# remove all towers, enemies etc and prepare the game start-state
		global waveNum, playerGold, castleHP
		
		waveNum = 0
		playerGold = 0
		castleHP = 100

	def dmgCastle(self, dmg):
		global castleHP
		if testing: print("Castle taking " + str(dmg) + " damage!")
		castleHP -= dmg

	def drawText(self, dialogueString):
		# generate text
		dialogueText = TextNode('dialogueText')
		# dialogueText.setFont(TextFont)
		dialogueText.setText(dialogueString)
		# probably need to use dialogueText.calcWidth(string) or dialogueText.setWordwrap(float) for varying text output
		# dialogueText.setSlant(float) needed for Traveller dialogue
		# use dialogueText.setGlyphScale(float) and dialogueText.setGlyphShift(float) for wobbly, missized text
		dialogueText.setTextColor(1.,1.,1.,1.) # n.b. should change for different characters
		dialogueText.setShadow(0.1, 0.1)
		dialogueText.setShadowColor(0,0,0,0.6)
		dialogueText.setCardColor(0.1,0.1,0.1,0.2)
		# note that method dialogueText.setCardTexture(texture) exists
		dialogueText.setCardAsMargin(0.5,0.5,0.5,0.1)
		dialogueText.setCardDecal(True)
		dialogueText.setFrameCorners(True)
		dialogueTextNP = aspect2d.attachNewNode(dialogueText)
		dialogueTextNP.setScale(0.1)
		dialogueTextNP.setPos(-1.4,0.,-0.6)

		return dialogueTextNP

	def popupText(self, textString, duration):
		# generate text
		popupText = TextNode('popupText-'+str(duration)+'s')
		# popupText.setFont(TextFont)
		popupText.setText(textString)
		# probably need to use dialogueText.calcWidth(string) or dialogueText.setWordwrap(float) for varying text output
		# dialogueText.setSlant(float) needed for Traveller dialogue
		# use dialogueText.setGlyphScale(float) and dialogueText.setGlyphShift(float) for wobbly, missized text
		popupText.setTextColor(1.,1.,1.,1.) # n.b. should change for different characters
		popupText.setShadow(0.1, 0.1)
		popupText.setShadowColor(0,0,0,0.6)
		popupText.setCardColor(0.1,0.1,0.1,0.2)
		# note that method popupText.setCardTexture(texture) exists
		popupText.setCardAsMargin(0.5,0.5,0.5,0.1)
		popupText.setCardDecal(True)
		popupText.setFrameCorners(True)
		popupTextNP = aspect2d.attachNewNode(popupText)
		popupTextNP.setScale(0.1)
		popupTextNP.setPos(-1.4,0.,-0.6)
		Sequence(Wait(duration),popupTextNP.colorScaleInterval(1,(1.,1.,1.,0.)),Func(popupTextNP.removeNode)).start()

		return popupTextNP

	def quit(self): 		# exit the game in a reasonable fashion
		self.fsm.cleanup()
		base.userExit()

app = DuckOfCards()
app.run()
