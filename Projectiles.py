from direct.showbase.ShowBase import ShowBase
from Units import Seeker
from panda3d.core import NodePath

class Projectile(Seeker):
	def __init__(model, node, target, damage, speed):
		Seeker.__init__(model, node, target, damage, speed)

class Arrow(Projectile):
	def __init__(target):
		model: GeomNode = base.loader.loadModel("assets/arrow2.gltf")
		node: NodePath = render.attachNewNode("arrow")
		damage: float = 10.0
		speed: float = 0.5
		Projectile.__init__(model, node, target, damage, speed)
