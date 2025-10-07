from direct.showbase.ShowBase import ShowBase
from panda3d.core import CardMaker, loadPrcFileData#, TextureStage
from panda3d.core import Texture, SamplerState, CollisionBox, CollisionNode, BitMask32, Point3
from panda3d.core import CollisionRay, CollisionTraverser, CollisionHandlerQueue
from math import sin

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
		self.set_background_color(0.,0.,0.,1.)

		# generate tiles
		self.generateTerrain()

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

		# initialise camera position and angle:
		self.cam.setPos(0.,-20.,10.)
		self.cam.lookAt(0.,0.,0.)

		# listen for left-clicks
		self.accept("mouse1", self.onMouse)

		self.taskMgr.add(self.tilePickerWatcher, 'tilePickerWatcher', taskChain='default')
		self.taskMgr.add(self.update, "update", taskChain='default')

	# LOADING FUNCTIONS: 				=========================

	def generateTerrain(self):
		card_maker = CardMaker('card')
		#card_maker.setColor(1.,1.,1.,1.)
		card_maker.setFrame(-1.,1.,-1.,1.)
		card_maker.setHasUvs(1)
		card_maker.clearColor()
		self.centreTile = self.render.attachNewNode(card_maker.generate())
		self.centreTile.setPos(0.,0.,-10.)
		self.centreTile.setHpr(0., -90., 45.)

		groundTile = loader.loadTexture("../duck-of-cards/assets/ground-tile_4.png")
		groundTile.setWrapU(Texture.WM_clamp)
		groundTile.setWrapV(Texture.WM_clamp)
		groundTile.setMagfilter(SamplerState.FT_nearest)
		groundTile.setMinfilter(SamplerState.FT_nearest)
		self.centreTile.setTexture(groundTile, 1)
		self.centreTile.setTransparency(1)

		self.hilightCard = self.render.attachNewNode(card_maker.generate())
		self.hilightCard.setPos(0.,0.,-10.)
		self.hilightCard.setHpr(0., -90., 45.)
		highlightTile = loader.loadTexture("../duck-of-cards/assets/ground-tile-highlight_4.png")
		highlightTile.setWrapU(Texture.WM_clamp)
		highlightTile.setWrapV(Texture.WM_clamp)
		highlightTile.setMagfilter(SamplerState.FT_nearest)
		highlightTile.setMinfilter(SamplerState.FT_nearest)

		tileInd = 0
		for x in range(width):
			#x -= width/2
			#x -= 0.5
			for y in range(height):
				#y -= height/2
				#y -= 0.5
				tileInd += 1
				tile = self.render.attachNewNode("tileGRASS"+str(x)+":"+str(y)+"-"+str(tileInd))
				tileScaleFactor = 1.4
				#tilex = lambda x, y : (tileScaleFactor*x - y*tileScaleFactor)
				#tiley = lambda x, y : (tileScaleFactor*x + y*tileScaleFactor) - 50.*tileScaleFactor
				tilex = tileScaleFactor*x - y*tileScaleFactor
				tiley = (tileScaleFactor*x + y*tileScaleFactor) - 50.*tileScaleFactor
				tile.setPos(tilex,tiley,0.)

				tileHitbox = CollisionBox(Point3(0., 0., -0.1),Point3(1.9, 1.9, 0.1))
				tileColl = CollisionNode(str(tile)+'-cnode')
				tileColl.setIntoCollideMask(BitMask32(0x01))
				colliderNp = tile.attachNewNode(tileColl)
				#colliderNp.setPos(tilex/100000,tiley/100000 - 1.,-.1)
				colliderNp.setPos(tilex,tiley,-10.)
				#colliderNp.setHpr(45., 0., 0.)
				colliderNp.node().addSolid(tileHitbox)
				colliderNp.show()

				self.centreTile.instanceTo(tile)

	# TASKS/PROCESSES: 					=========================

	def update(self, task):
		#self.t += 0.01
		#print(self.cardnp.getPos())
		#sint = sin(self.t)
		#self.cardnp.setPos(2. * sint,0.,0.)
		#self.cardnp.setHpr(180. * sint, 0., 0.)
		#self.cardnp.setColor(sint*sint,1-sint*sint,1.)
		return task.cont

	def tilePickerWatcher(self, task):
		if self.hitTile != None: 			# clear highlighting on non-hovered tiles
			#for tile in self.tileMap.getChildren():
				#if tile != self.hitTile:
				#tile.findTexture(self.tileTS).load(self.groundPNM)
				#tile.setTexture(self.tileTS, self.groundTex, 2)
				#print(tile.ls())
			self.hitTile = None
		if (self.mouseWatcherNode.hasMouse()): # condition to protect from NaN when offscreen
			# get mouse position and traverse tileMap with the pickerRay
			mousePos = self.mouseWatcherNode.getMouse()
			self.tPickerRay.setFromLens(self.camNode, mousePos.getX(), mousePos.getY())
			self.tilePicker.traverse(self.render)

			if (self.tpQueue.getNumEntries() > 0): 	# when mouse ray collides with tiles:
				# sort by closest first
				self.tpQueue.sortEntries() 
				# find tile node and get tile index
				tileColl = self.tpQueue.getEntry(0).getIntoNodePath().getNode(1)
				tileInd = int(tileColl.getName().split("-")[1]) # trim name to index
				# highlight on mouseover
				self.hitTile = self.render.getChild(tileInd)
				#print("highlighting: " + str(self.hitTile))
				#self.hitTile.set_texture(self.tileTS, self.tileHighlight, 1)
				#self.hitTile.findTexture(self.tileTS).load(self.tileHighlight)
				#print(tileInd)

		return task.cont

	# CALLABLE FUNCTIONS/EVENTS: 		=========================

	def onMouse(self):
		if(self.hitTile != None):
				self.hilightCard.instanceTo(self.hitTile)

app = DuckBase()
app.run()
