from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import *
import Units as unit
import SpriteModel as sm
from __future__ import annotations
from typing import Any#, Generic, TypeVar
from collections.abc import Optional

class Enemy(sm.SpriteMod, unit.ChaseTarget):
	def __init__(self, model:GeomNode, node:NodePath, damage:float, speed:float, hp:float, moveSeq:Sequence=None):
		self.target: NodePath = base.castle
		self.dying: bool = False
		self.model: GeomNode = model
		self.node: NodePath = node
		self.damage: float = damage
		self.speed: float = speed
		self.hp: float = hp
		self.hitSphere, self.hitNp = unit.makeColliders(node)

		self.moveSeq: Sequence = unit.chaseTarget(self,self.target) if moveSeq is None else moveSeq

	def takeDamage()

	def kill()

	def despawn()

	def attack()

class BasicEnemy(Enemy):
	def __init__(self, pos:Vec3) -> None:
		self.name: str = "BasicDog"
		speed: float = 1.
		model, node = sm.loadModel(self.name,pos)
		damage: float = 5.0
		hp: float = 20.0
		pos += Vec3(0.,0.,1.)
		Enemy.__init__(self, model, node, damage, speed, hp)

def runTest() -> None:
	testEnemy = BasicEnemy(Vec3(10.,10.,0.))
	testEnemy = testEnemy(kill)

if __name__ == '__main__':
	#print("running")
	runTest()
