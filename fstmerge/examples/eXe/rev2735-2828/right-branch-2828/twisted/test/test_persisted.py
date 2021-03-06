import sys
from twisted.trial import unittest
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
from twisted.persisted import styles, aot
class VersionTestCase(unittest.TestCase):
    def testNullVersionUpgrade(self):
        global NullVersioned
        class NullVersioned:
            ok = 0
        pkcl = pickle.dumps(NullVersioned())
        class NullVersioned(styles.Versioned):
            persistenceVersion = 1
            def upgradeToVersion1(self):
                self.ok = 1
        mnv = pickle.loads(pkcl)
        styles.doUpgrade()
        assert mnv.ok, "initial upgrade not run!"
    def testVersionUpgrade(self):
        global MyVersioned
        class MyVersioned(styles.Versioned):
            persistenceVersion = 2
            persistenceForgets = ['garbagedata']
            v3 = 0
            v4 = 0
            def __init__(self):
                self.somedata = 'xxx'
                self.garbagedata = lambda q: 'cant persist'
            def upgradeToVersion3(self):
                self.v3 += 1
            def upgradeToVersion4(self):
                self.v4 += 1
        mv = MyVersioned()
        assert not (mv.v3 or mv.v4), "hasn't been upgraded yet"
        pickl = pickle.dumps(mv)
        MyVersioned.persistenceVersion = 4
        obj = pickle.loads(pickl)
        styles.doUpgrade()
        assert obj.v3, "didn't do version 3 upgrade"
        assert obj.v4, "didn't do version 4 upgrade"
        pickl = pickle.dumps(obj)
        obj = pickle.loads(pickl)
        styles.doUpgrade()
        assert obj.v3 == 1, "upgraded unnecessarily"
        assert obj.v4 == 1, "upgraded unnecessarily"
    def testNonIdentityHash(self):
        global ClassWithCustomHash
        class ClassWithCustomHash(styles.Versioned):
            def __init__(self, unique, hash):
                self.unique = unique
                self.hash = hash
            def __hash__(self):
                return self.hash
        v1 = ClassWithCustomHash('v1', 0)
        v2 = ClassWithCustomHash('v2', 0)
        pkl = pickle.dumps((v1, v2))
        del v1, v2
        ClassWithCustomHash.persistenceVersion = 1
        ClassWithCustomHash.upgradeToVersion1 = lambda self: setattr(self, 'upgraded', True)
        v1, v2 = pickle.loads(pkl)
        styles.doUpgrade()
        self.assertEquals(v1.unique, 'v1')
        self.assertEquals(v2.unique, 'v2')
        self.failUnless(v1.upgraded)
        self.failUnless(v2.upgraded)
    def testUpgradeDeserializesObjectsRequiringUpgrade(self):
        global ToyClassA, ToyClassB
        class ToyClassA(styles.Versioned):
            pass
        class ToyClassB(styles.Versioned):
            pass
        x = ToyClassA()
        y = ToyClassB()
        pklA, pklB = pickle.dumps(x), pickle.dumps(y)
        del x, y
        ToyClassA.persistenceVersion = 1
        def upgradeToVersion1(self):
            self.y = pickle.loads(pklB)
            styles.doUpgrade()
        ToyClassA.upgradeToVersion1 = upgradeToVersion1
        ToyClassB.persistenceVersion = 1
        ToyClassB.upgradeToVersion1 = lambda self: setattr(self, 'upgraded', True)
        x = pickle.loads(pklA)
        styles.doUpgrade()
        self.failUnless(x.y.upgraded)
class MyEphemeral(styles.Ephemeral):
    def __init__(self, x):
        self.x = x
class EphemeralTestCase(unittest.TestCase):
    def testEphemeral(self):
        o = MyEphemeral(3)
        self.assertEquals(o.__class__, MyEphemeral)
        self.assertEquals(o.x, 3)
        pickl = pickle.dumps(o)
        o = pickle.loads(pickl)
        self.assertEquals(o.__class__, styles.Ephemeral)
        self.assert_(not hasattr(o, 'x'))
class Pickleable:
    def __init__(self, x):
        self.x = x
    def getX(self):
        return self.x
class A:
    """
    dummy class
    """
    def amethod(self):
        pass
class B:
    """
    dummy class
    """
    def bmethod(self):
        pass
def funktion():
    pass
try:
    from twisted.persisted import marmalade
except ImportError:
    pass
