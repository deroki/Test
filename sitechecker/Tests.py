import unittest
#from sitechecker import siteChecker
from sitechecker.sitechecker import  siteChecker


newdict = {"mysite" : { 'ssh' : True}}
olddict = {"mysite" : { 'ssh' : False}}
result = {"mysite" : { 'ssh' : True, 'ssh_c' : 1}}

class TestComparer(unittest.TestCase):
    newdict = {"mysite" : { 'ssh' : True}}
    olddict = {"mysite" : { 'ssh' : False}}
    def setUp(self):
        pass
    def test_repeatedfeats(self):
        SC = siteChecker()
        self.assertEqual(SC.CompareDicts(olddict,newdict, ['ssh']), result)

if __name__ == "__main__":
    unittest.main()