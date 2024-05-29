"""ReAct Agent strategies for Code."""

from typing import Any, Dict, Tuple

import re
import tiktoken

from langchain.agents.react.base import DocstoreExplorer
from langchain_community.docstore.wikipedia import Wikipedia
from langchain_core.language_models.chat_models import BaseChatModel
from tiktoken.core import Encoding

from agential.cog.functional.react import _is_halted, _prompt_agent
from agential.cog.strategies.react.base import ReActBaseStrategy
from agential.utils.parse import remove_newline


def parse_code_action(action: str) -> Tuple[str, str]:
    pattern = re.compile(r"(Finish|Implement|Test)\[\s*```python\s*(.*?)\s*```\s*\]", re.DOTALL | re.IGNORECASE)

    try:
        match = pattern.findall(action)[0]
        action_type = match[0].capitalize()
        content = match[1].strip()
    except IndexError:
        action_type = ""
        content = ""

    return action_type, content


class ReActCodeStrategy(ReActBaseStrategy):
    """A strategy class for Code benchmarks using the ReAct agent.

    Attributes:
        llm (BaseChatModel): The language model used for generating answers and critiques.
        max_steps (int): The maximum number of steps the agent can take.
        max_tokens (int): The maximum number of tokens allowed for a response.
        
        enc (Encoding): The encoding used for the language model.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        max_steps: int = 6,
        max_tokens: int = 3896,
        docstore: DocstoreExplorer = DocstoreExplorer(Wikipedia()),
        enc: Encoding = tiktoken.encoding_for_model("gpt-3.5-turbo"),
    ) -> None:
        """Initialization."""
        super().__init__(llm)
        self.max_steps = max_steps
        self.max_tokens = max_tokens
        self.docstore = docstore
        self.enc = enc

        self._scratchpad = ""
        self._finished = False

    def generate(
        self,
        question: str,
        examples: str,
        prompt: str,
        additional_keys: Dict[str, str],
        **kwargs: Dict[str, Any],
    ) -> str:
        """Generates a thought based on the question, examples, and prompt.

        Args:
            question (str): The question to be answered.
            examples (str): Examples to guide the generation process.
            prompt (str): The prompt used for generating the thought.
            additional_keys (Dict[str, str]): Additional keys for the generation process.
            **kwargs (Dict[str, Any]): Additional arguments.

        Returns:
            str: The generated thought.
        """
        max_steps = kwargs.get("max_steps", self.max_steps)  # type: ignore

        self._scratchpad += "\nThought:"
        thought = _prompt_agent(
            llm=self.llm,
            question=question,
            scratchpad=self._scratchpad,
            examples=examples,
            max_steps=max_steps,  # type: ignore
            additional_keys=additional_keys,
            prompt=prompt,
        ).split("Action")[0]
        self._scratchpad += " " + thought

        return thought

    def generate_action(
        self,
        question: str,
        examples: str,
        prompt: str,
        additional_keys: Dict[str, str],
        **kwargs: Dict[str, Any],
    ) -> Tuple[str, str]:
        """Generates an action based on the question, examples, and prompt.

        Args:
            question (str): The question to be answered.
            examples (str): Examples to guide the generation process.
            prompt (str): The prompt used for generating the action.
            additional_keys (Dict[str, str]): Additional keys for the generation process.
            **kwargs (Dict[str, Any]): Additional arguments.

        Returns:
            Tuple[str, str]: The generated action type and query.
        """
        max_steps = kwargs.get("max_steps", self.max_steps)
        self._scratchpad += "\nAction:"
        action = _prompt_agent(
            llm=self.llm,
            question=question,
            scratchpad=self._scratchpad,
            examples=examples,
            max_steps=max_steps,  # type: ignore
            additional_keys=additional_keys,
            prompt=prompt,
        )
        action = action.split("Observation")[0]

        self._scratchpad += " " + action
        action_type, query = parse_code_action(action)

        return action_type, query

    def generate_observation(self, idx: int, action_type: str, query: str) -> str:
        """Generates an observation based on the action type and query.

        Args:
            idx (int): The index of the observation.
            action_type (str): The type of action to be performed.
            query (str): The query for the action.

        Returns:
            str: The generated observation.
        """
        self._scratchpad += f"\nObservation {idx}: "
        if action_type.lower() == "finish":
            self._answer = query
            self._finished = True
            obs = query
        elif action_type.lower() == "implement":
            try:
                obs = remove_newline(self.docstore.search(query))
            except Exception:
                obs = "Could not find that page, please try again."
        elif action_type.lower() == "test":
            try:
                obs = remove_newline(self.docstore.lookup(query))
            except ValueError:
                obs = "The last page Searched was not found, so you cannot Lookup a keyword in it. Please try one of the similar pages given."
        else:
            obs = "Invalid Action. Valid Actions are Implement[<code>] Test[<topic>] and Finish[<answer>]."
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
            "observation": obs,
        }

    def halting_condition(
        self,
        idx: int,
        question: str,
        examples: str,
        prompt: str,
        **kwargs: Dict[str, Any],
    ) -> bool:
        """Determines whether the halting condition has been met.

        Args:
            idx (int): The current step index.
            question (str): The question being answered.
            examples (str): Examples to guide the generation process.
            prompt (str): The prompt used for generating the thought and action.
            **kwargs (Dict[str, Any]): Additional arguments.

        Returns:
            bool: True if the halting condition is met, False otherwise.
        """
        max_steps = kwargs.get("max_steps", self.max_steps)

        return _is_halted(
            finished=self._finished,
            idx=idx,
            question=question,
            scratchpad=self._scratchpad,
            examples=examples,
            max_steps=max_steps,  # type: ignore
            max_tokens=self.max_tokens,
            enc=self.enc,
            prompt=prompt,
        )

    def reset(self) -> None:
        """Resets the internal state of the strategy.

        Resets the scratchpad and the finished flag.
        """
        self._scratchpad = ""
        self._finished = False


class ReActMBPPStrategy(ReActCodeStrategy):
    """A strategy class for the MBPP benchmark using the ReAct agent."""

    pass


class ReActHEvalStrategy(ReActCodeStrategy):
    """A strategy class for the HumanEval benchmark using the ReAct agent."""

    pass