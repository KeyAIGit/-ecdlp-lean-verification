#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_results_portal as portal


class ResultsPortalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.stats = {
            "ledger_rows": 307,
            "distinct_results": 268,
            "proved_modules": 179,
        }
        self.researchos = {"ledger_rows": 172}
        self.product = {
            "repository_url": "https://github.com/KeyAIGit/-ecdlp-lean-verification",
            "category": "verification workspace for AI research",
        }

    def test_markdown_preserves_separate_denominators(self) -> None:
        text = portal.render_markdown(self.stats, self.researchos)
        self.assertIn("479 ledger entries", text)
        self.assertIn("not a shared distinct-theorem denominator", text)
        self.assertIn("VERIFIED_RESEARCHOS.md", text)
        self.assertNotIn("~440 distinct", text)

    def test_results_page_has_direct_sources_and_boundary(self) -> None:
        text = portal.render_results_html(
            self.stats, self.researchos, self.product, "https://keyai.org"
        )
        self.assertIn('data-page="results"', text)
        self.assertIn('data-nav-page="results"', text)
        self.assertIn("One front door. Two isolated ledgers.", text)
        self.assertIn("479", text)
        self.assertIn("not a\n          shared distinct-theorem count", text)
        self.assertIn("assets/site-refresh.css", text)
        self.assertIn('rel="canonical" href="https://keyai.org/results.html"', text)

    def test_repo_links_are_normalized(self) -> None:
        href = portal.repo_url(self.product, "STATUS.md")
        self.assertEqual(
            "https://github.com/KeyAIGit/-ecdlp-lean-verification/blob/main/STATUS.md",
            href,
        )

    def test_crawl_map_lists_every_public_page(self) -> None:
        text = portal.render_sitemap("https://keyai.org")
        for page in (
            "https://keyai.org/",
            "https://keyai.org/results.html",
            "https://keyai.org/dashboard.html",
            "https://keyai.org/explore.html",
            "https://keyai.org/pilot.html",
        ):
            self.assertIn(page, text)
        self.assertEqual(
            "User-agent: *\nAllow: /\nSitemap: https://keyai.org/sitemap.xml\n",
            portal.render_robots("https://keyai.org"),
        )

    def test_output_normalization_is_idempotent(self) -> None:
        text = "alpha\n\n"
        self.assertEqual("alpha\n", portal.normalized(text))
        self.assertEqual(portal.normalized(text), portal.normalized(portal.normalized(text)))


if __name__ == "__main__":
    unittest.main()
