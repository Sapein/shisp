"""
This handles all transient state that is needed.
"""

import errors

from dataclasses import dataclass

@dataclass
class GlobalState:
    """
    This encapsulates all compiler state that
    we need to keep track of across modules.
    """

    source_files: list[str]
    errors: dict[str, list[errors.ShispError]]
    warnings: dict[str, list[errors.ShispWarn]]

    options: list[str]

    current_file: str

    def add_error_file(self, src_file: str, error: errors.ShispError):
        try:
            self.errors = {**self.errors,
                           src_file: [*self.errors[src_file], error]}
        except KeyError:
            self.errors = {**self.errors,
                           src_file: [error]}

    def add_warning_file(self, src_file: str, warning: errors.ShispWarn):
        self.warnings = {**self.errors,
                         src_file: [*self.warnings[src_file], error]}

    def change_file(self, file: str):
        self.current_file = file

    def add_error(self, error: errors.ShispError):
        self.add_error_file(self.current_file, error)

    def add_warning(self, warning: errors.ShispWarn):
        self.add_warning_file(self.current_file, warning)
