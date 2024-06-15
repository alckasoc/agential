"""Reflexion Agent.

Original Paper: https://arxiv.org/abs/2303.11366
Paper Repositories:
    - https://github.com/noahshinn/reflexion-draft
    - https://github.com/noahshinn/reflexion
"""

import re

from typing import Any, Dict, List, Optional, Tuple


from langchain_core.language_models.chat_models import BaseChatModel

from agential.cog.agent.base import BaseAgent
from agential.cog.eval.reflexion import EM
from agential.cog.functional.reflexion import (
    _is_halted,
    _prompt_react_agent,
    _truncate_scratchpad,
)
from agential.cog.modules.reflect.reflexion import (
    ReflexionCoTReflector,
    ReflexionReActReflector,
)
from agential.cog.prompts.agent.reflexion import (
    HOTPOTQA_FEWSHOT_EXAMPLES_REFLEXION_REACT_REFLECT,
    REFLEXION_REACT_INSTRUCTION_HOTPOTQA,
    REFLEXION_REACT_REFLECT_INSTRUCTION_HOTPOTQA,
)
from agential.cog.prompts.benchmark.hotpotqa import HOTPOTQA_FEWSHOT_EXAMPLES_REACT
from agential.cog.strategies.strategy_factory import ReflexionCoTStrategyFactory, ReflexionReActStrategyFactory
from agential.utils.parse import remove_newline


def parse_action(string: str) -> Tuple[str, str]:
    """Parses an action string into an action type and its argument.

    This method is used in ReAct and Reflexion.

    Args:
        string (str): The action string to be parsed.

    Returns:
        Tuple[str, str]: A tuple containing the action type and argument.
    """
    pattern = r"^(\w+)\[(.+)\]$"
    match = re.match(pattern, string)

    if match:
        action_type = match.group(1)
        argument = match.group(2)
    else:
        action_type = ""
        argument = ""
    return action_type, argument


class ReflexionCoTAgent(BaseAgent):
    """Reflexion with Chain-of-Thought actor.

    Attributes:
        llm (BaseChatModel): The language model used to generate responses.
        mode (Dict[str, str]): The mode of the agent.
        reflector (Optional[ReflexionCoTReflector]): An optional reflector module for guided self-reflection.
        **strategy_kwargs (Dict[str, Any]): Additional keyword arguments for the strategy.
        
    Methods:
        generate(): Generates a response.
        reset(): Resets the agent's state for a new problem-solving session.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        mode: Dict[str, str],
        reflector: Optional[ReflexionCoTReflector] = None,
        **strategy_kwargs: Dict[str, Any],
    ) -> None:
        """Initialization."""
        super().__init__()

        self.llm = llm
        self.mode = mode

        self.strategy = ReflexionCoTStrategyFactory().get_strategy(
            mode=self.mode, llm=self.llm, reflector=reflector, **strategy_kwargs
        )

    def generate(
        self,
        question: str,
        key: str,
        examples: str,
        prompt: str,
        reflect_examples: str,
        reflect_prompt: str,
        reflection_strategy: str,
        additional_keys: Dict[str, str] = {},
        reflect_additional_keys: Dict[str, str] = {},
        patience: int = 1,
        reset: bool = True,
        **kwargs: Dict[str, Any],
    ) -> List[Tuple[bool, str, Tuple[str, str, str]]]:
        """Generates a response based on the provided context, question, and key.

        The `generate` method internally calls reflect (if possible), resets the memory,
        and generates a thought, action, and the observation (Finish).

        Args:
            question (str): The question to answer.
            key (str): The key to evaluate the correctness of the answer.
            examples (str, optional): Fewshot examples.
            prompt (str, optional): Prompt template string.
            reflect_examples (str, optional): Reflection fewshot examples.
            reflect_prompt (str, optional): Reflect prompt template string.
            reflection_strategy (str): The strategy to use for reflection. Can be one of "last_attempt",
                "reflexion", or "last_attempt_and_reflexion".
            reset (bool): Resets the agent's memory. Defaults to True.

        Returns:
            result (List[Tuple[bool, str, List[str, str, str]]]): A list of tuples containing (is_correct, answer, output)
                where output is a thought-action-observation 3-tuple.
        """
        # Reset.
        if reset:
            self.reset()

        idx, patience_cnt = 0, 0
        out = []
        while not self.strategy.halting_condition(idx=idx, key=key, **kwargs):

            # Reflect if possible.
            reflections = ""
            if self.strategy.reflect_condition(
                idx=idx,
                reflection_strategy=reflection_strategy,
                key=key,
            ):
                reflections = self.strategy.reflect(
                    reflection_strategy=reflection_strategy,
                    question=question,
                    examples=reflect_examples,
                    prompt=reflect_prompt,
                    additional_keys=reflect_additional_keys,
                )

            self.strategy.reset(only_scratchpad=True)

            # Think.
            thought = self.strategy.generate(
                question=question,
                examples=examples,
                reflections=reflections,
                prompt=prompt,
                additional_keys=additional_keys,
                **kwargs,
            )

            # Act.
            action_type, query = self.strategy.generate_action(
                question=question,
                examples=examples,
                reflections=reflections,
                prompt=prompt,
                additional_keys=additional_keys,
                **kwargs,
            )

            # Observe.
            is_correct, obs = self.strategy.generate_observation(
                action_type=action_type, query=query, key=key
            )

            out.append(
                self.strategy.create_output_dict(
                    thought=thought,
                    action_type=action_type,
                    obs=obs,
                    is_correct=is_correct,
                )
            )

            # Increment patience counter.
            if not is_correct:
                patience_cnt += 1
            if patience_cnt == patience:
                break

            idx += 1

        return out

    def reset(self) -> None:
        """Resets the agent's memory and state."""
        self.strategy.reset()


