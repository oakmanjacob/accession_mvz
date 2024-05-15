import unittest

from ranges.sheets import SheetParser
from ranges.units import DistanceUnit, WeightUnit

class TestSheetParser(unittest.TestCase):
    def test_is_recorded(self):
        self.assertFalse(SheetParser.is_recorded("not Recorded"))
        self.assertFalse(SheetParser.is_recorded("NOT RECORDED"))
        self.assertFalse(SheetParser.is_recorded("not recorded"))
        self.assertFalse(SheetParser.is_recorded(None))
        self.assertFalse(SheetParser.is_recorded("NOT Recoded"))
        self.assertFalse(SheetParser.is_recorded("no recorded"))
        self.assertFalse(SheetParser.is_recorded(""))
    

if __name__ == "__main__":
    unittest.main()