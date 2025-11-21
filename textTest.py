from direct.showbase.ShowBase import ShowBase
#from panda3d.core import TextPropertiesManager, TextProperties, TextNode
from panda3d.core import NodePath, CardMaker, Texture, Vec3
from direct.fsm.FSM import FSM
#from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *


class SpriteMod(FSM):
	def __init__(self, name, pos, speed) -> None:
		# TODO this can be cleaned up using the defaultFilter(self, request, args) method 
		# 	and a lookup table {('TopRight','Right'):'BottomRight',('TopRight','Left'):'TopLeft'} etc

		FSM.__init__(self, (str(name) + 'FSM')) # must be called when overloading

		tsmEgg: GeomNode = base.loader.loadModel(f"assets/{name}.egg")
		self.tsmSwitchNP: NodePath = tsmEgg.getChild(0)
		#for x in self.tsmSwitch.children: print(x)
		self.node: NodePath = render.attachNewNode("testspritemod")
		self.node.set_pos(pos)
		tsmEgg.wrtReparentTo(self.node)

		self.speed: float = speed
		#self.period: float = 90. / speed

		self.node.setH(self.node.getH() + 45)

		self.request("BottomLeft")

	def defaultFilter(self, request, args) -> str:
		return 'BottomLeft'

	# TODO standing still

	# def enterLeft(self) -> None:
	# 	self.tsmSwitch.setVisibleChild(1)

	# def enterRight(self) -> None:
	# 	self.tsmSwitch.setVisibleChild(2)

	# def enterFront(self) -> None:
	# 	self.tsmSwitch.setVisibleChild(3)

	# def enterBack(self) -> None:
	# 	self.tsmSwitch.setVisibleChild(0)

	def enterTopLeft(self) -> None:
		# lerp round
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()
		self.tsmSwitchNP.node().setVisibleChild(1)
		print(self.tsmSwitchNP.node().getVisibleChild())

	#def exitTopLeft(self) -> None:
	#	#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)

	def filterTopLeft(self, request, args) -> str: # process input while facing the top left (-x,+y)
		if (request == 'Left'):
			return 'BottomLeft'
		elif (request == 'Right'):
			return 'TopRight'
		elif (request == 'Flip'):
			return 'BottomRight'
		else:
			return None

	def enterTopRight(self) -> None:
		# lerp round
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()
		self.tsmSwitchNP.node().setVisibleChild(2)
		print(self.tsmSwitchNP.node().getVisibleChild())

	#def exitTopRight(self) -> None:
	#	self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])	
	#	#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)
	#	#self.node.setTexHpr(TextureStage.getDefault(), 0,0,0)

	def filterTopRight(self, request, args) -> str: # process input while facing top right (+x,+y)
		if (request == 'Left'):
			return 'TopLeft'
		elif (request == 'Right'):
			return 'BottomRight'
		elif (request == 'Flip'):
			return 'BottomLeft'
		else:
			return None

	def enterBottomRight(self) -> None:
		# lerp round
		#print(str(self.node) + " facing bottom right")
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()
		self.tsmSwitchNP.node().setVisibleChild(2)
		print(self.tsmSwitchNP.node().getVisibleChild())

	#def exitXneg(self) -> None:	
	#	self.nodepath.set_scale(self.nodepath.get_scale()[0],self.nodepath.get_scale()[1]*-1,self.nodepath.get_scale()[2])
	#	#self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
		
	def filterBottomRight(self, request, args) -> str: # process input while facing bottom right (+x,-y)
		if (request == 'Left'):
			return 'TopRight'
		elif (request == 'Right'):
			return 'BottomLeft'
		elif (request == 'Flip'):
			return 'TopLeft'
		else:
			return None

	def enterBottomLeft(self) -> None:
		# lerp round
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()
		self.tsmSwitchNP.node().setVisibleChild(1)
		print(self.tsmSwitchNP.node().getVisibleChild())

	#def exitYneg(self) -> None:
	#	self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
	#	self.nodepath.set_scale(0.05,0.05,0.05)
	#	#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)

	def filterBottomLeft(self, request, args) -> str: # process input while facing bottom left (-x,+y)
		if (request == 'Left'):
			return 'BottomRight'
		elif (request == 'Right'):
			return 'TopLeft'
		elif (request == 'Flip'):
			return 'TopRight'
		else:
			return None


