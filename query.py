import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent


def query(csv_path="organizations-10000.csv"):
    # Load CSV
    df = pd.read_csv(csv_path)

    # LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    # Create agent
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        allow_dangerous_code=True,
        agent_type="openai-tools",
        max_iterations=2
    )

    cleaning_prompt = """
    Analyze the dataframe and fix schema issues:
    - Convert numeric columns stored as strings to numbers
    - Convert date-like columns to datetime
    - Convert yes/no or true/false columns to boolean
    - Strip commas, currency symbols, and whitespace from numeric fields 
    - Keep changes in-place on the dataframe
    - Print a brief summary of what was changed
    - Save the COMPLETE file as {cleaned.csv}
    """

    agent.invoke(cleaning_prompt)

    # ---- STEP 2: Ask actual question on cleaned data ----
    return


answer = query(
    csv_path="organizations-10000.csv"
)

print(answer)
