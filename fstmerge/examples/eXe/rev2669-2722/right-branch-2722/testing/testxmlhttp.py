import unittest
from exe.webui.outlinepane         import OutlinePane
from exe.engine.package            import Package
from exe.webui.webserver           import WebServer
from exe.webui.packageredirectpage import PackageRedirectPage
from exe.application               import Application
from exe.engine.path               import Path
class FakeClient(object):
    """Pretends to be a webnow client object"""
    def __init__(self):
        self.calls = [] # All methods called on this object
    def logCall(self, _name_, *args, **kwargs):
        self.calls.append((_name_, args, kwargs))
    def __getattr__(self, name):
        """Always returns a callable"""
        return lambda *args, **kwargs: self.logCall(name, *args, **kwargs)
class TestOutline(unittest.TestCase):
    def setUp(self):
        class MyConfig:
            def __init__(self):
                self.port       = 8081
                self.dataDir    = Path(".")
                self.webDir     = Path(".")
                self.exeDir     = Path(".")
                self.configDir  = Path(".")
                self.styles     = ["default"]
        app = Application()
        app.config = MyConfig()
        app.preLaunch()
        self.client = FakeClient()
        self.package = Package('temp')
        app.webServer.root.bindNewPackage(self.package)
        self.outline = app.webServer.root.children['temp'].outlinePane
    def testAddAndDel(self):
        """Should be able to add a node to the package"""
        def checkAdd(id_, title):
            assert ('call', ('XHAddChildTreeItem', id_, title), {}) in self.client.calls, self.client.calls
            assert str(self.package.currentNode.title) == title, title
            assert self.package.currentNode.id == id_, id_
        self.outline.handleAddChild(self.client, '0') # Home/root node
        checkAdd('1', 'Topic')    # 1.0
        self.outline.handleAddChild(self.client, '1')
        checkAdd('2', 'Section')  # 1.0.0
        self.outline.handleAddChild(self.client, '2')
        checkAdd('3', 'Unit')     # 1.0.0.0
        self.outline.handleAddChild(self.client, '3')
        checkAdd('4', '?????')    # 1.0.0.0.0
        self.outline.handleAddChild(self.client, '0')
        checkAdd('5', 'Topic')    # 1.1
        self.outline.handleAddChild(self.client, '0')
        checkAdd('6', 'Topic')    # 1.2
        self.outline.handleAddChild(self.client, '1')
        checkAdd('7', 'Section')  # 1.0.1
        self.outline.handleAddChild(self.client, '1')
        checkAdd('8', 'Section') # 1.0.2
        self.outline.handleAddChild(self.client, '2')
        checkAdd('9', 'Unit') # 1.0.0.1
        self.outline.handleAddChild(self.client, '2')
        checkAdd('10', 'Unit') # 1.0.0.2
        n12 = self.package.findNode('10')
        n4 = self.package.findNode('2')
        assert n12.parent is n4, n12.parent
        assert n12 in n4.children
        assert n4.parent.id == '1'
        assert n4.parent.parent.id == '0'
        assert n4.parent.parent.parent is None
        self.client.calls = []
        self.outline.handleDelNode(self.client, 'false', '2') # Del 
        assert not self.client.calls
        assert self.package.findNode('2')
        self.outline.handleDelNode(self.client, 'true', '0')
        assert not self.client.calls
        assert self.package.findNode('0')
        oldNode = self.package.currentNode
        self.package.currentNode = self.package.findNode('3')
        self.outline.handleDelNode(self.client, 'true', '3')
        assert ('call', ('XHDelNode', '3'), {}) in self.client.calls, self.client.calls
        assert self.package.currentNode.id == '2', self.package.currentNode.id
        assert self.package.findNode('3') is None
        assert self.package.findNode('4') is None
        assert self.package.findNode('1')
        assert self.package.findNode('2')
        assert self.package.findNode('9')
        assert self.package.findNode('10')
        assert self.package.findNode('7')
        assert self.package.findNode('8')
        oldNode = self.package.currentNode
        self.outline.handleDelNode(self.client, 'true', '1')
        assert ('call', ('XHDelNode', '1'), {}) in self.client.calls, self.client.calls
        assert self.package.findNode('1') is None
        assert self.package.findNode('2') is None
        assert self.package.findNode('9') is None
        assert self.package.findNode('10') is None
        assert self.package.findNode('7') is None
        assert self.package.findNode('8') is None
        assert self.package.currentNode == oldNode, "Current node shouldn't have changed"
    def testRenNode(self):
        """Should be able to rename nodes"""
        self.outline.handleRenNode(self.client, '0', 'Genesis')
        assert str(self.package.findNode('0').title) == 'Genesis'
        assert ('sendScript', ('XHRenNode("Genesis")',), {}) in self.client.calls, self.client.calls
if __name__ == "__main__":
    unittest.main()
