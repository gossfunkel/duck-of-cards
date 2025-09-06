from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, BitMask32, Vec3, CollisionCapsule, CollisionNode, TransformState, LMatrix4
from panda3d.core import TransformState, TextureStage, VBase3
from direct.interval.IntervalGlobal import *
from direct.fsm.FSM import FSM

class SpriteMod(FSM):
	def __init__(self, name, pos, speed):
		FSM.__init__(self, (str(name) + 'FSM')) # must be called when overloading

		self.pos = pos
		self.speed = speed

		#self.mirrorMat = TransformState.makeMat(LMatrix4(1,-1,1))
		#self.mirrorTS = TransformState.makeScale(VBase3(0, -1, 0))

		self.xNode = Vec3(self.node.getX()+5, self.node.getY(), self.node.getZ())
		self.yNode = Vec3(self.node.getX(), self.node.getY()+5,self.node.getZ())
		self.xNegNode = Vec3(self.node.getX()-5, self.node.getY(),self.node.getZ())
		self.yNegNode = Vec3(self.node.getX(), self.node.getY()-5,self.node.getZ())

	def enterX(self):
		# TODO lerp round
		#print(self.node.getX(), self.node.getY(), self.node.getZ())
		print(str(self.node) + " facing X")
		self.node.lookAt(self.xNode)

	#def exitX(self):
	#	#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)

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
		print(str(self.node) + " facing Y")
		self.node.lookAt(self.yNode)
		#self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
		#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)
		#self.node.setTexHpr(TextureStage.getDefault(), 0,180,0)
		#self.node.setTexRotate(self.node.findAllTextureStages()[0], 180)

	#def exitY(self):
	#	self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])	
	#	#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)
	#	#self.node.setTexHpr(TextureStage.getDefault(), 0,0,0)

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
		print(str(self.node) + " facing Xneg")
		#self.nodepath.set_scale(self.nodepath.get_scale()[0],self.nodepath.get_scale()[1]*-1,self.nodepath.get_scale()[2])
		#self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
		self.node.lookAt(self.xNegNode)

	#def exitXneg(self):	
	#	self.nodepath.set_scale(self.nodepath.get_scale()[0],self.nodepath.get_scale()[1]*-1,self.nodepath.get_scale()[2])
	#	#self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
		
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
		print(str(self.node) + " facing Yneg")
		self.node.lookAt(self.yNegNode)
		#self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
		#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)

	#def exitYneg(self):
	#	self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
	#	self.nodepath.set_scale(0.05,0.05,0.05)
	#	#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)

	def filterYneg(self, request, args): # process input while facing +x
		if (request == 'Left'):
			return 'X'
		elif (request == 'Right'):
			return 'Xneg'
		elif (request == 'Flip'):
			return 'Yneg'
		else:
			return None

class SpriteModSide(SpriteMod):
	def enterX(self):
		print(str(self.node) + " facing X (SpriteModSide)")
		self.node.lookAt(self.xNode)
		self.node.setH(90) # flip model to correct face

	def exitX(self):
		self.node.setH(0) # flip model to correct face

	def enterY(self):
		print(str(self.node) + " facing Y (SpriteModSide)")
		self.node.lookAt(self.yNode)
		#self.nodepath.set_scale(self.nodepath.get_scale()[0],self.nodepath.get_scale()[1]*-1,self.nodepath.get_scale()[2])
		self.node.setH(180) # flip model to correct face

	def exitY(self):
		#self.nodepath.set_scale(self.nodepath.get_scale()[0],self.nodepath.get_scale()[1]*-1,self.nodepath.get_scale()[2])
		self.node.setH(0) # flip model to correct face

	def enterXneg(self):
		print(str(self.node) + " facing Xneg (SpriteModSide)")
		self.node.lookAt(self.xNegNode)
		self.node.setH(-90) # flip model to correct face

	def exitXneg(self):
		self.node.setH(0) # flip model to correct face

