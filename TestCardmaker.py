from direct.showbase.ShowBase import ShowBase
from panda3d.core import CardMaker, loadPrcFileData, Shader, ShaderInput, TextNode #, TextureStage,
from panda3d.core import Texture, SamplerState, CollisionBox, CollisionNode, BitMask32, Point3
from panda3d.core import CollisionRay, CollisionTraverser, CollisionHandlerQueue, Vec3
from direct.actor.Actor import Actor
from direct.interval.FunctionInterval import Wait
from direct.interval.LerpInterval import LerpHprInterval
from math import sin, sqrt
from direct.fsm.FSM import FSM

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

class SpriteMod(FSM):
	def __init__(self, name, pos, speed):
		# TODO this can be cleaned up using a defaultFilter(self, request, args) method 
		# 	and a lookup table {('TopRight','Right'):'BottomRight',('TopRight','Left'):'TopLeft'} etc

		FSM.__init__(self, (str(name) + 'FSM')) # must be called when overloading

		#self.pos = pos
		self.speed = speed
		self.period = 90. / speed

		self.node.setH(45)

	def defaultFilter(self, request, args):
		return 'BottomLeft'

	def enterTopLeft(self):
		# TODO lerp round
		#print(self.node.getX(), self.node.getY(), self.node.getZ())
		print(str(self.node) + " facing top left")
		#self.node.lookAt(self.tlNode)
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()

	#def exitTopLeft(self):
	#	#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)

	def filterTopLeft(self, request, args): # process input while facing the top left (-x,+y)
		if (request == 'Left'):
			return 'BottomLeft'
		elif (request == 'Right'):
			return 'TopRight'
		elif (request == 'Flip'):
			return 'BottomRight'
		else:
			return None

	def enterTopRight(self):
		# TODO lerp round
		print(str(self.node) + " facing top right")
		#self.node.lookAt(self.trNode)
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()
		#self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
		#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)
		#self.node.setTexHpr(TextureStage.getDefault(), 0,180,0)
		#self.node.setTexRotate(self.node.findAllTextureStages()[0], 180)

	#def exitTopRight(self):
	#	self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])	
	#	#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)
	#	#self.node.setTexHpr(TextureStage.getDefault(), 0,0,0)

	def filterTopRight(self, request, args): # process input while facing top right (+x,+y)
		if (request == 'Left'):
			return 'TopLeft'
		elif (request == 'Right'):
			return 'BottomRight'
		elif (request == 'Flip'):
			return 'BottomLeft'
		else:
			return None

	def enterBottomRight(self):
		# TODO lerp round
		print(str(self.node) + " facing bottom right")
		#self.nodepath.set_scale(self.nodepath.get_scale()[0],self.nodepath.get_scale()[1]*-1,self.nodepath.get_scale()[2])
		#self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
		#self.node.lookAt(self.brNode)
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()

	#def exitXneg(self):	
	#	self.nodepath.set_scale(self.nodepath.get_scale()[0],self.nodepath.get_scale()[1]*-1,self.nodepath.get_scale()[2])
	#	#self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
		
	def filterBottomRight(self, request, args): # process input while facing bottom right (+x,-y)
		if (request == 'Left'):
			return 'TopRight'
		elif (request == 'Right'):
			return 'BottomLeft'
		elif (request == 'Flip'):
			return 'TopLeft'
		else:
			return None

	def enterBottomLeft(self):
		# TODO lerp round
		print(str(self.node) + " facing bottom left")
		#self.node.lookAt(self.blNode)
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()
		#self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
		#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)

	#def exitYneg(self):
	#	self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
	#	self.nodepath.set_scale(0.05,0.05,0.05)
	#	#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)

	def filterBottomLeft(self, request, args): # process input while facing bottom left (-x,+y)
		if (request == 'Left'):
			return 'BottomRight'
		elif (request == 'Right'):
			return 'TopLeft'
		elif (request == 'Flip'):
			return 'TopRight'
		else:
			return None

