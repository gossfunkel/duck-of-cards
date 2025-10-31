from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, BitMask32, Vec3, CollisionCapsule, CollisionNode, TransformState, LMatrix4
from panda3d.core import TransformState, TextureStage, VBase3
from direct.task import Task
from direct.interval.IntervalGlobal import *
from direct.fsm.FSM import FSM

class SpriteMod(FSM):
	def __init__(self, name, pos, speed) -> None:
		# TODO this can be cleaned up using the defaultFilter(self, request, args) method 
		# 	and a lookup table {('TopRight','Right'):'BottomRight',('TopRight','Left'):'TopLeft'} etc

		FSM.__init__(self, (str(name) + 'FSM')) # must be called when overloading

		#self.pos: Vec3 = pos
		self.speed: float = speed
		#self.period: float = 90. / speed

		self.node.setH(self.node.getH() + 45)

	def defaultFilter(self, request, args) -> str:
		return 'BottomLeft'

	def enterTopLeft(self) -> None:
		# TODO lerp round
		#print(self.node.getX(), self.node.getY(), self.node.getZ())
		#print(str(self.node) + " facing top left")
		#self.node.lookAt(self.tlNode)
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()

	#def exitTopLeft(self) -> None:
	#	#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)

	def filterTopLeft(self, request, args) -> str: # process input while facing the top left (-x,+y)
		if (request == 'Left'):
			return 'BottomLeft'
		elif (request == 'Right'):
			return 'TopRight'
		elif (request == 'Flip'):
			return 'BottomRight'
		else:
			return None

	def enterTopRight(self) -> None:
		# TODO lerp round
		#print(str(self.node) + " facing top right")
		#self.node.lookAt(self.trNode)
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()

	#def exitTopRight(self) -> None:
	#	self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])	
	#	#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)
	#	#self.node.setTexHpr(TextureStage.getDefault(), 0,0,0)

	def filterTopRight(self, request, args) -> str: # process input while facing top right (+x,+y)
		if (request == 'Left'):
			return 'TopLeft'
		elif (request == 'Right'):
			return 'BottomRight'
		elif (request == 'Flip'):
			return 'BottomLeft'
		else:
			return None

	def enterBottomRight(self) -> None:
		# TODO lerp round
		#print(str(self.node) + " facing bottom right")
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()

	#def exitXneg(self) -> None:	
	#	self.nodepath.set_scale(self.nodepath.get_scale()[0],self.nodepath.get_scale()[1]*-1,self.nodepath.get_scale()[2])
	#	#self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
		
	def filterBottomRight(self, request, args) -> str: # process input while facing bottom right (+x,-y)
		if (request == 'Left'):
			return 'TopRight'
		elif (request == 'Right'):
			return 'BottomLeft'
		elif (request == 'Flip'):
			return 'TopLeft'
		else:
			return None

	def enterBottomLeft(self) -> None:
		# TODO lerp round
		#print(str(self.node) + " facing bottom left")
		#self.node.lookAt(self.blNode)
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()

	#def exitYneg(self) -> None:
	#	self.nodepath.set_tex_scale(TextureStage.getDefault(), float(self.nodepath.get_tex_scale(TextureStage.getDefault())[0]*-1),float(self.nodepath.get_tex_scale(TextureStage.getDefault())[1])) #,self.nodepath.get_scale()[2])
	#	self.nodepath.set_scale(0.05,0.05,0.05)
	#	#self.node.setTexTransform(TextureStage.getDefault(), self.mirrorTS)

	def filterBottomLeft(self, request, args) -> str: # process input while facing bottom left (-x,+y)
		if (request == 'Left'):
			return 'BottomRight'
		elif (request == 'Right'):
			return 'TopLeft'
		elif (request == 'Flip'):
			return 'TopRight'
		else:
			return None