class Enemy(SpriteModSide):
	def __init__(self, name, pos, facing, speed):
		assert pos != None, f'Enemy spawning with no position!'
		# create node
		self.node = base.enemyModelNd.attachNewNode(name)
		self.node.setPos(pos)
		self.nodepath = base.enemyModel.instanceTo(self.node)
		super().__init__(str(name), pos, speed)
		assert (facing == 'X' or facing == 'Y' or facing == 'Xneg' or facing == 'Yneg'), f'Enemy given incorrect facing direction!'
		print(str(name) + " spawning")

		#self.node.setColor(1.,0.5,0.5,1.)

		# debug:
		print(str(self.node) + " spawned at " + str(self.node.getPos()))
		assert (self.node.getPos()[0] != 0 or self.node.getPos()[1] != 0), f'Enemy spawning at 0,0!'
		#self.node.setH(-30)
		# modified target vector to prevent enemies flying into air or sinking into ground as they approach castle
		self.targetPos = base.castle.model.getPos() - Vec3(0.,0.,.5)

		# define dying tag and set to False until enemy loses all HP
		self.dying = False

		#self.nodepath.setH(90)
		# make them look where they're going
		self.demand(facing)
		#if (self.node.getPos()[0] > 1):
		#	self.demand('Xneg')
		#elif (self.node.getPos()[1] > 1):
		#	self.demand('Yneg')
		#elif (self.node.getPos()[0] < -1):
		#	self.demand('X')
		#else: 
		#	# this condition should be fine due to the assertion, but could always leave it to throw an error
		#	self.demand('Y')
		#self.node.lookAt(self.targetPos)
		#if (self.targetPos.getX() - self.nodepath.getPos()[0] > 2 or self.targetPos.getX() - self.nodepath.getPos()[0] < -2):
		#	# entity and target x are more than 2 units apart
		#	if (self.targetPos.getX() > self.nodepath.getPos()[0]): # target is further 'up' x relative to entity
		#		self.demand('X')
		#		#print(str(self.node)+" facing X")
		#	else: 								# target is lower down x-axis relative to entity
		#		self.demand('Xneg')
		#		#print(str(self.node)+" facing Xneg")
		#else: # entity and target x are less than 2 units apart (aligned on x axis)
		#	if (self.targetPos.getY() > self.nodepath.getPos()[1]): # target is further 'up' y relative to entity
		#		self.demand('Y')
		#		#print(str(self.node)+" facing Y")
		#	else: 								# target is lower down y-axis relative to entity
		#		self.demand('Yneg')
		#		#print(str(self.node)+" facing Yneg")

		self.hp = 20.0
						#CollisionCapsule(ax, ay, az, bx, by, bz, radius)
		self.hitSphere = CollisionCapsule(0., -0.25, 0.75, 0., 0.2, 0.75, .125)
		hcnode = CollisionNode('{}-cnode'.format(str(self.node)))
		hcnode.setIntoCollideMask(BitMask32(0x02))
		self.hitNp = self.node.attachNewNode(hcnode)
		self.hitNp.node().addSolid(self.hitSphere)
		#self.hitNp.show() 								# uncomment to show hitbox

		self.move = self.node.posInterval(30./self.speed, self.targetPos, self.node.getPos())
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
		# make sure this doesn't get called multiple times
		self.dying = True
		# stop moving and don't blink
		self.moveSeq.clearIntervals()
		self.dmgSeq.clearIntervals()
		# remove update task from taskMgr
		if (base.taskMgr.getTasksNamed(str(self.node)+"_update") != None):
			base.taskMgr.remove(base.taskMgr.getTasksNamed(str(self.node)+"_update"))	
		self.node.removeNode() 	

	def despawnDie(self):
		# make sure this doesn't get called multiple times
		self.dying = True
		print(str(self.node) + " dying")
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
		self.node.removeNode() 

	def damage(self, dmg):
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

class NormalInnocentDuck(SpriteMod): 
	def __init__(self, name, pos, speed):
		self.node = base.duckNp.attachNewNode(name)
		self.node.setPos(pos)
		self.nodepath = base.duckModel.instanceTo(self.node)
		self.nodepath.setH(180)
		super().__init__(str(name), pos, speed)
		#print("spawning a normal duck")
		self.demand('Xneg')
		#self.speed = speed

		self.hp = 1000000

		# temporary integer ticker to rotate the random duck
		self.t = 0


		base.taskMgr.add(self.update, "update-"+str(self.node), taskChain='default')
	
	def update(self, task):
		if base.fsm.state == 'Gameplay':
			self.t += int(1 * self.speed)
		
		# rotate the random duck
		if ((self.t % 90) == 1):
			#print("duck turning")
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
