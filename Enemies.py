from direct.showbase.ShowBase import ShowBase
from Units import PursuitAttacker
from SpriteModel import SpriteMod

class Enemy(SpriteMod, PursuitAttacker): 
	def __init__(model, node, damage, speed, hp)
		target: Vec3 = Vec3(base.castle.node.getX(),base.castle.node.getY(),self.node.getZ())
		PursuitAttacker.__init__(model, node, target, damage, speed, hp)

	def kill(self) -> int:
		# make sure this doesn't get called multiple times
		self.dying = True
		#print(str(self.node) + " dying")
		# stop moving and don't blink
		self.moveSeq.pause()
		self.dmgSeq.pause()
		# do a wee animation?
		# give player gold
		base.giveGold(5)
		self.despawn()
		return 1
