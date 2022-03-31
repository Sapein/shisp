"""
This handles all transient state that is needed.
"""

from dataclasses import dataclass
import compiler_errors

@dataclass(frozen=True)
class CompilerState:
    """
    This encapsulates all compiler state that
    we need to keep track of across modules.
    """

    source_files: list[str]
    errors: dict[str, compiler_errors.ShispError]
    warnings: dict[str, compiler_errors.ShispWarn]

    options: list[str]

    def add_error(self, src_file: str, error: compiler_errors.ShispError) -> CompilerState:
        new_errors = {**self.errors,
                       src_file: [*self.errors[src_file], error]}
        return CompilerState(self.source_files, new_errors, self.warnings)

    def add_warning(self, src_file: str, warning: compiler_errors.ShispWarn) -> CompilerState:
        new_warnings = {**self.errors,
                       src_file: [*self.warnings[src_file], error]}
        return CompilerState(self.source_files, self.errors, new_warnings)
