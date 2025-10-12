from direct.showbase.ShowBase import ShowBase, CollisionBox, CollisionNode, Point3

class CoordTest(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		#x = 1
		#y = 1
		for x in range(3):
			for y in range(3):
				smiley = self.loader.loadModel("smiley")
				smiley.setPos(x,y,0.)
				smiley.setScale(0.1)
				smiley.reparentTo(render)
				
				hitbox = CollisionBox(Point3(x, y, -0.1),Point3(x+1., y+1., .2))
				collNode = CollisionNode(str(smiley)+'-cnode')
				#collNode.setIntoCollideMask(BitMask32(0x01))
				colliderNp = smiley.attachNewNode(collNode)
				colliderNp.node().addSolid(hitbox)
				colliderNp.show()

		self.cam.setPos(0,-5,0)

tester = CoordTest()
tester.run()
 