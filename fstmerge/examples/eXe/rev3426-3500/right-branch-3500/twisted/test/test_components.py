"""Test cases for Twisted component architecture."""
from twisted.trial import unittest, util
from twisted.python import components
import warnings
compWarn = {'category':components.ComponentsDeprecationWarning}
suppress = [util.suppress(**compWarn)]
warnings.filterwarnings('ignore', **compWarn)
class IAdder(components.Interface):
    """A sample interface that adds stuff."""
    def add(self, a, b):
        """Returns the sub of a and b."""
        raise NotImplementedError
class ISub(IAdder):
    """Sub-interface."""
class IMultiply(components.Interface):
    """Interface that multiplies stuff."""
    def multiply(self, a, b):
        """Multiply two items."""
        raise NotImplementedError
class IntAdder:
    """Class that implements IAdder interface."""
    __implements__ = IAdder
    def add(self, a, b):
        return a + b
class Sub:
    """Class that implements ISub."""
    __implements__ = ISub
    def add(self, a, b):
        return 3
class IntMultiplyWithAdder:
    """Multiply, using Adder object."""
    __implements__ = IMultiply
    def __init__(self, adder):
        self.adder = adder
    def multiply(self, a, b):
        result = 0
        for i in range(a):
            result = self.adder.add(result, b)
        return result
components.registerAdapter(IntMultiplyWithAdder, IntAdder, IMultiply)
class MultiplyAndAdd:
    """Multiply and add."""
    __implements__ = (IAdder, IMultiply)
    def add(self, a, b):
        return a + b
    def multiply(self, a, b):
        return a * b
class IFoo(ISub):
    pass
class FooAdapterForMAA:
    __implements__ = IFoo
    def __init__(self, instance):
        self.instance = instance
    def add(self, a, b):
        return self.instance.add(a, b)
components.registerAdapter(FooAdapterForMAA, MultiplyAndAdd, IFoo)
class InterfacesTestCase(unittest.TestCase):
    """Test interfaces."""
    tuples = ([1, [1]],
              [(2, 3), [2, 3]],
              [(2, (3, (4,)), (1, 5)), [2, 3, 4, 1, 5]],
              [(), []],
              )
    def testModules(self):
        self.assertEquals(components.Interface.__module__, "twisted.python.components")
        self.assertEquals(IAdder.__module__, "twisted.test.test_components")
        self.assertEquals(IFoo.__module__, "twisted.test.test_components")
    def testTupleTrees(self):
        for tree, result in self.tuples:
            self.assertEquals(components.tupleTreeToList(tree), result)
    def testClasses(self):
        components.fixClassImplements(Sub)
        components.fixClassImplements(MultiplyAndAdd)
        self.assert_( IMultiply.implementedBy(MultiplyAndAdd) )
        self.assert_( IAdder.implementedBy(MultiplyAndAdd) )
        self.assert_( IAdder.implementedBy(Sub) )
        self.assert_( ISub.implementedBy(Sub) )
    def testInstances(self):
        o = MultiplyAndAdd()
        self.assert_( components.implements(o, IMultiply) )
        self.assert_( components.implements(o, IMultiply) )
        o = Sub()
        self.assert_( components.implements(o, IAdder) )
        self.assert_( components.implements(o, ISub) )
    def testOther(self):
        self.assert_( not components.implements(3, ISub) )
        self.assert_( not components.implements("foo", ISub) )
    def testGetInterfaces(self):
        l = components.getInterfaces(Sub)
        l.sort()
        l2 = [IAdder, ISub]
        l2.sort()
        self.assertEquals(l, l2)
        l = components.getInterfaces(MultiplyAndAdd)
        l.sort()
        l2 = [IAdder, IMultiply]
        l2.sort()
        self.assertEquals(l, l2)
    def testSuperInterfaces(self):
        l = components.superInterfaces(ISub)
        l.sort()
        l2 = [ISub, IAdder]
        l2.sort()
        self.assertEquals(l, l2)
class Compo(components.Componentized):
    num = 0
    def inc(self):
        self.num = self.num + 1
        return self.num
class IAdept(components.Interface):
    def adaptorFunc(self):
        raise NotImplementedError()
class IElapsed(components.Interface):
    def elapsedFunc(self):
        """
        1!
        """
class Adept(components.Adapter):
    __implements__ = IAdept,
    def __init__(self, orig):
        self.original = orig
        self.num = 0
    def adaptorFunc(self):
        self.num = self.num + 1
        return self.num, self.original.inc()
class Elapsed(components.Adapter):
    __implements__ = IElapsed
    def elapsedFunc(self):
        return 1
components.registerAdapter(Adept, Compo, IAdept)
components.registerAdapter(Elapsed, Compo, IElapsed)
class AComp(components.Componentized):
    pass
class BComp(AComp):
    pass
class CComp(BComp):
    pass
class ITest(components.Interface):
    pass
class ITest2(components.Interface):
    pass
class ITest3(components.Interface):
    pass
