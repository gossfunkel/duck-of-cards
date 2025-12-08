from direct.showbase.ShowBase import ShowBase
import units as unit
from panda3d.core import NodePath
#from dataclasses import dataclass

class Projectile(unit.Unit):
	def __init__(self, model, target, damage, node=None, pos=None):
		self.model: GeomNode = model
		self.node: NodePath = render.attachNewNode("ProjectileNode") if node is None else node
		if pos is not None:
			self.node.setPos(pos)
		self.target: NodePath = target
		self.damage: float = damage
		#self.speed: float = speed
		self.move = self.node.posInterval(.5, self.getTargetPos(), 
										self.node.getPos(), fluid=1, blendType='noBlend') if move is None else move
		self.moveSeq: Sequence = unit.seekTarget(self,self.target) if moveSeq is None else moveSeq
		# TODO explosion on collision?

	def hitTarget(self) -> None:
		# do damage and remove 
		if (type(self.target) is unit.Unit):
			if self.target.isAlive():
				self.target(unit.hit, self)
				#print(f"Projectile hitting {self.node.getPos()}")
		self.despawn()

#@dataclass
class Arrow(Projectile):
	def __init__(self, pos, target):
		model: GeomNode = base.loader.loadModel("assets/arrow2.gltf")
		node: NodePath = render.attachNewNode("arrow")
		node.setPos(pos)
		target: NodePath = target
		damage: float = 10.0
		#self.speed: float = 0.5
		Projectile.__init__(self, model, target, damage, node)

#@dataclass(frozen=True) # make a read-only dataclass
class Fireball(Projectile):
	def __init__(self, pos, target):
		model: GeomNode = base.loader.loadModel("assets/fireball.egg")
		node: NodePath = render.attachNewNode("fireball")
		node.setPos(pos)
		target: NodePath = target
		damage: float = 15.0
		#self.speed: float = 0.3
		Projectile.__init__(self, model, target, damage, node)
