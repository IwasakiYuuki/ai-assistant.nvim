from rplugin.python3.ai_assistant.request_chatgpt import RequestChatGPT


class TestRequestChatGPT:
    async def test_chat_completions(self):
        content, tokens = await RequestChatGPT.chat_completions(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who won the world series in 2020?"},
                {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
                {"role": "user", "content": "Where was it played?"}
            ],
            request_timeout=15,
        )
        assert isinstance(content, str)
        assert isinstance(tokens, int)
