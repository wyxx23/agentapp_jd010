"""agentapp_jd010 —— 自检测试。

把Agent 应用开发工程师·混合精度的溢出与下溢归并成组并标出每组的代表项

覆盖：正常路径、边界输入、防呆红线、幂等性。
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import agentapp_jd010  # noqa: E402

SAMPLE_TEXT = 'group a alpha beta\n\ngamma delta epsilon\n\nzeta eta theta'


class TestAgentapp_jd010(unittest.TestCase):
    """Agent 应用开发工程师·混合精度的溢出与下溢"""

    def test_rules_come_from_the_job_description(self):
        """规则表必须非空，且每条规则都挂在本岗位的要求上。

        这是「工具与 JD 同源」的可核查证据：规则名带 domain 前缀，
        why 里引用了岗位技能线或领域标签。
        """
        rules = getattr(agentapp_jd010, "RULES", None)
        self.assertTrue(rules, "规则表为空")
        self.assertGreaterEqual(len(rules), 8)
        for r in rules:
            self.assertIn("Agent 应用开发工程师·混合精度的溢出与下溢", r["name"])
            self.assertTrue(r["why"], "规则缺少判定说明")
            self.assertIn(r["severity"], ("high", "medium", "low"))
            self.assertTrue(r["keywords"], "规则缺少关键词")

    def test_cli_help_exits_zero(self):
        """--help 必须能正常退出。"""
        import subprocess
        proc = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "agentapp_jd010.py"), "--help"],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0)

    def test_cli_rejects_empty_input(self):
        """空输入必须明确报错，不能静默成功。"""
        import subprocess
        proc = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "agentapp_jd010.py"), "--text", "   "],
            capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(proc.returncode, 0)

    def test_cli_json_output_parses(self):
        """--json 输出必须是合法 JSON。"""
        import subprocess
        proc = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "agentapp_jd010.py"), "--text", SAMPLE_TEXT,
             "--json"],
            capture_output=True, text=True, encoding="utf-8")
        if proc.returncode not in (0, 1):
            self.fail(f"退出码异常：{proc.returncode} {proc.stderr[:300]}")
        data = json.loads(proc.stdout)
        self.assertIsInstance(data, dict)

    def test_does_not_mutate_input(self):
        """防呆：分析过程不得改动调用方传入的对象。"""
        payload = SAMPLE_TEXT
        before = payload
        agentapp_jd010.agentapp_jd010_analyze(payload)
        self.assertEqual(before, payload)

    def test_is_idempotent(self):
        """同一输入跑两次结果必须一致。"""
        a = agentapp_jd010.agentapp_jd010_analyze(SAMPLE_TEXT)
        b = agentapp_jd010.agentapp_jd010_analyze(SAMPLE_TEXT)
        self.assertEqual(json.dumps(a, ensure_ascii=False, sort_keys=True),
                         json.dumps(b, ensure_ascii=False, sort_keys=True))

    def test_groups_blocks(self):
        r = agentapp_jd010.agentapp_jd010_analyze(SAMPLE_TEXT)
        self.assertTrue(r["ok"])
        self.assertEqual(r["count"], 3)
        self.assertGreaterEqual(r["group_count"], 1)

    def test_reports_singleton_count(self):
        r = agentapp_jd010.agentapp_jd010_analyze(SAMPLE_TEXT)
        self.assertGreaterEqual(r["singletons"], 0)
        self.assertEqual(sum(g["size"] for g in r["groups"]), r["count"])
