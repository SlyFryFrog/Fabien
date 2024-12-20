import json
import ollama
from ollama import ChatResponse
from src.constants import MEMORY_DIR, MODELS


class FabienAI:
    def __init__(self):
        self.guild_memory: dict[str, list[dict[str, str]]] = {}
        self.model: str = MODELS[0]

    def get_response(self, user_name: str, user_id: str, message: str) -> str:
        system_prompt: dict[str, str] = {
            "role": "system",
            "content": 
                "You are a frog named Fabien from a far away magical land."
                "You are a helpful ai, but when prompted to and messaged in a rude manner, roast people."
                "Keep your responses short, to the point. Make jokes that a human would make when prompted - do not be cringe."
                "You are here to entertain and act as a general-purpose ai."
                f"Be polite unless otherwise initiated by {user_name}."
                f"Respond to {user_name} in English unless directly spoken to in French."
        }

        # Adjust memory context window and add user message
        memory: list[dict[str, str]] = self.guild_memory.get(user_id, [])
        memory.append({"role": "user", "content": message})
        memory = [system_prompt] + memory[-100:]

        ollama_response: ChatResponse = ollama.chat(model=self.model, messages=memory)

        # Remove system prompt from chat history
        index: int = memory.index(system_prompt)
        memory.pop(index)

        assistant_response: str = ollama_response["message"]["content"]
        assistant_response = assistant_response.replace("<|start_header_id|>assistant<|end_header_id|>\n", "")
        print(assistant_response)
        memory.append({"role": "assistant", "content": assistant_response})

        self.guild_memory[user_id] = memory

        return assistant_response
    
    def save_memory(self):
        with open(f"{MEMORY_DIR}guild_memory.json", "w") as file:
            json.dump(self.guild_memory, file, indent=4)
    
    def load_memory(self):
        with open(f"{MEMORY_DIR}guild_memory.json", "r") as file:
            self.guild_memory = json.load(file)
    
    def clear_user_memory(self, user_id: str) -> None:
        self.guild_memory[user_id] = []