class Enemy(SpriteMod):
	def __init__(self, name, pos, speed) -> None:
		assert pos != None, f'Enemy spawning with no position!'
		#print(str(name) + " spawning")
		self.model = base.loader.loadModel("assets/dogboard1.gltf")
		#self.model.setP(90)
		self.model.setScale(0.1)
		#self.model.setPos(0.,0.,.8)
		self.node: NodePath = base.enemyModelNd.attachNewNode("enemy-" + str(name))
		self.model.reparent_to(self.node)
		self.node.setPos(pos + Vec3(0.,0.,-.12))
		self.node.setP(90)
		super().__init__(str(name), pos, speed)

		facing: str
		if (pos.getX() > 0 and pos.getY() > 0):
			#print("enemy +x +y")
			self.model.setH(180)
			self.node.setHpr(-270,180,0)
			#self.node.setH(-270)
			facing = 'TopRight'
		elif (pos.getX() <= 0 and pos.getY() > 0):
			#print("enemy -x +y")
			#self.model.setH(0)
			facing = 'TopLeft'
		elif (pos.getX() > 0 and pos.getY() <= 0):
			#print("enemy +x -y")
			self.node.setHpr(-90,0,0)
			facing = 'BottomRight'
		elif (pos.getX() <= 0 and pos.getY() <= 0):
			#print("enemy -x -y")
			self.model.setH(270)
			facing = 'BottomLeft'
		else:
			raise AssertionError("Enemy spawn location bugged!")
		#print(str(self.node) + " spawned at " + str(self.node.getPos()))
		assert (self.node.getPos()[0] != 0 or self.node.getPos()[1] != 0), f'Enemy spawning at 0,0!'
		# make them look where they're going
		self.request(facing)
		#self.node.setH(-30)
		# modified target vector to prevent enemies flying into air or sinking into ground as they approach castle
		self.targetPos: Vec3 = Vec3(base.castle.node.getX(),base.castle.node.getY(),self.node.getZ())

		# define dying tag and set to False until enemy loses all HP
		self.dying: bool = False
		self.hp: float = 20.0
										  #CollisionCapsule(ax, ay,    az,   bx, by,  bz, radius)
		self.hitSphere: CollisionCapsule = CollisionCapsule(0., -0.25, 0.75, 0., 0.2, 0.75, .125)
		hcnode = CollisionNode('{}-cnode'.format(str(self.node)))
		hcnode.setIntoCollideMask(BitMask32(0x02))
		self.hitNp: NodePath = self.node.attachNewNode(hcnode)
		self.hitNp.node().addSolid(self.hitSphere)
		#self.hitNp.show() 								# uncomment to show hitbox
		self.move: Interval = self.node.posInterval(30./self.speed, self.targetPos, self.node.getPos())
		self.moveSeq: Sequence = Sequence(
			self.move,
			Func(self.despawnAtk)
		)
		self.dmgSeq: Sequence = Sequence(Func(self.node.setColor,1.,0.,0.,1.),
				Wait(0.05),
				Func(self.node.setColor,1.,0.5,0.5,1.))

		self.moveSeq.start()

		base.taskMgr.add(self.updateEnemy, "update_"+str(self.node), taskChain='default')

	def updateEnemy(self, task) -> int:
		if (self.hp <= 0.0): 
			# die if health gets too low
			#self.despawnDie()
			return task.done
		# otherwise, keep going :)
		return task.cont

	def despawnAtk(self) -> None:
		# damage the castle
		# and do a wee animation?
		base.castle.takeDmg()

		# clean up the node
		#print(str(self.node) + " despawning")
		# make sure this doesn't get called multiple times
		self.dying = True
		# stop moving and don't blink
		self.moveSeq.clearIntervals()
		self.dmgSeq.clearIntervals()
		# remove update task from taskMgr
		if (base.taskMgr.getTasksNamed(str(self.node)+"_update") != None):
			base.taskMgr.remove(base.taskMgr.getTasksNamed(str(self.node)+"_update"))
		# clean up node
		self.node.removeNode() 	

	def despawnDie(self) -> int:
		# make sure this doesn't get called multiple times
		self.dying = True
		#print(str(self.node) + " dying")
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
		return 1

	def damage(self, dmg) -> None:
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
	def __init__(self, name, pos, speed) -> None:
		self.model = loader.loadModel("assets/duckboard1.gltf")
		self.model.setScale(0.04)
		#self.model.setP(90)
		self.node: NodePath = render.attachNewNode("duck-" + str(name))
		self.model.reparent_to(self.node)
		self.node.setPos(pos)
		#self.nodepath = base.duckModel.instanceTo(self.node)
		# self.nodepath.setR(90)
		# self.nodepath.setH(90)
		super().__init__(str(name), pos, speed)
		#print("spawning a normal duck")
		#self.demand('BottomRight')
		#self.speed = speed

		self.hp: float = 1000000.0

		base.taskMgr.add(self.updateDuck, "update_"+str(self.node), taskChain='default')
	
	def updateDuck(self, task) -> int:
		if base.fsm.state == 'Gameplay':
			# rotate the random duck
			if ((task.frame % 150) == 1):
				#print("duck turning")
				self.request('Right')
				#self.turnRight()

		return Task.cont

	#def turnRight(self):
	#	self.demand('Right')

	#def turnLeft(self):
	#	self.demand('Left')

	#def turnAround(self):
	#	self.demand('Flip')

# load models in here?
