__author__ = "Cyril Jaquier"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2010-07-25 12:47:03 $"
__copyright__ = "Copyright (c) 2004 Cyril Jaquier"
__license__ = "GPL"
import unittest, socket, time, pickle
from server.failmanager import FailManager
from server.failmanager import FailManagerEmpty
from server.failticket import FailTicket
class AddFailure(unittest.TestCase):
	def setUp(self):
		"""Call before every test case."""
		self.__items = [['193.168.0.128', 1167605999.0],
					    ['193.168.0.128', 1167605999.0],
					    ['193.168.0.128', 1167605999.0],
					    ['193.168.0.128', 1167605999.0],
					    ['193.168.0.128', 1167605999.0],
					    ['87.142.124.10', 1167605999.0],
					    ['87.142.124.10', 1167605999.0],
					    ['87.142.124.10', 1167605999.0]]
		
		self.__failManager = FailManager()
		for i in self.__items:
			self.__failManager.addFailure(FailTicket(i[0], i[1]))
	def tearDown(self):
		"""Call after every test case."""
	
	def testAdd(self):
		self.assertEqual(self.__failManager.size(), 2)
	
	def _testDel(self):
		self.__failManager.delFailure('193.168.0.128')
		self.__failManager.delFailure('111.111.1.111')
		
		self.assertEqual(self.__failManager.size(), 1)
		
	def testCleanupOK(self):
		timestamp = 1167606999.0
		self.__failManager.cleanup(timestamp)
		self.assertEqual(self.__failManager.size(), 0)
		
	def testCleanupNOK(self):
		timestamp = 1167605990.0
		self.__failManager.cleanup(timestamp)
		self.assertEqual(self.__failManager.size(), 2)
	
	def testbanOK(self):
		self.__failManager.setMaxRetry(5)
		
		ticket = self.__failManager.toBan()
		self.assertEqual(ticket.getIP(), "193.168.0.128")
	
	def testbanNOK(self):
		self.__failManager.setMaxRetry(10)
		self.assertRaises(FailManagerEmpty, self.__failManager.toBan)
