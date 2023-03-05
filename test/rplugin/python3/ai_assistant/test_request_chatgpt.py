from openai.openai_object import OpenAIObject
from rplugin.python3.ai_assistant.request_chatgpt import RequestChatGPT


class TestRequestChatGPT:
    def test_chat_completions(self):
        res = RequestChatGPT.chat_completions(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who won the world series in 2020?"},
                {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
                {"role": "user", "content": "Where was it played?"}
            ]
        )
        assert isinstance(res, OpenAIObject)
        assert "choices" in res
        assert len(res["choices"]) >= 1
        assert "finish_reason" in res["choices"][0]
        assert res["choices"][0]["finish_reason"] == "stop"

    def test_generate_code(self):
        res = RequestChatGPT.generate_code(
            instruction="Write a fizzbuzz function in Python."
        )
        assert isinstance(res, str)
        assert res != ""
