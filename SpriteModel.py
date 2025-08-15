from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, BitMask32, Vec3, CollisionCapsule, CollisionNode
from direct.interval.IntervalGlobal import *
from direct.fsm.FSM import FSM

class SpriteMod(FSM):
	def __init__(self, name, pos, speed):
		FSM.__init__(self, (str(name) + 'FSM')) # must be called when overloading

		self.pos = pos
		self.speed = speed

	def enterX(self):
		# TODO lerp round
		print(self.node.getX()+5, self.node.getY(), self.node.getZ())
		self.node.lookAt(self.node.getX()+5, self.node.getY(), self.node.getZ())

	def filterX(self, request, args): # process input while facing +x
		if (request == 'Left'):
			return 'Y'
		elif (request == 'Right'):
			return 'Yneg'
		elif (request == 'Flip'):
			return 'Xneg'
		else:
			return None

	def enterY(self):
		# TODO lerp round
		self.node.lookAt(self.node.getX(), self.node.getY()+5,self.node.getZ())

	def filterY(self, request, args): # process input while facing +x
		if (request == 'Left'):
			return 'Xneg'
		elif (request == 'Right'):
			return 'X'
		elif (request == 'Flip'):
			return 'Yneg'
		else:
			return None

	def enterXneg(self):
		# TODO lerp round
		self.node.lookAt(self.node.getX()-5, self.node.getY(),self.node.getZ())

	def filterXneg(self, request, args): # process input while facing +x
		if (request == 'Left'):
			return 'Yneg'
		elif (request == 'Right'):
			return 'Y'
		elif (request == 'Flip'):
			return 'X'
		else:
			return None

	def enterYneg(self):
		# TODO lerp round
		self.node.lookAt(self.node.getX(), self.node.getY()-5,self.node.getZ())

	def filterYneg(self, request, args): # process input while facing +x
		if (request == 'Left'):
			return 'X'
		elif (request == 'Right'):
			return 'Xneg'
		elif (request == 'Flip'):
			return 'Yneg'
		else:
			return None

class Enemy(SpriteMod):
	def __init__(self, name, pos, speed):
		super().__init__(str(name), pos, speed)

		print(str(name) + " spawning")
		self.node = base.enemyModelNd.attachNewNode(name)
		self.node.setPos(pos)
		self.node.setColor(1.,0.5,0.5,1.)
		#self.node.setH(-30)
		# modified target vector to prevent enemies flying into the air as they approach castle
		self.targetPos = base.castle.model.getPos() - Vec3(0.,0.,1.)

		base.enemyModel.instanceTo(self.node)
		
		# make them look where they're going
		#self.node.lookAt(self.targetPos)
		if (self.targetPos.getX() - pos.getX() > 1 or self.targetPos.getX() - pos.getX() < -1):
			# entity and target x are more than 1 unit apart
			if (self.targetPos.getX() > pos.getX()): # target is further 'up' x relative to entity
				self.demand('X')
				#print(str(self.node)+" facing X")
			else: 								# target is lower down x-axis relative to entity
				self.demand('Xneg')
				#print(str(self.node)+" facing Xneg")
		else: # entity and target x are less than 1 unit apart (aligned on x axis)
			if (self.targetPos.getY() > pos.getY()): # target is further 'up' y relative to entity
				self.demand('Y')
				#print(str(self.node)+" facing Y")
			else: 								# target is lower down y-axis relative to entity
				self.demand('Yneg')
				#print(str(self.node)+" facing Yneg")

		self.hp = 20.0
		
		#self.speed = speed # allows slowing and rushing effects

						# CollisionCapsule(ax, ay, az, bx, by, bz, radius)
		self.hitSphere = CollisionCapsule(0.09, -0.1, 1.2,0.09, -0.1, 1.45, .12)
		hcnode = CollisionNode('{}-cnode'.format(str(self.node)))
		hcnode.setIntoCollideMask(BitMask32(0x02))
		self.hitNp = self.node.attachNewNode(hcnode)
		self.hitNp.node().addSolid(self.hitSphere)
		#self.hitNp.show() 								# uncomment to show hitbox

		self.move = self.node.posInterval(20./self.speed, self.targetPos, self.node.getPos())
		self.moveSeq = Sequence(
			self.move,
			Func(self.despawnAtk)
		)

		self.dmgSeq = Sequence(Func(self.node.setColor,1.,0.,0.,1.),
				Wait(0.05),
				Func(self.node.setColor,1.,0.5,0.5,1.))

		self.moveSeq.start()

		base.taskMgr.add(self.update, "update-"+str(self.node), taskChain='default')

	def update(self, task):
		if (self.hp <= 0.0): # die if health gets too low
			#self.despawnDie()
			return task.done
		# otherwise, keep going :)
		return task.cont

	def despawnAtk(self):
		# damage the castle
		# and do a wee animation?
		base.castle.takeDmg()

		# clean up the node
		print(str(self.node) + " despawning")
		self.despawnDie()

	def despawnDie(self):
		# stop moving and don't blink
		self.moveSeq.clearIntervals()
		self.dmgSeq.clearIntervals()
		# remove update task from taskMgr
		if (base.taskMgr.getTasksNamed(str(self.node)+"_update") != None):
			base.taskMgr.remove(base.taskMgr.getTasksNamed(str(self.node)+"_update"))
		# do a wee animation?
		# give player gold
		base.giveGold(5)
		# clean up the node
		print(str(self.node) + " dying")
		self.node.removeNode() 

	def damage(self, dmg):
		# take the damage
		self.hp -= dmg

		# then flash red for a moment
		if self.hp > 0: self.dmgSeq.start()
		else: 
			self.despawnDie()
		# this seems to cause despawnDie to run twice, somehow. I should do proper garbage collection
		# on these objects, and remove the enemies as well as their nodes

class NormalInnocentDuck(SpriteMod): 
	def __init__(self, name, pos, speed):
		super().__init__(str(name), pos, speed)
		print("spawning a normal duck")
		self.node = base.duckNp.attachNewNode(name)
		self.node.setPos(pos)
		self.demand('Xneg')
		#self.speed = speed

		self.hp = 1000000

		# temporary integer ticker to rotate the random duck
		self.t = 0

		base.duckModel.instanceTo(self.node)

		base.taskMgr.add(self.update, "update-"+str(self.node), taskChain='default')
	
	def update(self, task):
		if base.fsm.state == 'Gameplay':
			self.t += int(1 * self.speed)
		
		# rotate the random duck
		if ((self.t % 90) == 1):
			print("duck turning")
			self.demand('Right')
			#self.turnRight()

		return task.cont

	#def turnRight(self):
	#	self.demand('Right')

	#def turnLeft(self):
	#	self.demand('Left')

	#def turnAround(self):
	#	self.demand('Flip')

# load models in here?
