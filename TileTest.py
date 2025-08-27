from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, DirectionalLight, OrthographicLens, Vec3
from panda3d.core import CollisionBox, CollisionNode, BitMask32, CollisionRay, CollisionTraverser
from panda3d.core import CollisionHandlerQueue, TextureStage, Texture
#import complexpbr as cpbr

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

class TileTest(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		base.disableMouse()

		# initialise pbr for models, and shaders
		#cpbr.apply_shader(self.render)
		#cpbr.screenspace_init()
		#render.setShaderAuto()
		#cpbr.set_cubebuff_active()
		#cpbr.set_cubebuff_inactive()
		#base.complexpbr_z_tracking = True

		# create sunlight
		self.dirLight = DirectionalLight('dirLight')
		self.dirLight.setColorTemperature(6000)
		self.dirLight.setShadowCaster(True, 512, 512)
		#self.dirLight.setAttenuation(1,0,1)
		self.dirLightNp = render.attachNewNode(self.dirLight)
		self.dirLightNp.setHpr(-70,-40,20)
		render.setLight(self.dirLightNp)

		self.cam.setPos(0.,0.,3.)
		# isometric angle 35.264deg
		self.cam.setHpr(-45,-35.264,0)
		self.cam.setPos(self.cam, self.cam.getPos() + Vec3(0.,-12.,-4.))
		# orthographic lens to commit to isometric/dimetric view
		self.lens = OrthographicLens()
		self.lens.setFilmSize(12, 8)  						# <--- update according to resolution
		self.lens.setNearFar(-40,40)
		self.cam.node().setLens(self.lens)

		# generate ground tile model and instance, creating node map
		self.tileMap = self.render.attachNewNode("tileMap")
		self.tileModel = self.loader.loadModel("assets/groundTile.egg")

		self.tileTS = TextureStage('tileTS')
		self.tileTS.setMode(TextureStage.M_add)
		self.tileTS.setTexcoordName('UVMap')
		self.tileHighlight = self.loader.loadTexture("assets/highlight-tile.png")
		#self.groundTex = self.tileModel.find('**/Base')
		#print(self.groundTex)
		self.groundTex = self.loader.loadTexture("assets/ground-tile.png")

		tile = self.tileMap.attachNewNode("tile-0")
		tile.setPos(0,0,0)
		self.tileModel.instanceTo(tile)
		tile.set_texture(self.tileTS, self.groundTex, 1)
		tileHitbox = CollisionBox(tile.getPos(),1., 1., 1.)
		tileColl = CollisionNode(str(tile)+'-cnode')
		tileColl.setIntoCollideMask(BitMask32(0x01))
		tileNp = tile.attachNewNode(tileColl)
		tileNp.node().addSolid(tileHitbox)
		#tileNp.show()
		tile = self.tileMap.attachNewNode("tile-1")
		tile.setPos(2,0,0)
		self.tileModel.instanceTo(tile)
		tile.set_texture(self.tileTS, self.groundTex, 1)
		tileHitbox = CollisionBox(tile.getPos()-Vec3(2,0,0),1., 1., 1.)
		tileColl = CollisionNode(str(tile)+'-cnode')
		tileColl.setIntoCollideMask(BitMask32(0x01))
		tileNp = tile.attachNewNode(tileColl)
		tileNp.node().addSolid(tileHitbox)
		#tileNp.show()

		self.tPickerRay = CollisionRay()
		self.tilePicker = CollisionTraverser()
		self.tpQueue = CollisionHandlerQueue()
		tpNode = CollisionNode('tp-node')
		tpNode.setFromCollideMask(BitMask32(0x01))
		tpNp = self.cam.attachNewNode(tpNode)
		tpNode.addSolid(self.tPickerRay)
		self.tilePicker.addCollider(tpNp, self.tpQueue)
		self.hitTile = None
		#self.tilePicker.showCollisions(render)

		self.pathTex = loader.loadTexture("assets/road-tile.png")
		self.pathTS = TextureStage('path-textureStage')
		self.pathTS.setTexcoordName('UVMap')
		self.pathTS.setMode(TextureStage.MDecal)

		tile.setTexture(self.pathTS, self.pathTex)
		#tile.setTexHpr(self.pathTS, 0,0,0)

		self.taskMgr.add(self.update, "update", taskChain='default')

	def update(self, task):
		if self.hitTile != None: 			# clear highlighting on non-hovered tiles
			for tile in self.tileMap.getChildren():
				#if tile != self.hitTile:
				tile.set_texture(self.tileTS, self.groundTex, 1)
				print('texture cleared on ' + str(tile))
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

		return task.cont

app = TileTest()
app.run()
