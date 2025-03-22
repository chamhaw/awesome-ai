import unittest

import app.prompt.user_prompts
from app.agent.rag import retrieve_knowledge_from_rag, retrieve_knowledge_from_local


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here
    def test_from_rag(self):
        retrieve_knowledge_from_rag(app.prompt.user_prompts.user_prompt_demo1)

    def test_from_local(self):
        knowledge = retrieve_knowledge_from_local("../../knowledge")
        print(knowledge)

if __name__ == '__main__':
    unittest.main()
