"""ReAct prompts and fewshot examples."""


REACT_INSTRUCTION_HOTPOTQA = """Solve a question answering task with interleaving Thought, Action, Observation steps. Thought can reason about the current situation, and Action can be three types: 
(1) Search[entity], which searches the exact entity on Wikipedia and returns the first paragraph if it exists. If not, it will return some similar entities to search.
(2) Lookup[keyword], which returns the next sentence containing keyword in the last passage successfully found by Search.
(3) Finish[answer], which returns the answer and finishes the task.
You may take as many steps as necessary.
Here are some examples:
{examples}
(END OF EXAMPLES)
Question: {question}{scratchpad}"""

REACT_WEBTHINK_SIMPLE6_FEWSHOT_EXAMPLES = """
Question: What is the elevation range for the area that the eastern sector of the Colorado orogeny extends into?
Thought 1: I need to search Colorado orogeny, find the area that the eastern sector of the Colorado orogeny extends into, then find the elevation range of the area.
Action 1: Search[Colorado orogeny]
Observation 1: The Colorado orogeny was an episode of mountain building (an orogeny) in Colorado and surrounding areas.
Thought 2: It does not mention the eastern sector. So I need to look up eastern sector.
Action 2: Lookup[eastern sector]
Observation 2: (Result 1 / 1) The eastern sector extends into the High Plains and is called the Central Plains orogeny.
Thought 3: The eastern sector of Colorado orogeny extends into the High Plains. So I need to search High Plains and find its elevation range.
Action 3: Search[High Plains]
Observation 3: High Plains refers to one of two distinct land regions:
Thought 4: I need to instead search High Plains (United States).
Action 4: Search[High Plains (United States)]
Observation 4: The High Plains are a subregion of the Great Plains. From east to west, the High Plains rise in elevation from around 1,800 to 7,000 ft (550 to 2,130 m).[3]
Thought 5: High Plains rise in elevation from around 1,800 to 7,000 ft, so the answer is 1,800 to 7,000 ft.
Action 5: Finish[1,800 to 7,000 ft]
Question: Musician and satirist Allie Goertz wrote a song about the "The Simpsons" character Milhouse, who Matt Groening named after who?
Thought 1: The question simplifies to "The Simpsons" character Milhouse is named after who. I only need to search Milhouse and find who it is named after.
Action 1: Search[Milhouse]
Observation 1: Milhouse Mussolini Van Houten is a recurring character in the Fox animated television series The Simpsons voiced by Pamela Hayden and created by Matt Groening.
Thought 2: The paragraph does not tell who Milhouse is named after, maybe I can look up "named after".
Action 2: Lookup[named after]
Observation 2: (Result 1 / 1) Milhouse was named after U.S. president Richard Nixon, whose middle name was Milhous. 
Thought 3: Milhouse was named after U.S. president Richard Nixon, so the answer is Richard Nixon.
Action 3: Finish[Richard Nixon]
Question: Which documentary is about Finnish rock groups, Adam Clayton Powell or The Saimaa Gesture?
Thought 1: I need to search Adam Clayton Powell and The Saimaa Gesture, and find which documentary is about Finnish rock groups.
Action 1: Search[Adam Clayton Powell]
Observation 1: Could not find [Adam Clayton Powell]. Similar: ['Adam Clayton Powell III', 'Seventh Avenue (Manhattan)', 'Adam Clayton Powell Jr. State Office Building', 'Isabel Washington Powell', 'Adam Powell', 'Adam Clayton Powell (film)', 'Giancarlo Esposito'].
Thought 2: To find the documentary, I can search Adam Clayton Powell (film).
Action 2: Search[Adam Clayton Powell (film)]
Observation 2: Adam Clayton Powell is a 1989 American documentary film directed by Richard Kilberg.
The film is about the rise and fall of influential African-American politician Adam Clayton Powell Jr.[3][4] It was later aired as part of the PBS series The American Experience.
Thought 3: Adam Clayton Powell (film) is a documentary about an African-American politician, not Finnish rock groups. So the documentary about Finnish rock groups must instead be The Saimaa Gesture.
Action 3: Finish[The Saimaa Gesture]
Question: What profession does Nicholas Ray and Elia Kazan have in common?
Thought 1: I need to search Nicholas Ray and Elia Kazan, find their professions, then find the profession they have in common.
Action 1: Search[Nicholas Ray]
Observation 1: Nicholas Ray (born Raymond Nicholas Kienzle Jr., August 7, 1911 – June 16, 1979) was an American film director, screenwriter, and actor best known for the 1955 film Rebel Without a Cause.
Thought 2: Professions of Nicholas Ray are director, screenwriter, and actor. I need to search Elia Kazan next and find his professions.
Action 2: Search[Elia Kazan]
Observation 2: Elia Kazan was an American film and theatre director, producer, screenwriter and actor.
Thought 3: Professions of Elia Kazan are director, producer, screenwriter, and actor. So profession Nicholas Ray and Elia Kazan have in common is director, screenwriter, and actor.
Action 3: Finish[director, screenwriter, actor]
Question: Which magazine was started first Arthur's Magazine or First for Women?
Thought 1: I need to search Arthur's Magazine and First for Women, and find which was started first.
Action 1: Search[Arthur's Magazine]
Observation 1: Arthur's Magazine (1844-1846) was an American literary periodical published in Philadelphia in the 19th century. 
Thought 2: Arthur's Magazine was started in 1844. I need to search First for Women next.
Action 2: Search[First for Women]
Observation 2: First for Women is a woman's magazine published by Bauer Media Group in the USA.[1] The magazine was started in 1989. 
Thought 3: First for Women was started in 1989. 1844 (Arthur's Magazine) < 1989 (First for Women), so Arthur's Magazine was started first.
Action 3: Finish[Arthur's Magazine]
Question: Were Pavel Urysohn and Leonid Levin known for the same type of work?
Thought 1: I need to search Pavel Urysohn and Leonid Levin, find their types of work, then find if they are the same.
Action 1: Search[Pavel Urysohn]
Observation 1: Pavel Samuilovich Urysohn (February 3, 1898 â August 17, 1924) was a Soviet mathematician who is best known for his contributions in dimension theory.
Thought 2: Pavel Urysohn is a mathematician. I need to search Leonid Levin next and find its type of work.
Action 2: Search[Leonid Levin]
Observation 2: Leonid Anatolievich Levin is a Soviet-American mathematician and computer scientist. 
Thought 3: Leonid Levin is a mathematician and computer scientist. So Pavel Urysohn and Leonid Levin have the same type of work. 
Action 3: Finish[yes]
"""




