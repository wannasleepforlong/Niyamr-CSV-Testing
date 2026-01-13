import streamlit as st
import pandas as pd
import os
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from io import StringIO
import sys
from prompt_corrector import correct_prompt

st.title("NIYAMR CHAT APP (+preprompt)")
st.write("Upload your CSV & ask anything")

openai_key = st.text_input(
    "Enter your OpenAI API Key",
    type="password",
    help="Your key is not stored"
)

if openai_key:
    # os.environ["OPENAI_API_KEY"] = openai_key

    file = st.file_uploader("Select your file", type=["csv"])
    if file is not None:
        df = pd.read_csv(file)

        st.write("### Data Preview")
        st.dataframe(df.head())

        question = st.text_area("Ask your question here")
        
        preprompt_on = st.toggle("Preprompt", value=False)

        if st.button("Submit") and question:
            with st.spinner("Processing your question..."):
                try:
                    current_question = question
                    if preprompt_on:
                        with st.status("Correcting prompt...", expanded=False) as status:
                            table_head = df.head(5).to_string()
                            current_question = correct_prompt(question, table_head, openai_key)
                            st.write(f"**Original:** {question}")
                            st.write(f"**Corrected:** {current_question}")
                            status.update(label="Prompt corrected!", state="complete", expanded=False)
                    
                    llm = ChatOpenAI(
                        model="gpt-4o-mini",
                        temperature=0,
                        openai_api_key=openai_key
                    )
                    
                    agent = create_pandas_dataframe_agent(
                        llm,
                        df,
                        verbose=True,
                        allow_dangerous_code=True,
                        agent_type="openai-tools",
                        max_iterations=2,
                        return_intermediate_steps=True
                    )
                    
                    # Get the full response with intermediate steps
                    result = agent.invoke({"input": current_question})
                    
                    st.success("### Answer:")
                    st.write(result["output"])
                    
                    # Show intermediate steps (the actual code execution and results)
                    if "intermediate_steps" in result and result["intermediate_steps"]:
                        with st.expander("🔍 View Detailed Execution Steps", expanded=False):
                            for i, (action, observation) in enumerate(result["intermediate_steps"]):
                                st.markdown(f"**Step {i+1}:**")
                                
                                # Show the action/code executed
                                if hasattr(action, 'tool_input'):
                                    st.code(action.tool_input, language="python")
                                
                                # Show the observation/result
                                st.markdown("**Result:**")
                                
                                # Check if observation is a dataframe or can be converted to one
                                try:
                                    if isinstance(observation, pd.DataFrame):
                                        st.dataframe(observation)
                                    elif isinstance(observation, str) and observation.strip():
                                        # Try to display as dataframe if it looks like tabular data
                                        try:
                                            temp_df = pd.read_csv(StringIO(observation))
                                            st.dataframe(temp_df)
                                        except:
                                            st.text(observation)
                                    else:
                                        st.write(observation)
                                except:
                                    st.write(observation)
                                
                                st.divider()
                    
                    # # Additionally, check if the result itself contains a dataframe
                    # with st.expander("📊 Complete Output Data", expanded=True):
                    #     output_text = result["output"]
                        
                    #     # Try to extract and display any dataframes mentioned
                    #     if "dataframe" in output_text.lower() or "df" in output_text.lower():
                    #         st.info("The response references dataframe operations. Check the execution steps above for detailed results.")
                        
                    #     # Try to evaluate if the output is describing a dataframe result
                    #     st.markdown("**Full Response:**")
                    #     st.write(output_text)

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Try rephrasing your question or check column names.")
                    
                    with st.expander("Debug Information"):
                        import traceback
                        st.code(traceback.format_exc())
else:
    st.warning("Please enter your OpenAI API key to continue.")