"""Unit tests for ExpeL memory module."""

import re
import joblib

from langchain_core.embeddings import Embeddings
from tiktoken.core import Encoding
from discussion_agents.cog.modules.memory.expel import ExpeLExperienceMemory
from discussion_agents.cog.prompts.react import REACT_WEBTHINK_SIMPLE6_FEWSHOT_EXAMPLES

fewshot_questions = re.findall(r'Question: (.+?)\n', REACT_WEBTHINK_SIMPLE6_FEWSHOT_EXAMPLES)
fewshot_keys = re.findall(r'Action \d+: Finish\[(.+?)\]', REACT_WEBTHINK_SIMPLE6_FEWSHOT_EXAMPLES)
blocks = re.split(r'(?=Question: )', REACT_WEBTHINK_SIMPLE6_FEWSHOT_EXAMPLES)[1:]  # Split and ignore the first empty result

fewshot_examples = []
for block in blocks:
    # Extract all thoughts, actions, and observations within each block
    thoughts = re.findall(r'(Thought \d+: .+?)\n', block)
    actions = re.findall(r'(Action \d+: .+?)\n', block)
    observations = re.findall(r'(Observation \d+: .+)', block)
    
    # Combine them into tuples and add to the examples list
    fewshot_examples.append(list(zip(thoughts, actions, observations)))


def test_expel_experience_memory_init(expel_experiences_10_fake_path: str) -> None:
    """Test ExpeLExperienceMemory initialization."""
    experiences = joblib.load(expel_experiences_10_fake_path)

    # Test empty initialization.
    memory = ExpeLExperienceMemory()
    assert memory.experiences == {'idxs': [], 'questions': [], 'keys': [], 'trajectories': [], 'reflections': []}
    assert not memory.fewshot_questions
    assert not memory.fewshot_keys
    assert not memory.fewshot_examples
    assert memory.strategy == "task"
    assert memory.reranker_strategy is None
    assert isinstance(memory.embedder, Embeddings)
    assert memory.k_docs == 24
    assert isinstance(memory.encoder, Encoding)
    assert memory.max_fewshot_tokens == 500
    assert memory.num_fewshots == 6
    assert not memory.success_traj_docs
    assert memory.vectorstore is None

    # Test with experiences parameter.
    memory = ExpeLExperienceMemory(experiences)
    assert memory.experiences == experiences
    assert not memory.fewshot_questions
    assert not memory.fewshot_keys
    assert not memory.fewshot_examples
    assert memory.strategy == "task"
    assert memory.reranker_strategy is None
    assert isinstance(memory.embedder, Embeddings)
    assert memory.k_docs == 24
    assert isinstance(memory.encoder, Encoding)
    assert memory.max_fewshot_tokens == 500
    assert memory.num_fewshots == 6
    assert len(memory.success_traj_docs) == 38
    assert memory.vectorstore
    
    success_traj_doc_types = [
        "task",
        "action",
        "action",
        "action",
        "action",
        "action",
        "action",
        "thought",
        "thought",
        "thought",
        "thought",
        "thought",
        "thought",
        "step",
        "step",
        "step",
        "step",
        "step",
        "step",
    ] * 2

    for type_, doc in zip(success_traj_doc_types, memory.success_traj_docs):
        assert type_ == doc.metadata['type']

    # Test with no experiences and fewshot examples.
    memory = ExpeLExperienceMemory(
        fewshot_questions=fewshot_questions,
        fewshot_keys=fewshot_keys,
        fewshot_examples=fewshot_examples
    )
    assert list(memory.experiences.keys()) == ['idxs', 'questions', 'keys', 'trajectories', 'reflections']
    for v in memory.experiences.values():
        assert len(v) == 6
    assert memory.fewshot_questions
    assert memory.fewshot_keys
    assert memory.fewshot_examples
    assert memory.strategy == "task"
    assert memory.reranker_strategy is None
    assert isinstance(memory.embedder, Embeddings)
    assert memory.k_docs == 24
    assert isinstance(memory.encoder, Encoding)
    assert memory.max_fewshot_tokens == 500
    assert memory.num_fewshots == 6
    assert len(memory.success_traj_docs) == 48
    assert memory.vectorstore

    # Test with experiences and fewshot examples.
    memory = ExpeLExperienceMemory(
        experiences=experiences,
        fewshot_questions=fewshot_questions,
        fewshot_keys=fewshot_keys,
        fewshot_examples=fewshot_examples
    )
    assert list(memory.experiences.keys()) == ['idxs', 'questions', 'keys', 'trajectories', 'reflections']
    for v in memory.experiences.values():
        assert len(v) == 16
    assert memory.fewshot_questions
    assert memory.fewshot_keys
    assert memory.fewshot_examples
    assert memory.strategy == "task"
    assert memory.reranker_strategy is None
    assert isinstance(memory.embedder, Embeddings)
    assert memory.k_docs == 24
    assert isinstance(memory.encoder, Encoding)
    assert memory.max_fewshot_tokens == 500
    assert memory.num_fewshots == 6
    assert len(memory.success_traj_docs) == 86
    assert memory.vectorstore


