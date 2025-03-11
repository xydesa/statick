"""Apply rstcheck tool and gather results."""

import logging
import re
import subprocess
from typing import Match, Optional, Pattern

from statick_tool.issue import Issue
from statick_tool.package import Package
from statick_tool.tool_plugin import ToolPlugin


class RstcheckToolPlugin(ToolPlugin):
    """Apply rstcheck tool and gather results."""

    def get_name(self) -> str:
        """Get name of tool."""
        return "rstcheck"

    def get_file_types(self) -> list[str]:
        """Return a list of file types the plugin can scan."""
        return ["rst_src"]

    def get_binary(  # pylint: disable=unused-argument
        self, level: Optional[str] = None, package: Optional[Package] = None
    ) -> str:
        """Get tool binary name."""
        return "rstcheck"

    # pylint: disable=too-many-locals
    def process_files(
        self, package: Package, level: str, files: list[str], user_flags: list[str]
    ) -> Optional[list[str]]:
        """Run tool and gather output."""
        tool_bin = self.get_binary()

        flags: list[str] = []
        flags += user_flags

        total_output: list[str] = []

        try:
            exe = [tool_bin] + flags + files
            output = subprocess.check_output(
                exe, stderr=subprocess.STDOUT, universal_newlines=True
            )
            total_output.append(output)

        except subprocess.CalledProcessError as ex:
            if ex.returncode == 1:  # markdownlint returns 1 upon linting errors
                total_output.append(ex.output)
            else:
                logging.warning("%s failed! Returncode = %d", tool_bin, ex.returncode)
                logging.warning("%s exception: %s", self.get_name(), ex.output)
                return None

        except OSError as ex:
            logging.warning("Couldn't find %s! (%s)", tool_bin, ex)
            return None

        for output in total_output:
            logging.debug("%s", str(output))

        return total_output

    def parse_output(
        self, total_output: list[str], package: Optional[Package] = None
    ) -> list[Issue]:
        """Parse tool output and report issues."""
        rstcheck_re = r"(.+):(\d+):\s\((.+)/(\d)\)\s(.+)"
        parse: Pattern[str] = re.compile(rstcheck_re)
        issues: list[Issue] = []

        for output in total_output:
            for line in output.split("\n"):
                match: Optional[Match[str]] = parse.match(line)
                if match:
                    issues.append(
                        Issue(
                            match.group(1),
                            int(match.group(2)),
                            self.get_name(),
                            match.group(3),
                            int(match.group(4)),
                            match.group(5),
                            None,
                        )
                    )
        return issues
