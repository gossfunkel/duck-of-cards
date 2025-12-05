from direct.showbase.ShowBase import ShowBase
from panda3d.core import BitMask32, CollisionNode, CollisionSphere, CollisionTraverser, CollisionHandlerQueue
from panda3d.core import Vec3, ModelPool
from direct.interval.IntervalGlobal import *
import Projectiles
import numpy as np
import tools

# tower types data

class PlayerCastle():
	def __init__(self) -> None:
		model: GeomNode = loader.loadModel("assets/playerBase.gltf")
		model.setScale(0.2)
		self.node: NodePath = render.attachNewNode("castleMap")
		model.reparentTo(self.node)
		self.node.setPos(0.,0.,0.)
		self.node.setH(-45)
		self.node.setTag("castle", '0')
		#model.node().setIntoCollideMask(BitMask32(0x04))

		#self.node.ls()

	def damage(self, dmg) -> None:
		# take damage
		base.dmgCastle(dmg)
		# flash red for a moment TODO don't use setColor, have a shader or something
		Sequence(Func(self.node.setColor,1.2,0.1,0.1,1.),
				Wait(0.1),
				Func(self.node.setColor,0.3,0.35,0.6,1.)).start()
		base.mapImg.setRed(int(base.width/2),int(base.length/2),base.mapImg.getRed(int(base.width/2),int(base.length/2))- dmg/100.)

	def isAlive(self) -> bool:
		return True if base.getCastleHP() > 0 else False

class Tower():
	def __init__(self, pos, u ,v) -> None:
		towerModel: NodePath = base.loader.loadModel("assets/tower.gltf")
		print("spawning tower at " + str(pos))
		towerModel.setScale(0.2)
		#towerModel.setP(90)
		self.node: NodePath = render.attachNewNode("tower")
		self.node.setTag("u",str(u))
		self.node.setTag("v",str(v))
		towerModel.wrtReparentTo(self.node)
		self.landPosition: Vec3 = pos
		#self.u: int = u
		#self.v: int = v
		self.node.setPos(pos.getX(),pos.getY(),pos.getZ() + .04)
		#self.node.setScale()
		self.rateOfFire: float = 1.0
		self.damage: float = 1.0
		self.range: float = 5.0
		self.numShots: int = 1
		self.cooldown: float = 3.0
		self.onCD: bool = True
		self.damageType: str = "physical"

		self.vel: Vec3 = Vec3(0.,0.,-0.2)

		# initialise detection of enemies in range
		self.rangeSphere: CollisionSphere = CollisionSphere(0, 0, 0, self.range)
		rcnode = CollisionNode(str(self.node) + '-range-cnode')
		rcnode.setFromCollideMask(BitMask32(0x02))
		self.rangeColliderNp: NodePath = self.node.attachNewNode(rcnode)
		self.rangeColliderNp.node().addSolid(self.rangeSphere)
		#self.rangeColliderNp.show()

		self.enemyDetector: CollisionTraverser = CollisionTraverser(str(self.node) + '-enemy-detector')
		self.detectorQueue: CollisionHandlerQueue = CollisionHandlerQueue()
		self.enemyDetector.addCollider(self.rangeColliderNp, self.detectorQueue)
		#self.enemyDetector.showCollisions(base.enemyModelNd)

		self.cdInt: Interval = Wait(self.cooldown/self.rateOfFire)
		self.cdSeq: Sequence = Sequence(self.cdInt,Func(self.cdOFF))
		self.scanSeq: Sequence = Sequence(Func(self.update))
		self.cdSeq.start()
		self.scanSeq.loop()

		base.taskMgr.add(self.land, str(self.node)+"_land", taskChain='default')
		# update task replaced with sequence for pausability

	def land(self, task) -> int:
		dist: Vec3 = self.node.getPos() - self.landPosition
		sumDist: float = np.sqrt(dist[0]*dist[0] + dist[1]*dist[1] + dist[2]*dist[2])
		#print("dist:" + str(dist))
		if (sumDist < tools.epsilon and sumDist > 0):
			self.node.setPos(self.landPosition)
			# TODO: play clunk noise
			#print("tower landed at " + str(self.node.getPos()))
			return task.done
		else:
			pos, self.vel = tools.calcDampedSHM(self.node.getPos(),self.vel,self.landPosition,globalClock.getDt(),15., .99)
			self.node.setPos(pos)
			#print("pos: " + str(self.node.getPos()) + " | vel: " + str(self.vel))
			return task.cont

	def update(self) -> None:
		if not self.onCD: self.attackScan()

	#def update(self, task):
		#	# scan for enemies if not on cooldown
		#	if not self.onCD: self.attackScan()
		#	return task.cont
		#def pause(self):
		#	base.taskMgr.getTasksNamed(str(self.node)+"_update").pause() 
		#   ^ this pause method isn't a thing. using a sequence instead of the task

	#def takedmg(self):
		#base.mapImg.setRed(self.u,self.v,base.mapImg.getRed(self.u,self.v)-0.05)

	def cdOFF(self) -> bool:
		if not self.onCD: return 1
		else: 
			self.onCD = False
			return 0

	def attackScan(self) -> None:
		# check for intersecting collisionsolids
		self.enemyDetector.traverse(base.enemyModelNd)
		#print("scanning...")

		if (self.detectorQueue.getNumEntries() > 0):
			print("enemy detected!")
			# sort queue of detected solids by closest (n.b. edit here for priority options)
			self.detectorQueue.sortEntries()

			# find nodePoint and ID of detected enemy
			enemyNp = self.detectorQueue.entries[0].getIntoNodePath()
			#target = self.detectorQueue.entries[0].getSurfacePoint(enemyNp)
			#enemyId = enemyNp.getName()[26:len(enemyNp.getName())-6] #print(enemyId)
			enemyId = enemyNp.getName().split("-")[3]
			print(enemyId)
			# FIRE
			self.launchProjectiles(enemyId)

			# put self on cooldown
			self.onCD = True
			self.cdSeq.start()

	def launchProjectiles(self, enemy) -> Projectiles.Arrow:
		print(f"firing at {enemy}")
		newArrows = []
		for _ in range(self.numShots):
			newArrows.append(Projectiles.Arrow(self.node.getPos(), enemy))
		return newArrows

class MagicTower(Tower):
	def __init__(self, pos, u, v) -> None:
		Tower.__init__(self, pos, u, v)
		self.node.removeNode()
		ModelPool.releaseModel("assets/tower.gltf")
		self.damageType = "magic"
		towerModel: NodePath = base.loader.loadModel("assets/magicTower.gltf")
		self.node: NodePath = render.attachNewNode("tower")
		self.node.setTag("u",str(u))
		self.node.setTag("v",str(v))
		towerModel.wrtReparentTo(self.node)

	def launchProjectiles(self, enemy) -> Projectiles.Fireball:
		#print("firing at " + enemy)
		newFireballs = []
		for _ in range(self.numShots):
			newFireballs.append(Projectiles.Fireball(self.node.getPos(), enemy))
		return newFireballs
