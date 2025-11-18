from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath

class ChaseTarget():
	def __init__(model, node, target, damage, speed):
		assert model is not None, f'A model must be provided to ChaseTarget! Try hiding it after if you want it to be invisible'
		assert target is not None, f'ChaseTarget requires a target!'
		assert damage is not None, f'ChaseTarget requires damage'
		assert speed is not None, f'ChaseTarget requires speed'

		self.model = model
		self.node: NodePath = render.attachNewNode("ChaseTargetNode") if node is None else self.node: NodePath = node
		self.target = target
		self.damage = damage
		self.speed = speed

	def despawn(self) -> None:
		# do damage and remove TODO fix this
		self.target.damage(self.damage)
		ModelPool.releaseModel(self.model)
		self.node.removeNode()

class Seeker(ChaseTarget):

class PursuitAttacker(ChaseTarget):

class Sieger(PursuitAttacker):

