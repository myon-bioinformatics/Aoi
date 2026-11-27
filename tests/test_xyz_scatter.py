import unittest
from dragowing import xyz_figure

class XYZTest(unittest.TestCase):
    def test_csv(self):
        trace = xyz_figure("a,b,c,name\n1,2,3,alpha\n4,5,6,beta\n", ("a","b","c"), label="name")["data"][0]
        self.assertEqual(trace["type"], "scatter3d")
        self.assertEqual(trace["x"], [1,4])
        self.assertEqual(trace["text"], ["alpha","beta"])

    def test_tsv(self):
        self.assertEqual(xyz_figure("x\ty\tz\n1\t2\t3\n", delimiter="\t")["data"][0]["z"], [3])

    def test_invalid(self):
        for data in ("x,y,z\n", "x,y,z\nNaN,1,2\n", "x,y\n1,2\n", "x,x,y,z\n1,2,3,4\n"):
            with self.subTest(data=data), self.assertRaises(ValueError):
                xyz_figure(data)
