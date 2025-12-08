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
		unit.Unit(self,model,node,damage,speed,moveSeq)
		self.target: NodePath = base.castle
		self.hitSphere, self.hitNp = unit.makeColliders(node)
		#self.moveSeq: Sequence = unit.seekTarget(self,self.target) if moveSeq is None else moveSeq
		
		base.taskMgr.add(self.update, f"{str(self.node)}_update", taskChain='default')

	def update(self, task) -> int:
		if not self.dying:
			if base.fsm.state == 'Gameplay':
				pos = self.node.getPos()
				self.node.setPos(pos + Vec3(((self.target.x + pos.x)/2)*self.speed/3 * globalClock.getDt(),
											((self.target.y + pos.y)/2)*self.speed/3 * globalClock.getDt(),
											((self.target.z + pos.z)/2)*self.speed/3 * globalClock.getDt()))
				self.still = False if self.speed else True
			return task.cont
		if self.dying:
			return task.done

	def despawn(self):
		# hacky solution to not giving gold if not killed
		if hp <= 0:
			base.giveGold(5)
		super().despawn()

class BasicEnemy(Enemy):
	def __init__(self, pos:Vec3) -> None:
		self.name: str = "BasicDog"
		speed: float = 1.
		pos += Vec3(0.,0.,1.)
		model, node = sm.loadModel(self.name,pos)
		damage: float = 5.0
		hp: float = 20.0
		Enemy.__init__(self, model, node, damage, speed, hp)

# def runTest() -> None:
# 	testEnemy = BasicEnemy(Vec3(10.,10.,0.))
# 	testEnemy = testEnemy(kill)

# if __name__ == '__main__':
# 	#print("running")
# 	runTest()
