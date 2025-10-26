from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, DirectionalLight, Vec3, TextNode, CardMaker
from direct.interval.IntervalGlobal import *
import numpy as np 

config_vars = """
win-size 1200 800
show-frame-rate-meter 1
hardware-animated-vertices true
basic-shaders-only false
model-cache-dir
threading-model Cull/Draw
"""
loadPrcFileData("", config_vars)

epsilon = 0.0001

def calcDampedSHM(pos,vel,equilibriumPos,deltaTime,angularFreq,dampRatio):
	assert (angularFreq >= 0.), f'SHM angular frequency parameter must be positive!'
	assert (dampRatio >= 0.), f'SHM damping ratio parameter must be positive!'

	#dist = pos - equilibriumPos
	#if (dist < epsilon): 
	#	# close enough
	#	return equilibriumPos,Vec3(0,0,0)

	if (angularFreq < epsilon):
		print("SHM frequency too low to change motion!")
		pospos = 1.
		posvel = 0.
		velpos = 0.
		velvel = 1.
	else:
		if (dampRatio > 1. + epsilon):
			# overdamped formula
			za = -angularFreq * dampRatio
			zb = angularFreq * np.sqrt(dampRatio*dampRatio - 1.)
			z1 = za - zb
			z2 = za + zb

			e1 = np.exp(z1 * deltaTime)
			e2 = np.exp(z2 * deltaTime)

			invTwoZb = 1. / (2. * zb)

			e1OverTwoZb = e1 * invTwoZb
			e2OverTwoZb = e2 * invTwoZb

			z1e1OverTwoZb = z1 * e1OverTwoZb
			z2e2OverTwoZb = z2 * e2OverTwoZb

			pospos = e1OverTwoZb * z2e2OverTwoZb + e2OverTwoZb
			posvel = -e1OverTwoZb + e2OverTwoZb
			velpos = (z1e1OverTwoZb - z2e2OverTwoZb + e2) * z2 
			velvel = -z1e1OverTwoZb + z2e2OverTwoZb
		elif (dampRatio < 1. - epsilon):
			# underdamped formula
			omegaZeta = angularFreq * dampRatio
			alpha 	  = angularFreq * np.sqrt(1. - dampRatio * dampRatio)

			expTerm = np.exp(-omegaZeta * deltaTime)
			cosTerm = np.cos(alpha * deltaTime)
			sinTerm = np.sin(alpha * deltaTime)

			invAlpha = 1. / alpha 

			expSin = expTerm * sinTerm
			expCos = expTerm * cosTerm
			expOmegaZetaSinOverAlpha = expTerm * omegaZeta * sinTerm * invAlpha

			pospos = expCos + expOmegaZetaSinOverAlpha
			posvel = expSin * invAlpha
			velpos = -expSin * alpha - omegaZeta * expOmegaZetaSinOverAlpha
			velvel = expCos - expOmegaZetaSinOverAlpha
		else:
			# critically damped formula
			expTerm = np.exp(-angularFreq * deltaTime)
			timeExp = deltaTime * expTerm
			timeExpFreq = timeExp * angularFreq

			pospos = timeExpFreq + expTerm
			posvel = timeExp
			velpos = -angularFreq * timeExpFreq
			velvel = -timeExpFreq + expTerm

	pos = pos - equilibriumPos
	oldvel = vel
	vel = pos * velpos + oldvel * velvel
	pos = pos * pospos + oldvel * posvel + equilibriumPos

	return pos, vel

def popupText(textString, duration):
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
	#popupText.setCardColor(0.1,0.1,0.1,0.2)
	# note that method popupText.setCardTexture(texture) exists
	#popupText.setCardAsMargin(0.5,0.5,0.5,0.1)
	#popupText.setCardDecal(True)
	#popupText.setFrameCorners(True)
	popupTextNP = aspect2d.attachNewNode(popupText)
	popupTextNP.setScale(0.1)
	popupTextNP.setPos(np.random.random()-.4,0.,np.random.random() - .5)
	Sequence(Wait(duration),popupTextNP.colorScaleInterval(1,(1.,1.,1.,0.)),Func(popupTextNP.removeNode)).start()

	return popupTextNP

class DuckBase(ShowBase):
	def __init__(self):		#			=========================
		ShowBase.__init__(self)
		self.set_background_color(1.,.8,.8)

		self.duckModel = loader.loadModel("assets/roundDuck.gltf")
		dirLight = DirectionalLight('dirLight')
		dirLight.setColorTemperature(6000)
		dirLight.setShadowCaster(True, 512, 512)
		dirLightNp = render.attachNewNode(dirLight)
		dirLightNp.setHpr(30,20,-70)
		render.setLight(dirLightNp)
		#self.duckModel.setP(90)
		self.duckModel.reparent_to(render)
		self.duckModel.set_pos(0.,500.,-1.)
		self.duckVel = Vec3(0.,10.,0.)
		self.card_maker = CardMaker('heart')
		self.card_maker.setHasUvs(1)
		self.card_maker.clearColor()
		self.card_maker.setFrame(-0.05,.05,-.05,0.05)

		self.accept("space", self.perturbDuck)
		self.accept("b", self.perturbDuckHarder)
		self.accept("enter", self.perturbDuckHardest)
		self.accept("x", self.kiss)

		self.taskMgr.add(self.update, "update", taskChain='default')

		#self.camera.set_position(0.,-50.,10.)

	def update(self, task):
		#self.model.setH(self.model.getH() + 1)
		pos, self.duckVel = calcDampedSHM(self.duckModel.get_pos(), self.duckVel, Vec3(0,25,-3),globalClock.getDt(), 20., 0.35)
		self.duckModel.set_pos(pos)
		return task.cont

	def perturbDuck(self):
		popupText("boop", 1.)
		#direction = self.duckModel.getPosDelta(self.camera)
		#print("camera: " + str(self.camera.get_pos()))
		#print("model: " + str(self.duckModel.get_pos()))
		#print("direction: " + str(direction))
		direction = self.duckModel.get_pos() - self.camera.get_pos()
		self.duckVel += Vec3(15. * direction[0],15. * direction[1],12. * direction[2])
		#self.duckVel += Vec3(0.,10.,0.)
		#self.duckModel.set_pos(self.duckModel.get_pos() + direction.dot(10.))

	def perturbDuckHarder(self):
		popupText("bonk", 2.)
		direction = self.duckModel.get_pos() - self.camera.get_pos()
		self.duckVel += Vec3(25. * direction[0],25. * direction[1],25. * direction[2])

	def perturbDuckHardest(self):
		popupText("boffff", 3.)
		direction = self.duckModel.get_pos() - self.camera.get_pos()
		self.duckVel += Vec3(50. * direction[0],50. * direction[1],50. * direction[2])

	def kiss(self):
		print("luv u")
		heartSprite = self.render2d.attachNewNode(self.card_maker.generate())
		heartSprite.setTransparency(1)
		heartSprite.setTexture(loader.loadTexture("assets/heart.png"))
		heartSprite.set_pos(np.random.random() - .5, 0, np.random.random() - .5)
		Sequence(Wait(2.),heartSprite.colorScaleInterval(1,(1.,1.,1.,0.)),Func(heartSprite.removeNode)).start()
		direction = self.duckModel.get_pos() - self.camera.get_pos()
		self.duckVel += Vec3(.25*direction[0],.25*direction[1],.1*direction[2])

app = DuckBase()
app.run()
