from typing import Optional, Dict, Any, List, Tuple

from langchain_core.language_models.chat_models import BaseChatModel

from discussion_agents.cog.modules.memory.expel import ExpeLExperienceMemory, ExpeLInsightMemory
from discussion_agents.cog.agent.base import BaseAgent
from discussion_agents.cog.agent.reflexion import ReflexionReActAgent

from discussion_agents.cog.functional.expel import (
    gather_experience,
    categorize_experiences,
    get_folds,
    _prompt_compare_critique,
    parse_insights,
    remove_err_operations,
    retrieve_insight_index,
    get_operations_compare, 
    get_operations_success,
)
from discussion_agents.utils.general import shuffle_chunk_list
from discussion_agents.cog.prompts.expel import EXPEL_REFLEXION_REACT_INSTRUCTION


class ExpeLAgent(BaseAgent):
    def __init__(
        self,
        llm: BaseChatModel,
        self_reflect_llm: BaseChatModel, 
        action_llm: BaseChatModel,
        reflexion_react_kwargs: Optional[Dict[str, Any]] = {},
        reflexion_react_agent: Optional[ReflexionReActAgent] = None,
        experience_memory: Optional[ExpeLExperienceMemory] = None,
        insight_memory: Optional[ExpeLInsightMemory] = None,
        success_batch_size: int = 8
    ) -> None:
        super().__init__()

        self.llm = llm

        if not reflexion_react_agent:
            self.reflexion_react_agent = ReflexionReActAgent(
                self_reflect_llm=self_reflect_llm,
                action_llm=action_llm,
                **reflexion_react_kwargs
            )
        else:
            self.reflexion_react_agent = reflexion_react_agent

        if not experience_memory:
            self.experience_memory = ExpeLExperienceMemory()
        else:
            self.experience_memory = experience_memory

        if not insight_memory:
            self.insight_memory = ExpeLInsightMemory()
        else:
            self.insight_memory = insight_memory

        self.success_batch_size = success_batch_size

    def generate(
        self, 
        question: str, 
        key: str, 
        reflect: bool = True, 
        reset: bool = False,
        reset_reflexion: bool = True,
        strategy: str = "reflexion",
        prompt: str = EXPEL_REFLEXION_REACT_INSTRUCTION,
        examples: Optional[str] = None,
    ):
        if reset_reflexion:
            self.reflexion_react_agent.reset()

        if reset:
            self.reset()

        if reflect:
            self.update_rules()  # TODO

        # Needs to be changed.
        if not examples:
            queries = {
                "task": question,
            }
            examples = self.experience_memory.load_memories()['fewshots']

        self.reflexion_react_agent.generate(
            question=question,
            key=key,
            examples=examples,
            strategy=strategy,
            prompt=prompt,
            reflect_examples=,
            reflect_prompt=
        )

        # self.experience_memory.add_memories(
        #     questions=experience['questions'],
        #     keys=experience['keys'],
        #     trajectories=experience['trajectories'],
        #     reflections=experience['reflections']
        # )

    def reset(self) -> None:
        self.reflexion_react_agent.reset()
        self.experience_memory.clear()
        self.insight_memory.clear()

    def gather_experience(
        self, 
        questions: List[str],
        keys: List[str],
        strategy: Optional[str] = "reflexion"
    ) -> None:
        # Gather experience.
        self.reflexion_react_agent.reset()
        experiences = gather_experience(
            reflexion_react_agent=self.reflexion_react_agent,
            questions=questions,
            keys=keys,
            strategy=strategy
        )
        self.reflexion_react_agent.reset()

        self.experience_memory.add_memories(
            questions=experiences['questions'],
            keys=experiences['keys'],
            trajectories=experiences['trajectories'],
            reflections=experiences['reflections']
        )

        # Extract insights.
        categories = categorize_experiences(self.experience_memory.experiences)
        folds = get_folds(categories, len(self.experience_memory))

        for fold, train_idxs in folds.items():

            train_category_idxs = {
                category: list(set(train_idxs).intersection(set(category_idxs)))  # type: ignore
                for category, category_idxs in categories.items()
            }

            # Compare.
            for train_idx in train_category_idxs["compare"]:
                question = experiences["questions"][train_idx]
                trajectory = experiences["trajectories"][
                    train_idx
                ]  # List[Tuple[bool, str, List[Tuple[str, str, str]]]].

                # Compare the successful trial with all previous failed trials.
                success_trial = "\n".join(["\n".join(step) for step in trajectory[-1][-1]])
                for failed_trial in trajectory[:-1]:
                    failed_trial = "\n".join(["\n".join(step) for step in failed_trial[-1]])
                    insights = self.insight_memory.load_memories()['insights']

                    operations = get_operations_compare(
                        llm=self.llm,
                        insights=insights,
                        question=question,
                        success_trial=success_trial,
                        failed_trial=failed_trial,
                        is_full=self.insight_memory.max_num_insights < len(insights)
                    )
                    self.update_insights(operations=operations)

            # Success.
            batched_success_trajs_idxs = shuffle_chunk_list(
                train_category_idxs["success"], self.success_batch_size
            )
            for success_idxs in batched_success_trajs_idxs:
                insights = self.insight_memory.load_memories()['insights']

                # Concatenate batched successful trajectories.
                concat_success_trajs = []
                for idx in success_idxs:
                    success_traj_str = "\n".join(
                        ["\n".join(step) for step in experiences["trajectories"][idx][0][-1]]
                    )
                    concat_success_trajs.append(
                        f"{experiences['questions'][idx]}\n{success_traj_str}"
                    )
                success_trials = "\n\n".join(concat_success_trajs)

                operations = get_operations_success(
                    llm=self.llm,
                    success_trials=success_trials,
                    insights=insights,
                    is_full=self.insight_memory.max_num_insights < len(insights)
                )
                self.update_insights(operations=operations)

    def update_insights(self, operations: List[Tuple[str, str]]) -> None:
        # Update rules with comparison insights.
        for i in range(len(operations)):
            insights = self.insight_memory.load_memories()['insights']
            operation, operation_insight = operations[i]
            operation_type = operation.split(" ")[0]

            if operation_type == "REMOVE":
                insight_idx = retrieve_insight_index(
                    insights, operation_insight
                )
                self.insight_memory.delete_memories(insight_idx)
            elif operation_type == "AGREE":
                insight_idx = retrieve_insight_index(
                    insights, operation_insight
                )
                self.insight_memory.update_memories(
                    idx=insight_idx,
                    update_type="AGREE"
                )
            elif operation_type == "EDIT":
                insight_idx = int(operation.split(" ")[1]) - 1
                self.insight_memory.update_memories(
                    idx=insight_idx,
                    update_type="EDIT",
                    insight=operation_insight,
                )
            elif operation_type == "ADD":
                self.insight_memory.add_memories(
                    [{"insight": operation_insight, "score": 2}]
                )