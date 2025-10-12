from direct.showbase.ShowBase import ShowBase
from panda3d.core import BitMask32, CollisionNode, CollisionSphere, CollisionTraverser, CollisionHandlerQueue
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import *

class PlayerCastle():
	def __init__(self):
		self.model = base.loader.loadModel("assets/playerBase.gltf")
		self.node = render.attachNewNode("castleMap")
		self.model.reparentTo(self.node)
		self.model.setScale(0.2)
		self.node.setPos(0.,0.,0.)
		self.node.setP(90)
		self.model.setColor(0.3,0.35,0.6,1.)
		self.model.setTag("castle", '1')
		self.model.node().setIntoCollideMask(BitMask32(0x04))

	def takeDmg(self):
		# take damage
		base.dmgCastle(5.0)
		# flash red for a moment
		Sequence(Func(self.model.setColor,1.2,0.1,0.1,1.),
				Wait(0.1),
				Func(self.model.setColor,0.3,0.35,0.6,1.)).start()

class Arrow():
	def __init__(self, pos, enemyId):
		self.arrowModel = base.loader.loadModel("assets/arrow2.gltf")
		self.node = render.attachNewNode("arrow")
		self.arrowModel.reparentTo(self.node)
		self.arrowModel.setScale(0.06)
		self.enemy = base.enemies[int(enemyId)]
		self.damage = 10.0
		self.node.setP(30)
		self.node.setY(-45) 
		# modified origin for realism. 
		self.node.setPos(pos + Vec3(-.1, 0., .7))
		self.node.lookAt(self.getTargetPos())
		#projectileNp = render.attachNewNode(ActorNode('projectile'))
		# self.cnode = CollisionNode('arrowColNode')
		# self.cnode.setFromCollideMask(BitMask32(0x00))
		# self.fromObject = self.node.attachNewNode(self.cnode)
		# self.fromObject.node().addSolid(CollisionSphere(0, 0, 0, .2))
		#self.fromObject.show()
		self.move = self.node.posInterval(.5, self.getTargetPos(), 
											self.node.getPos(), fluid=1, blendType='noBlend')

		# on arrival/despawn, do damage to enemy
		self.despawnInt = Func(self.despawn)
		self.moveSeq = Sequence(
			self.move,
			self.despawnInt
		).start()

	def getTargetPos(self):
		# get up-to-date position
		# TODO - TAKE LEAD POSITION IN PURSUIT (i.e. arrows should fly to where enemies are going)
		p = self.enemy.node.getPos()
		# adjust for visual accuracy
		#p[0] += .55
		#p[1] -= .3
		p[2] += .75
		return p

	def despawn(self):
		# do damage and remove
		self.enemy.damage(self.damage)
		self.node.removeNode()

class Tower():
	def __init__(self, pos):
		towerModel = base.loader.loadModel("assets/tower.gltf")
		towerModel.setScale(0.2)
		self.node = render.attachNewNode("tower")
		towerModel.reparentTo(self.node)
		self.node.setPos(pos)
		self.node.setP(90)
		#self.node.setScale()
		self.rateOfFire = 1.0
		self.damage = 1.0
		self.range = 5.0
		self.cooldown = 3.0
		self.onCD = True

		# initialise detection of enemies in range
		self.rangeSphere = CollisionSphere(0, 0, 0, self.range)
		rcnode = CollisionNode(str(self.node) + '-range-cnode')
		rcnode.setFromCollideMask(BitMask32(0x02))
		self.rangeColliderNp = self.node.attachNewNode(rcnode)
		self.rangeColliderNp.node().addSolid(self.rangeSphere)
		#self.rangeColliderNp.show()

		self.enemyDetector = CollisionTraverser(str(self.node) + '-enemy-detector')
		self.detectorQueue = CollisionHandlerQueue()
		self.enemyDetector.addCollider(self.rangeColliderNp, self.detectorQueue)
		#self.enemyDetector.showCollisions(base.enemyModelNd)

		self.cdInt = Wait(self.cooldown/self.rateOfFire)
		self.cdSeq = Sequence(self.cdInt,Func(self.cdOFF))
		self.scanSeq = Sequence(Func(self.update))
		self.cdSeq.start()
		self.scanSeq.loop()

		#base.taskMgr.add(self.update, str(self.node)+"_update", taskChain='default')
		# task replaced with sequence for pausability

	def update(self):
		if not self.onCD: self.attackScan()

	#def update(self, task):
		#	# scan for enemies if not on cooldown
		#	if not self.onCD: self.attackScan()
		#	return task.cont
		#def pause(self):
		#	base.taskMgr.getTasksNamed(str(self.node)+"_update").pause() 
		#   ^ this pause method isn't a thing. using a sequence instead of the task

	def cdOFF(self):
		if not self.onCD: return 1
		else: 
			self.onCD = False
			return 0

	def attackScan(self):
		# check for intersecting collisionsolids
		self.enemyDetector.traverse(base.enemyModelNd)
		#print("scanning...")

		if (self.detectorQueue.getNumEntries() > 0):
			#print("enemy detected!")
			# sort queue of detected solids by closest (n.b. edit here for priority options)
			self.detectorQueue.sortEntries()

			# find nodePoint and ID of detected enemy
			enemyNp = self.detectorQueue.entries[0].getIntoNodePath()
			#target = self.detectorQueue.entries[0].getSurfacePoint(enemyNp)
			enemyId = enemyNp.getName()[26:len(enemyNp.getName())-6] #print(enemyId)
			# FIRE
			self.launchProjectiles(enemyId)

			# put self on cooldown
			self.onCD = True
			self.cdSeq.start()

	def launchProjectiles(self, enemy):
		print("firing at " + enemy)
		newArrow = Arrow(self.node.getPos(), enemy)