class NormalInnocentDuck(SpriteMod): 
	def __init__(self, name, pos, speed):
		#self.model = Actor("assets/duckboard1.gltf")
		self.model = loader.loadModel("assets/duckboard1.gltf")
		self.model.setScale(0.1)
		self.model.setP(90)
		self.node = render.attachNewNode("duck-" + str(name))
		self.model.reparent_to(self.node)
		self.node.setPos(pos)
		#self.nodepath = base.duckModel.instanceTo(self.node)
		# self.nodepath.setR(90)
		# self.nodepath.setH(90)
		super().__init__(str(name), pos, speed)
		#print("spawning a normal duck")
		#self.demand('BottomRight')
		#self.speed = speed

		self.hp = 1000000

		# temporary integer ticker to rotate the random duck
		self.t = 0

		base.taskMgr.add(self.updateDuck, "update-"+str(self.node), taskChain='default')
	
	def updateDuck(self, task):
		#if base.fsm.state == 'Gameplay':
		self.t += int(1 * self.speed)
		
		# rotate the random duck
		if ((self.t % 90) == 1):
			#print("duck turning")
			self.demand('Right')
			#self.turnRight()

		return task.cont

	#def turnRight(self):
	#	self.demand('Right')

	#def turnLeft(self):
	#	self.demand('Left')

	#def turnAround(self):
	#	self.demand('Flip')

