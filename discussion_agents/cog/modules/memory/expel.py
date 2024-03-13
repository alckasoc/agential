"""ExpeL's memory implementations.

Original Paper: https://arxiv.org/abs/2308.10144
Paper Repository: https://github.com/LeapLabTHU/ExpeL
"""

from typing import Any, Dict, List, Optional, Tuple
from copy import deepcopy
from scipy.spatial.distance import cosine

import tiktoken
from tiktoken.core import Encoding

from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents.base import Document

from discussion_agents.cog.modules.memory.base import BaseMemory
from langchain_core.embeddings import Embeddings
from langchain_community.embeddings import HuggingFaceEmbeddings


class ExpeLExperienceMemory(BaseMemory):
    """ExpeL's experience pool memory.

    Attributes:
        experiences (Dict[str, List], optional): A dictionary storing experience data, 
            where each key is a task identifier. Generated from `gather_experience`.
        fewshot_questions (List[str], optional): A list of questions used in fewshot learning scenarios.
        fewshot_keys (List[str], optional): A list of answers (keys) corresponding to the fewshot questions.
        fewshot_examples (List[List[Tuple[str, str, str]]], optional): A nested list where each list 
            contains tuples of (thought, action, observation) used as fewshot examples.
        strategy (str): The strategy employed for handling and vectorizing experiences.
        reranker_strategy (str, optional): The re-ranking strategy to be applied based on similarity measures.
        embedder (Embeddings): An embedding object used for generating vector embeddings of documents.
        k_docs (int): The number of documents to return from a similarity search.
        encoder (Encoding): An encoder object used for token counting within documents.
        max_fewshot_tokens (int): The maximum number of tokens allowed in a single fewshot example.
        num_fewshots (int): The number of fewshot examples to utilize or retrieve.
    """
    def __init__(
        self,
        experiences: Optional[Dict[str, List]] = {},
        fewshot_questions: Optional[List[str]] = [],
        fewshot_keys: Optional[List[str]] = [],
        fewshot_examples: Optional[List[List[Tuple[str, str, str]]]] = [],
        strategy: str = "task",
        reranker_strategy: Optional[str] = None,
        embedder: Embeddings = HuggingFaceEmbeddings(),
        k_docs: int = 24,
        encoder: Encoding = tiktoken.encoding_for_model("gpt-3.5-turbo"),
        max_fewshot_tokens: int = 500,
        num_fewshots: int = 6
    ) -> None:
        """Initializes the memory with optional experiences, fewshot examples, and strategies.
        """
        super().__init__()

        self.experiences = deepcopy(experiences) if experiences else \
            {'idxs': [], 'questions': [], 'keys': [], 'trajectories': [], 'reflections': []}
        self.fewshot_questions = fewshot_questions
        self.fewshot_keys = fewshot_keys
        self.fewshot_examples = fewshot_examples
        self.strategy = strategy
        self.reranker_strategy = reranker_strategy
        self.embedder = embedder
        self.k_docs = k_docs
        self.encoder = encoder
        self.max_fewshot_tokens = max_fewshot_tokens
        self.num_fewshots = num_fewshots

        # Collect all successful trajectories.
        success_traj_idxs = []
        if len(self.experiences['idxs']):
            success_traj_idxs = []
            for idx in self.experiences['idxs']:
                is_correct, _, _ = self.experiences['trajectories'][idx][0]  # Success on zero-th trial.
                if is_correct: success_traj_idxs.append(idx)

        self.success_traj_docs = []
        for idx in success_traj_idxs:
            question = self.experiences["questions"][idx]
            trajectory = self.experiences["trajectories"][idx][
                0
            ]  # Zero-th trial of trajectory.
            is_correct, _, steps = trajectory
            assert is_correct  # Ensure trajectory is successful.

            # Add the task.
            self.success_traj_docs.append(
                Document(
                    page_content=question, metadata={"type": "task", "task_idx": idx}
                )
            )

            # Add all trajectory actions.
            self.success_traj_docs.extend(
                [
                    Document(
                        page_content=action,
                        metadata={"type": "action", "task_idx": idx},
                    )
                    for (_, action, _) in steps
                ]
            )

            # Add all trajectory thoughts.
            self.success_traj_docs.extend(
                [
                    Document(
                        page_content=thought,
                        metadata={"type": "thought", "task_idx": idx},
                    )
                    for (thought, _, _) in steps
                ]
            )

            # Add each step.
            for step in steps:
                self.success_traj_docs.append(
                    Document(
                        page_content="\n".join(step),
                        metadata={"type": "step", "task_idx": idx},
                    )
                )

        # If including fewshot examples in experiences.
        if fewshot_questions and fewshot_keys and fewshot_examples:
            # Update self.experiences.
            for question, key, steps in zip(fewshot_questions, fewshot_keys, fewshot_examples):
                idx = max(self.experiences['idxs'], default=-1) + 1

                self.experiences['idxs'].append(idx)
                self.experiences['questions'].append(question)
                self.experiences['keys'].append(key)
                self.experiences['trajectories'].append(
                    [
                        (True, key, steps)
                    ]
                )
                self.experiences['reflections'].append([])

                # Update self.success_traj_docs.

                # Add the task.
                self.success_traj_docs.append(
                    Document(
                        page_content=question, metadata={
                            "type": "task", 
                            "task_idx": idx
                        }
                    )
                )

                # Add all trajectory actions.
                self.success_traj_docs.extend(
                    [
                        Document(
                            page_content=action,
                            metadata={"type": "action", "task_idx": idx},
                        )
                        for (_, action, _) in steps
                    ]
                )

                # Add all trajectory thoughts.
                self.success_traj_docs.extend(
                    [
                        Document(
                            page_content=thought,
                            metadata={"type": "thought", "task_idx": idx},
                        )
                        for (thought, _, _) in steps
                    ]
                )

                # Add each step.
                for step in steps:
                    self.success_traj_docs.append(
                        Document(
                            page_content="\n".join(step),
                            metadata={"type": "step", "task_idx": idx},
                        )
                    )

        # Create vectorstore.
        self.vectorstore = None
        if len(self.experiences['idxs']):
            self.vectorstore = FAISS.from_documents(
                [doc for doc in self.success_traj_docs if doc.metadata['type'] == self.strategy], 
                self.embedder
            )

    def clear(self) -> None:
        """Clears all stored experiences from the memory.

        Resets the memory to its initial empty state.
        """
        self.experiences = {'idxs': [], 'questions': [], 'keys': [], 'trajectories': [], 'reflections': []}
        self.success_traj_docs = []
        self.vectorstore = None

    def add_memories(
        self,
        questions: List[str],
        keys: List[str],
        trajectories: List[List[Tuple[bool, str, List[Tuple[str, str, str]]]]],
        reflections: Optional[List[List[str]]] = [],
    ) -> None:
        """Adds new experiences to the memory, including associated questions, keys, 
        trajectories, and optional reflections.

        Args:
            questions (List[str]): Questions related to the experiences being added.
            keys (List[str]): Answers corresponding to the provided questions.
            trajectories (List[List[Tuple[bool, str, List[Tuple[str, str, str]]]]]): A list of trajectories where each 
                trajectory is a list of tuples with a boolean indicating success, an action taken, and a list of steps.
            reflections (Optional[List[List[str]]], default=[]): A list of additional reflective notes on the experiences.
        """
        assert len(questions) == len(keys) == len(trajectories)

        if reflections:
            assert len(reflections) == len(questions)
        else:
            reflections = [[] for _ in range(len(questions))]

        start_idx = max(self.experiences["idxs"]) + 1

        # Update experiences.
        self.experiences["idxs"].extend(
            list(
                range(
                    start_idx,
                    start_idx + len(questions),
                )
            )
        )
        self.experiences["questions"].extend(questions)
        self.experiences["keys"].extend(keys)
        self.experiences["trajectories"].extend(trajectories)
        self.experiences["reflections"].extend(reflections)

        # Update success_traj_docs.
        success_traj_idxs = []
        for idx, trajectory in enumerate(trajectories, start_idx):
            is_correct, _, _ = trajectory[0]
            if is_correct: success_traj_idxs.append(idx)

        for idx in success_traj_idxs:
            question = self.experiences["questions"][idx]
            trajectory = self.experiences["trajectories"][idx][
                0
            ]  # Zero-th trial of trajectory.
            is_correct, _, steps = trajectory
            assert is_correct  # Ensure trajectory is successful.

            # Add the task.
            self.success_traj_docs.append(
                Document(
                    page_content=question, metadata={"type": "task", "task_idx": idx}
                )
            )

            # Add all trajectory actions.
            self.success_traj_docs.extend(
                [
                    Document(
                        page_content=action,
                        metadata={"type": "action", "task_idx": idx},
                    )
                    for (_, action, _) in steps
                ]
            )

            # Add all trajectory thoughts.
            self.success_traj_docs.extend(
                [
                    Document(
                        page_content=thought,
                        metadata={"type": "thought", "task_idx": idx},
                    )
                    for (thought, _, _) in steps
                ]
            )

            # Add each step.
            for step in steps:
                self.success_traj_docs.append(
                    Document(
                        page_content="\n".join(step),
                        metadata={"type": "step", "task_idx": idx},
                    )
                )

        if success_traj_idxs:
            # Create vectorstore.
            self.vectorstore = FAISS.from_documents(
                [doc for doc in self.success_traj_docs if doc.metadata['type'] == self.strategy], 
                self.embedder
            )

    def _fewshot_doc_token_count(self, fewshot_doc: Document) -> int:
        """Returns the token count of a given document's successful trajectory.
        
        Args:
            fewshot_doc (Document): The document containing trajectory data.
        
        Returns:
            int: The token count of the document's trajectory.
        """
        task_idx = fewshot_doc.metadata['task_idx']
        trajectory = self.experiences['trajectories'][task_idx]
        _, _, steps = trajectory[0]  # A successful trial.
        steps_str = "\n".join(["\n".join(step) for step in steps])
        return len(self.encoder.encode(steps_str))

    def load_memories(self, queries: Dict[str, str], query_type: str) -> Dict[str, Any]:
        """Retrieves fewshot documents based on a similarity search, with optional re-ranking strategies.
        
        Args:
            queries (Dict[str, str]): The queries to perform similarity search against.
            query_type (str): The type of query to use for the search.
        
        Returns:
            Dict[str, Any]: A dictionary of retrieved fewshot documents (strings).
        """

        if not self.experiences:
            return 

        # Query the vectorstore.
        fewshot_docs = self.vectorstore.similarity_search(queries[query_type], k=self.k_docs)

        # Post-processing.

        # Re-ranking, optional.
        if not self.reranker_strategy or (self.reranker_strategy == 'thought' and not queries['thought']):
            fewshot_docs = list(fewshot_docs)
        elif self.reranker_strategy == 'length':
            fewshot_docs = list(sorted(fewshot_docs, key=self._fewshot_doc_token_count, reverse=True))
        elif self.reranker_strategy == 'thought' and queries['thought']:
            fewshot_tasks = set([doc.metadata['task_idx'] for doc in fewshot_docs])
            subset_docs = list(filter(lambda doc: doc.metadata['type'] == 'thought' and doc.metadata['task_idx'] in fewshot_tasks, list(self.success_traj_docs)))
            fewshot_docs = sorted(subset_docs, key=lambda doc: cosine(self.embedder.embed_query(doc.page_content), self.embedder.embed_query(queries['thought'])))
        elif self.reranker_strategy == 'task':
            fewshot_tasks = set([doc.metadata['task_idx'] for doc in fewshot_docs])
            subset_docs = list(filter(lambda doc: doc.metadata['type'] == 'thought' and doc.metadata['task_idx'] in fewshot_tasks, list(self.success_traj_docs)))
            fewshot_docs = sorted(subset_docs, key=lambda doc: cosine(self.embedder.embed_query(doc.page_content), self.embedder.embed_query(queries['task'])))
        else:
            raise NotImplementedError
        
        current_tasks = set()
        fewshots = []

        # Filtering.
        # Exclude fewshot documents that exceed the token limit 
        # or have already been selected as fewshot examples to avoid redundancy.
        for fewshot_doc in fewshot_docs:
            task_idx = fewshot_doc.metadata["task_idx"]
            question = self.experiences['questions'][task_idx]
            trajectory = self.experiences['trajectories'][task_idx]
            _, _, steps = trajectory[0]  # Zero-th successful trial.
            steps = "\n".join(["\n".join(step) for step in steps])

            if len(self.encoder.encode(steps)) <= self.max_fewshot_tokens and \
                task_idx not in current_tasks:
                fewshots.append(f"{question}\n{steps}")
                current_tasks.add(task_idx)

            if len(fewshots) == self.num_fewshots:
                break

        return {"fewshots": fewshots}


    def show_memories(self) -> Dict[str, Any]:
        """Displays the current set of stored experiences and vectorstore information.
        
        Returns:
            Dict[str, Any]: A dictionary containing experiences, succcessful trajectory documents, and vectorstore details.
        """
        return {
            "experiences": self.experiences,
            "success_traj_docs": self.success_traj_docs,
            "vectorstore": self.vectorstore
        }