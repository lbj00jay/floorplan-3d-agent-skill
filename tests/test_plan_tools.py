import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("plan_tools",ROOT/"skills/floorplan-image/scripts/plan_tools.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

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
    def test_template_matches_root(self):
        self.assertEqual((ROOT/"index.html").read_bytes(),(ROOT/"skills/floorplan-image/assets/index.html").read_bytes())

if __name__=="__main__":unittest.main()
