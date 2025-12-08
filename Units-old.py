from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, Vec3, CollisionCapsule, CollisionNode, BitMask32
from SpriteModel import SpriteMod
from direct.interval.IntervalGlobal import *
import numpy as np

class ChaseTarget():
	def __init__(self, model, target, damage, speed, node=None, move=None):
		assert model is not None, f'A model must be provided to ChaseTarget! Try hiding it after construction if you want it to be invisible'
		assert target is not None, f'ChaseTarget requires a target!'
		assert damage is not None, f'ChaseTarget requires damage'
		assert speed is not None, f'ChaseTarget requires speed'

		self.model: GeomNode = model
		self.target: NodePath = target
		self.damage: float = damage
		self.speed: float = speed
		# default construction of new node if not passed
		self.node: NodePath = render.attachNewNode("ChaseTargetNode") if node is None else node
		# default move interval if none passed as args
		self.move = self.node.posInterval(.5, self.getTargetPos(), 
										self.node.getPos(), fluid=1, blendType='noBlend') if move is None else move

		# on arrival/despawn, do damage to enemy
		self.moveSeq: Sequence = Sequence(
			self.move,
			Func(self.attack)
		)
		self.moveSeq.start()

	def getTargetPos(self) -> Vec3:
		# gets overridden in subclasses
		#print(f"ChaseTarget has {self.target.getPos()} as target")
		return self.target.getPos()

	def attack(self) -> None:
		if self.target.isAlive():
			self.target.damage(self.damage)
			Sequence(wait(1),self.moveSeq).start()
		else:
			# TODO: probably shouldn't just automatically die if no target
			self.despawn()

	def despawn(self) -> None:
		# do damage and remove TODO fix this
		print(f"ChaseTarget despawning at {self.node.getPos()}")
		self.node.removeNode()
		#base.ModelPool.releaseModel(self.model)

# deprecated - split between Enemy and Projectile
# class Seeker(ChaseTarget):
# 	def __init__(self, model, target, damage, speed, node):
# 		ChaseTarget.__init__(self, model, target, damage, speed, node)

# 	def getTargetPos(self) -> Vec3:
# 		# get up-to-date position
# 		# TODO - TAKE LEAD POSITION IN PURSUIT (i.e. arrows should fly to where enemies are going)
# 		p: Vec3 = self.target.node.getPos()
# 		# adjust z-coord for visual accuracy
# 		p[2] += .5
# 		#print(f"Seeker targeting {p}")
# 		return p

# deprecated - all of this can be in Enemy
class PursuitAttacker(ChaseTarget):
	# wondering whether to split some of this off as a 'Targetable' class, but I think all of these are both
	def __init__(self, model, target, damage, speed, hp, node):
		assert hp > 0, f'PursuitAttacker cannot be spawned with 0 or less hp!'
		# define dying tag and set to False until unit loses all HP
		self.dying: bool = False
		self.hp: float = hp
										  #CollisionCapsule(ax, ay,    az,   bx, by,  bz, radius)
		self.hitSphere: CollisionCapsule = CollisionCapsule(0., -0.25, 0.75, 0., 0.2, 0.75, .125)
		hcnode = CollisionNode('{}-cnode'.format(str(self.node)))
		hcnode.setIntoCollideMask(BitMask32(0x02))
		self.hitNp: NodePath = self.node.attachNewNode(hcnode)
		self.hitNp.node().addSolid(self.hitSphere)

		# calculate distance to target in order to calculate time-length of move Interval
		dist = self.getTargetPos() - node.getPos()
		dist = np.sqrt(dist.x * dist.x + dist.y * dist.y + dist.z * dist.z)
		# set Interval and pass to ChaseTarget constructor to load into Sequence
		self.move = self.node.posInterval(dist/speed, self.getTargetPos(), 
											self.node.getPos(), fluid=1, blendType='noBlend')
		ChaseTarget.__init__(self, model, target, damage, speed, node, self.move)

	def takeDamage(self):
		# take the damage
		self.hp -= dmg

		# check that it's not already in the process of despawning
		if not self.dying:
			# flash red for a moment
			if self.hp > 0: self.dmgSeq.start()
			else: # die if hp is 0 or less
				self.despawnDie()
		# this seems to cause despawnDie to run twice, somehow. I should do proper garbage collection
		# on these objects, and remove the enemies as well as their nodes

	def despawn(self) -> None:
		# clean up the node
		#print(str(self.node) + " despawning")
		# make sure this doesn't get called multiple times
		print(f"PursuitAttacker despawning at {self.node.getPos()}")
		self.dying = True
		# clean up sequences
		if self.moveSeq is not None:
			self.moveSeq.clearIntervals()
		#if self.dmgSeq is not None:
		#	self.dmgSeq.clearIntervals()
		# remove update task from taskMgr
		if (base.taskMgr.getTasksNamed(str(self.node)+"_update") != None):
			base.taskMgr.remove(base.taskMgr.getTasksNamed(str(self.node)+"_update"))
		# clean up node
		self.node.removeNode() 	

	def kill(self) -> int:
		# make sure this doesn't get called multiple times
		self.dying = True
		#print(str(self.node) + " dying")
		# stop moving and don't blink
		self.moveSeq.pause()
		self.dmgSeq.pause()
		# do a wee animation?
		self.despawn()
		return 1

#class Sieger(PursuitAttacker):
#	def __init__()
