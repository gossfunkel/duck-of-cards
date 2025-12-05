from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, Vec3, CollisionCapsule, CollisionNode, BitMask32
from direct.interval.IntervalGlobal import *
from __future__ import annotations
from typing import Any
from collections.abc import Callable

class Unit():
	def __init__(self,model:GeomNode,node:NodePath,damage:float,speed:float)
	self.model: GeomNode = model
	self.node: NodePath
	self.target: NodePath
	self.damage: float
	self.speed: float
	self.moveSeq: Sequence

	# pretty sure this is terrible code security/privacy but it feels like a good way
	# 	to inject dependencies at runtime
	def __call__(self, func: Callable[[Any],Any], arg:Any):
		# execute function with arg - e.g. damage(arrow) to do damage via an arrow
		output = func(arg)
		if type(output) == Callable[[Any],Any]:
			output = output()
		return output

def despawn(self:Unit) -> None:
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

def hit(self:Unit, hitter:Unit):
	self.hp -= hitter.damage
	return despawn if self.hp <= 0 else self.hp

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

def timeToTarget(unit:ChaseTarget, targetNode:NodePath) -> float | None:
	# calculate distance to target in order to calculate time-length of move Interval
	if speed == 0: return None
	dist = getTargetPos(unit) - targetNode.getPos()
	dist = np.sqrt(dist.x * dist.x + dist.y * dist.y + dist.z * dist.z)
	return dist/speed

def chaseTarget(unit:ChaseTarget, targetNode: NodePath) -> Sequence:
	moveInt: Interval = unit.node.posInterval(.5, unit.target.getPos(), unit.node.getPos(), fluid=1, 
									blendType='noBlend')# if move is None else move

	# on arrival/despawn, do damage to enemy
	#self.despawnInt = Func(self.despawn)
	moveSeq: Sequence = Sequence(
		self.move,
		Func(self.attack)
	)
	moveSeq.start()
	return moveSeq