class ReflexionReActAgent(BaseAgent):
    """Reflexion with ReAct actor.

    Attributes:
        llm (BaseChatModel): The language model used to generate responses.
        mode (Dict[str, str]): The mode of the agent.
        reflector (Optional[ReflexionReActReflector]): An optional reflector module for guided self-reflection. Defaults to None.
        **strategy_kwargs (Dict[str, Any]): Additional keyword arguments for the strategy.

    Methods:
        generate(): Generates a response.
        reset(): Resets the agent's state for a new problem-solving session.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        mode: Dict[str, str],
        reflector: Optional[ReflexionReActReflector] = None,
        **strategy_kwargs: Dict[str, Any],
    ) -> None:
        """Initialization."""
        super().__init__()
        
        self.llm = llm
        self.mode = mode

        self.strategy = ReflexionReActStrategyFactory().get_strategy(
            mode=self.mode, llm=self.llm, reflector=reflector, **strategy_kwargs
        )

    def _generate_react(
        self,
        question: str,
        key: str,
        examples: str,
        reflections: str,
        prompt: str,
        additional_keys: Dict[str, str] = {},
        **kwargs: Dict[str, Any],
    ):
        out = []
        step_idx = 1
        self.strategy.reset(no_reflector=True)
        while not self.strategy.react_halting_condition(
            step_idx=step_idx, 
            question=question,
            examples=examples,
            reflections=reflections,
            prompt=prompt,
            additional_keys=additional_keys,
            **kwargs
        ):
            # Think.
            thought = self.strategy.generate(
                question=question,
                examples=examples,
                reflections=reflections,
                prompt=prompt,
                additional_keys=additional_keys,
                **kwargs
            )

            # Act.
            action_type, query = self.strategy.generate_action(
                question=question,
                examples=examples,
                reflections=reflections,
                prompt=prompt,
                additional_keys=additional_keys,
                **kwargs
            )

            # Observe.
            is_correct, obs = self.strategy.generate_observation(
                step_idx=step_idx,
                action_type=action_type,
                query=query,
                key=key,
            )

            out.append(
                self.strategy.react_create_output_dict(
                    thought=thought,
                    action_type=action_type,
                    query=query,
                    obs=obs,
                    is_correct=is_correct,
                )
            )

            step_idx += 1

        return step_idx, is_correct, out

    def generate(
        self,
        question: str,
        key: str,
        examples: str,
        prompt: str,
        reflect_examples: str,
        reflect_prompt: str,
        reflection_strategy: Optional[str] = None,
        additional_keys: Dict[str, str] = {},
        reflection_additional_keys: Dict[str, str] = {},
        patience: int = 1,
        reset: bool = True,
        **kwargs: Dict[str, Any],
    ) -> List[Tuple[bool, str, List[Tuple[str, str, str]]]]:
        """Processes a given question through ReAct and reflects using Reflexion strategies when possible.

        Iteratively applies the think-act-observe cycle to generate an answer for the question.
        The process continues until the operation is halted based on certain conditions.

        Args:
            question (str): The question to be processed.
            key (str): The answer to the question.
            examples (str, optional): Fewshot examples. 
            reflection_strategy (Optional[str]): The reflection strategy. Can be of 3 types. Defaults to None.
                - "last_attempt": This strategy uses only 'question' and 'scratchpad'. The 'reflections' list is updated with the current scratchpad.
                - "reflexion": This strategy uses all the parameters. It adds a new reflexion generated by the language model to the 'reflections' list.
                - "last_attempt_and_reflexion": This strategy combines the 'last_attempt' and 'reflexion' strategies.
            reset (bool): Whether to reset the internal state before processing. Defaults to True.
            prompt (str, optional): Prompt template string. 
            reflect_examples (str, optional): Reflection fewshot examples. 
            reflect_prompt (str, optional): Reflect prompt template string. 
            additional_keys (Dict[str, str], optional): Additional keys for the prompt. Defaults to {}.
            **kwargs (Dict[str, Any]): Additional keyword arguments for the strategy.

        Returns:
            result (List[Tuple[bool, str, List[Tuple[str, str, str]]]]): List of trials where each trial is
                in the format (is_correct, answer, output) and output is in a thought-action-observation 3-tuple.
        """
        # Reset.
        if reset:
            self.reset()

        idx, step_idx, patience_cnt = 1, 1, 0
        out = []
        while self.strategy.halting_condition(idx=idx, key=key, **kwargs):
            # Reflect if possible.
            reflections = ""
            if self.strategy.reflect_condition(
                step_idx=step_idx, 
                reflection_strategy=reflection_strategy, 
                question=question,
                examples=examples,
                key=key,
                prompt=prompt,
                additional_keys=additional_keys,
                **kwargs
            ):
                reflections = self.strategy.reflect(
                    reflection_strategy=reflection_strategy,
                    question=question,
                    examples=reflect_examples,
                    prompt=reflect_prompt,
                    additional_keys=reflection_additional_keys,
                )

            step_idx, is_correct, react_out = self._generate_react(
                question=question,
                key=key,
                examples=examples,
                reflections=reflections,
                prompt=prompt,
                additional_keys=additional_keys,
                **kwargs
            )

            out.append(
                self.strategy.create_output_dict(
                    react_out=react_out,
                    reflections=reflections,
                )
            )

            # Increment patience counter.
            if not is_correct:
                patience_cnt += 1
            if patience_cnt == patience:
                break
            
            idx += 1

        return out

    def reset(self) -> None:
        """Resets the internal state of the ReflexionReAct agent.

        Sets the step number, finished flag, and scratchpad to their initial values.
        """
        self.strategy.reset()