import os
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key="sk-XXXX")

response = llm.invoke(f"""You are prompt corrector which make sure it elaborates the prompt so it searches for case. Give only this prompt corrected prompt for the table query below:
#Prompt
{prompt}
#Table
{table}
Return only the corrected prompt so it handles edge cases""")

print(response.content)
