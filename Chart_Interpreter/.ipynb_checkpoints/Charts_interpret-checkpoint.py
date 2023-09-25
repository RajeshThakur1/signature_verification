#IMPORTS
import streamlit as st
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from transformers import AutoProcessor, Pix2StructForConditionalGeneration
from transformers import Pix2StructProcessor, Pix2StructForConditionalGeneration
import requests
import gradio as gr
from langchain import PromptTemplate, OpenAI, LLMChain
from transformers import AutoTokenizer, AutoModel
import openai
import os
from langchain import PromptTemplate, OpenAI, LLMChain
device = "cuda" if torch.cuda.is_available() else "cpu"
model_clip = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor_clip = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
model = Pix2StructForConditionalGeneration.from_pretrained("google/deplot").to(device)
processor = AutoProcessor.from_pretrained("google/deplot")

os.environ['OPENAI_API_KEY'] = "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"
openai.api_key = os.environ.get("OPENAI_API_KEY")

#This function will use deplot to get data 
def get_data_from_chart(chart_type:str,image_path):
  #barcharts
  if(chart_type=="Vertical Barchart" or chart_type=="Horizontal Barchart"):
    model.load_state_dict(torch.load(f="BarChart_DePlot.pth"))
  # elif(chart_type=="Piechart"):
  #   model.load_state_dict(torch.load(f="PieChart_DePlot.pth"))
  image = Image.open(image_path)
  inputs = processor(images=image, text="Chart Data", return_tensors="pt").to(device)
  predictions = model.generate(**inputs, max_new_tokens=512)
  return processor.decode(predictions[0], skip_special_tokens=True) 

#This function uses CLIP to classify the chart
def process_image(input_image):
    # Load the uploaded image
    image = Image.open(input_image)
    inputs = processor_clip(text=["Barchart","Piechart","Linechart"], images=image, return_tensors="pt", padding=True)
    outputs = model_clip(**inputs)
    logits_per_image = outputs.logits_per_image  # this is the image-text similarity score
    probs = logits_per_image.softmax(dim=1)
    #print(probs)
    highest_prob_index = torch.argmax(probs)
    highest_prob_label = ["Barchart","Piechart","Linechart"][highest_prob_index]
    print(f"The label with the highest probability is: {highest_prob_label}")
    return get_data_from_chart(highest_prob_label,input_image)


#This function will create a proper HTML table from the data
def table_generator(image_path):
  data=process_image(image_path)
  #print(data)
  prompt_template = """
  You are given data for a chart delimited by triple backticks :
  ```{data}```
  Act as an expert table generator to create a meaningful table with the given data to have appropriate rows and columns.
  Make sure that no two rows have the same values .
  Convert the data to a table format
  The table must be :
  -returned in an HTML format 
  -enclose the table with <table> tags"""

  llm = OpenAI(temperature=0, max_tokens=1024)
  llm_chain = LLMChain(
      llm=llm,
      prompt=PromptTemplate(template=prompt_template, input_variables=["data"])
  )
  answer = llm_chain({"data":data})
  return answer["text"]

#Used for querying
def image_querying(query,data):
  if not query or query =="":
   return "Please enter you Question "
  prompt_template = """
  You are given a table of data for a chart delimited by triple backticks :
  ```{data}```
  From the table answer the following query:
  query:{query}
  answer:"""

  llm = OpenAI(temperature=0, max_tokens=1024)
  llm_chain = LLMChain(
      llm=llm,
      prompt=PromptTemplate(template=prompt_template, input_variables=["query","data"])
  )
  answer = llm_chain({"query":query,"data":data})
  return answer["text"]


#IMPORTS (unchanged)

def main():
    st.set_page_config(layout="wide")
    st.title("CHART-INTERPRETER")

    # Divide the screen into two columns
    col1, col2 = st.columns(2)
    table =""

    # Column 1: Upload the chart
    with col1:
        st.header("Upload Chart")
        uploaded_image = st.file_uploader("Upload the chart you want to query", type=["jpg", "png", "jpeg"])
        st.divider()
        
        if uploaded_image is not None:
            st.header("Analysis and Querying")
            query = st.text_area("Enter your query:")
            submit_button = st.button("Submit")
            table = table_generator(uploaded_image)
            st.divider()
            if submit_button:
                if not query:
                    st.warning("Please enter a query.")
                else:
                    output = image_querying(query, table)
                    st.subheader("Output:")
                    st.text_area(label="Archita", value=output, height=200, label_visibility="collapsed")
                    

    # Column 2: Show Image and Table
    with col2:
        st.header("Results")
        
        if uploaded_image is not None:
            show_image, show_table = st.tabs(["Show Image", "Show Table"])
        
            with show_image:
                st.subheader("Uploaded Image")
                st.image(uploaded_image, caption="Uploaded Image.", use_column_width=True)
                
            with show_table:
                st.subheader("Generated Table")
                #table = table_generator(uploaded_image)
                st.markdown(table, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
