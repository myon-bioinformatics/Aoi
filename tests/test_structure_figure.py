import unittest

from dragowing.dragowing import structure_figure


class StructureFigureTests(unittest.TestCase):
    def test_uses_measured_coordinates_and_only_supplied_edges(self):
        atom = dict(type="Atom", chain="A", residue="CYS", element="S", name="SG", altloc="", x=1, y=2)
        nodes = [dict(atom, id="a0", z=3, residue_id="3"), dict(atom, id="a1", z=5, residue_id="40")]
        contact = dict(source="a0", target="a1", relation="nearAtom", labels=["disulfide-candidate"], distance_angstrom=2)
        graph = dict(schema="structure-graph/1", unit="angstrom", nodes=nodes, edges=[contact], model="1", contact_count=1)
        figure = structure_figure(graph)
        line, markers = figure["data"]
        self.assertEqual(line["z"], [3, 5, None])
        self.assertIn("2.000 Å", line["text"][0])
        self.assertEqual(markers["z"], [3, 5])
        self.assertEqual(figure["layout"]["scene"]["aspectmode"], "data")
