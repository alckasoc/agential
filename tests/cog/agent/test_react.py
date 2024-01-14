"""Unit tests for ReAct."""
from tiktoken import Encoding
from langchain.llms.fake import FakeListLLM
from langchain.agents.react.base import DocstoreExplorer

from discussion_agents.cog.agent.react import ReActAgent, ZeroShotReActAgent


def test_init() -> None:
    llm = FakeListLLM(responses=["1"])
    agent = ReActAgent(llm=llm)
    assert agent.llm
    assert agent.max_steps == 6
    assert agent.max_tokens == 3896
    assert isinstance(agent.docstore, DocstoreExplorer)
    assert isinstance(agent.enc, Encoding)

    assert agent.step_n == 1
    assert agent.finished == False
    assert agent.scratchpad == ""


def test_generate() -> None:
    llm = FakeListLLM(responses=["1"])
    agent = ReActAgent(llm=llm)


# def test_generate() -> None:
#     """Tests generate method."""
#     # Test search.
#     responses = [
#         "I need to search for the best kick boxer in the world and find information about his controversies and crimes.\nAction 1: Search[best kick boxer in the world]",
#         'Thought 2: Since the question mentions "he", I need to search for male kick boxers.\nAction 2: Search[male kick boxers]',
#         'Thought 3: The kick boxer in question must have a Wikipedia page. I should try searching for the name mentioned in the question, possibly with keywords like "controversies" and "crimes". \nAction 3: Search[best kick boxer controversies crimes]',
#         'Thought 4: The question mentions that the kick boxer was once considered the best, so I should try searching for "former" best kick boxer.\nAction 4: Search[former best kick boxer controversies crimes]',
#         'Thought 5: The question mentions "he" and "crimes of violence outside of the ring", so I should try searching for male kick boxers who have been involved in crimes.\nAction 5: Search[male kick boxers crimes of violence]',
#         'Thought 6: The question mentions "he" and "crimes of violence outside of the ring", so I should try searching for male kick boxers who have been involved in crimes of violence.\nAction 6: Search[male kick boxers crimes of violence outside of the ring]',
#         'Thought 7: I should try searching for the name mentioned in the question, possibly with keywords like "kick boxer" and "controversies". \nAction 7: Search[kick boxer controversies]',
#     ]

#     q = 'Who was once considered the best kick boxer in the world, however he has been involved in a number of controversies relating to his "unsportsmanlike conducts" in the sport and crimes of violence outside of the ring'
#     agent = ReActAgent(llm=FakeListLLM(responses=responses))
#     out = agent.generate(observation=q)
#     assert isinstance(out, str)

#     # Test except catch.
#     thought = 'Thought 2: Since the question mentions "he", I need to search for male kick boxers.'
#     responses = responses[:1] + [thought] + ["Search[male kick boxers]"] + responses[2:]
#     agent = ReActAgent(llm=FakeListLLM(responses=responses))
#     out = agent.generate(observation=q)
#     assert isinstance(out, str)
#     assert not agent.page
#     assert not agent.lookup_cnt
#     assert not agent.lookup_keyword
#     assert not agent.lookup_list

#     # Test lookup.
#     q = "What movie did actress Irene Jacob complete before the American action crime thriller film directed by Stuart Bird?"
#     responses = [
#         "Thought 1: I need to search Irene Jacob and find the movie she completed before the American action crime thriller film directed by Stuart Bird.\nAction 1: Search[Irene Jacob]",
#         'Thought 2: The passage does not mention the movie Irene Jacob completed before the American action crime thriller film directed by Stuart Bird. Maybe I can look up "before".\nAction 2: Lookup[before]',
#         "Thought 3: The movie Irene Jacob completed before the American action crime thriller film directed by Stuart Bird is Eternity.\nAction 3: Finish[Eternity]",
#     ]
#     llm = FakeListLLM(responses=responses)
#     agent = ReActAgent(llm=llm)
#     out = agent.generate(observation=q)
#     assert isinstance(out, str)
#     assert agent.page
#     assert agent.lookup_cnt == 1
#     assert agent.lookup_keyword == "before"
#     assert agent.lookup_list


def test_zeroshot_react_init() -> None:
    """Tests ZeroShotReActAgent's initialization."""
    agent = ZeroShotReActAgent(llm=FakeListLLM(responses=["1"]))
    assert agent is not None
    assert agent.llm is not None
    assert len(agent.tools) >= 1
    assert agent.agent is not None