class Enemy(SpriteMod):
	def __init__(self, name, pos, facing, speed):
		assert pos != None, f'Enemy spawning with no position!'

		self.model = loader.loadModel("assets/dogboard1.gltf")
		self.model.setP(90)
		#self.model.setH(45)
		self.model.setScale(0.1)
		#self.model.setPos(0.,0.,.8)
		self.node = base.enemyModelNd.attachNewNode("enemy-" + str(name))
		self.model.reparent_to(self.node)
		self.node.setPos(pos + Vec3(0.,0.,0.))
		#self.node.show()
		#self.node.setScale(0.0001)
		#self.nodepath = base.enemyModel.instanceTo(self.node)
		super().__init__(str(name), pos, speed)
		assert (facing == 'TopLeft' or facing == 'TopRight' or facing == 'BottomLeft' or facing == 'BottomRight'), f'Enemy generated with incorrect direction to face!'
		print(str(name) + " spawning")

		#self.node.setColor(1.,0.5,0.5,1.)

		# debug:
		print(str(self.node) + " spawned at " + str(self.node.getPos()))
		assert (self.node.getPos()[0] != 0 or self.node.getPos()[1] != 0), f'Enemy spawning at 0,0!'
		#self.node.setH(-30)
		# modified target vector to prevent enemies flying into air or sinking into ground as they approach castle
		#self.targetPos = base.castle.model.getPos() - Vec3(0.,0.,.5)

		# define dying tag and set to False until enemy loses all HP
		self.dying = False

		#self.nodepath.setH(90)
		# make them look where they're going
		self.demand(facing)
		#if (self.node.getPos()[0] > 1):
		#	self.demand('Xneg')
		#elif (self.node.getPos()[1] > 1):
		#	self.demand('Yneg')
		#elif (self.node.getPos()[0] < -1):
		#	self.demand('X')
		#else: 
		#	# this condition should be fine due to the assertion, but could always leave it to throw an error
		#	self.demand('Y')
		#self.node.lookAt(self.targetPos)
		#if (self.targetPos.getX() - self.nodepath.getPos()[0] > 2 or self.targetPos.getX() - self.nodepath.getPos()[0] < -2):
		#	# entity and target x are more than 2 units apart
		#	if (self.targetPos.getX() > self.nodepath.getPos()[0]): # target is further 'up' x relative to entity
		#		self.demand('X')
		#		#print(str(self.node)+" facing X")
		#	else: 								# target is lower down x-axis relative to entity
		#		self.demand('Xneg')
		#		#print(str(self.node)+" facing Xneg")
		#else: # entity and target x are less than 2 units apart (aligned on x axis)
		#	if (self.targetPos.getY() > self.nodepath.getPos()[1]): # target is further 'up' y relative to entity
		#		self.demand('Y')
		#		#print(str(self.node)+" facing Y")
		#	else: 								# target is lower down y-axis relative to entity
		#		self.demand('Yneg')
		#		#print(str(self.node)+" facing Yneg")

		self.hp = 20.0
						#CollisionCapsule(ax, ay, az, bx, by, bz, radius)
		#self.hitSphere = CollisionCapsule(0., -0.25, 0.75, 0., 0.2, 0.75, .125)
		#hcnode = CollisionNode('{}-cnode'.format(str(self.node)))
		#hcnode.setIntoCollideMask(BitMask32(0x02))
		#self.hitNp = self.node.attachNewNode(hcnode)
		#self.hitNp.node().addSolid(self.hitSphere)
		#self.hitNp.show() 								# uncomment to show hitbox

		#self.move = self.node.posInterval(30./self.speed, self.targetPos, self.node.getPos())
		#self.moveSeq = Sequence(
		#	self.move,
		#	Func(self.despawnAtk)
		#)

		#self.dmgSeq = Sequence(Func(self.node.setColor,1.,0.,0.,1.),
		#		Wait(0.05),
		#		Func(self.node.setColor,1.,0.5,0.5,1.))

		#self.moveSeq.start()

		base.taskMgr.add(self.updateEnemy, "update_"+str(self.node), taskChain='default')

	def updateEnemy(self, task):
		if (self.hp <= 0.0): # die if health gets too low
			#self.despawnDie()
			return task.done
		# otherwise, keep going :)
		return task.cont

	# def despawnAtk(self):
	# 	# damage the castle
	# 	# and do a wee animation?
	# 	base.castle.takeDmg()

	# 	# clean up the node
	# 	print(str(self.node) + " despawning")
	# 	# make sure this doesn't get called multiple times
	# 	self.dying = True
	# 	# stop moving and don't blink
	# 	self.moveSeq.clearIntervals()
	# 	self.dmgSeq.clearIntervals()
	# 	# remove update task from taskMgr
	# 	if (base.taskMgr.getTasksNamed(str(self.node)+"_update") != None):
	# 		base.taskMgr.remove(base.taskMgr.getTasksNamed(str(self.node)+"_update"))
	# 	# clean up node
	# 	self.node.removeNode() 	

	def despawnDie(self):
		# make sure this doesn't get called multiple times
		self.dying = True
		print(str(self.node) + " dying")
		# stop moving and don't blink
		self.moveSeq.clearIntervals()
		self.dmgSeq.clearIntervals()
		# remove update task from taskMgr
		if (base.taskMgr.getTasksNamed(str(self.node)+"_update") != None):
			base.taskMgr.remove(base.taskMgr.getTasksNamed(str(self.node)+"_update"))
		# do a wee animation?
		# give player gold
		base.giveGold(5)
		# clean up the node
		self.node.removeNode() 

	def damage(self, dmg):
		# take the damage
		self.hp -= dmg

		# check that it's not already in the process of despawning
		if not self.dying:
			# flash red for a moment
			if self.hp > 0: self.dmgSeq.start()
			else: # die if hp is 0 or less
				self.despawnDie()
		# this seems to cause despawnDie to run twice, somehow. I should do proper garbage collection
		# on these objects, and remove the enemies as well as their nodes

class Tower():
	def __init__(self, pos):
		towerModel = base.loader.loadModel("assets/tower.gltf")
		towerModel.setScale(0.2)
		towerModel.setP(90)
		self.node = render.attachNewNode("tower")
		towerModel.wrtReparentTo(self.node)
		self.node.setPos(pos)
		#self.node.setP(180)
		#self.node.setScale()
		self.rateOfFire = 1.0
		self.damage = 1.0
		self.range = 5.0
		self.cooldown = 3.0
		self.onCD = True

