from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, Vec3, CollisionCapsule, CollisionNode, BitMask32
from direct.interval.IntervalGlobal import *
from __future__ import annotations
from typing import Any
from collections.abc import Callable

class Unit():
	def __init__(self,model:GeomNode,node:NodePath,damage:float,speed:float,hp:float,moveSeq:Sequence=None):
		self.model: GeomNode = model
		self.node: NodePath = node
		#self.target: NodePath
		self.damage: float = damage
		self.speed: float = speed
		self.dying: bool = False
		self.hp: float = hp

	# pretty sure this is terrible code security/privacy but it feels like a good way
	# 	to inject dependencies at runtime
	def __call__(self, func: Callable[[Any],Any], arg:Any=None):
		# execute function with arg - e.g. damage(arrow) to do damage via an arrow
		output = func(arg)
		if type(output) == Callable[[Any],Any]:
			if (output == self.despawn):
				print("don't try to kill enemies by passing despawn! Do damage")
			else:
				print("Unit executing received function")
				output()
			# elif (output == hit()):
			# 	hit()
			# else:
			# 	print("Unrecognised function sent to Unit")
			#output = output()
		return output

	def despawn(self:Unit) -> None:
		# clean up the node
		#print(str(self.node) + " despawning")
		# make sure this doesn't get called multiple times
		print(f"Unit despawning at {self.node.getPos()}")
		self.dying = True
		#if self.dmgSeq is not None:
		#	self.dmgSeq.clearIntervals()
		# remove update task from taskMgr
		if (base.taskMgr.getTasksNamed(str(self.node)+"_update") != None):
			base.taskMgr.remove(base.taskMgr.getTasksNamed(str(self.node)+"_update"))
		# clean up node
		self.node.removeNode() 	

# Unit attacks something else, doing its damage
def attack(unit:Unit, target:Unit):
	if (type(target) is Unit):
		target(hit(unit))
	else:
		target.damage(unit.damage)

def hit(unit:Unit, hitter:Unit):
	# take the damage
	unit.hp -= hitter.damage
	
	# check that it's not already in the process of despawning
	if not unit.dying:
		# flash red for a moment
		if unit.hp > 0: 
			#self.dmgSeq.start()
		else: # die if hp is 0 or less
			unity.despawn()
			return 0
	return unit.hp

def getTargetPos(unit:ChaseTarget) -> Vec3:
	# TODO handle different targets differently (mapping needed??)
	#print(f"ChaseTarget has {self.target.getPos()} as target")
	return unit.target.getPos()

def makeColliders(node:NodePath, bitmask:int=0x02) -> CollisionCapsule, NodePath:
	#		  					  CollisionCapsule(ax, ay,    az,   bx, by,  bz, radius)
	hitSphere: CollisionCapsule = CollisionCapsule(0., -0.25, 0.75, 0., 0.2, 0.75, .125)
	hcnode = CollisionNode('{}-cnode'.format(str(node)))
	hcnode.setIntoCollideMask(BitMask32(0x02))
	hitNp: NodePath = node.attachNewNode(hcnode)
	hitNp.node().addSolid(hitSphere)
	return hitSphere, hitNp

def timeToTarget(unit:Unit, targetNode:NodePath) -> float | None:
	# calculate distance to target in order to calculate time-length of move Interval
	if speed == 0: return None
	dist = getTargetPos(unit) - targetNode.getPos()
	dist = np.sqrt(dist.x * dist.x + dist.y * dist.y + dist.z * dist.z)
	return dist/speed

def seekTarget(unit:Unit, targetNode: NodePath) -> Sequence:
	moveInt: Interval = unit.node.posInterval(timeToTarget(unit,targetNode), unit.target.getPos(), unit.node.getPos(), fluid=1, 
									blendType='noBlend')

	# on arrival/despawn, do damage to enemy
	moveSeq: Sequence = Sequence(
		unit.move,
		Func(hit),
		Func(unit.despawn)
	)
	moveSeq.start()
	return moveSeq
