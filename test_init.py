import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import os

# Dummy data
df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

# Dummy key for initialization check (won't actually call OpenAI)
os.environ["OPENAI_API_KEY"] = "sk-dummy"

try:
    llm = ChatOpenAI(model="gpt-4o-mini")
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        allow_dangerous_code=True,
        handle_parsing_errors=True,
        max_iterations=5,
        # help: verify if passing as direct arg works or if default is fine
        # return_intermediate_steps=False 
    )
    print("Agent created successfully!")
except Exception as e:
    print(f"Error: {e}")
