from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, BitMask32, Vec3, CollisionCapsule, CollisionNode, TransformState, LMatrix4
from panda3d.core import TransformState, TextureStage, VBase3
from direct.task import Task
from direct.interval.IntervalGlobal import *
from direct.fsm.FSM import FSM

# call to load a SpriteModel from Assets and place in the world
def loadModel(name: str, pos: Vec3) -> GeomNode, NodePath:
	model: GeomNode = base.loader.loadModel(f"assets/{name}.egg")
	node: NodePath = render.attachNewNode(f"spritemod-{name}")
	node.set_pos(pos)
	model.reparentTo(self.node)
	return model, node

class SpriteMod(FSM):
	def __init__(self, name, pos, speed) -> None:
		# TODO this can be cleaned up using the defaultFilter(self, request, args) method 
		# 	and a lookup table {('TopRight','Right'):'BottomRight',('TopRight','Left'):'TopLeft'} etc

		self.speed: float = speed
		FSM.__init__(self, (str(name) + 'FSM')) # must be called when overloading

		# models are saved as egg-texture-cards so that I can use this SwitchNode to flick between textures on a card
		# formatted 0: still front 1: moving left 2: moving right 3: still back [TODO? 4: attack left 5: attack right? 6: death?]
		self.model, self.node = loadModel(name,pos)
		#self.model: GeomNode = base.loader.loadModel(f"assets/{name}.egg")
		self.tsmSwitch: SwitchNode = self.model.getChild(0).node()
		#for x in self.tsmSwitch.children: print(x)
		#self.node: NodePath = render.attachNewNode("testspritemod")
		#self.node.set_pos(pos)
		#self.model.reparentTo(self.node)

		#self.still: bool = False if speed else True

		#self.pos: Vec3 = pos
		#self.period: float = 90. / speed

		self.node.setH(self.node.getH() + 225)

		# must initialise its start state to kick off the fsm
		self.request("BottomRight")

		#base.taskMgr.add(self.update, "update_"+str(self.node), taskChain='default')
		# locate this task in base.taskMgr to modify it, or overload update() in subclass

	# def update(self, task) -> int:
	# 	#if base.fsm.state == 'Gameplay':
	# 		#move
	# 	self.still = False if self.speed else True
	# 	return task.cont

	def defaultFilter(self, request, args) -> str:
		return 'BottomRight'

	def enterTopLeft(self) -> None:
		# lerp round and switch textures
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()
		#if not self.still: self.tsmSwitch.setVisibleChild(1)
		if (self.speed > 0.): self.tsmSwitch.setVisibleChild(1)
		else: self.tsmSwitch.setVisibleChild(0)
		#print(self.tsmSwitch.getVisibleChild())

	#def exitTopLeft(self) -> None:
	#	pass

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
		# lerp round and switch textures
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()
		#if not self.still: self.tsmSwitch.setVisibleChild(2)
		if (self.speed > 0.): self.tsmSwitch.setVisibleChild(2)
		else: self.tsmSwitch.setVisibleChild(0)
		#print(self.tsmSwitch.getVisibleChild())

	#def exitTopRight(self) -> None:
	#	pass

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
		# lerp round and switch textures
		#print(str(self.node) + " facing bottom right")
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()
		#if not self.still: self.tsmSwitch.setVisibleChild(2)
		if (self.speed > 0.): self.tsmSwitch.setVisibleChild(2)
		else: self.tsmSwitch.setVisibleChild(3)
		#print(self.tsmSwitch.getVisibleChild())

	#def exitXneg(self) -> None:	
	#	pass
		
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
		# lerp round and switch textures
		self.node.hprInterval(.5, Vec3(self.node.getH()-90,0,0)).start()
		#if not self.still: self.tsmSwitch.setVisibleChild(1)
		if (self.speed > 0.): self.tsmSwitch.setVisibleChild(1)
		else: self.tsmSwitch.setVisibleChild(3)
		#print(self.tsmSwitch.getVisibleChild())

	#def exitYneg(self) -> None:
	#	pass

	def filterBottomLeft(self, request, args) -> str: # process input while facing bottom left (-x,+y)
		if (request == 'Left'):
			return 'BottomRight'
		elif (request == 'Right'):
			return 'TopLeft'
		elif (request == 'Flip'):
			return 'TopRight'
		else:
			return None
