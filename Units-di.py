from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, Vec3, CollisionCapsule, CollisionNode, BitMask32
from direct.interval.IntervalGlobal import *
from __future__ import annotations
from typing import Any
from collections.abc import Callable

class ChaseTarget():
	self.model: GeomNode
	self.node: NodePath
	self.target: NodePath
	self.damage: float
	self.speed: float
	self.moveSeq: Sequence

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

def accumulate(x: int) -> int:
	return x + 1

def double(x: int) -> int:
	return x * 2

def main() -> None:
	funky = Functor(5)
	funky = funky(accumulate)(double)
	print(funky)

if __name__ == '__main__':
	#print("running")
	main()
