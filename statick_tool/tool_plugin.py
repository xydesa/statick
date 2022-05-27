"""Tool plugin."""
import os
import shlex
from typing import List, Optional

from statick_tool.issue import Issue
from statick_tool.package import Package
from statick_tool.statick_plugin import StatickPlugin


# No stubs available for IPlugin so ignoring type.
class ToolPlugin(StatickPlugin):
    """Default implementation of tool plugin."""

    @classmethod
    def get_tool_dependencies(cls) -> List[str]:
        """Get a list of tools that must run before this one."""
        return []

    def scan(self, package: Package, level: str) -> Optional[List[Issue]]:
        """Run tool and gather output."""

    def get_user_flags(self, level: str, name: Optional[str] = None) -> List[str]:
        """Get the user-defined extra flags for a specific tool/level combination."""
        if name is None:
            name = self.get_name()  # pylint: disable=assignment-from-no-return
        assert self.plugin_context is not None
        user_flags = self.plugin_context.config.get_tool_config(name, level, "flags")
        flags: List[str] = []
        if user_flags:
            # See https://github.com/python/typeshed/issues/1476 for
            # justification to ignore.
            lex = shlex.shlex(user_flags, posix=True)
            lex.whitespace_split = True
            flags = list(lex)
        return flags

    @staticmethod
    def is_valid_executable(path: str) -> bool:
        """Return whether a provided command exists and is executable.

        If the provided path has an extension on it, don't change it, otherwise try
        adding common extensions.
        """
        # On Windows, PATHEXT contains a list of extensions which can be
        # appended to a program name when searching PATH.
        extensions = os.environ.get("PATHEXT", None)
        _, path_ext = os.path.splitext(path)
        if path_ext or not extensions:
            return os.path.isfile(path) and os.access(path, os.X_OK)

        extensions_list = extensions.split(";")
        # Add "" (no extension) as a possibility.
        extensions_list.insert(0, "")
        for ext in extensions_list:
            extended_path = path + ext
            if os.path.isfile(extended_path) and os.access(extended_path, os.X_OK):
                return True

        return False

    @staticmethod
    def command_exists(command: str) -> bool:
        """Return whether a particular command is available on $PATH."""
        fpath, _ = os.path.split(command)

        if fpath:
            # Contains a path, not just a command, so don't search PATH
            return ToolPlugin.is_valid_executable(command)

        for path in os.environ["PATH"].split(os.pathsep):
            exe_path = os.path.join(path, command)
            if ToolPlugin.is_valid_executable(exe_path):
                return True

        return False
