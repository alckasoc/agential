"""Reflexion Agent strategies for QA."""

import re
from typing import Optional, Dict, Any, Tuple
from agential.cog.modules.reflect.reflexion import (
    ReflexionCoTReflector,
)
from agential.cog.strategies.reflexion.base import ReflexionCoTBaseStrategy
from langchain_core.language_models.chat_models import BaseChatModel
from agential.cog.functional.reflexion import (
    _prompt_cot_agent
)
from agential.cog.eval.reflexion import EM
from agential.utils.parse import remove_newline


def parse_qa_action(string: str) -> Tuple[str, str]:
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


class ReflexioCoTQAStrategy(ReflexionCoTBaseStrategy):
    """A strategy class for QA benchmarks using the ReflexionCoT agent.

    Attributes:
        llm (BaseChatModel): The language model used for generating answers and critiques.

    """
    def __init__(
        self,
        llm: BaseChatModel,
        reflector: Optional[ReflexionCoTReflector] = None,
        max_reflections: int = 3,
        max_trials: int = 1,
        patience: int = 1,
    ) -> None:
        """Initialization."""
        super().__init__(llm)
        self.llm = llm
        self.max_reflections = max_reflections
        self.max_trials = max_trials
        self.patience = patience

        if not reflector:
            reflector = ReflexionCoTReflector(
                llm=llm, max_reflections=max_reflections
            )
        self.reflector = reflector

        self._scratchpad = ""
        self._finished = False
        self._answer = ""

    def generate(
        self,
        question: str,
        examples: str,
        reflections: str,
        context: str,
        prompt: str,
        additional_keys: Dict[str, str],
        **kwargs: Dict[str, Any],
    ) -> str:
        """Generates a thought based on the question, examples, and prompt.

        Args:
            question (str): The question to be answered.
            examples (str): Examples to guide the generation process.
            reflections (str): Reflections to consider during generation.
            context (str): The context for the generation process.
            prompt (str): The prompt used for generating the thought.
            additional_keys (Dict[str, str]): Additional keys for the generation process.
            **kwargs (Dict[str, Any]): Additional arguments.

        Returns:
            str: The generated thought.
        """
        self._scratchpad += "\nThought:"
        thought = _prompt_cot_agent(
            llm=self.llm,
            examples=examples,
            reflections=reflections,
            question=question,
            scratchpad=self._scratchpad,
            context=context,
            prompt=prompt,
        )
        thought = remove_newline(thought).split("Action")[0]
        self._scratchpad += " " + thought

        return thought

    def generate_action(
        self,
        question: str,
        examples: str,
        reflections: str,
        context: str,
        prompt: str,
        additional_keys: Dict[str, str],
        **kwargs: Dict[str, Any],
    ) -> Tuple[str, str]:
        """Generates an action based on the question, examples, and prompt.

        Args:
            question (str): The question to be answered.
            examples (str): Examples to guide the generation process.
            reflections (str): Reflections to consider during generation.
            context (str): The context for the generation process.
            prompt (str): The prompt used for generating the action.
            additional_keys (Dict[str, str]): Additional keys for the generation process.
            **kwargs (Dict[str, Any]): Additional arguments.

        Returns:
            Tuple[str, str]: The generated action type and query.
        """

        self._scratchpad += "\nAction:"
        action = _prompt_cot_agent(
            llm=self.llm,
            examples=examples,
            reflections=reflections,
            question=question,
            scratchpad=self._scratchpad,
            context=context,
            prompt=prompt,
        )
        action = remove_newline(action).strip().split("\n")[0]
        self._scratchpad += " " + action
        action_type, query = parse_qa_action(action)

        return action_type, query

    def generate_observation(self, action_type: str, query: str, key: str) -> str:
        """Generates an observation based on the action type and query.

        Args:
            action_type (str): The type of action to be performed.
            query (str): The query for the action.
            key (str): The key for the observation.

        Returns:
            str: The generated observation.
        """
        self._scratchpad += f"\nObservation: "
        if action_type.lower() == "finish":
            self._finished = True
            self._answer = query
            if EM(self._answer, key):
                obs = "Answer is CORRECT"
            else:
                obs = "Answer is INCORRECT"
        else:
            obs = "Invalid action type, please try again."
        self._scratchpad += obs

        return obs

    def create_output_dict(
        self, thought: str, action_type: str, query: str, obs: str
    ) -> Dict[str, str]:
        """Creates a dictionary of the output components.

        Args:
            thought (str): The generated thought.
            action_type (str): The type of action performed.
            query (str): The query for the action.
            obs (str): The generated observation.

        Returns:
            Dict[str, str]: A dictionary containing the thought, action type, query, and observation.
        """
        return {
            "thought": thought,
            "action_type": action_type,
            "query": query,
            "obs": obs,
        }

    def halting_condition(
        self,
        idx: int,
        question: str,
        examples: str,
        prompt: str,
        key: str,
        additional_keys: Dict[str, str],
        **kwargs: Dict[str, Any],
    ) -> bool:
        """Determines whether the halting condition has been met.

        Args:
            idx (int): The current step index.
            question (str): The question being answered.
            examples (str): Examples to guide the generation process.
            prompt (str): The prompt used for generating the thought and action.
            key (str): The key for the observation.
            additional_keys (Dict[str, str]): Additional keys for the generation process.
            **kwargs (Dict[str, Any]): Additional arguments.

        Returns:
            bool: True if the halting condition is met, False otherwise.
        """
        max_trials = kwargs.get("max_trials", self.max_trials)
        return not EM(self._answer, key) and idx < max_trials

    def reset(self) -> None:
        """Resets the internal state of the strategy.

        Resets the scratchpad and the finished flag.
        """
        self.reflector.reset()
        self._scratchpad = ""
        self._finished = False
        self._answer = ""

    def reflect(
        self, 
        reflection_strategy: str, 
        question: str, 
        context: str, 
        examples: str, 
        prompt: str, 
        additional_keys: Dict[str, str]
    ) -> str:
        """
        Reflects on a given question, context, examples, prompt, and additional keys using the specified reflection strategy.

        Args:
            reflection_strategy (str): The strategy to use for reflection.
            question (str): The question to be reflected upon.
            context (str): The context in which the question is being asked.
            examples (str): Examples to guide the reflection process.
            prompt (str): The prompt or instruction to guide the reflection.
            additional_keys (Dict[str, str]): Additional keys for the reflection process.

        Returns:
            str: The reflection string.
        """
        reflection = self.reflector.reflect(
            reflection_strategy=reflection_strategy,
        )

    def reflect_condition(
        self,
        reflection_strategy: str,
        question: str,
        context: str,
        examples: str,
        prompt: str,
        additional_keys: Dict[str, str],
        **kwargs: Dict[str, Any],
    ) -> bool:
        """
        Determines whether the reflection condition has been met.

        Args:
            reflection_strategy (str): The strategy to use for reflection.
            question (str): The question to be reflected upon.
            context (str): The context in which the question is being asked.
            examples (str): Examples to guide the reflection process.
            prompt (str): The prompt or instruction to guide the reflection.
            additional_keys (Dict[str, str]): Additional keys for the reflection process.

        Returns:
            bool: True if the reflection condition is met, False otherwise.
        """
        pass