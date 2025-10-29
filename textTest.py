from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextPropertiesManager, TextProperties, TextNode

class MarkdownText(TextNode):
	def __init__(self, name):
		super().__init__(self, name)

		self.forceUpdate()

	# def __init__(self, name, TextProperties):
	# 	TODO overwrite copy contructor properly

	def generate(self):
		# return a new geomnode based on self
		super().generate()

	def bakeMarkdown(self):
		# return a p3d TextNode with formatting cooked-in
		text = TextNode(self.name)
		text.setText(self.getText())
		return text

class TextTest(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		tpMgr = TextPropertiesManager.getGlobalPtr()

		#font = loader.loadFont('assets/Nunito-Regular.ttf')
		font = loader.loadFont('cmr12.egg')

		tpRed = TextProperties() 
		tpRed.setTextColor(1,0,0,1)
		tpSlant = TextProperties() 
		tpSlant.setSlant(0.3)
		tpFont = TextProperties() 
		tpFont.setFont(font)

		tpMgr.setProperties("red", tpRed)
		tpMgr.setProperties("slant", tpSlant)
		tpMgr.setProperties("font", tpFont)

		textGen = TextNode("Test Text Generator")
		textGen.setText("The \1slant\1quick\2 \1red\1brown fox\2 jumps over the \1font\1lazy dog\2.")
		textGen.setTextColor(1,1,1,1)
		textNP = aspect2d.attachNewNode(textGen.generate())
		textNP.setScale(0.1)
		textNP.setPos(-1,0,0)

testApp = TextTest()
testApp.run()
