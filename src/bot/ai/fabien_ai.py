import json
import ollama
from src.constants import MEMORY_DIR, MODELS


class FabienAI:
    def __init__(self):
        self.guild_memory: dict[str, list[dict[str, str]]] = {}
        self.model: str = MODELS[0]

    async def get_response(self, user_name: str, guild_id: str, message: str):
        with open("rsc/memory/prompt.json", "r") as file:
            system_prompt: dict[str, str] = json.load(file)

        # Adjust memory context window and add user message
        memory: list[dict[str, str]] = self.guild_memory.get(guild_id, [])
        memory.append({"role": "user", "content": f"You're speaking with {user_name}. They said '{message}'"})
        memory = [system_prompt] + memory[-100:]

        # Stream the response (sync to async wrapper)
        def stream_response():
            return ollama.chat(model=self.model, messages=memory, stream=True)
        
        assistant_response: dict[str, str] = {"role": "assistant", "content": ""}

        for chunk in stream_response():
            assistant_response["content"] += chunk.message.content
            yield chunk.message.content  # Convert sync generator to async

        # Remove system prompt from chat history
        memory = memory[1:]  # Remove system prompt (always first)

        # Append the final assistant response to memory
        memory.append(assistant_response)
        self.guild_memory[guild_id] = memory

    def get_whole_response(self, user_name: str, guild_id: str, message: str):
        with open("rsc/memory/prompt.json", "r") as file:
            system_prompt: dict[str, str] = json.load(file)

        # Adjust memory context window and add user message
        memory: list[dict[str, str]] = self.guild_memory.get(guild_id, [])
        memory.append({"role": "user", "content": f"You're speaking with {user_name}. They said '{message}'"})
        memory = [system_prompt] + memory[-100:]

        ollama_response = ollama.chat(model=self.model, messages=memory)
        
        assistant_response: dict[str, str] = {"role": "assistant", "content": ollama_response["message"]["content"]}

        # Remove system prompt from chat history
        memory = memory[1:]  # Remove system prompt (always first)

        # Append the final assistant response to memory
        memory.append(assistant_response)
        self.guild_memory[guild_id] = memory

        return ollama_response["message"]["content"]

    async def save_memory(self):
        with open(f"{MEMORY_DIR}guild_memory.json", "w") as file:
            json.dump(self.guild_memory, file, indent=4)

    def load_memory(self):
        with open(f"{MEMORY_DIR}guild_memory.json", "r") as file:
            self.guild_memory = json.load(file)

    def clear_memory(self, id: str) -> None:
        self.guild_memory[id] = []
    