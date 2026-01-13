from langchain_openai import ChatOpenAI

def correct_prompt(prompt, table_head, api_key):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=api_key
    )

    system_prompt = f"""You are a prompt corrector which makes sure it elaborates the prompt so it searches for cases. 
Give only this corrected prompt for the table query below.
Return only the corrected prompt so it handles edge cases and is more detailed for a pandas agent to understand.

#Prompt
{prompt}

#Table Preview (First 5 rows)
{table_head}
"""
    response = llm.invoke(system_prompt)
    return response.content.strip()
