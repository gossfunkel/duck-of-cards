from direct.showbase.ShowBase import ShowBase
from panda3d.core import CardMaker, loadPrcFileData, Shader, ShaderInput, TextNode #, TextureStage,
from panda3d.core import Texture, SamplerState, CollisionBox, CollisionNode, BitMask32, Point3
from panda3d.core import CollisionRay, CollisionTraverser, CollisionHandlerQueue
from direct.interval.FunctionInterval import Wait
from math import sin, sqrt

config_vars = """
win-size 1200 800
show-frame-rate-meter 1
hardware-animated-vertices true
basic-shaders-only false
threading-model Cull/Draw
"""
loadPrcFileData("", config_vars)

width = 100
height = 100

class DuckBase(ShowBase):
	def __init__(self):		#			=========================
		ShowBase.__init__(self)

		# disable default editor mouse behaviour
		#base.disableMouse()

		# ticker
		self.t = 0.
		self.inDialogue = False
		self.set_background_color(0.6,0.6,0.6,1.)

		self.dialogue = ["QUACK! I mean QUICK! Attackers are at the gates!\nThere's no time to explain- you, traveller!",
							"> ...", "Yes, you! What's your name?", 
							"Wait- there's no TIME! Take this;\nit is one of my fine and valuable magic cards.",
							"It will summon a magical tower to defend\nthe innocent ducks of the pond\nwherever you place it."]

		self.card_maker = CardMaker('card')
		self.card_maker.setHasUvs(1)
		self.card_maker.clearColor()

		# generate tiles
		self.generateTerrain()

		# create dialogue UI
		self.enterDialogue()

		#initialise the tile picker
		# self.tPickerRay = CollisionRay()
		# self.tilePicker = CollisionTraverser()
		# self.tpQueue = CollisionHandlerQueue()
		# tpNode = CollisionNode('tp-node')
		# tpNode.setFromCollideMask(BitMask32(0x01))
		# tpNp = self.cam.attachNewNode(tpNode)
		# tpNode.addSolid(self.tPickerRay)
		# self.tilePicker.addCollider(tpNp, self.tpQueue)
		# self.hitTile = None
		#UNCOMMENT FOR DEBUG 
		#self.tilePicker.showCollisions(render)
		#tpNp.show()

		# initialise camera position and angle:
		self.cam.setPos(0.,-20.,10.)
		self.cam.lookAt(0.,0.,0.)

		# listen for left-clicks
		self.accept("mouse1", self.onMouse)

		#self.taskMgr.add(self.tilePickerWatcher, 'tilePickerWatcher', taskChain='default')
		self.taskMgr.add(self.update, "update", taskChain='default')

	# LOADING FUNCTIONS: 				=========================

	def generateTerrain(self):
		#card_maker.setColor(1.,1.,1.,1.)
		self.tileScaleFactor = sqrt(2) # pythagoras; turning squares sideways makes triangles maybe?
		self.card_maker.setFrame(0.,self.tileScaleFactor,0.,self.tileScaleFactor)

		self.groundTex = loader.loadTexture("../duck-of-cards/assets/ground-tile_4.png")
		self.groundTex.setWrapU(Texture.WM_clamp)
		self.groundTex.setWrapV(Texture.WM_clamp)
		self.groundTex.setMagfilter(SamplerState.FT_nearest)
		self.groundTex.setMinfilter(SamplerState.FT_nearest)

<<<<<<< HEAD
		# self.hilightCard = self.render.attachNewNode(card_maker.generate())
		# self.hilightCard.setPos(0.,0.,-10.)
		# self.hilightCard.setHpr(0., -90., 45.)
		self.highlightTex = loader.loadTexture("../duck-of-cards/assets/ground-tile-highlight_4.png")
		self.highlightTex.setWrapU(Texture.WM_clamp)
		self.highlightTex.setWrapV(Texture.WM_clamp)
		self.highlightTex.setMagfilter(SamplerState.FT_nearest)
		self.highlightTex.setMinfilter(SamplerState.FT_nearest)
