import numpy as np 

epsilon = 0.0001

def calcDampedSHM(pos,vel,equilibriumPos,deltaTime,angularFreq,dampRatio):
	assert (angularFreq >= 0.), f'SHM angular frequency parameter must be positive!'
	assert (dampRatio >= 0.), f'SHM damping ratio parameter must be positive!'

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
