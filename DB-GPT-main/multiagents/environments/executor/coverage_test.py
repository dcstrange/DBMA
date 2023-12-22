from __future__ import annotations

import os
import subprocess
import multiprocessing
from typing import TYPE_CHECKING, Any, List, Tuple

from multiagents.agents import ExecutorAgent

from . import BaseExecutor, executor_registry


def execute_command(command: str, result_list) -> str:
    # TODO: make it more secure
    result = subprocess.run(command, capture_output=True, shell=True, encoding="utf-8")
    result_list.append(f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    # return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"


@executor_registry.register("coverage-test")
class CoverageTestExecutor(BaseExecutor):
    def step(
        self,
        agent: ExecutorAgent,
        task_description: str,
        solution: List[str],
        *args,
        **kwargs,
    ) -> Any:
        from evaluate_commongen import scoring

        coverage, missing_tokens = scoring([solution], [task_description])
        if len(missing_tokens[0]) == 0:
            missing_tokens = "No missing tokens."
        else:
            missing_tokens = ", ".join(missing_tokens[0])
        result = f"Coverage: {coverage*100:.2f}%\nMissing Tokens: {missing_tokens}"
        return result
