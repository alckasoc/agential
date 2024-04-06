"""ActRe meetsd ReAct Agent implementation.

This includes the original ReAct agent implementation
and ActRe meets ReAct Agent implementation.


Original React Paper: https://arxiv.org/abs/2210.03629
ActRe meets ReAct Paper: https://arxiv.org/abs/2403.14589
React Paper Repository: https://github.com/ysymyth/ReAct

"""
import random

from typing import Any, Dict, List, Optional, Tuple

import tiktoken

from langchain.agents.react.base import DocstoreExplorer
from langchain.schema import AIMessage, HumanMessage
from langchain_community.docstore.wikipedia import Wikipedia
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field
from tiktoken.core import Encoding

from discussion_agents.cog.agent.base import BaseAgent
from discussion_agents.cog.functional.react import _is_halted, _prompt_agent
from discussion_agents.cog.modules.memory.react import ReActMemory
from discussion_agents.cog.prompts.react import (
    HOTPOTQA_FEWSHOT_EXAMPLES,
    REACT_INSTRUCTION_HOTPOTQA,
)
from discussion_agents.utils.parse import parse_action, remove_newline


class ReActOutput(BaseModel):
    """Output parsing for the ReAct agent.

    Attributes:
        thought: str
        action: str
        observation: str.
    """

    thought: str = Field(..., description="The thought generated by the agent.")
    action: str = Field(..., description="The action taken by the agent.")
    observation: str = Field(..., description="The observation made by the agent.")


class ActReAgent(BaseAgent):
    """ActRe prompting agent."""

    def __init__(
        self,
        llm: BaseChatModel,
        memory: Optional[ReActMemory] = None,
        max_tokens: int = 3896,
        enc: Encoding = tiktoken.encoding_for_model("gpt-3.5-turbo"),
    ) -> None:
        """Initialization."""
        super().__init__()
        self.llm = llm

        if not memory:
            self.memory = ReActMemory()
        else:
            self.memory = memory

        self.max_tokens = max_tokens
        self.enc = enc

    def synthesize_reason(
        self, observation: str, action: str
    ) -> str | list[str | dict[Any, Any]]:
        """Synthesizes the reasoning for a given observation and action."""
        prompt = (
            f"Observation: {observation}\n"
            f"Action: {action}\n"
            "Synthesize the reasoning for the above action based on the observation:"
        )

        reason = self.llm([HumanMessage(content=prompt)]).content

        return reason

    def generate(self, observation: str, action: str) -> str:
        """Generates the synthesized reasoning for a given observation and action."""
        self.memory.add_memories(f"\nObservation: {observation}")
        self.memory.add_memories(f"\nAction: {action}")

        reason = self.synthesize_reason(observation, action)
        if isinstance(reason, str):
            self.memory.add_memories(f"\nSynthesized Reasoning: {reason}")
        else:
            raise ValueError("Synthesized reasoning should be a string.")

        return reason


