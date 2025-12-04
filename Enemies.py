from direct.showbase.ShowBase import ShowBase
from Units import PursuitAttacker, Seeker
from SpriteModel import SpriteMod

class Enemy(SpriteMod, PursuitAttacker, Seeker): 
	def __init__(self, model, node, damage, speed, hp) -> None:
		self.target: NodePath = base.castle
		#print(target)
		PursuitAttacker.__init__(self, model, self.target, damage, speed, hp, node)

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

class BasicEnemy(Enemy):
	def __init__(self, pos) -> None:
		self.name: str = "BasicDog"
		self.speed: float = 1.
		SpriteMod.__init__(self, self.name, pos, self.speed)
		self.damage: float = 5.0
		self.hp: float = 20.0
		Enemy.__init__(self, self.model, self.node, self.damage, self.speed, self.hp)
