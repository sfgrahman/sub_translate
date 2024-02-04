from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)

from langchain_openai import ChatOpenAI
import srt
import os
import streamlit as st
from io import StringIO
import time
import base64

from dotenv import load_dotenv
load_dotenv(override=True)
# DIR = "tempDir/"
def srtFileProcess(fileData):
    subs = list(srt.parse(fileData))
    return subs


def get_translated_filename(filepath,LANG, ln=None):
    timestr = time.strftime("%Y%m%d_%H%M%S")
    root, ext = os.path.splitext(os.path.basename(filepath))
    if ln is not None:
        return f"{root}_English_{LANG}_{timestr}{ext}"
    else:
        return f"{root}_English_{LANG}_both_{timestr}{ext}"
    
        
examples = [
    {"input": "We have won the Great War.", "output": "我们赢得了大战"},
    {"input": "Now we will win the last war.", "output": "现在我们将赢得最后一战。"},
]
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)


chat = ChatOpenAI(temperature=0)

st.title("Subtitle translator")

user_input = st.file_uploader("Upload srt file here", type=(["srt"]))
user_input_con = st.file_uploader("Upload continuous file here", type=(["txt"]))
# st.write(user_input.name)
option = st.selectbox(
    'Select your language',
    ('Chinese', 'Turkish', 'Japanese','Vietnamese','German','French','Spanish','Portuguese', 'Traditional Chinese'))


submit_button = st.button("Start Translation")
if submit_button:
    with st.spinner('Translating. Wait for result...'):
        final_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that translates English to {option}, Only translate the text input, don't add any explanation of your own.do not produce any other text, you will make the most accurate and authentic to the source translation possible."),
            few_shot_prompt,
            ("human", "{input}"),
            ])
        
        result = srtFileProcess(StringIO(user_input.getvalue().decode("utf-8")))
        # result_test=[]
        result_ln =srtFileProcess(StringIO(user_input.getvalue().decode("utf-8")))
    
        for i in range(0, len(result)):
            chain = final_prompt | chat
            res = chain.invoke({"input": result[i].content, "option":option}).content
            f_con = result[i].content + '\n' + res
            result[i].content = f_con
            result_ln[i].content = res
            # result_test.append(res)
        
        output = srt.compose(result)
        file_both = get_translated_filename(user_input.name, option)
        # with open(f"{DIR}{file_both}","w", encoding="utf-8") as handle:
        #     handle.write(output) 
            
        # with open(f"{DIR}{file_both}","r", encoding="utf-8") as handle:
            # data = handle.read()    
        b64 = base64.b64encode(output.encode()).decode() 
        final_url = f'<a href="data:file/text;base64,{b64}" download="{file_both}">Download Translated file with both </a>'
        st.markdown(final_url, unsafe_allow_html=True)
        
        output_ln = srt.compose(result_ln)
        file_tn = get_translated_filename(user_input.name, option, "only")
        # with open(f"{DIR}{file_tn}","w", encoding="utf-8") as handle:
            # handle.write(output_ln) 
            
        # with open(f"{DIR}{file_tn}","r", encoding="utf-8") as handle:
            # data = handle.read()    
        b64 = base64.b64encode(output_ln.encode()).decode() 
        final_url_ln = f'<a href="data:file/text;base64,{b64}" download="{file_tn}"> Download Translated file only</a>'
        st.markdown(final_url_ln, unsafe_allow_html=True)
        output_show = output.replace("\n","<br>")
        st.markdown(output_show, unsafe_allow_html=True)
            
        
    
        