class ActreReActAgent(BaseAgent):
    """ActRe meets ReAct agent from the original paper.

    Implements the ActRe meets ReAct algorithm as described in the original paper.
    This agent uses a language model to iteratively process a question
    through a sequence of think-act-observe steps, utilizing a document
    store for information retrieval.

    Attributes:
        llm (BaseChatModel): The language model used by the agent.
        max_steps (int): Maximum number of steps to process the question.
        max_tokens (int): Maximum token limit for the language model.
        docstore (DocstoreExplorer): Document store for information retrieval.
        enc (Encoding): Encoder for calculating token lengths.

    See: https://github.com/ysymyth/ReAct
    """

    def __init__(
        self,
        llm: BaseChatModel,
        memory: Optional[ReActMemory] = None,
        max_steps: int = 6,
        max_tokens: int = 3896,
        docstore: DocstoreExplorer = DocstoreExplorer(Wikipedia()),
        enc: Encoding = tiktoken.encoding_for_model("gpt-3.5-turbo"),
    ) -> None:
        """Initialization."""
        super().__init__()
        self.llm = llm

        if not memory:
            self.memory = ReActMemory()
        else:
            self.memory = memory

        self.max_steps = max_steps
        self.max_tokens = max_tokens
        self.docstore = docstore
        self.enc = enc

        # Internal variables.
        self._step_n = 1  #: :meta private:
        self._finished = False  #: :meta private:
        self.epsilon = 0.1

    def sample_alternative_action(self, action: str) -> str:
        """Randomly samples an alternative action based on the current action."""
        action_type, query = parse_action(action)

        if action_type.lower() == "search":
            alternative_actions = [
                f"Search[{random.choice(['information', 'details', 'facts'])} about {query}]",
                f"Search[{query} {random.choice(['overview', 'summary', 'introduction'])}]",
                f"Search[{random.choice(['related to', 'similar to', 'connected with'])} {query}]",
            ]
        elif action_type.lower() == "lookup":
            alternative_actions = [
                f"Lookup[{random.choice(['definition', 'meaning', 'explanation'])} of {query}]",
                f"Lookup[{query} {random.choice(['in the context of', 'with respect to', 'in relation to'])}]",
                f"Lookup[{random.choice(['examples', 'instances', 'illustrations'])} of {query}]",
            ]
        else:
            alternative_actions = [
                action
            ]  # Keep the original action if it's not "Search" or "Lookup"

        return random.choice(alternative_actions)

    def generate(
        self,
        question: str,
        reset: bool = True,
        examples: str = HOTPOTQA_FEWSHOT_EXAMPLES,
        prompt: str = REACT_INSTRUCTION_HOTPOTQA,
    ) -> List[ReActOutput]:
        """Processes a given question through ActRe then ReAct.

        Iteratively applies the think-act-observe cycle to generate an answer for the question.
        The process continues until the operation is halted based on certain conditions.

        Args:
            question (str): The question to be processed.
            react_agent (ReActAgent): The ReAct agent to be used for generating actions and observations.
            reset (bool, optional): Whether to reset the internal state before processing. Defaults to True.
            epsilon (float, optional): The probability of exploring an alternative action. Defaults to 0.1.
            examples (str, optional): Few-shot examples to provide context for the question. Defaults to HOTPOTQA_FEWSHOT_EXAMPLES.
            prompt (str, optional): The instruction prompt for the ReAct agent. Defaults to REACT_INSTRUCTION_HOTPOTQA.

        Returns:
            List[ReActOutput]: The list of accumulated output from the ActRe and ReAct process,
                each tuple consists of a thought-action-observation triplet in format of ReActOutput.
        """
        if reset:
            self.reset()

        out = []
        while not _is_halted(
            finished=self._finished,
            step_n=self._step_n,
            question=question,
            scratchpad=self.memory.load_memories()["scratchpad"],
            examples=examples,
            max_steps=self.max_steps,
            max_tokens=self.max_tokens,
            enc=self.enc,
            prompt=prompt,
        ):
            # Think.
            self.memory.add_memories("\nThought:")
            thought = _prompt_agent(
                llm=self.llm,
                question=question,
                scratchpad=self.memory.load_memories()["scratchpad"],
                examples=examples,
                max_steps=self.max_steps,
                prompt=prompt,
            ).split("Action")[0]
            self.memory.add_memories(" " + thought)

            # Act.
            self.memory.add_memories("\nAction:")
            action = _prompt_agent(
                llm=self.llm,
                question=question,
                scratchpad=self.memory.load_memories()["scratchpad"],
                examples=examples,
                max_steps=self.max_steps,
                prompt=prompt,
            ).split("Observation")[0]
            self.memory.add_memories(" " + action)
            action_type, query = parse_action(action)

            # Observe.
            self.memory.add_memories(f"\nObservation {self._step_n}: ")
            if action_type.lower() == "finish":
                self._answer = query
                self._finished = True
                obs = query
            elif action_type.lower() == "search":
                try:
                    obs = remove_newline(self.docstore.search(query))
                except Exception:
                    obs = "Could not find that page, please try again."
            elif action_type.lower() == "lookup":
                try:
                    obs = remove_newline(self.docstore.lookup(query))
                except ValueError:
                    obs = "The last page Searched was not found, so you cannot Lookup a keyword in it. Please try one of the similar pages given."
            elif random.random() < self.epsilon:
                alternative_action = self.sample_alternative_action(action)

                # Synthesize the reasoning for the alternative action using ActReAgent
                actre_agent = ActReAgent(self.llm, self.memory)
                alternative_reason = actre_agent.generate(obs, alternative_action)

                # Use the synthesized reason and alternative action for the next step
                thought = alternative_reason
                action = alternative_action
            else:
                obs = "Invalid Action. Valid Actions are Lookup[<topic>] Search[<topic>] and Finish[<answer>]."
            self.memory.add_memories(obs)

            out.append(
                ReActOutput(
                    thought=f"Thought: {thought}",
                    action=f"Action: {action}",
                    observation=f"Observation {self._step_n}: {obs}",
                )
            )

            self._step_n += 1

        return out

    def retrieve(self) -> Dict[str, Any]:
        """Retrieves the current state of the agent's memory.

        Returns:
            Dict[str, Any]: The current state of the agent's memory.
        """
        return self.memory.load_memories()

    def reset(self) -> None:
        """Resets the internal state of the ReAct agent.

        Sets the step number, finished flag, and scratchpad to their initial values.
        """
        self._step_n = 1
        self._finished = False
        self.memory.clear()