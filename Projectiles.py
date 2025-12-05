from direct.showbase.ShowBase import ShowBase
import units as unit
from panda3d.core import NodePath
#from dataclasses import dataclass

class Projectile():
	def __init__(self, model, target, damage, speed, node):
		unit.ChaseTarget.__init__(self, model, target, damage, speed, node)
		# TODO localise variables here
		self.model: GeomNode = model
		# TODO explosion on collision?

#@dataclass
class Arrow(Projectile):
	def __init__(self, target):
		self.model: GeomNode = base.loader.loadModel("assets/arrow2.gltf")
		self.node: NodePath = render.attachNewNode("arrow")
		self.target: NodePath = target
		self.damage: float = 10.0
		self.speed: float = 0.5
		Projectile.__init__(self, self.model, self.node, self.target, self.damage, self.speed)

#@dataclass(frozen=True) # make a read-only dataclass
class Fireball(Projectile):
	def __init__(self, target):
		self.model: GeomNode = base.loader.loadModel("assets/fireball.egg")
		self.node: NodePath = render.attachNewNode("fireball")
		self.target: NodePath = target
		self.damage: float = 15.0
		self.speed: float = 0.3
		Projectile.__init__(self, self.model, self.node, self.target, self.damage, self.speed)
