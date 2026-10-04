import unittest
from inning_pilot import cell,parse

class InningPilotTests(unittest.TestCase):
    def test_x_is_not_a_zero_run_inning(self):
        self.assertEqual(cell('X','home',True),{'runs':None,'played':False,'completed':False})
        self.assertEqual(cell('0','home',True),{'runs':0,'played':True,'completed':True})

    def test_walkoff_runs_are_retained_but_incomplete(self):
        self.assertEqual(cell('２ｘ','home',True),{'runs':2,'played':True,'completed':False})

    def test_unknown_or_misplaced_cells_fail(self):
        for value,side,last in [('?', 'home',True),('X','away',True),('1X','home',False),('', 'home',True)]:
            with self.assertRaises(ValueError):cell(value,side,last)

    def test_wrong_score_is_rejected(self):
        def row(name,values):
            return '<tr><td class="gmscoreteam">'+name+'</td>'+''.join('<td class="gmscore">'+v+'</td>' for v in values)+'</tr>'
        html='<div id="gmdivresult"><table>'+row('中日',['0']*9+['-','1','0','0'])+row('東京ヤクルト',['0']*8+['X','-','0','0','0'])+'</table></div>'
        with self.assertRaisesRegex(ValueError,'total'):
            parse(html,{'away':'d','home':'s','as':1,'hs':0})

if __name__=='__main__':unittest.main()