REACT_INSTRUCTION_FEVER = """Determine if there is Observation that SUPPORTS or REFUTES a Claim, or if there is NOT ENOUGH INFORMATION.  and Action can be two types: 
(1) Search[entity], which searches the exact entity on Wikipedia and returns the first paragraph if it exists. If not, it will return some similar entities to search.
(3) Finish[answer], which returns the answer and finishes the task.
You may take as many steps as necessary.
Here are some examples:
{examples}
(END OF EXAMPLES)
Question: {question}{scratchpad}"""


REACT_WEBTHINK_SIMPLE3_FEVER_EXAMPLES = """
Claim: Nikolaj Coster-Waldau worked with the Fox Broadcasting Company.
Thought 1: I need to search Nikolaj Coster-Waldau and find if he has worked with the Fox Broadcasting Company.
Action 1: Search[Nikolaj Coster-Waldau]
Observation 1: Nikolaj William Coster-Waldau (born 27 July 1970) is a Danish actor and producer. He graduated from the Danish National School of Performing Arts in Copenhagen in 1993,[1] and had his breakthrough role in Denmark with the film Nightwatch (1994). He played Jaime Lannister in the HBO fantasy drama series Game of Thrones, for which he received two Primetime Emmy Award nominations for Outstanding Supporting Actor in a Drama Series.. Coster-Waldau has appeared in numerous films in his native Denmark and Scandinavia, including Headhunters (2011) and A Thousand Times Good Night (2013). In the U.S, his debut film role was in the war film Black Hawk Down (2001), playing Medal of Honor recipient Gary Gordon.[2] He then played a detective in the short-lived Fox television series New Amsterdam (2008), and appeared in the 2009 Fox television film Virtuality, originally intended as a pilot.
Thought 2: Because he "appeared in the 2009 Fox television film Virtuality", he should have worked with the Fox Broadcasting Company.
Action 2: Finish[SUPPORTS]

Claim: Stranger Things is set in Bloomington, Indiana.
Thought 1: I should search for Stranger Things, and see if it is set in Bloomington, Indiana.
Action 1: Search[Stranger Things]
Observation 1: Stranger Things is an American science fiction horror drama television series created by the Duffer Brothers. Set in the 1980s, primarily in the fictional town of Hawkins, Indiana, the series centers on a number of mysteries and supernatural events occurring around the town and their impact on an ensemble of child and adult characters. 
Thought 2: The observation says that it is set in a "fictional town of Hawkins, Indiana", so it is not set in Bloomington.
Action 2: Finish[REFUTES]

Claim: Beautiful reached number two on the Billboard Hot 100 in 2003.?
Thought 1: I need to search the song Beautiful and find if it reached number two on the Billboard Hot 100 in 2003.
Action 1: Search[Beautiful]
Observation 1: Could not find [Beautiful]. Similar: ['Beautiful', 'Beautiful, Beautiful', 'A Beautiful Mind (film)', 'Beautiful (Christina Aguilera song)', 'Life Is Beautiful'].
Thought 2: From suggestions, I should search "Beautiful (Christina Aguilera song)" to find the song.
Action 2: Search[Beautiful (Christina Aguilera song)]
Observation 2: "Beautiful" is a song recorded by American singer Christina Aguilera for her fourth studio album, Stripped (2002).
Thought 3: It does not mention Billboard, so I need to look up "Billboard Hot 100" to find if it reached number two on it in 2003.
Action 3: Lookup[Billboard Hot 100]
Observation 3: (Result 1 / 3) The song peaked at number two on the Billboard Hot 100 in the United States, where it was certified Gold for 500,000 units shipped.
Thought 4: It only says the song peaked at number two on the Billboard Hot 100, but not if it was in 2003. I am not sure if this claim is true or not.
Action 4: Finish[NOT ENOUGH INFO]
"""


REACT_ALFWORLD_INSTRUCTION = """
Interact with a household to solve a task. Here are two examples.
{examples}
Here is the task
{question}
{scratchpad}
"""