class ITest4(components.Interface):
    pass
class Test(components.Adapter):
    __implements__ = ITest, ITest3, ITest4
    def __init__(self, orig):
        pass
class Test2:
    __implements__ = ITest2,
    temporaryAdapter = 1
    def __init__(self, orig):
        pass
components.registerAdapter(Test, AComp, ITest)
components.registerAdapter(Test, AComp, ITest3)
components.registerAdapter(Test2, AComp, ITest2)
class ComponentizedTestCase(unittest.TestCase):
    """Simple test case for caching in Componentized.
    """
    def testComponentized(self):
        c = Compo()
        assert c.getComponent(IAdept).adaptorFunc() == (1, 1)
        assert c.getComponent(IAdept).adaptorFunc() == (2, 2)
        assert IElapsed(IAdept(c)).elapsedFunc() == 1
    def testInheritanceAdaptation(self):
        c = CComp()
        co1 = c.getComponent(ITest)
        co2 = c.getComponent(ITest)
        co3 = c.getComponent(ITest2)
        co4 = c.getComponent(ITest2)
        assert co1 is co2
        assert co3 is not co4
        c.removeComponent(co1)
        co5 = c.getComponent(ITest)
        co6 = c.getComponent(ITest)
        assert co5 is co6
        assert co1 is not co5
    def testMultiAdapter(self):
        c = CComp()
        co1 = c.getComponent(ITest)
        co2 = c.getComponent(ITest2)
        co3 = c.getComponent(ITest3)
        co4 = c.getComponent(ITest4)
        assert co4 == None
        assert co1 is co3
class AdapterTestCase(unittest.TestCase):
    """Test adapters."""
    def testNoAdapter(self):
        o = Sub()
        multiplier = components.getAdapter(o, IMultiply, None)
        self.assertEquals(multiplier, None)
    def testSelfIsAdapter(self):
        o = IntAdder()
        adder = components.getAdapter(o, IAdder, None)
        self.assert_( o is adder )
    def testGetAdapter(self):
        o = IntAdder()
        self.assertEquals(o.add(3, 4), 7)
        multiplier = components.getAdapter(o, IMultiply, None)
        self.assertEquals(multiplier.multiply(3, 4), 12)
    def testGetAdapterClass(self):
        mklass = components.getAdapterClass(IntAdder, IMultiply, None)
        self.assertEquals(mklass, IntMultiplyWithAdder)
    def testGetSubAdapter(self):
        o = MultiplyAndAdd()
        self.assert_( not components.implements(o, IFoo) )
        foo = components.getAdapter(o, IFoo, None)
        self.assert_( isinstance(foo, FooAdapterForMAA) )
    def testParentInterface(self):
        o = Sub()
        adder = components.getAdapter(o, IAdder, None)
        self.assertIdentical(o, adder)
    def testBadRegister(self):
        self.assertRaises(ValueError, components.registerAdapter, IntMultiplyWithAdder, IntAdder, IMultiply)
    def testAllowDuplicates(self):
        components.ALLOW_DUPLICATES = 1
        try: 
            components.registerAdapter(IntMultiplyWithAdder, IntAdder,
                                       IMultiply)
        except ValueError:
            self.fail("Should have allowed re-registration")
        components.ALLOW_DUPLICATES = 0
        self.assertRaises(ValueError, components.registerAdapter,
                          IntMultiplyWithAdder, IntAdder, IMultiply)
    def testAdapterGetComponent(self):
        o = object()
        a = Adept(o)
        self.assertRaises(components.CannotAdapt, IAdder, a)
        self.assertEquals(IAdder(a, default=None), None)
    def testMultipleInterfaceRegistration(self):
        class IMIFoo(components.Interface):
            pass
        class IMIBar(components.Interface):
            pass
        class MIFooer(components.Adapter):
            __implements__ = IMIFoo, IMIBar
        class Blegh:
            pass
        components.registerAdapter(MIFooer, Blegh, IMIFoo, IMIBar)
        self.assert_(isinstance(IMIFoo(Blegh()), MIFooer))
        self.assert_(isinstance(IMIBar(Blegh()), MIFooer))
class IMeta(components.Interface):
    def __adapt__(o, dflt):
        if hasattr(o, 'add'):
            return o
        elif hasattr(o, 'num'):
            return MetaAdder(o)
        return dflt
class MetaAdder(components.Adapter):
    __implements__ = IMeta
    def add(self, num):
        return self.original.num + num
class BackwardsAdder(components.Adapter):
    __implements__ = IMeta
    def add(self, num):
        return self.original.num - num
class MetaNumber:
    def __init__(self, num):
        self.num = num
class FakeAdder:
    def add(self, num):
        return num + 5
class FakeNumber:
    num = 3
class ComponentNumber(components.Componentized):
    def __init__(self):
        self.num = 0
        components.Componentized.__init__(self)
class ComponentMeta(components.Adapter):
    __implements__ = IMeta
    def __init__(self, original):
        components.Adapter.__init__(self, original)
        self.num = self.original.num