=======
		self.hilightCard = self.render.attachNewNode(card_maker.generate())
		self.hilightCard.setPos(0.,0.,-11.)
		self.hilightCard.setHpr(0., -90., 45.)
		highlightTile = loader.loadTexture("../duck-of-cards/assets/ground-tile-highlight_4.png")
		highlightTile.setWrapU(Texture.WM_clamp)
		highlightTile.setWrapV(Texture.WM_clamp)
		highlightTile.setMagfilter(SamplerState.FT_nearest)
		highlightTile.setMinfilter(SamplerState.FT_nearest)
>>>>>>> 38eab376c5c0e91543f7992dcfcb5b95b1bd8221

		tileInd = 0
		for x in range(width):
			for y in range(height):
				tileInd += 1
				tile = self.render.attachNewNode(self.card_maker.generate())#"tileGRASS"+str(x)+":"+str(y)+"-"+str(tileInd)
				tile.setPos(x-y,x+y-50,0.)
				tile.setHpr(0., -90., 45.)
				tile.setTransparency(1)

<<<<<<< HEAD
				tileHitbox = CollisionBox(Point3(0, 0, -0.1),Point3(1.4, 1.4, .01))
				tileColl = CollisionNode('cnode_'+str(tile))
=======
<<<<<<< HEAD
				print(self.centreTile.getTightBounds())

				tileHitbox = CollisionBox(Point3(0., 0., -0.1),Point3(1., 1., 0.1))
=======
				tileHitbox = CollisionBox(Point3(0., 0., -0.1),Point3(1., 1., .2))
>>>>>>> 2635c5e8558aade14953e2503ef2c102322a6c10
				tileColl = CollisionNode(str(tile)+'-cnode')