REACT_ALFWORLD_PROMPTS_EXAMPLE  = {
    "react_put_0": """
        You are in the middle of a room. Looking quickly around you, you see a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a countertop 1, a garbagecan 1, a handtowelholder 2, a handtowelholder 1, a sinkbasin 2, a sinkbasin 1, a toilet 1, a toiletpaperhanger 1, and a towelholder 1.
        Your task is to: put some spraybottle on toilet.
        Action 1: think: To solve the task, I need to find and take a sparybottle, then put it on toilet.
        Observation 1: OK.
        Action 2: think: First I need to find a spraybottle. A spraybottle is more likely to appear in cabinet (1-4), countertop (1), toilet (1), sinkbasin (1-2), garbagecan (1). I can check one by one, starting with cabinet 1.
        Observation 2: OK.
        Action 3: go to cabinet 1
        Observation 3: On the cabinet 1, you see a cloth 1, a soapbar 1, a soapbottle 1.
        Action 4: go to cabinet 2
        Observation 4: The cabinet 2 is closed.
        Action 5: open cabinet 2
        Observation 5: You open the cabinet 2. The cabinet 2 is open. In it, you see a candle 1, and a spraybottle 2.
        Action 6: think: Now I find a spraybottle (2). Next, I need to take it. \n>take spraybottle 2 from cabinet 2
        Observation 6: You pick up the spraybottle 2 from the cabinet 2.
        Action 7: think: Now I take a spraybottle (2). Next, I need to put it in/on toilet 1.
        Observation 7: OK.
        Action 8: go to toilet 1
        Observation 8: On the toilet 1, you see a soapbottle 2.
        Action 9: put spraybottle 2 in/on toilet 1
        Observation 9: You put the spraybottle 2 in/on the toilet 1.
    """, 
    "react_put_1": """
        You are in the middle of a room. Looking quickly around you, you see a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 1, a diningtable 3, a diningtable 2, a diningtable 1, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a sidetable 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.
        Your task is to: find some apple and put it in sidetable.
        Action 1: think: To solve the task, I need to find and take an apple, then put it in sidetable.
        Observation 1: OK.
        Action 2: think: First I need to find an apple. An apple is more likely to appear in fridges (1), diningtables (1-3), sidetables (1), countertops (1), sinkbasins (1), garbagecan (1). I can check one by one, starting with fridge 1.
        Observation 2: OK.
        Action 3: go to fridge 1
        Observation 3: The fridge 1 is closed.
        Action 4: open fridge 1
        Observation 4: You open the fridge 1. The fridge 1 is open. In it, you see a lettuce 2, a mug 2, a potato 2, and a tomato 1.
        Action 5: go to diningtable 1
        Observation 5: On the diningtable 1, you see nothing.
        Action 6: go to diningtable 2
        Observation 6: On the diningtable 2, you see a pineapple 1.
        Action 7: go to diningtable 3
        Observation 7: On the diningtable 3, you see a bowl 2, a bowl 1, a bread 2, and a bread 1.
        Action 8: go to sidetable 1
        Observation 8:On the sidetable 1, you see a cup 1, a lettuce 1, a peppershaker 3, a potato 1, and a saltshaker 1.
        Action 9: go to countertop 1
        Observation 9: On the countertop 1, you see a butterknife 1, a dishsponge 1, and a soapbottle 1.
        Action 10: go to sinkbasin 1
        Observation 10: On the sinkbasin 1, you see a cup 2, a egg 1, a mug 1, and a potato 3.
        Action 11: go to garbagecan 1
        Observation 11: On the garbagecan 1, you see a apple 3, and a egg 3.
        Action 12: think: Now I find an apple (3). Next, I need to take it.\n>take apple 3 from garbagecan 1
        Observation 12: You pick up the apple 3 from the garbagecan 1.
        Action 13: think: Now I find an apple (3). Next, I need to put it in/on sidetable 1.
        Observation 13: OK.
        Action 14: go to sidetable 1
        Observation 14: On the sidetable 1, you see a cup 1, a lettuce 1, a peppershaker 3, a potato 1, and a saltshaker 1.
        Action 15: put apple 3 in/on sidetable 1
        Observation 15: You put the apple 3 in/on the sidetable 1.
    """, 
    "react_put_2": """
        You are in the middle of a room. Looking quickly around you, you see a bathtubbasin 1, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a countertop 1, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a dresser 1, a garbagecan 1, a handtowelholder 1, a sinkbasin 2, a sinkbasin 1, a toilet 1, a toiletpaperhanger 1, and a towelholder 1.
        Your task is to: put a soapbottle in garbagecan.
        Action 1: think: To solve the task, I need to find and take a soapbottle, and put it in garbagecan.
        Observation 1: OK.
        Action 2: think: First I need to find a soapbottle. A soapbottle is more likely to appear in toilet (1), sinkbasin (1-2), bathtubbasin (1), cabinet (1-4), countertop (1), dresser (1), drawer (1-4), garbagecan (1). I can check one by one, starting with toilet 1.
        Observation 2: OK.
        Action 3: go to toilet 1
        Observation 3: On the toilet 1, you see nothing.
        Action 4: go to sinkbasin 1
        Observation 4: On the sinkbasin 1, you see nothing.
        Action 5: go to sinkbasin 2
        Observation 5: On the sinkbasin 2, you see nothing.
        Action 6: go to bathtubbasin 1
        Observation 6: On the bathtubbasin 1, you see a cloth 2.
        Action 7: go to cabinet 1
        Observation 7: The cabinet 1 is closed.
        Action 8: open cabinet 1
        Observation 8: You open the cabinet 1. The cabinet 1 is open. In it, you see nothing.
        Action 9: go to cabinet 2
        Observation 9: The cabinet 2 is closed.
        Action 10: open cabinet 2
        Observation 10: You open the cabinet 2. The cabinet 2 is open. In it, you see nothing.
        Action 11: go to cabinet 3
        Observation 11: The cabinet 3 is closed.
        Action 12: open cabinet 3
        Observation 12: You open the cabinet 3. The cabinet 3 is open. In it, you see a toiletpaper 2.
        Action 13: go to cabinet 4
        Observation 13: The cabinet 4 is closed.
        Action 14: open cabinet 4
        Observation 14: You open the cabinet 4. The cabinet 4 is open. In it, you see a spraybottle 2.
        Action 15: go to countertop 1
        Observation 15: On the countertop 1, you see a soapbottle 2, and a spraybottle 1.
        Action 16: think: Now I find a soapbottle (2). Next, I need to take it.
        Observation 16: OK.
        Action 17: take soapbottle 2 from countertop 1
        Observation 17:You pick up the soapbottle 2 from the countertop 1.
        Action 18: think: Now I take a soapbottle (2). Next, I need to put it in/on garbagecan 1.
        Observation 18: OK.
        Action 19: go to garbagecan 1
        Observation 19: On the garbagecan 1, you see nothing.
        Action 20: put soapbottle 2 in/on garbagecan 1
        Observation 20: You put the soapbottle 2 in/on the garbagecan 1.
    """, 
    "react_clean_0": """
        You are in the middle of a room. Looking quickly around you, you see a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 1, a diningtable 1, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a shelf 3, a shelf 2, a shelf 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.
        Your task is to: put a clean lettuce in diningtable.
        Action 1: think: To solve the task, I need to find and take a lettuce, then clean it with sinkbasin, then put it in diningtable. 
        Observation 1: OK.
        Action 2: think: First I need to find a lettuce. A lettuce is more likely to appear in fridge (1), diningtable (1), sinkbasin (1), stoveburner (1-3), cabinet (1-13). I can check one by one, starting with fridge 1.
        Observation 2: OK.
        Action 3: go to fridge 1
        Observation 3: The fridge 1 is closed.
        Action 4: open fridge 1
        Observation 4: You open the fridge 1. The fridge 1 is open. In it, you see a cup 3, a egg 2, a potato 3, and a potato 2.
        Action 5: go to diningtable 1
        Observation 5: On the diningtable 1, you see a apple 1, a bread 1, a butterknife 2, a cup 2, a fork 2, a knife 2, a knife 1, a ladle 1, a lettuce 1, a mug 2, a mug 1, a pan 2, a peppershaker 1, a spatula 3, a tomato 2, and a tomato 1.
        Action 6: think: Now I find a lettuce (1). Next, I need to take it.
        Observation 6: OK.
        Action 7: take lettuce 1 from diningtable 1
        Observation 7: You pick up the lettuce 1 from the diningtable 1.
        Action 8: think: Now I take a lettuce (1). Next, I need to go to sinkbasin (1) and clean it.
        Observation 8: OK.
        Action 9: go to sinkbasin 1
        Observation 9: On the sinkbasin 1, you see a apple 2, a ladle 2, a spoon 1, and a tomato 3.
        Action 10: clean lettuce 1 with sinkbasin 1
        Observation 10: You clean the lettuce 1 using the sinkbasin 1.
        Action 11: think: Now I clean a lettuce (1). Next, I need to put it in/on diningtable 1.
        Observation 11: OK.
        Action 12: go to diningtable 1
        Observation 12: On the diningtable 1, you see a apple 1, a bread 1, a butterknife 2, a cup 2, a fork 2, a knife 2, a knife 1, a ladle 1, a mug 2, a mug 1, a pan 2, a peppershaker 1, a spatula 3, a tomato 2, and a tomato 1.
        Action 13: put lettuce 1 in/on diningtable 1
        Observation 13: You put the lettuce 1 in/on the diningtable 1.
    """, 
    "react_clean_1": """
        You are in the middle of a room. Looking quickly around you, you see a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 1, a diningtable 3, a diningtable 2, a diningtable 1, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a sidetable 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.
        Your task is to: clean some apple and put it in sidetable.
        Action 1: think: To solve the task, I need to find and take an apple, then clean it with sinkbasin, then put it in sidetable.
        Observation 1: OK.
        Action 2: think: First I need to find an apple. An apple is more likely to appear in fridges (1), diningtable (1-3), sidetable (1), countertop (1), sinkbasin (1), garbagecan (1). I can check one by one, starting with fridge 1.
        Observation 2: OK.
        Action 3: go to fridge 1
        Observation 3: The fridge 1 is closed.
        Action 4: open fridge 1
        Observation 4: You open the fridge 1. The fridge 1 is open. In it, you see a lettuce 2, a mug 2, a potato 2, and a tomato 1.
        Action 5: go to diningtable 1
        Observation 5: On the diningtable 1, you see nothing.
        Action 6: go to diningtable 2
        Observation 6: On the diningtable 2, you see a pineapple 1.
        Action 7: go to diningtable 3
        Observation 7: On the diningtable 3, you see a bowl 2, a bowl 1, a bread 2, and a bread 1.
        Action 8: go to sidetable 1
        Observation 8: On the sidetable 1, you see a cup 1, a lettuce 1, a peppershaker 3, a potato 1, and a saltshaker 1.
        Action 9: go to countertop 1
        Observation 9: On the countertop 1, you see a butterknife 1, a dishsponge 1, and a soapbottle 1.
        Action 10: go to sinkbasin 1
        Observation 10: On the sinkbasin 1, you see a cup 2, a egg 1, a mug 1, and a potato 3.
        Action 11: go to garbagecan 1
        Observation 11: On the garbagecan 1, you see a apple 3, and a egg 3.
        Action 12: think: Now I find an apple (3). Next, I need to take it.
        Observation 12: OK.
        Action 13: take apple 3 from garbagecan 1
        Observation 13: You pick up the apple 3 from the garbagecan 1.
        Action 14: think: Now I take an apple (3). Next, I need to go to sinkbasin (1) and clean it.
        Observation 14: OK.
        Action 15: go to sinkbasin 1
        Observation 15: On the sinkbasin 1, you see a cup 2, a egg 1, a mug 1, and a potato 3.
        Action 16: clean apple 3 with sinkbasin 1
        Observation 16: You clean the apple 3 using the sinkbasin 1.
        Action 17: think: Now I clean an apple (3). Next, I need to put it in/on sidetable 1.
        Observation 17: OK.
        Action 18: go to sidetable 1
        Observation 18: On the sidetable 1, you see a cup 1, a lettuce 1, a peppershaker 3, a potato 1, and a saltshaker 1.
        Action 19: put apple 3 in/on sidetable 1
        Observation 19: You put the apple 3 in/on the sidetable 1.
    """, 
    "react_heat_0": """
        You are in the middle of a room. Looking quickly around you, you see a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 3, a countertop 2, a countertop 1, a diningtable 1, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.
        Your task is to: heat some egg and put it in diningtable.
        Action 1: think: To solve the task, I need to find and take an egg, then heat it with microwave, then put it in diningtable.
        Observation 1: OK.
        Action 2: think: First I need to find an egg. An egg is more likely to appear in fridge (1), countertop (1-3), diningtable (1), stoveburner (1-4), toaster (1), garbagecan (1), cabinet (1-10). I can check one by one, starting with fridge 1.
        Observation 2: OK.
        Action 3: open fridge 1
        Observation 3: You open the fridge 1. The fridge 1 is open. In it, you see a lettuce 2, a mug 2, and a potato 3.
        Action 4: go to countertop 1
        Observation 4: On the countertop 1, you see a bread 1, a fork 1, and a saltshaker 1.
        Action 5: go to countertop 2
        Observation 5: On the countertop 2, you see nothing.
        Action 6: go to countertop 3
        Observation 6: On the countertop 3, you see a bowl 1, a butterknife 1, a egg 2, a kettle 2, a plate 1, a sink 1, and a spatula 2.
        Action 7: think: Now I find an egg (2). Next, I need to take it.
        Observation 7: OK.
        Action 8: take egg 2 from countertop 3
        Observation 8: You pick up the egg 2 from the countertop 3.
        Action 9: think: Now I take an egg (2). Next, I need go to a microwave (1) and heat it.
        Observation 9: OK.
        Action 10: go to microwave 1
        Observation 10: The microwave 1 is closed.
        Action 11: heat egg 2 with microwave 1
        Observation 11: You heat the egg 2 using the microwave 1.
        Action 12: think: Now I heat an egg (2). Next, I need to put it in/on diningtable 1.
        Observation 12: OK.
        Action 13: go to diningtable 1
        Observation 13: On the diningtable 1, you see a apple 2, a bread 3, a egg 1, a kettle 1, a knife 1, a mug 1, a papertowelroll 1, a peppershaker 2, a potato 1, a soapbottle 1, and a spatula 1.
        Action 14: put egg 2 in/on diningtable 1
        Observation 14: You put the egg 2 in/on the diningtable 1.
    """, 
    "react_heat_1": """
        You are in the middle of a room. Looking quickly around you, you see a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 1, a diningtable 1, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a shelf 3, a shelf 2, a shelf 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.
        Your task is to: put a hot apple in fridge.
        Action 1: think: To solve the task, I need to find and take an apple, then heat it with microwave, then put it in fridge.
        Observation 1: OK.
        Action 2: think: First I need to find an apple. An apple is more likely to appear in fridge (1), diningtable (1), coffeetable (1), drawer (1), cabinet (1-13), garbagecan (1). I can check one by one, starting with fridge 1.
        Observation 2: OK.
        Action 3: go to fridge 1
        Observation 3: The fridge 1 is closed.
        Action 4: open fridge 1
        Observation 4: You open the fridge 1. The fridge 1 is open. In it, you see a cup 1, and a egg 1.
        Action 5: go to diningtable 1
        Observation 5: On the diningtable 1, you see a apple 1, a bread 1, a fork 3, a fork 2, a fork 1, a mug 2, a peppershaker 3, a plate 2, a pot 1, a soapbottle 3, a spatula 1, a spoon 3, a spoon 2, a spoon 1, a winebottle 3, and a winebottle 2.
        Action 6: think: Now I find an apple (1). Next, I need to take it.
        Observation 6: OK.
        Action 7: take apple 1 from diningtable 1
        Observation 7: You pick up the apple 1 from the diningtable 1.
        Action 8: think: Now I take an apple (1). Next, I need to go to a microwave (1) and heat it.
        Observation 8: OK.
        Action 9: go to microwave 1
        Observation 9: The microwave 1 is closed.
        Action 10: heat apple 1 with microwave 1
        Observation 10: You heat the apple 1 using the microwave 1.
        Action 11: think: Now I heat an apple (1). Next, I need to put it in/on fridge 1.
        Observation 11: OK.
        Action 12: go to fridge 1
        Observation 12: The fridge 1 is open. In it, you see a cup 1, and a egg 1.
        Action 13: put apple 1 in/on fridge 1
        Observation 13:You put the apple 1 in/on the fridge 1.
    """, 
    "react_cool_0": """
        You are in the middle of a room. Looking quickly around you, you see a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 2, a countertop 1, a diningtable 1, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a safe 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.
        Your task is to: cool some pan and put it in stoveburner.
        Action 1: think: To solve the task, I need to find and take a pan, then cool it with fridge, then put it in stoveburner.
        Observation 1: OK.
        Action 2: think: First I need to find a pan. An pan is more likely to appear in stoveburner (1-4), sinkbasin (1), diningtable (1), countertop (1-2), cabinet (1-16), drawer (1-5). I can check one by one, starting with stoveburner 1.
        Observation 2: OK.
        Action 3: go to stoveburner 1
        Observation 3: On the stoveburner 1, you see nothing.
        Action 4: go to stoveburner 2
        Observation 4: On the stoveburner 2, you see a pot 1.
        Action 5: go to stoveburner 3
        Observation 5: On the stoveburner 3, you see a pan 1.
        Action 6: take pan 1 from stoveburner 3 \n>think: Now I find a pan (1). Next, I need to take it.
        Observation 6: OK.\nYou pick up the pan 1 from the stoveburner 3.
        Action 7: think: Now I take a pan (1). Next, I need to go to a fridge (1) and cool it.
        Observation 7: OK.
        Action 8: go to fridge 1
        Observation 8: The fridge 1 is closed.
        Action 9: cool pan 1 with fridge 1
        Observation 9: You cool the pan 1 using the fridge 1.
        Action 10: think: Now I cool a pan (1). Next, I need to put it in/on stoveburner 1.
        Observation 10: OK.
        Action 11: go to stoveburner 1
        Observation 11: On the stoveburner 1, you see nothing.
        Action 12: put pan 1 in/on stoveburner 1
        Observation 12: You put the pan 1 in/on the stoveburner 1.
    """, 
    "react_cool_1": """
        You are in the middle of a room. Looking quickly around you, you see a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 3, a countertop 2, a countertop 1, a drawer 9, a drawer 8, a drawer 7, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a shelf 3, a shelf 2, a shelf 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.
        Your task is to: put a cool mug in shelf.
        Action 1: think: To solve the task, I need to find and take a mug, then cool it with fridge, then put it in shelf.
        Observation 1: OK.
        Action 2: think: First I need to find a mug. A mug is more likely to appear in countertop (1-3), coffeemachine (1), cabinet (1-9), shelf (1-3), drawer (1-9). I can check one by one, starting with countertop 1.
        Observation 2: OK.
        Action 3: go to countertop 1
        Observation 3: On the countertop 1, you see a knife 1, a pan 2, a pan 1, and a plate 1.
        Action 4: go to countertop 2
        Observation 4: On the countertop 2, you see a apple 2, a butterknife 2, a fork 3, a houseplant 1, a knife 2, a lettuce 3, a spatula 1, and a winebottle 1.
        Action 5: go to countertop 3
        Observation 5: On the countertop 3, you see a apple 1, a book 1, a bread 1, a butterknife 3, a glassbottle 2, a glassbottle 1, a knife 3, a lettuce 2, a lettuce 1, a papertowelroll 1, a plate 3, a spoon 1, a statue 1, and a vase 2.
        Action 6: go to coffeemachine 1
        Observation 6: On the coffeemachine 1, you see nothing.
        Action 7: go to cabinet 1
        Observation 7: The cabinet 1 is closed.
        Action 8: open cabinet 1
        Observation 8: You open the cabinet 1. The cabinet 1 is open. In it, you see nothing.
        Action 9: go to cabinet 2
        Observation 9: The cabinet 2 is closed.
        Action 10: open cabinet 2
        Observation 10: You open the cabinet 2. The cabinet 2 is open. In it, you see nothing.
        Action 11: go to cabinet 3
        Observation 11: The cabinet 3 is closed.
        Action 12: open cabinet 3
        Observation 12: You open the cabinet 3. The cabinet 3 is open. In it, you see a pot 1.
        Action 13: go to cabinet 4
        Observation 13: On the cabinet 4, you see nothing.
        Action 14: go to cabinet 5
        Observation 14: The cabinet 5 is closed.
        Action 15: open cabinet 5
        Observation 15: You open the cabinet 5. The cabinet 5 is open. In it, you see nothing.
        Action 16: go to cabinet 6
        Observation 16: The cabinet 6 is closed.
        Action 17: open cabinet 6
        Observation 17: You open the cabinet 6. The cabinet 6 is open. In it, you see a mug 3.
        Action 18: think: Now I find a mug (3). Next, I need to take it.
        Observation 18: OK.
        Action 19: take mug 3 from cabinet 6
        Observation 19: You pick up the mug 3 from the cabinet 6.
        Action 20: think: Now I take a mug (3). Next, I need to go to a fridge (1) and cool it.
        Observation 20: OK.
        Action 21: go to fridge 1
        Observation 21: The fridge 1 is closed.
        Action 22: cool mug 3 with fridge 1
        Observation 22: You cool the mug 3 using the fridge 1.
        Action 23: think: Now I cool the mug. Next, I need to put it in/on shelf 1.
        Observation 23: OK.
        Action 24: go to shelf 1
        Observation 24: On the shelf 1, you see a cup 2, a cup 1, a peppershaker 1, and a saltshaker 1.
        Action 25: put mug 3 in/on shelf 1
        Observation 25: You put the mug 3 in/on the shelf 1.
    """,  "react_puttwo_0": """
        You are in the middle of a room. Looking quickly around you, you see a armchair 2, a armchair 1, a bed 1, a countertop 1, a diningtable 1, a drawer 2, a drawer 1, a dresser 1, a garbagecan 1, a laundryhamper 1, and a sidetable 1.
        Your task is to: put two creditcard in dresser.
        Action 1: think: To solve the task, I need to find and take the first creditcard, then put it in dresser, then find and take the second creditcard, then put it in dresser.
        Observation 1: OK.
        Action 2: think: First I need to find the first creditcard. A creditcard is more likely to appear in drawer (1-2), coutertop (1), sidetable (1), diningtable (1), armchair (1-2), bed (1). I can check one by one, starting with drawer 1.
        Observation 2: OK.
        Action 3: go to drawer 1
        Observation 3: The drawer 1 is closed.
        Action 4: open drawer 1
        Observation 4: You open the drawer 1. The drawer 1 is open. In it, you see a book 1, a cd 1, and a pen 1.
        Action 5: go to drawer 2
        Observation 5: The drawer 2 is closed.
        Action 6: open drawer 2
        Observation 6: You open the drawer 2. The drawer 2 is open. In it, you see nothing.
        Action 7: go to countertop 1
        Observation 7: On the countertop 1, you see a cellphone 2, a creditcard 4, a creditcard 3, a creditcard 2, a mirror 1, a pencil 2, and a pencil 1.
        Action 8: think: Now I find the first creditcard (2). Next, I need to take it. I can find the second creditcard (3) later in countertop 1.
        Observation 8: OK.
        Action 9: take creditcard 2 from countertop 1
        Observation 9: You pick up the creditcard 2 from the countertop 1.
        Action 10: think: Now I take the first creditcard (2). Next, I need to put it in/on dresser 1.
        Observation 10: OK.
        Action 11: go to dresser 1
        Observation 11: On the dresser 1, you see a mug 1, and a television 1.
        Action 12: put creditcard 2 in/on dresser 1
        Observation 12: You put the creditcard 2 in/on the dresser 1.
        Action 13: think: Now I put the first creditcard in dresser. Next, I need to find the second creditcard. I can directly go to countertop 1.
        Observation 13: OK.
        Action 14: go to countertop 1
        Observation 14: On the countertop 1, you see a cellphone 2, a creditcard 4, a creditcard 3, a mirror 1, a pencil 2, and a pencil 1.
        Action 15: think: Now I find the second creditcard (3). Next, I need to take it.
        Observation 15: OK.
        Action 16: take creditcard 3 from countertop 1
        Observation 16: You pick up the creditcard 3 from the countertop 1.
        Action 17: think: Now I take the second creditcard (3). Next, I need to put it in/on dresser 1.
        Observation 17: OK.
        Action 18: go to dresser 1
        Observation 18: On the dresser 1, you see a creditcard 2, a mug 1, and a television 1.
        Action 19: put creditcard 3 in/on dresser 1
        Observation 19: You put the creditcard 3 in/on the dresser 1.
    """, 
    "react_puttwo_1": """
        You are in the middle of a room. Looking quickly around you, you see a coffeetable 1, a diningtable 1, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a dresser 1, a garbagecan 1, a sidetable 2, a sidetable 1, and a sofa 1.
        Your task is to: put two cellphone in sofa.
        Action 1: think: To solve the task, I need to find and take the first cellphone, then put it in sofa, then find and take the second cellphone, then put it in sofa.
        Observation 1: OK.
        Action 2: think: First I need to find the first cellphone. A cellphone is more likely to appear in coffeetable (1), diningtable (1), sidetable (1-2), drawer (1-4), sofa (1), dresser (1), garbagecan (1). I can check one by one, starting with coffeetable 1.
        Observation 2: OK.
        Action 3: go to coffeetable 1
        Observation 3: On the coffeetable 1, you see a box 1, a cellphone 3, and a plate 1.
        Action 4: take cellphone 3 from coffeetable 1
        Observation 4: You pick up the cellphone 3 from the coffeetable 1.
        Action 5: think: Now I find the first cellphone (3). Next, I need to put it in/on sofa 1.
        Observation 5: OK.
        Action 6: go to sofa 1
        Observation 6: On the sofa 1, you see a newspaper 2, a pillow 1, a remotecontrol 2, and a remotecontrol 1.
        Action 7: put cellphone 3 in/on sofa 1
        Observation 7: You put the cellphone 3 in/on the sofa 1.
        Action 8: think: Now I put the first cellphone in sofa. Next, I need to find the second cellphone. I have visited coffeetable (1), so the second cellphone is more likely to appear in diningtable (1), sidetable (1-2), drawer (1-4), sofa (1), dresser (1), garbagecan (1). I can check one by one, starting with coffeetable 1.
        Observation 8: OK.
        Action 9: go to diningtable 1
        Observation 9: On the diningtable 1, you see a cellphone 2, a keychain 2, a laptop 1, a statue 2, and a statue 1.
        Action 10: think: Now I find the second cellphone (2). Next, I need to take it.
        Observation 10: OK.
        Action 11: take cellphone 2 from diningtable 1
        Observation 11: You pick up the cellphone 2 from the diningtable 1.
        Action 12: think: Now I take the second cellphone (2). Next, I need to put it in/on sofa 1.
        Observation 12: OK.
        Action 13: go to sofa 1
        Observation 13: On the sofa 1, you see a cellphone 3, a newspaper 2, a pillow 1, a remotecontrol 2, and a remotecontrol 1.
        Action 14: put cellphone 2 in/on sofa 1
        Observation 14: You put the cellphone 2 in/on the sofa 1.
    """,  
    "react_examine_0": """
        You are in the middle of a room. Looking quickly around you, you see a bed 1, a desk 1, a drawer 3, a drawer 2, a drawer 1, a garbagecan 1, a safe 1, a shelf 5, a shelf 4, a shelf 3, a shelf 2, a shelf 1, a sidetable 2, and a sidetable 1.
        Your task is to: look at bowl under the desklamp.
        Action 1: think: To solve the task, I need to find and take a bowl, then find and use a desklamp. 
        Observation 1: OK. 
        Action 2: think: First I need to find a bowl. A bowl is more likely to appear in drawer (1-3), desk (1), sidetable (1-2), shelf (1-5), garbagecan (1). I can check one by one, starting with drawer 1.
        Observation 2: OK.
        Action 3: go to drawer 1
        Observation 3: On the drawer 1, you see nothing.
        Action 4: go to drawer 2
        Observation 4: The drawer 2 is closed.
        Action 5: open drawer 2
        Observation 5: You open the drawer 2. The drawer 2 is open. In it, you see nothing.
        Action 6: go to drawer 3
        Observation 6: The drawer 3 is closed.
        Action 7: open drawer 3
        Observation 7: You open the drawer 3. The drawer 3 is open. In it, you see nothing.
        Action 8: go to desk 1
        Observation 8: On the desk 1, you see a alarmclock 2, a book 1, a cellphone 1, a keychain 1, a laptop 2, a laptop 1, and a pen 3.
        Action 9: go to sidetable 1
        Observation 9: On the sidetable 1, you see a cd 1, a pen 1, and a pencil 1.
        Action 10: go to shelf 1
        Observation 10: On the shelf 1, you see nothing.
        Action 11: go to shelf 2
        Observation 11: On the shelf 2, you see a bowl 1.
        Action 12: think: Now I find a bowl (1). Next, I need to take it.
        Observation 12: OK.
        Action 13: take bowl 1 from shelf 2
        Observation 13: You pick up the bowl 1 from the shelf 2.
        Action 14: think: Now I take a bowl (1). Next, I need to find a desklamp. A desklamp is more likely to appear in desk (1), sidetable (1-2), shelf (1-5), bed (1), drawer (1-3). I can check one by one, starting with desk 1.
        Observation 14: OK.
        Action 15: go to desk 1
        Observation 15: On the desk 1, you see a alarmclock 2, a book 1, a cellphone 1, a keychain 1, a laptop 2, a laptop 1, and a pen 3.
        Action 16: go to sidetable 1
        Observation 16: On the sidetable 1, you see a cd 1, a pen 1, and a pencil 1.
        Action 17: go to sidetable 2
        Observation 17: On the sidetable 2, you see a alarmclock 1, a desklamp 1, and a pen 2.
        Action 18: think: Now I find a desklamp (1). Next, I need to use it.
        Observation 18: OK.
        Action 19: use desklamp 1
        Observation 19: You turn on the desklamp 1.
    """, 
    "react_examine_1": """
        You are in the middle of a room. Looking quickly around you, you see a bed 1, a drawer 10, a drawer 9, a drawer 8, a drawer 7, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a dresser 1, a garbagecan 1, a shelf 9, a shelf 8, a shelf 7, a shelf 6, a shelf 5, a shelf 4, a shelf 3, a shelf 2, and a shelf 1.
        Your task is to: examine the pen with the desklamp.
        Action 1: think: To solve the task, I need to find and take a pen, then find and use a desklamp. First I need to find a pen. A pen is more likely to appear in drawer (1-10), shelf (1-9), bed (1), garbagecan (1). I can check one by one, starting with drawer 1.
        Observation 1: OK.
        Action 2: go to drawer 1
        Observation 2: The drawer 1 is closed.
        Action 3: open drawer 1
        Observation 3: You open the drawer 1. The drawer 1 is open. In it, you see nothing.
        Action 4: go to drawer 2
        Observation 4: The drawer 2 is closed.
        Action 5: open drawer 2
        Observation 5: You open the drawer 2. The drawer 2 is open. In it, you see nothing.
        Action 6: go to drawer 3
        Observation 6: The drawer 3 is closed.
        Action 7: open drawer 3
        Observation 7: You open the drawer 3. The drawer 3 is open. In it, you see nothing.
        Action 8: go to drawer 4
        Observation 8: The drawer 4 is closed.
        Action 9: open drawer 4
        Observation 9: You open the drawer 4. The drawer 4 is open. In it, you see a cd 3, a keychain 1, and a pen 2.
        Action 10: think: Now I find a pen (2). Next, I need to take it.
        Observation 10: OK.
        Action 11: take pen 2 from drawer 4
        Observation 11: You pick up the pen 2 from the drawer 4.
        Action 12: think: Now I take a pen (2). Next, I need to find a desklamp. A desklamp is more likely to appear in dresser (1), shelf (1-9), bed (1), garbagecan (1), drawer (1-10). I can check one by one, starting with dresser 1.
        Observation 12: OK.
        Action 13: go to dresser 1
        Observation 13: On the dresser 1, you see a alarmclock 2, a alarmclock 1, a book 1, a cd 1, a creditcard 1, a desklamp 1, a keychain 2, a pen 3, and a pen 1.
        Action 14: think: Now I find a desklamp (1). Next, I need to use it.
        Observation 14: OK.
        Action 15: use desklamp 1
        Observation 15: You turn on the desklamp 1.
    """
}