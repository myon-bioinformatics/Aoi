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

    def test_scoreboard_rows_match_modest_parser(self):
        # Values locked to selectolax 0.4.13 Modest HTMLParser on the same fragments.
        def cells(vals):
            parts=[]
            for i,v in enumerate(vals):
                parts.append('<td class="gmscore">'+v+'</td>')
                if i in (2,5):
                    parts.append('<td class="gmscspan"><br /></td>')
            return ''.join(parts)
        real=('<div id="gmdivresult"><table>'
              '<tr><td class="gmscorettl" colspan="13"><br /></td><td class="gmscorettl">Ｒ</td></tr>'
              '<tr><td class="gmscoreteam">阪　神</td>'+cells(['0']*9)+'<td align="center" class="gmscore">-</td><td align="center" class="gmscore">0</td><td class="gmscore">4</td><td class="gmscore">0</td></tr>'
              '<tr><td class="gmscoreteam">読　売</td>'+cells(['0','0','0','0','3','0','0','1','X'])+'<td align="center" class="gmscore">-</td><td align="center" class="gmscore">4</td><td class="gmscore">10</td><td class="gmscore">1</td></tr>'
              '</table></div>')
        rows=parse(real,{'away':'t','home':'g','as':0,'hs':4})
        self.assertEqual([(r['team'],r['side']) for r in rows],[('t','away'),('g','home')])
        self.assertEqual([c['runs'] for c in rows[0]['cells']],[0]*9)
        self.assertEqual([c['runs'] for c in rows[1]['cells']],[0,0,0,0,3,0,0,1,None])
        self.assertEqual(rows[1]['cells'][-1],{'runs':None,'played':False,'completed':False})
        marked=('<div id="gmdivresult"><table>'
                '<tr><td class="gmscoreteam">中　日</td>'+cells([' 0 ','\n1\n','２','0','0','0','0','0','<span>0</span>'])+'<td class="gmscore">-</td><td class="gmscore">3</td><td class="gmscore">8</td><td class="gmscore">1</td></tr>'
                '<tr><td class="gmscoreteam"> 東京ヤクルト </td>'+cells(['0']*8+['２ｘ'])+'<td class="gmscore">-</td><td class="gmscore">2</td><td class="gmscore">9</td><td class="gmscore">0</td></tr>'
                '</table></div>')
        rows=parse(marked,{'away':'d','home':'s','as':3,'hs':2})
        self.assertEqual([(r['team'],r['side']) for r in rows],[('d','away'),('s','home')])
        self.assertEqual([c['runs'] for c in rows[0]['cells']],[0,1,2,0,0,0,0,0,0])
        self.assertTrue(all(c['played'] and c['completed'] for c in rows[0]['cells']))
        self.assertEqual([c['runs'] for c in rows[1]['cells']],[0,0,0,0,0,0,0,0,2])
        self.assertEqual(rows[1]['cells'][-1],{'runs':2,'played':True,'completed':False})

if __name__=='__main__':unittest.main()