def test_expel_experience_memory_clear(expel_experiences_10_fake_path: str) -> None:
    """Test ExpeLExperienceMemory clear method."""
    experiences = joblib.load(expel_experiences_10_fake_path)
    memory = ExpeLExperienceMemory(experiences)
    assert memory.experiences
    assert memory.success_traj_docs
    assert memory.vectorstore
    memory.clear()
    for v in memory.experiences.values():
        assert not v
    assert not memory.success_traj_docs
    assert not memory.vectorstore


def test_expel_experience_memory_add_memories(expel_experiences_10_fake_path: str) -> None:
    """Test ExpeLExperienceMemory add_memories method."""
    experiences = joblib.load(expel_experiences_10_fake_path)

    # Successful trajectory.
    success_questions = [
        experiences['questions'][3]
    ]
    success_keys = [
        experiences['keys'][3]
    ]
    success_trajectories = [
        experiences['trajectories'][3]
    ]
    success_reflections = [
        []
    ]

    # Failed trajectories (multiple).
    fail_questions = [
        experiences['questions'][0],
        experiences['questions'][1],
    ]
    fail_keys = [
        experiences['keys'][0],
        experiences['keys'][1],
    ]
    fail_trajectories = [
        experiences['trajectories'][0],
        experiences['trajectories'][1]
    ]
    fail_reflections = [
        experiences['reflections'][0],
        experiences['reflections'][1]
    ]

    # Test with empty memory (with and without reflection).
    memory = ExpeLExperienceMemory()
    memory.add_memories(
        success_questions,
        success_keys,
        success_trajectories,
        success_reflections
    )
    assert memory.experiences['idxs'] == [0]
    assert memory.experiences['questions'][0] == success_questions[0]
    assert memory.experiences['keys'][0] == success_keys[0]
    assert memory.experiences['trajectories'][0]  == success_trajectories[0]
    assert memory.experiences['reflections'][0] == success_reflections[0]
    assert len(memory.success_traj_docs) == 19
    assert memory.success_traj_docs[0].metadata['task_idx'] == 0
    assert memory.vectorstore

    memory.add_memories(
        success_questions,
        success_keys,
        success_trajectories,
    )
    assert memory.experiences['idxs'] == [0, 1]
    assert memory.experiences['questions'][1] == success_questions[0]
    assert memory.experiences['keys'][1] == success_keys[0]
    assert memory.experiences['trajectories'][1]  == success_trajectories[0]
    assert memory.experiences['reflections'][1] == success_reflections[0]
    assert len(memory.success_traj_docs) == 38
    assert memory.success_traj_docs[0].metadata['task_idx'] == 0
    assert memory.success_traj_docs[-1].metadata['task_idx'] == 1
    assert memory.vectorstore    

    # Test with non-empty memory (with reflection).
    memory.add_memories(
        success_questions,
        success_keys,
        success_trajectories,
        success_reflections
    )
    assert memory.experiences['idxs'] == [0, 1, 2]
    assert memory.experiences['questions'][2] == success_questions[0]
    assert memory.experiences['keys'][2] == success_keys[0]
    assert memory.experiences['trajectories'][2]  == success_trajectories[0]
    assert memory.experiences['reflections'][2] == success_reflections[0]
    assert len(memory.success_traj_docs) == 57
    assert memory.success_traj_docs[0].metadata['task_idx'] == 0
    assert memory.success_traj_docs[20].metadata['task_idx'] == 1
    assert memory.success_traj_docs[-1].metadata['task_idx'] == 2
    assert memory.vectorstore    

    # Test with adding only failed trajectories.
    memory.add_memories(
        fail_questions,
        fail_keys,
        fail_trajectories,
        fail_reflections
    )
    assert memory.experiences['idxs'] == [0, 1, 2, 3, 4]
    assert memory.experiences['questions'][3] == fail_questions[0]
    assert memory.experiences['questions'][4] == fail_questions[1]
    assert memory.experiences['keys'][3] == fail_keys[0]
    assert memory.experiences['keys'][4] == fail_keys[1]
    assert memory.experiences['trajectories'][3]  == fail_trajectories[0]
    assert memory.experiences['trajectories'][4] == fail_trajectories[1]
    assert memory.experiences['reflections'][3] == fail_reflections[0]
    assert memory.experiences['reflections'][4] == fail_reflections[1]
    assert len(memory.success_traj_docs) == 57
    assert memory.success_traj_docs[0].metadata['task_idx'] == 0
    assert memory.success_traj_docs[20].metadata['task_idx'] == 1
    assert memory.success_traj_docs[50].metadata['task_idx'] == 2
    assert memory.vectorstore    

    # Test with a mix of failed and successful trajectories.
    memory.add_memories(
        success_questions + fail_questions,
        success_keys + fail_keys,
        success_trajectories + fail_trajectories,
        success_reflections + fail_reflections
    )
    assert memory.experiences['idxs'] == [0, 1, 2, 3, 4, 5, 6, 7]
    assert memory.experiences['questions'][5] == success_questions[0]
    assert memory.experiences['questions'][6] == fail_questions[0]
    assert memory.experiences['questions'][7] == fail_questions[1]
    assert memory.experiences['keys'][5] == success_keys[0]
    assert memory.experiences['keys'][6] == fail_keys[0]
    assert memory.experiences['keys'][7] == fail_keys[1]
    assert memory.experiences['trajectories'][5] == success_trajectories[0]
    assert memory.experiences['trajectories'][6]  == fail_trajectories[0]
    assert memory.experiences['trajectories'][7] == fail_trajectories[1]
    assert memory.experiences['reflections'][5] == success_reflections[0]
    assert memory.experiences['reflections'][6] == fail_reflections[0]
    assert memory.experiences['reflections'][7] == fail_reflections[1]
    assert len(memory.success_traj_docs) == 76
    assert memory.success_traj_docs[0].metadata['task_idx'] == 0
    assert memory.success_traj_docs[20].metadata['task_idx'] == 1
    assert memory.success_traj_docs[56].metadata['task_idx'] == 2
    assert memory.success_traj_docs[57].metadata['task_idx'] == 5
    assert memory.vectorstore  



