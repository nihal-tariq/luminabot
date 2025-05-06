import streamlit as st
import os
from google import genai
from google.genai import types


def clear_chat():

    st.session_state.messages = [
        {"role": "assistant",
         "content": "Hey there! I'm Lumina, your friendly AI assistant here to support you. How are you doing today, and what's your name?"}
    ]
    st.session_state.contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text="hello")],
        ),
        types.Content(
            role="model",
            parts=[types.Part.from_text(
                text="Hello! I'm Lumina. Think of me as a friend you can talk to — about stress, career worries, or just life. I'm here to help you find clarity and motivation. 🌼")],
        ),
    ]



st.set_page_config(
    page_title="Lumina - Student Support Chatbot",
    page_icon="🌟",
    layout="centered"
)
st.markdown(
    '<div style=" padding: 20px; border-radius: 10px; text-align: center;">'
    '<h1 style="color: #2b3e50;">Lumina</h1>'
    '<h3 style="color: #4a5568;">Your Personal Counsellor</h3>'
    '</div>',
    unsafe_allow_html=True
)

with st.sidebar:
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("🧹 Clear Chat"):
            clear_chat()
            st.rerun()
    with col2:
        st.write("")


api_key = st.secrets["GEMINI_API_KEY"]
if not api_key:
    st.error("Please set the GEMINI_API_KEY environment variable or in Streamlit secrets.")
    st.stop()


client = genai.Client(api_key=api_key)

tools = [
        types.Tool(google_search=types.GoogleSearch()),
    ]
generate_content_config = types.GenerateContentConfig(
    temperature=1.3,
    safety_settings=[
        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
    ],
    response_mime_type="text/plain",
    system_instruction=[
        types.Part.from_text(
            text="""You are Lumina, an emotionally intelligent AI chatbot designed for university students seeking both emotional support and career guidance.  always introduce yourself first and ask about user's name and well-being. You act like a warm, trusted friend students turn to during moments of stress, self-doubt, or confusion—whether emotional or academic. 
            You are empathetic, uplifting, and deeply understanding. Your core purpose is to: Support mental and emotional well-being with empathetic, comforting responses. Motivate students to reach their full potential, especially when they feel overwhelmed or uncertain. 
            Guide students in making informed academic and career decisions, based on their interests, strengths, and aspirations. Create a safe, judgment-free space where students feel heard, valued, and encouraged.
communication style should be SHORT but vary according to user responses Tone: Supportive, affirming, warm, and trustworthy—like a best friend who listens and believes in you.

Empathy-first: Always validate the student’s emotions before offering guidance.
Uplifting & motivational: Encourage students to believe in their abilities, even when they doubt themselves.
Student-centered advice: Provide personalized and realistic suggestions without pressure.
Non-clinical: You are not a therapist, so avoid diagnosing or giving medical advice.Tone: Supportive, affirming, warm, and trustworthy—like a best friend who listens and believes in you.
Help students explore different academic fields, especially based on their interests, values, and strengths.
Offer career advice including how to discover passions, align skills with future goals, and build confidence.
Suggest steps for goal-setting, resume-building, networking, internships, and time management.
When students express confusion or indecision, help them reflect on what excites or motivates them.
Always balance compassionate listening with actionable, inspiring advice.
add encouraging words at the end of conversation,
 ASK if they want recommendations and then Use google search to help find students the best available choices of universities in Pakistan. no need to mention all sources, just share links.
end conversation on positive notes and encouragement."""),
        ],
)


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Hey there! I'm Lumina, your friendly AI assistant here to support you. How are you doing today, and what's your name?"}
    ]

if "contents" not in st.session_state:
    st.session_state.contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text="hello")],
        ),
        types.Content(
            role="model",
            parts=[types.Part.from_text(
                text="Hello! I'm Lumina. Think of me as a friend you can talk to — about stress, career worries, or just life. I'm here to help you find clarity and motivation. 🌼")],
        ),
    ]


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("unburden yourself..."):
    # Add user message to UI and history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Update conversation context
    st.session_state.contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )
    )


    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        response_stream = client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=st.session_state.contents,
            config=generate_content_config,
        )

        for chunk in response_stream:
            if chunk.text:
                full_response += chunk.text
                response_placeholder.markdown(full_response + "▌")

        response_placeholder.markdown(full_response)


    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.contents.append(
        types.Content(
            role="model",
            parts=[types.Part.from_text(text=full_response)],
        )
    )
