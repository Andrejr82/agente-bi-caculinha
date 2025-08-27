from typing import List, Dict, Any, Optional
import logging
import threading
from queue import Queue
from core.llm_base import BaseLLMAdapter
from core.config.config import Config
from openai import OpenAI, APITimeoutError, APIConnectionError, RateLimitError

class OpenAILLMAdapter(BaseLLMAdapter):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(
            api_key=Config().OPENAI_API_KEY,
            timeout=30.0,  # Adiciona um timeout de 30 segundos
        )

    def get_completion(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        q = Queue()

        def worker():
            try:
                # Prepare arguments for the API call
                api_args = {
                    "model": Config().LLM_MODEL_NAME,
                    "messages": messages,
                    "temperature": 0, # Set temperature to 0 for more deterministic output
                    # "seed": 42, # Uncomment and set a fixed seed for even more reproducibility if supported by the model
                }
                if tools:
                    api_args["tools"] = tools
                    api_args["tool_choice"] = "auto" # Let the model decide whether to call a tool

                self.logger.info("Making OpenAI API call...")
                response = self.client.chat.completions.create(**api_args)
                self.logger.info("OpenAI API call finished.")

                # Extract message content
                message_content = response.choices[0].message.content
                tool_calls = response.choices[0].message.tool_calls

                result = {"content": message_content}
                if tool_calls:
                    result["tool_calls"] = tool_calls
                
                q.put(result)

            except APITimeoutError as e:
                self.logger.error(f"OpenAI API call timed out: {e}")
                q.put({"error": f"Error getting completion from OpenAI: Request timed out - {e}"})
            except APIConnectionError as e:
                self.logger.error(f"OpenAI API connection error: {e}")
                q.put({"error": f"Error getting completion from OpenAI: Connection error - {e}"})
            except RateLimitError as e:
                self.logger.error(f"OpenAI API rate limit exceeded: {e}")
                q.put({"error": f"Error getting completion from OpenAI: Rate limit exceeded - {e}"})
            except Exception as e:
                self.logger.error(f"An unexpected error occurred during OpenAI API call: {e}", exc_info=True)
                q.put({"error": f"An unexpected error occurred while getting completion from OpenAI: {e}"})

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=60.0)

        if thread.is_alive():
            self.logger.error("OpenAI API call timed out after 60 seconds.")
            return {"error": "Error getting completion from OpenAI: Request timed out"}
        else:
            return q.get()