class ComponentAdder(ComponentMeta):
    def add(self, num):
        self.num += num
        return self.num
class ComponentDoubler(ComponentMeta):
    def add(self, num):
        self.num += (num * 2)
        return self.original.num
components.registerAdapter(MetaAdder, MetaNumber, IMeta)
components.registerAdapter(ComponentAdder, ComponentNumber, IMeta)
class IAttrX(components.Interface):
    def x(self):
        pass
class IAttrXX(components.Interface):
    def xx(self):
        pass
class Xcellent:
    __implements__ = IAttrX
    def x(self):
        return 'x!'
class DoubleXAdapter:
    num = 42
    def __init__(self, original):
        self.original = original
    def xx(self):
        return (self.original.x(), self.original.x())
    def __cmp__(self, other):
        return cmp(self.num, other.num)
components.registerAdapter(DoubleXAdapter, IAttrX, IAttrXX)
class TestMetaInterface(unittest.TestCase):
    def testBasic(self):
        n = MetaNumber(1)
        self.assertEquals(IMeta(n).add(1), 2)
    def testInterfaceAdaptMethod(self):
        a = FakeAdder()
        self.assertIdentical(IMeta(a), a)
        n2 = FakeNumber()
        self.assertEquals(IMeta(n2).add(3), 6)
    def testComponentizedInteraction(self):
        c = ComponentNumber()
        IMeta(c).add(1)
        IMeta(c).add(1)
        self.assertEquals(IMeta(c).add(1), 3)
    def testRegistryPersistence(self):
        n = MetaNumber(1)
        i1 = IMeta(n, persist=True)
        i2 = IMeta(n, persist=True)
        i3 = IMeta(n, persist=False)
        i4 = IMeta(n)
        self.assertIdentical(i1, i2)
        self.assertNotEqual(i1, i3)
        self.assertIdentical(i1, i4)
        import weakref
        r = weakref.ref(i1)
        del i1, i2, i3, i4
        self.assertNotEqual(r(), IMeta(n))
        self.assertNotEqual(IMeta(n), IMeta(n))
    def testAdapterWithCmp(self):
        xx = IAttrXX(Xcellent())
        self.assertEqual(('x!', 'x!'), xx.xx())
class IISource1(components.Interface): pass
class IISource2(components.Interface): pass
class IIDest1(components.Interface): pass
class Dest1Impl(components.Adapter):
    __implements__ = IIDest1
class Dest1Impl2(components.Adapter):
    __implements__ = IIDest1
class Source12:
    __implements__ = IISource1, IISource2
class Source21:
    __implements__ = IISource2, IISource1
IISource1.adaptWith(Dest1Impl,  IIDest1)
IISource2.adaptWith(Dest1Impl2, IIDest1)
class TestInterfaceInterface(unittest.TestCase):
    def testBasic(self):
        s12 = Source12()
        d = IIDest1(s12)
        self.failUnless(isinstance(d, Dest1Impl), str(s12))
        s21 = Source21()
        d = IIDest1(s21)
        self.failUnless(isinstance(d, Dest1Impl2), str(s21))
class TestZIBC(unittest.TestCase):
    def testAttributes(self):
        class IFoo(components.Interface):
            a = 3
        self.assertEquals(IFoo.a, 3)
from zope import interface as zinterface
class IZope(zinterface.Interface):
    def amethod(a, b):
        pass
class Zopeable:
    pass
class Zoper:
    zinterface.implements(IZope, IAdder)
components.backwardsCompatImplements(Zoper) # add __implements__
components.registerAdapter(lambda o: id(o), Zopeable, IZope)
class SubZoper(Zoper):
    zinterface.implements(ISub)
class OldStyle:
    __implements__ = IAdder
class NewSubOfOldStyle(OldStyle):
    zinterface.implements(IZope)
components.backwardsCompatImplements(NewSubOfOldStyle)
class TestZope(unittest.TestCase):
    def testAdapter(self):
        x = Zopeable()
        self.assertEquals(id(x), IZope(x))
    def testOldSubclass(self):
        class IFoo(components.Interface):
            pass
        class ThirdParty(Zoper):
            __implements__ = Zoper.__implements__, IFoo
        self.assert_(components.implements(ThirdParty(), IAdder))
        self.assert_(components.implements(ThirdParty(), IFoo))
        self.assert_(components.implements(ThirdParty(), IZope))
    def testNewSubclass(self):
        o = SubZoper()
        self.assert_(components.implements(o, IZope))
        self.assert_(components.implements(o, ISub))
    def testNewSubclassOfOld(self):
        o = NewSubOfOldStyle()
        self.assert_(components.implements(o, IZope))
        self.assert_(components.implements(o, IAdder))
    def testSignatureString(self):
        self.assertEquals(IAdder['add'].getSignatureString(), "(a, b)")
        self.assertEquals(IZope['amethod'].getSignatureString(), "(a, b)")
warnings.filterwarnings('default', **compWarn)
