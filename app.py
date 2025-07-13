# frontend/app.py

import streamlit as st
import requests

st.set_page_config(page_title="GenAI Assistant", layout="wide")

st.title("GenAI Assistant")
st.write("Upload a PDF or TXT document to begin.")

# File upload widget
uploaded_file = st.file_uploader("Upload Document", type=["pdf", "txt", "doc", "docx"])
if uploaded_file:
    # Send the uploaded file to the backend
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    try:
        # response = requests.post("http://localhost:5000/upload", files=files)
        response = requests.post("http://127.0.0.1:5000/upload", files=files)

        data = response.json()
        summary = data.get("summary", "")
        if summary:
            st.subheader("Document Summary")
            st.write(summary)
        else:
            st.error("Failed to summarize document.")
    except Exception as e:
        st.error(f"Error contacting backend: {e}")
        st.stop()

    # Mode selection
    mode = st.radio("Interaction Mode", ["Ask Anything", "Challenge Me"])
    
    if mode == "Ask Anything":
        question = st.text_input("Enter your question about the document:")
        if st.button("Get Answer"):
            if question.strip():
                try:
                    res = requests.post("http://127.0.0.1:5000/ask", json={"question": question})
                    answer = res.json().get("answer", "")
                    st.subheader("Answer")
                    st.write(answer)
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please enter a question.")
    
    elif mode == "Challenge Me":
        if st.button("Generate Logic Question"):
            try:
                res = requests.get("http://127.0.0.1:5000/generate_question")
                question = res.json().get("question", "")
                if question:
                    st.subheader("Logic Question")
                    st.write(question)
                    st.session_state["logic_question"] = question
                else:
                    st.error("Failed to generate question.")
            except Exception as e:
                st.error(f"Error: {e}")
        
        # If a question has been generated, allow the user to answer it
        if "logic_question" in st.session_state:
            user_answer = st.text_input("Your Answer:")
            if st.button("Submit Answer"):
                if user_answer.strip():
                    try:
                        res = requests.post("http://127.0.0.1:5000/evaluate", json={"answer": user_answer})
                        result = res.json()
                        if result.get("correct"):
                            st.success("Correct!")
                        else:
                            st.error("Incorrect.")
                        st.write(f"The correct answer is: **{result.get('correct_answer', '')}**")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please enter an answer.")