else:
    class Marmaladeable(marmalade.DOMJellyable):
        jellyDOMVersion = 1
        def __init__(self, integer, instance, name, sequence):
            self.integer = integer
            self.instance = instance
            self.sequence = sequence
            self.name = name
        def jellyToDOM_1(self, jellier, element):
            from twisted.python.reflect import qual
            element.setAttribute("integer", str(self.integer))
            element.setAttribute("instance", qual(self.instance.__class__)) # not l33t enough
            element.setAttribute("name", str(self.name))
        def unjellyFromDOM_1(self, unjellier, element):
            from twisted.python.reflect import namedClass
            self.integer = int(element.getAttribute("integer"))
            self.instance = namedClass(element.getAttribute("instance"))()
            self.name = element.getAttribute("name")
            self.sequence = [self.instance, self.instance]
        def jellyToDOM_2(self, jellier, element):
            element.setAttribute("integer", str(self.integer))
            element.setAttribute("name", str(self.name))
            instanceNode = jellier.jellyToNode(self.instance) # l33ter!
            instanceNode.setAttribute("parent:role", "instance")
            element.appendChild(instanceNode)
            i = 0
            for seqel in self.sequence:
                seqNode = jellier.jellyToNode(seqel)
                seqNode.setAttribute("parent:role", "sequence:%d" % i)
                element.appendChild(seqNode)
                i = i + 1
        def unjellyFromDOM_2(self, unjellier, element):
            self.integer = int(element.getAttribute("integer"))
            self.name = element.getAttribute("name")
            from twisted.web.microdom import Element
            self.sequence = []
            i = 0
            for node in element.childNodes:
                if isinstance(node, Element):
                    if node.getAttribute("parent:role") == 'instance':
                        unjellier.unjellyAttribute(self, "instance", node)
                    else:
                        self.sequence.append(None)
                        unjellier.unjellyLater(node).addCallback(
                            self.gotSequenceItem, i)
                        i = i + 1
        def gotSequenceItem(self, seqitem, num):
            self.sequence[num] = seqitem
    class MarmaladeTestCase(unittest.TestCase):
        def testMarmaladeable(self):
            m = Marmaladeable(1, B(), "testing", [1, 2, 3])
            s = marmalade.jellyToXML(m)
            u = marmalade.unjellyFromXML(s)
            assert u.sequence == [u.instance, u.instance]
            u.sequence.append(u.instance)
            u.jellyDOMVersion = 2
            s2 = marmalade.jellyToXML(u)
            u2 = marmalade.unjellyFromXML(s2)
            self.assertEquals( u2.sequence,  [u2.instance, u2.instance, u2.instance])
        def testCopyReg(self):
            s = "foo_bar"
            sio = StringIO.StringIO()
            sio.write(s)
            assert marmalade.unjellyFromXML(marmalade.jellyToXML({1:sio}))[1].getvalue() == s
        def testMethodSelfIdentity(self):
            a = A()
            b = B()
            a.bmethod = b.bmethod
            b.a = a
            im_ = marmalade.unjellyFromXML(marmalade.jellyToXML(b)).a.bmethod
            self.assertEquals(im_.im_class, im_.im_self.__class__)
        def testBasicIdentity(self):
            dj = marmalade.DOMJellier().jellyToNode
            d = {'hello': 'world', "method": dj}
            l = [1, 2, 3,
                 "he\tllo\n\n\"x world!",
                 u"goodbye \n\t\u1010 world!",
                 1, 1.0, 100 ** 100l, unittest, marmalade.DOMJellier, d,
                 funktion,
                 True, False,
                 (2, 4, [2]),
                 ]
            t = tuple(l)
            l.append(l)
            l.append(t)
            l.append(t)
            uj = marmalade.unjellyFromXML(marmalade.jellyToXML([l, l]))
            assert uj[0] is uj[1]
            assert uj[1][0:5] == l[0:5]
class PicklingTestCase(unittest.TestCase):
    """Test pickling of extra object types."""
    def testModule(self):
        pickl = pickle.dumps(styles)
        o = pickle.loads(pickl)
        self.assertEquals(o, styles)
    def testClassMethod(self):
        pickl = pickle.dumps(Pickleable.getX)
        o = pickle.loads(pickl)
        self.assertEquals(o, Pickleable.getX)
    def testInstanceMethod(self):
        obj = Pickleable(4)
        pickl = pickle.dumps(obj.getX)
        o = pickle.loads(pickl)
        self.assertEquals(o(), 4)
        self.assertEquals(type(o), type(obj.getX))
    def testStringIO(self):
        f = StringIO.StringIO()
        f.write("abc")
        pickl = pickle.dumps(f)
        o = pickle.loads(pickl)
        self.assertEquals(type(o), type(f))
        self.assertEquals(f.getvalue(), "abc")
class EvilSourceror:
    def __init__(self, x):
        self.a = self
        self.a.b = self
        self.a.b.c = x
class NonDictState:
    def __getstate__(self):
        return self.state
    def __setstate__(self, state):
        self.state = state
class AOTTestCase(unittest.TestCase):
    def testSimpleTypes(self):
        obj = (1, 2.0, 3j, True, slice(1, 2, 3), 'hello', u'world', sys.maxint + 1, None, Ellipsis)
        rtObj = aot.unjellyFromSource(aot.jellyToSource(obj))
        self.assertEquals(obj, rtObj)
    def testMethodSelfIdentity(self):
        a = A()
        b = B()
        a.bmethod = b.bmethod
        b.a = a
        im_ = aot.unjellyFromSource(aot.jellyToSource(b)).a.bmethod
        self.assertEquals(im_.im_class, im_.im_self.__class__)
    def testBasicIdentity(self):
        aj = aot.AOTJellier().jellyToAO
        d = {'hello': 'world', "method": aj}
        l = [1, 2, 3,
             "he\tllo\n\n\"x world!",
             u"goodbye \n\t\u1010 world!",
             1, 1.0, 100 ** 100l, unittest, aot.AOTJellier, d,
             funktion
             ]
        t = tuple(l)
        l.append(l)
        l.append(t)
        l.append(t)
        uj = aot.unjellyFromSource(aot.jellyToSource([l, l]))
        assert uj[0] is uj[1]
        assert uj[1][0:5] == l[0:5]
    def testNonDictState(self):
        a = NonDictState()
        a.state = "meringue!"
        assert aot.unjellyFromSource(aot.jellyToSource(a)).state == a.state
    def testCopyReg(self):
        s = "foo_bar"
        sio = StringIO.StringIO()
        sio.write(s)
        uj = aot.unjellyFromSource(aot.jellyToSource(sio))
        assert uj.getvalue() == s
    def testFunkyReferences(self):
        o = EvilSourceror(EvilSourceror([]))
        j1 = aot.jellyToAOT(o)
        oj = aot.unjellyFromAOT(j1)
        assert oj.a is oj
        assert oj.a.b is oj.b
        assert oj.c is not oj.c.c
testCases = [VersionTestCase, EphemeralTestCase, PicklingTestCase]
