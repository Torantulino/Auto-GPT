from __future__ import annotations
import os
import time
from typing import List

import openai
import requests

from autogpt.config import Config
from autogpt.logs import logger
from autogpt.modelsinfo import COSTS

cfg = Config()
print_total_cost = cfg.debug_mode
session = requests.Session()


class ApiManager:
    def __init__(self, debug=False):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0
        self.total_budget = 0
        self.debug = debug

    def reset(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0
        self.total_budget = 0.0

    def create_chat_completion(
        self,
        messages: list,  # type: ignore
        model: str | None = None,
        temperature: float = cfg.temperature,
        max_tokens: int | None = None,
        deployment_id=None,
    ) -> str:
        """
        Create a chat completion and update the cost.
        Args:
        messages (list): The list of messages to send to the API.
        model (str): The model to use for the API call.
        temperature (float): The temperature to use for the API call.
        max_tokens (int): The maximum number of tokens for the API call.
        Returns:
        str: The AI's response.
        """
        if os.environ.get("USE_HUGGINGFACE", "False") != "False":
            convo_id = get_convo_id()
            time.sleep(1)
            return (
                generate_output(
                    "\n".join(
                        f'{message["role"]}: {message["message"]}'
                        for message in messages
                    ),
                    convo_id,
                )[0]["generated_text"]
                .split("<|assistant|>")[1]
                .strip()
            )

        if deployment_id is not None:
            response = openai.ChatCompletion.create(
                deployment_id=deployment_id,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=cfg.openai_api_key,
            )
        else:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=cfg.openai_api_key,
            )
        if self.debug:
            logger.debug(f"Response: {response}")
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        self.update_cost(prompt_tokens, completion_tokens, model)
        return response

    def update_cost(self, prompt_tokens, completion_tokens, model):
        """
        Update the total cost, prompt tokens, and completion tokens.

        Args:
        prompt_tokens (int): The number of tokens used in the prompt.
        completion_tokens (int): The number of tokens used in the completion.
        model (str): The model used for the API call.
        """
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_cost += (
            prompt_tokens * COSTS[model]["prompt"]
            + completion_tokens * COSTS[model]["completion"]
        ) / 1000
        if print_total_cost:
            print(f"Total running cost: ${self.total_cost:.3f}")

    def set_total_budget(self, total_budget):
        """
        Sets the total user-defined budget for API calls.

        Args:
        prompt_tokens (int): The number of tokens used in the prompt.
        """
        self.total_budget = total_budget

    def get_total_prompt_tokens(self):
        """
        Get the total number of prompt tokens.

        Returns:
        int: The total number of prompt tokens.
        """
        return self.total_prompt_tokens

    def get_total_completion_tokens(self):
        """
        Get the total number of completion tokens.

        Returns:
        int: The total number of completion tokens.
        """
        return self.total_completion_tokens

    def get_total_cost(self):
        """
        Get the total cost of API calls.

        Returns:
        float: The total cost of API calls.
        """
        return self.total_cost

    def get_total_budget(self):
        """
        Get the total user-defined budget for API calls.

        Returns:
        float: The total budget for API calls.
        """
        return self.total_budget


api_manager = ApiManager(cfg.debug_mode)


def get_convo_id():
    resp = session.post(
        "https://huggingface.co/chat/conversation",
        headers={"content-type": "application/json", "accept": "application/json"},
    )
    return resp.json()["conversationId"]


def generate_output(prompt, conversation_id):
    resp = session.post(
        f"https://huggingface.co/chat/conversation/{conversation_id}",
        headers={
            "content-type": "application/json",
            "accept": "application/json",
            "referrer": f"https://huggingface.co/chat/conversation/{conversation_id}",
        },
        json={
            "inputs": prompt,
            "options": {
                "use_cache": False,
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.9,
                    "top_p": 0.95,
                    "top_k": 50,
                    "repetition_penalty": 1.2,
                    "return_full_text": False,
                    "stop": ["<|endoftext|>"],
                    "truncate": 1024,
                    "watermark": False,
                },
            },
            "stream": False,
        },
    )
    return resp.json()