>>>>>>> 38eab376c5c0e91543f7992dcfcb5b95b1bd8221
				tileColl.setIntoCollideMask(BitMask32(0x01))
				if (x != 50 or y != 50):
					tileColl.setTag("TILEground",str(tileInd))
					tile.setTexture(self.groundTex, 1)
				else:
					tileColl.setTag("TILEpond",str(tileInd))
					tile.setTexture(loader.loadTexture("maps/noise.rgb"), 1)
				colliderNp = tile.attachNewNode(tileColl)
				colliderNp.setHpr(0., 90., 0.)
				colliderNp.node().addSolid(tileHitbox)
				#colliderNp.show()

	def enterDialogue(self):
		# generate a black fade from the bottom of the screen for the character background
		self.card_maker.setFrameFullscreenQuad()
		self.fadeBoxBack = self.render2d.attachNewNode(self.card_maker.generate())
		self.fadeBoxBack.setTransparency(1)
		fadeShader = Shader.load(Shader.SL_GLSL,
					 vertex="default.vert",
                     fragment="darkFade.frag")
		self.fadeBoxBack.setShader(fadeShader)
		self.fadeBoxBack.setShaderInput(ShaderInput('range',0.8))

		# display the sprite of the character addressing the player
		self.card_maker.setFrame(-0.1,1.,-1.,0.65)
		self.characterSprite = self.render2d.attachNewNode(self.card_maker.generate())
		self.characterSprite.setTransparency(1)
		self.characterSprite.setTexture(loader.loadTexture("assets/theDuke-sprite_ready.png"))

		# generate a black fade from the bottom of the screen for the text background
		self.card_maker.setFrameFullscreenQuad()
		self.fadeBoxFront = self.render2d.attachNewNode(self.card_maker.generate())
		self.fadeBoxFront.setTransparency(1)
		fadeShader = Shader.load(Shader.SL_GLSL,
					 vertex="default.vert",
                     fragment="darkFade.frag")
		self.fadeBoxFront.setShader(fadeShader)
		self.fadeBoxFront.setShaderInput(ShaderInput('range',1.4))

		self.inDialogue = True
		self.dialogueStep = 0
		
		self.dialogueTextNP = self.drawText(self.dialogue[self.dialogueStep])
		#wait for user to click
		self.clickWaiting = True
		

	def exitDialogue(self):
		# remove the dialogue box
		self.dialogueTextNP.removeNode()
		self.fadeBoxBack.removeNode()
		self.characterSprite.removeNode()
		self.fadeBoxFront.removeNode()

		self.inDialogue = False

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
		# note dialogueText.setCardTexture(texture) exists
		dialogueText.setCardAsMargin(0.5,0.5,0.5,0.1)
		dialogueText.setCardDecal(True)
		dialogueText.setFrameCorners(True)
		dialogueTextNP = aspect2d.attachNewNode(dialogueText)
		dialogueTextNP.setScale(0.1)
		dialogueTextNP.setPos(-1.4,0.,-0.6)

		return dialogueTextNP

	# TASKS/PROCESSES: 					=========================

	def update(self, task):
		#if (self.inDialogue):
		#	
		#self.t += 0.01
		#print(self.cardnp.getPos())
		#sint = sin(self.t)
		#self.cardnp.setPos(2. * sint,0.,0.)
		#self.cardnp.setHpr(180. * sint, 0., 0.)
		#self.cardnp.setColor(sint*sint,1-sint*sint,1.)
		return task.cont

	#def tilePickerWatcher(self, task):
		# if self.hitTile != None: 			# clear highlighting on non-hovered tiles
		# 	self.hitTile.setTexture(self.groundTex,1)
		# 	#for tile in self.tileMap.getChildren():
		# 		#if tile != self.hitTile:
		# 		#tile.findTexture(self.tileTS).load(self.groundPNM)
		# 		#tile.setTexture(self.tileTS, self.groundTex, 2)
		# 		#print(tile.ls())
		# 	self.hitTile = None
		# if (self.mouseWatcherNode.hasMouse()): # condition to protect from NaN when offscreen
		# 	# get mouse position and traverse tileMap with the pickerRay
		# 	mousePos = self.mouseWatcherNode.getMouse()
		# 	self.tPickerRay.setFromLens(self.camNode, mousePos.getX(), mousePos.getY())
		# 	self.tilePicker.traverse(self.render)

		# 	if (self.tpQueue.getNumEntries() > 0): 	# when mouse ray collides with tiles:
		# 		# sort by closest first
		# 		self.tpQueue.sortEntries() 
		# 		# find tile node and get tile index
		# 		tileColl = self.tpQueue.getEntry(0).getIntoNodePath()
		# 		#self.hitTile = tileColl.getNode(1)
		# 		#print(tileColl)
		# 		if (tileColl.getTag("TILEground") != ""):
		# 			# highlight on mouseover
		# 			tileInd = int(tileColl.getTag("TILEground"))
		# 			self.hitTile = self.render.getChild(tileInd)
		# 			self.hitTile.setTexture(self.highlightTex,1)
				
		# 		#print("highlighting: " + str(self.hitTile))
		# 		#self.hitTile.set_texture(self.tileTS, self.tileHighlight, 1)
		# 		#self.hitTile.findTexture(self.tileTS).load(self.tileHighlight)
		# 		#print(tileInd)

	#	return task.cont

	# CALLABLE FUNCTIONS/EVENTS: 		=========================

	def onMouse(self):
		if (self.clickWaiting):
			self.dialogueStep += 1
			if (self.dialogueStep < len(self.dialogue)):
				self.dialogueTextNP.node().setText(self.dialogue[self.dialogueStep])
				Wait(1)
			else:
				self.exitDialogue()
				self.clickWaiting = False
		#if(self.hitTile != None):
		#		self.hilightCard.instanceTo(self.hitTile)

app = DuckBase()
app.run()
