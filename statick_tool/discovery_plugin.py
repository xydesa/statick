"""Discovery plugin."""
import logging
import os
import subprocess
import sys
from typing import List, Optional

from statick_tool.exceptions import Exceptions
from statick_tool.package import Package
from statick_tool.statick_plugin import StatickPlugin


class DiscoveryPlugin(StatickPlugin):
    """Default implementation of discovery plugin."""

    @classmethod
    def get_discovery_dependencies(cls) -> List[str]:
        """Get a list of discovery plugins that must run before this one."""
        return []

    def scan(
        self, package: Package, level: str, exceptions: Optional[Exceptions] = None
    ) -> None:
        """Scan package to discover files for analysis.

        If exceptions is passed, then the plugin should (if practical) use it to filter
        which files the plugin detects.
        """

    def find_files(self, package: Package) -> None:
        """Walk the package path exactly once to discover files for analysis."""
        if package._walked:  # pylint: disable=protected-access
            return

        for root, _, files in os.walk(package.path):
            for fname in files:
                full_path = os.path.join(root, fname)
                abs_path = os.path.abspath(full_path)
                file_output = self.get_file_cmd_output(full_path)
                file_dict = {
                    "name": fname.lower(),
                    "path": abs_path,
                    "file_cmd_out": file_output,
                }
                package.files[abs_path] = file_dict

        package._walked = True  # pylint: disable=protected-access

    def get_file_cmd_output(self, full_path: str) -> str:
        """Run the file command (if it exists) on the supplied path.

        The output from the file command is converted to lowercase.
        There are two recommended ways to check it:
        1. When searching for a single string just use the python "in" operator:

            if "search string" in fild_dict["file_cmd_out"]:

        2. When searching for multiple different strings, use the `any()` function:

            expected_output = ("output_1", "output_2")
            if any(item in file_dict["file_cmd_out"] for item in expected_output):
        """
        if not self.file_command_exists():
            return ""

        try:
            output: str = subprocess.check_output(
                ["file", full_path], universal_newlines=True
            )
            return output.lower()
        except subprocess.CalledProcessError as ex:
            logging.warning(
                "Failed to run 'file' command. Returncode = %d", ex.returncode
            )
            logging.warning("Exception output: %s", ex.output)
            return ""

    @staticmethod
    def file_command_exists() -> bool:
        """Return whether the 'file' command is available on $PATH."""
        if sys.platform == "win32":
            command_name = "file.exe"
        else:
            command_name = "file"

        for path in os.environ["PATH"].split(os.pathsep):
            exe_path = os.path.join(path, command_name)
            if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                return True

        return False
