import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("plan_tools",ROOT/"skills/floorplan-image/scripts/plan_tools.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

from reconstruct import refine_plan, from_pixels, audit_plan

class PlanTests(unittest.TestCase):
    def setUp(self):self.p=json.loads((ROOT/"examples/two-room.json").read_text())
    def test_valid_fixture(self):self.assertEqual(m.validate(self.p),[])
    def test_blocked_door_rejected(self):
        self.p["walls"].append([4000,3400,4240,4300,"u"])
        with self.assertRaisesRegex(ValueError,"被实体墙覆盖"):m.validate(self.p)
    def test_self_intersection_rejected(self):
        self.p["rooms"][0]["poly"]=[[0,0],[4000,5000],[0,5000],[4000,0],[2000,-1000]]
        with self.assertRaisesRegex(ValueError,"自交"):m.validate(self.p)
    def test_unknown_type_rejected(self):
        self.p["furniture"][0]["type"]="hallucinated-sofa"
        with self.assertRaisesRegex(ValueError,"未知家具"):m.validate(self.p)
    def test_scale_requires_evidence(self):
        self.p["scale"]={"status":"measured"}
        with self.assertRaisesRegex(ValueError,"依据"):m.validate(self.p)
    def test_single_file_embedding_and_script_escape(self):
        self.p["title"]="</script><script>alert(1)</script>"
        with tempfile.TemporaryDirectory() as d:
            o=Path(d)/"index.html";m.build(self.p,o);s=o.read_text()
            payload=s.split("/* PLAN_DATA_START */",1)[1].split("/* PLAN_DATA_END */",1)[0]
            self.assertNotIn("</script>",payload)
            self.assertEqual(json.loads(payload),self.p)
            self.assertIn("Copyright (c) 2026 wuyi",s)
    def test_wall_anchor_preserves_free_furniture(self):
        anchored=next(f for f in self.p['furniture'] if f['id']=='I1')
        anchored['cy']+=70
        free=copy.deepcopy(next(f for f in self.p['furniture'] if f['id']=='I4'))
        result,changes=refine_plan(self.p)
        self.assertAlmostEqual(next(f for f in result['furniture'] if f['id']=='I1')['cy'],1000)
        self.assertEqual(next(f for f in result['furniture'] if f['id']=='I4'),free)
        self.assertEqual(self.p['furniture'][0]['cy'],1070)
        self.assertTrue(changes)
    def test_anchor_rejects_large_displacement(self):
        self.p['furniture'][0]['cy']+=1000
        with self.assertRaisesRegex(ValueError,'超过允许'):refine_plan(self.p)
    def test_anchor_rejects_wrong_back_direction(self):
        self.p['furniture'][0]['rot']=180
        with self.assertRaisesRegex(ValueError,'朝向'):refine_plan(self.p)
    def test_anchor_rejects_door_or_open_edge(self):
        self.p['walls']=[w for w in self.p['walls'] if w[1]!=-200]
        with self.assertRaisesRegex(ValueError,'缺少实体墙'):refine_plan(self.p)
    def test_observation_and_wall_metrics(self):
        result,_=refine_plan(self.p);report=audit_plan(result)
        self.assertEqual(report['wallCollisions'],[])
        self.assertTrue(all(f.get('anchorErrorMm',0)<.001 for f in report['furniture']))
    def test_pixels_keep_orientation_and_area_scale(self):
        o={'id':'test','title':'观测','image':{'width':400,'height':500},'rooms':[{'id':'R1','name':'房间','mat':'wood','polyPx':[[0,0],[400,0],[400,500],[0,500]],'calibrationAreaM2':20}],'walls':[],'furniture':[{'id':'I1','type':'bed','name':'床','bboxPx':[20,30,220,210],'rot':90}]}
        result=from_pixels(o)
        self.assertAlmostEqual(result['reference']['mmPerPixel'],10)
        self.assertEqual(result['furniture'][0]['w'],1800)
        self.assertEqual(result['furniture'][0]['d'],2000)
        self.assertEqual(result['scale']['status'],'estimated')
    def test_template_matches_root(self):
        self.assertEqual((ROOT/"index.html").read_bytes(),(ROOT/"skills/floorplan-image/assets/index.html").read_bytes())

if __name__=="__main__":unittest.main()