class DuckBase(ShowBase):
	def __init__(self):		#			=========================
		ShowBase.__init__(self)

		# disable default editor mouse behaviour
		#base.disableMouse()

		# ticker
		self.t = 0.
		self.inDialogue = False
		self.set_background_color(0.6,0.6,0.6,1.)

		#self.dialogue = ["QUACK! I mean QUICK! Attackers are at the gates!\nThere's no time to explain- you, traveller!",
		#					"> ...", "Yes, you! What's your name?", 
		#					"Wait- there's no TIME! Take this;\nit is one of my fine and valuable magic cards.",
		#					"It will summon a magical tower to defend\nthe innocent ducks of the pond\nwherever you place it."]

		self.card_maker = CardMaker('card')
		self.card_maker.setHasUvs(1)
		self.card_maker.clearColor()

		# generate tiles
		self.generateTerrain()

		# create dialogue UI
		#self.enterDialogue()

		randomDuck = NormalInnocentDuck("an_innocent_duck", Vec3(-1.,5.,0.), 1.5)
		self.enemyModelNd = render.attachNewNode("enemyNodes")
		newEnemy = Enemy("enemy-" + str(0), Vec3(1,5,0), 'TopRight', 1.)
		newTower = Tower(Vec3(0,4,0))

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

		# render.clear_material()
		# for ts in render.find_all_texture_stages():
		# 	render.clear_texture(ts)

		# initialise camera position and angle:
		self.camera.setPos(0.,-5.,0.)
		#self.camera.lookAt(0.,0.,0.)
		#self.camera.lookAt(randomDuck.model)

		# listen for left-clicks
		#self.accept("mouse1", self.onMouse)

		#self.taskMgr.add(self.tilePickerWatcher, 'tilePickerWatcher', taskChain='default')
		#self.taskMgr.add(self.update, "update", taskChain='default')

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

		# self.hilightCard = self.render.attachNewNode(card_maker.generate())
		# self.hilightCard.setPos(0.,0.,-10.)
		# self.hilightCard.setHpr(0., -90., 45.)
		self.highlightTex = loader.loadTexture("../duck-of-cards/assets/ground-tile-highlight_4.png")
		self.highlightTex.setWrapU(Texture.WM_clamp)
		self.highlightTex.setWrapV(Texture.WM_clamp)
		self.highlightTex.setMagfilter(SamplerState.FT_nearest)
		self.highlightTex.setMinfilter(SamplerState.FT_nearest)

		self.hilightCard = self.render.attachNewNode(self.card_maker.generate())
		self.hilightCard.setPos(0.,0.,-11.)
		self.hilightCard.setHpr(0., -90., 45.)
		highlightTile = loader.loadTexture("../duck-of-cards/assets/ground-tile-highlight_4.png")
		highlightTile.setWrapU(Texture.WM_clamp)
		highlightTile.setWrapV(Texture.WM_clamp)
		highlightTile.setMagfilter(SamplerState.FT_nearest)
		highlightTile.setMinfilter(SamplerState.FT_nearest)

		tileInd = 0
		for x in range(width):
			for y in range(height):
				tileInd += 1
				tile = self.render.attachNewNode(self.card_maker.generate())#"tileGRASS"+str(x)+":"+str(y)+"-"+str(tileInd)
				tile.setPos(x-y,x+y-50,0.)
				tile.setHpr(0., -90., 45.)
				tile.setTransparency(1)

				#tileHitbox = CollisionBox(Point3(0, 0, -0.1),Point3(1.4, 1.4, .01))
				#tileColl = CollisionNode('cnode_'+str(tile))
				#print(self.centreTile.getTightBounds())

				tileHitbox = CollisionBox(Point3(0., 0., -0.1),Point3(1., 1., 0.1))
				tileColl = CollisionNode(str(tile)+'-cnode')
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

	#def update(self, task):
		#if (self.inDialogue):
		#	
		#self.t += 0.01
		#print(self.cardnp.getPos())
		#sint = sin(self.t)
		#self.cardnp.setPos(2. * sint,0.,0.)
		#self.cardnp.setHpr(180. * sint, 0., 0.)
		#self.cardnp.setColor(sint*sint,1-sint*sint,1.)
		#return task.cont

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

	# def onMouse(self):
	# 	if (self.clickWaiting):
	# 		self.dialogueStep += 1
	# 		if (self.dialogueStep < len(self.dialogue)):
	# 			self.dialogueTextNP.node().setText(self.dialogue[self.dialogueStep])
	# 			Wait(1)
	# 		else:
	# 			self.exitDialogue()
	# 			self.clickWaiting = False
	# 	#if(self.hitTile != None):
	# 	#		self.hilightCard.instanceTo(self.hitTile)

app = DuckBase()
app.run()
