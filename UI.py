from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode, CardMaker
from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage

class UI():
	def __init__(self) -> None:
		# show remaining hit points
		self.castleHPdisplay: TextNode = TextNode('castle HP display')
		self.castleHPdisplay.setText(str(castleHP))
		self.castleHPdisplay.setFrameColor(0, 0, 1, 1)
		self.castleHPdisplay.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)
		self.castleTextNP: NodePath = aspect2d.attachNewNode(self.castleHPdisplay)
		self.castleTextNP.setScale(0.1)
		self.castleTextNP.setPos(-1.4,0., 0.85)

		# show current enemy wave
		self.waveDisplay: TextNode = TextNode('wave number display')
		self.waveDisplay.setText("Wave: " + str(waveNum))
		self.waveDisplay.setFrameColor(1, 0, 1, 1)
		self.waveDisplay.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)
		self.waveDisplayNP: NodePath = aspect2d.attachNewNode(self.waveDisplay)
		self.waveDisplayNP.setScale(0.05)
		self.waveDisplayNP.setPos(-0.9,0., 0.9)

		# show player gold
		self.goldDisplay: TextNode = TextNode('player gold display')
		self.goldDisplay.setText("GP: " + str(playerGold))
		self.goldDisplay.setFrameColor(1, 1, 0, 1)
		self.goldDisplay.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)
		self.goldDisplayNP: NodePath = aspect2d.attachNewNode(self.goldDisplay)
		self.goldDisplayNP.setScale(0.05)
		self.goldDisplayNP.setPos(-0.9,0., 0.82)

		#self.turretButt = DirectButton(text="", scale=0.05, 
		#						pos=(-0.3, 0, 0.9), command=base.pickTower)

		# construct 'game over' screen elements
		self.gameOverScreen = DirectDialog(frameSize=(-0.7, 0.7, -0.7, 0.7),
                                   			fadeScreen=0.4, relief=DGG.FLAT)
		self.gameOverScreen.hide()
		gameOverLabel = DirectLabel(text="Game Over!", parent=self.gameOverScreen,
										scale=0.1, pos=(0, 0, 0.2))
		restartBtn 	= DirectButton(text="Restart", command=base.fsm.exitGameOver, pos = (-0.3, 0, -0.2),
									parent=self.gameOverScreen, scale=0.1)
		quitBtn 	= DirectButton(text="Quit", command=base.quit, pos=(0.3, 0, -0.2),
									parent=self.gameOverScreen, scale=0.1)
		
		# construct 'card menu' elements
		self.cardMenuScreen = DirectFrame(frameSize = (-1.2, 1.2, -.8, .8),
		#							items = [newTowerBtn], initialItem = 0,
        #                           fadeScreen = 0.7,
                                   relief = DGG.FLAT)
		newCardMaker = CardMaker('newCard')
		newCardMaker.setFrame(0.,0.5,0.,0.605)

		# TODO: Flexible card menu for random ducky offerings
		# 	1) Randomly generate 3 numbers (weighted?). These index a list containing tuples of card texture filenames 
		# 		and their appropriate command (as a lambda?)
		# 	2) Create 3 cards, loading the variables that have now been filled with the textures
		# 	3) Load those textures into the buttons with the appropriate command

		newTowerCard = aspect2d.attachNewNode(newCardMaker.generate())
		newTowerCard.setScale(0.75)
		#newTowerCard.reparentTo(self.cardMenuScreen)
		newTowerCTex = loader.loadTexture('assets/cards/card-buildTower.png')
		newTowerCTex.set_format(Texture.F_srgb_alpha)
		newTowerCard.setTexture(newTowerCTex)
		newTowerBtn  = DirectButton(geom=newTowerCard, command=base.buyTower, relief=None,
										pos=(-1., 0, -0.5), parent=self.cardMenuScreen, scale=1.1)
		newTowerCard.hide() # has to be hidden *after* button is constructed or button will not have texture

		upgradeTowerCard = aspect2d.attachNewNode(newCardMaker.generate())
		upgradeTowerCard.setScale(0.75)
		upgradeTowerCTex = loader.loadTexture('assets/cards/card-tripleShot.png')
		upgradeTowerCTex.set_format(Texture.F_srgb_alpha)
		upgradeTowerCard.setTexture(upgradeTowerCTex)
		upgradeTowerBtn  = DirectButton(geom=upgradeTowerCard, command=base.upgradeTower, relief=None,
										pos=(-0.25, 0., -0.5), parent=self.cardMenuScreen, scale=1.1)
		upgradeTowerCard.hide() # has to be hidden *after* button is constructed or button will not have texture

		magicTowerCard = aspect2d.attachNewNode(newCardMaker.generate())
		magicTowerCard.setScale(0.75)
		magicTowerCTex = loader.loadTexture('assets/cards/card-magicTower.png')
		magicTowerCTex.set_format(Texture.F_srgb_alpha)
		magicTowerCard.setTexture(magicTowerCTex)
		magicTowerBtn  = DirectButton(geom=magicTowerCard, command=base.buyMagicTower, relief=None,
										pos=(0.5, 0., -0.5), parent=self.cardMenuScreen, scale=1.1)
		magicTowerCard.hide() # has to be hidden *after* button is constructed or button will not have texture


		self.cardMenuScreen.hide()
		self.cardMenuLabel = DirectLabel(text = "Welcome!\nWould you like to buy\none of my fine cards?", 
								parent=self.cardMenuScreen, scale=0.12, pos=(-0.9, 0, 0.55), text_align=TextNode.ALeft)
		dukeImgObj = OnscreenImage(image='assets/theDuke-sprite_ready.png', pos=(0.82, 0, 0.6), 
										parent=self.cardMenuScreen, scale=0.37)
		dukeImgObj.setTransparency(TransparencyAttrib.MAlpha)
		self.duckButtonMaps = loader.loadModel('assets/duck-button_maps')
		#self.duckButtonMaps.node().set_format(Texture.F_srgb)
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

	def update(self) -> None:
		# update hp display
		self.castleHPdisplay.setText(str(castleHP) + "hp")
		if castleHP < 25:
			self.castleHPdisplay.setFrameColor(1, 0, 0, 1)
			# update castle appearance
		# update wave display
		self.waveDisplay.setText("Wave: " + str(waveNum))
		# update player gold points display
		self.goldDisplay.setText("GP: " + str(playerGold))

	def drawText(self, dialogueString) -> NodePath:
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

	def popupText(self, textString, duration) -> NodePath:
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

	# def showCooldown(self, pos, cooldown):
	# 	cd = TextNode('cooldown at ' + str(pos))
	# 	cd.setText(str(cooldown))
	# 	cd.setFrameColor(1, 1, 1, .6)
	# 	cdNP = aspect2d.attachNewNode(cd)
	# 	cdNP.setScale(0.05)
	# 	# TODO : BROKEN : THIS RECEIVES THE WORLD POSITION, BUT IT NEEDS THE SCREEN POSITION
	# 	cdNP.setPos(pos)