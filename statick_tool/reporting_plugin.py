"""Result reporting plugin."""
from typing import Dict, List, Optional, Tuple

from statick_tool.issue import Issue
from statick_tool.package import Package
from statick_tool.statick_plugin import StatickPlugin


class ReportingPlugin(StatickPlugin):
    """Default implementation of reporting plugin."""

    def report(
        self, package: Package, issues: Dict[str, List[Issue]], level: str
    ) -> Tuple[Optional[None], bool]:
        """Run the report generator."""
