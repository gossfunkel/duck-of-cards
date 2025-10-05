from direct.showbase.ShowBase import ShowBase
from panda3d.core import CardMaker, loadPrcFileData#, TextureStage
from panda3d.core import Texture, SamplerState
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
	def __init__(self):		#	=========================
		ShowBase.__init__(self)

		# ticker
		self.t = 0.
		self.set_background_color(0.,0.,0.,1.)

		# generate tiles
		self.generateTerrain()

		# initialise camera position and angle:
		self.cam.setPos(0.,-20.,10.)
		self.cam.lookAt(0.,0.,0.)

		self.taskMgr.add(self.update, "update", taskChain='default')

	# LOADING FUNCTIONS: 		=========================

	def generateTerrain(self):
		card_maker = CardMaker('card')
		#card_maker.setColor(1.,1.,1.,1.)
		card_maker.setFrame(-1.,1.,-1.,1.)
		card_maker.setHasUvs(1)
		card_maker.clearColor()
		self.centreTile = self.render.attachNewNode(card_maker.generate())
		self.centreTile.setPos(0.,0.,0.)
		self.centreTile.setHpr(0., -90., 45.)

		groundTile = loader.loadTexture("../duck-of-cards/assets/ground-tile_4.png")
		groundTile.setWrapU(Texture.WM_clamp)
		groundTile.setWrapV(Texture.WM_clamp)
		groundTile.setMagfilter(SamplerState.FT_nearest)
		groundTile.setMinfilter(SamplerState.FT_nearest)
		self.centreTile.setTexture(groundTile, 1)
		self.centreTile.setTransparency(1)

		for x in range(width):
			for y in range(height):
				tile = self.render.attachNewNode("tile-GRASS"+str(x)+":"+str(y))
				tile.setPos((1.4*x-y*1.4),(1.4*x+y*1.4)-1.4*50.,0.)
				self.centreTile.instanceTo(tile)

	# TASKS/PROCESSES: 			=========================

	def update(self, task):
		#self.t += 0.01
		#print(self.cardnp.getPos())
		#sint = sin(self.t)
		#self.cardnp.setPos(2. * sint,0.,0.)
		#self.cardnp.setHpr(180. * sint, 0., 0.)
		#self.cardnp.setColor(sint*sint,1-sint*sint,1.)
		return task.cont

app = DuckBase()
app.run()