class TextTest(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		#newTowerCTex = loader.loadTexture('assets/cards/card-buildTower.png')
		#newTowerBtn	= DirectButton(text = "10", command = base.buyTower,
		#								pos = (-0.5, 0, -0.3), parent = self.cardMenuScreen, scale = 0.3)
		#self.duckButtonMaps = loader.loadModel('assets/duck-button_maps')
		#newCardMaker = CardMaker('newCard')
		#newCardMaker.setFrame(0.,0.5,0.,0.605)
		#print(tsmEgg.ls())
		#tsmKids = tsmEgg.children.getPath(0).children
		#print(tsmKids.ls())
		# testSpriteMod = render.attachNewNode("testSpriteMod")
		# backPath = NodePath('backPath')
		# tsmKids[0].copyTo(backPath)
		# backPath.reparent_to(testSpriteMod)
		# leftPath = NodePath('leftPath')
		# tsmKids[1].copyTo(leftPath)
		# backPath.reparent_to(testSpriteMod)
		# rightPath = NodePath('rightPath')
		# tsmKids[2].copyTo(rightPath)
		# backPath.reparent_to(testSpriteMod)
		# frontPath = NodePath('frontPath')
		# tsmKids[3].copyTo(frontPath)
		# backPath.reparent_to(testSpriteMod)
		# backPath.hide()
		# rightPath.show()
		tsmTest = SpriteMod("testspritemod", (0,0,0), 1)
		
		#tsmTest.request('Left')

		self.cam.set_pos(0,-2,0)
		#self.testspritemod.setScale(0.06)
		#self.node.setScale(0.6)
		#self.node.setP(30)
		#self.node.setY(-45) 

		#newTowerCard = aspect2d.attachNewNode(newCardMaker.generate())
		#newTowerCard.setScale(0.4)
		#newTowerCard.reparentTo(self.cardMenuScreen)
		#newTowerCTex = loader.loadTexture('assets/cards/card-buildTower.png')
		#newTowerCTex.set_format(Texture.F_srgb_alpha)
		#newTowerCard.setTexture(newTowerCTex)

		#self.towerButt = DirectButton(geom=newTowerCard, 
		#				command=self.request, extraArgs=['CardMenu'], 
		#				scale=1.3, pos=(-0.3,0,-0.4), relief=None)
		#newTowerCard.hide()

		# tpMgr = TextPropertiesManager.getGlobalPtr()

		# #font = loader.loadFont('assets/Nunito-Regular.ttf')
		# font = loader.loadFont('cmr12.egg')

		# tpRed = TextProperties() 
		# tpRed.setTextColor(1,0,0,1)
		# tpSlant = TextProperties() 
		# tpSlant.setSlant(0.3)
		# tpFont = TextProperties() 
		# tpFont.setFont(font)

		# tpMgr.setProperties("red", tpRed)
		# tpMgr.setProperties("slant", tpSlant)
		# tpMgr.setProperties("font", tpFont)

		# textGen = TextNode("Test Text Generator")
		# textGen.setText("The \1slant\1quick\2 \1red\1brown fox\2 jumps over the \1font\1lazy dog\2.")
		# textGen.setTextColor(1,1,1,1)
		# textNP = aspect2d.attachNewNode(textGen.generate())
		# textNP.setScale(0.1)
		# textNP.setPos(-1,0,0)

	def request(self, whereClicked):
		print(f"clicked button at {whereClicked}")

testApp = TextTest()
testApp.run()