def test_expel_experience_memory__fewshot_doc_token_count(expel_experiences_10_fake_path: str) -> None:
    """Test ExpeLExperienceMemory _fewshot_doc_token_count method."""
    experiences = joblib.load(expel_experiences_10_fake_path)

    # Testing with just experiences (1 success, a dupe).
    memory = ExpeLExperienceMemory(experiences)
    for doc in memory.success_traj_docs:
        token_count = memory._fewshot_doc_token_count(doc)
        assert token_count == 1245

    # Testing with fewshots only.
    gt_token_counts = [273] * 13 + [149] * 7 + [156] * 7 + [163] * 7 + [134] * 7 + [154] * 7
    memory = ExpeLExperienceMemory(
        fewshot_questions=fewshot_questions,
        fewshot_keys=fewshot_keys,
        fewshot_examples=fewshot_examples
    )
    for gt_token_count, doc in zip(gt_token_counts, memory.success_traj_docs):
        token_count = memory._fewshot_doc_token_count(doc)
        assert gt_token_count == token_count


def test_expel_experience_memory_load_memories(expel_experiences_10_fake_path: str) -> None:
    """Test ExpeLExperienceMemory load_memories method."""
    experiences = joblib.load(expel_experiences_10_fake_path)

    queries = {
        "task": 'The creator of "Wallace and Gromit" also created what animation comedy that matched animated zoo animals with a soundtrack of people talking about their homes? ',
        "thought": 'Thought: I should try a different approach. Let me search for press releases, industry news sources, or announcements specifically related to the name change and new acronym for VIVA Media AG in 2004. By focusing on more specialized sources, I may be able to find the accurate information needed to answer the question correctly. '
    }

    # Test when memory is empty.
    memory = ExpeLExperienceMemory()
    memory_dict = memory.load_memories(queries=queries, query_type="task")
    assert list(memory_dict.keys()) == ["fewshots"]
    assert not memory_dict['fewshots']

    # Test with every query type.

    # Test with every reranking strategy + error.

    # Test with varying max_fewshot_tokens.
    
    # Test with varying num_fewshots.


def test_expel_experience_memory_show_memories(expel_experiences_10_fake_path: str) -> None:
    """Test ExpeLExperienceMemory show_memories method."""
    experiences = joblib.load(expel_experiences_10_fake_path)

    # Test with empty memory.
    memory = ExpeLExperienceMemory()
    memory_dict = memory.show_memories()
    assert list(memory_dict.keys()) == ["experiences", "success_traj_docs", "vectorstore"]
    assert memory_dict['experiences'] == {'idxs': [], 'questions': [], 'keys': [], 'trajectories': [], 'reflections': []}
    assert not memory_dict['success_traj_docs']
    assert not memory_dict['vectorstore']

    # Test with non-empty memory.
    memory = ExpeLExperienceMemory(experiences)
    memory_dict = memory.show_memories()
    assert list(memory_dict.keys()) == ["experiences", "success_traj_docs", "vectorstore"]
    assert memory.experiences == memory_dict['experiences']
    assert len(memory_dict['success_traj_docs']) == 38
    assert memory_dict['vectorstore']
