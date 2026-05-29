from dotenv import load_dotenv
import os
from openai import OpenAI
from google import genai
import json

class AIClient:
    apikey: str 

    def __init__(self, env_var_name):
        try:
            print('inside the AI Client env_var_name ', env_var_name)
            #load_dotenv() --> used for loading the local env
            #self.ApiKey
            # render server 
            
            self.ApiKey = os.getenv(env_var_name)
        except Exception as e:
            print(f"Error during initialization: {e}")

    @property
    def ApiKey(self):
        return self.apikey
    
    @ApiKey.setter
    def ApiKey(self, value):
        self.apikey = os.getenv(value)
        if self.apikey is None:
            # Fixed: raising a ValueError instead of just a string
            raise ValueError(f"Environment variable {value} not found. Please assign the value.")
        
    def openAiConnect(self):
        try:
            client = OpenAI(api_key=self.apikey)
            response = client.responses.create(
                model="gpt-5.5",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "What teams are playing in this image?",
                            },
                            {
                                "type": "input_image",
                                "image_url": "https://api.nga.gov/iiif/a2e6da57-3cd1-4235-b20e-95dcaefed6c8/full/!800,800/0/default.jpg"
                            }
                        ]
                    }
                ]
            )
            print(response)
        except Exception as e:
            print(f"OpenAI Connection Error: {e}")
        
    def gemeniAiConnect(self, prompt):
        try:
            client = genai.Client(api_key=self.ApiKey)
            
            if not prompt:
                print("Prompt is empty. Please provide a valid prompt.")
                return None
            
            response = client.models.generate_content(
                    model= 'gemini-2.0-flash',#"gemini-3-flash-preview",
                    contents=prompt,  # Keep your text prompt simple here
                    config= self.fetchGeminiRequest()
                )

            print('response.text******************', response.text)
            
            if response.text:
                res = json.loads(response.text)
                print('res******************', type(res))
                return res
                
        except json.JSONDecodeError as je:
            print(f"JSON Parsing Error: {je}")
        except Exception as e:
            print(f"Gemini Connection Error: {e}")
        
        return None
    
    def fetchGeminiRequest(self):
        return {
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "OBJECT",
                    "properties": {
                        "topic": {
                            "type": "STRING"
                        },
                        "summary": {
                            "type": "STRING"
                        },
                        "sections": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "heading": {
                                        "type": "STRING"
                                    },
                                    "content": {
                                        "type": "ARRAY",
                                        "items": {
                                            "type": "STRING"
                                        }
                                    }
                                },
                                "required": ["heading", "content"]
                            }
                        },
                        "best_practices": {
                            "type": "ARRAY",
                            "items": {
                                "type": "STRING"
                            }
                        },
                        "limitations": {
                            "type": "ARRAY",
                            "items": {
                                "type": "STRING"
                            }
                        },
                        "example": {
                            "type": "STRING"
                        },
                        "flow_diagram": {
                            "type": "OBJECT",
                            "properties": {
                                "type": {
                                    "type": "STRING",
                                    "description": "Diagram style such as Mind Map, Flowchart, or Architecture Diagram"
                                },
                                "representation": {
                                    "type": "STRING",
                                    "description": "Structured text-based flow diagram using arrows, hierarchy, and indentation"
                                }
                            },
                            "required": ["type", "representation"]
                        }
                    },
                    "required": [
                        "topic",
                        "summary",
                        "sections",
                        "best_practices",
                        "limitations",
                        "example",
                        "flow_diagram"
                    ]
                }
            }
        
    def gemeniAiTokenCount(self):
        try:
            client = genai.Client(api_key=self.ApiKey)
            tokens = client.models.count_tokens(model='gemini-3-flash-preview', contents="Hello world")
            print(f"Cost: {tokens.total_tokens} tokens")
        except Exception as e:
            print(f"Error counting tokens: {e}")