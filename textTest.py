from direct.showbase.ShowBase import ShowBase
#from panda3d.core import TextPropertiesManager, TextProperties, TextNode
from panda3d.core import CardMaker, Texture
from direct.gui.DirectGui import *

# class MarkdownText(TextNode):
# 	def __init__(self, name):
# 		super().__init__(self, name)

# 		self.forceUpdate()

# 	# def __init__(self, name, TextProperties):
# 	# 	TODO overwrite copy contructor properly

# 	def generate(self):
# 		# return a new geomnode based on self
# 		super().generate()

# 	def bakeMarkdown(self):
# 		# return a p3d TextNode with formatting cooked-in
# 		text = TextNode(self.name)
# 		text.setText(self.getText())
# 		return text

class TextTest(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		#newTowerCTex = loader.loadTexture('assets/cards/card-buildTower.png')
		#newTowerBtn	= DirectButton(text = "10", command = base.buyTower,
		#								pos = (-0.5, 0, -0.3), parent = self.cardMenuScreen, scale = 0.3)
		#self.duckButtonMaps = loader.loadModel('assets/duck-button_maps')
		newCardMaker = CardMaker('newCard')
		newCardMaker.setFrame(0.,0.5,0.,0.605)

		newTowerCard = aspect2d.attachNewNode(newCardMaker.generate())
		#newTowerCard.setScale(0.4)
		#newTowerCard.reparentTo(self.cardMenuScreen)
		newTowerCTex = loader.loadTexture('assets/cards/card-buildTower.png')
		newTowerCTex.set_format(Texture.F_srgb_alpha)
		newTowerCard.setTexture(newTowerCTex)

		self.towerButt = DirectButton(geom=newTowerCard, 
						command=self.request, extraArgs=['CardMenu'], 
						scale=1.3, pos=(-0.3,0,-0.4), relief=None)
		newTowerCard.hide()

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
