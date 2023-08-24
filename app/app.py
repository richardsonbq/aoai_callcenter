import streamlit as st
import tempfile  
import time
import azure.cognitiveservices.speech as speechsdk
import openai
import os


# Initialize the parameters related to Azure OpenAI
openai.api_type = "azure"
openai.api_key = os.environ.get('OPENAI_API_KEY') 
openai.api_base = os.environ.get('OPENAI_API_ENDPOINT') 
openai.api_version = os.environ.get('OPENAI_API_VERSION') or "2023-06-01-preview"
COMPLETIONS_MODEL = os.environ.get('OPENAI_API_COMPLETION_MODEL') or "text-davinci-003"

# Initialize the parameters related to Azure Speech for text-to-speech and speech-to-text capabilities
SPEECH_KEY = os.environ.get('SPEECH_API_KEY')
SPEECH_SERVICE_REGION = os.environ.get('SPEECH_API_REGION') or "eastus"

# Define the supported languages and their language codes. You can add more languages here if needed  
languages = {  
    "English": "en-US",  
    "Spanish": "es-ES",  
    "Portuguese": "pt-BR" 
}

#Define the voices for synthesizing the responses. You can add/customize voices here if needed
voices = {  
    "English": "en-US-JessaNeural",  
    "Spanish": "es-ES-AlvaroNeural",  
    "Portuguese": "pt-BR-AntonioNeural" 
}

#Function to recognize speech from a file using the Speech SDK for Python
def recognize_speech_from_file(filename, speech_key, service_region, language):
    # Set up the subscription info for the Speech Service:
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region, speech_recognition_language=language)
    audio_config = speechsdk.audio.AudioConfig(filename=filename)
    # Creates a speech recognizer using a file as audio input, also specify the speech language
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,  audio_config=audio_config)

    global done 
    done = False
    global recognized_text_list 
    recognized_text_list=[]
    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        global done
        done = True

    def recognize_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        """callback for recognizing the recognized text"""
        global recognized_text_list
        recognized_text_list.append(evt.result.text)

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognized.connect(recognize_cb)
    speech_recognizer.session_started.connect(lambda evt: print('STT SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('STT SESSION STOPPED {}'.format(evt)))
 
    speech_recognizer.session_stopped.connect(stop_cb)
    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)

    speech_recognizer.stop_continuous_recognition()
    return recognized_text_list

#Function to synthesize speech from text to audio
def synthesize_speech(text, speech_key, service_region, language, voice):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region, speech_recognition_language=language)  
    speech_config.speech_synthesis_voice_name = voice
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)
    
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)  
    
    result = synthesizer.speak_text_async(text).get()  
  
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:  
        return result.audio_data  
    else:  
        print(f"Speech synthesis failed: {result}")  
        return None  

#Call Azure OpenAI service and return the text
def openai_completion(prompt, engine, temperature=0.5, max_tokens=400):
    return openai.Completion.create(
    prompt=prompt,
    temperature=temperature,
    max_tokens=max_tokens,
    engine=engine
    )["choices"][0]["text"].strip(" \n")

#Reset the session state to ensure new requests to Azure OpenAI can be done
def reset_openAI():
    st.session_state.response = None 

#Define the look and feel of the application
st.set_page_config(page_title="Call Center Analytics - Demo Solution", page_icon=":telephone_receiver:", layout="wide", initial_sidebar_state="expanded")
st.header("Call Center Analytics - Demo Solution")  
left_column, right_column = st.columns([7,4], gap="small")

#Initialize the session state for message history
if 'history' not in st.session_state:  
        st.session_state.history = []

# Add language selection and file uploader in the sidebar for Audio Transcription
with st.sidebar:
    selected_language = st.selectbox("Select audio language", options=list(languages.keys()))  
    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg", "flac"])

    if 'transcript' not in st.session_state:  
        st.session_state.transcript = None  

    if uploaded_file is not None:
        # Add a button to play the uploaded audio  
        st.audio(uploaded_file)

    submit_transcription = st.button("Transcribe Audio")

    if uploaded_file is not None and submit_transcription:  
        # Save the uploaded file to a temporary file and get its path  
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:  
            temp_file.write(uploaded_file.getvalue())  
            temp_file_path = temp_file.name  
    
        with st.spinner("Transcribing audio..."):  
            st.session_state.transcript = recognize_speech_from_file(temp_file_path, SPEECH_KEY, SPEECH_SERVICE_REGION, languages[selected_language]) 
            
        # Remove the temporary file after processing  
        os.remove(temp_file_path)  
        
    if st.session_state.transcript:  
        st.sidebar.write("Transcription:")  
        st.sidebar.success(st.session_state.transcript)

# Create a form in the left column for the custom prompt, responses and Audio Response
with left_column:
    transcription = str(st.session_state.transcript)

    # Add session state for user_prompt  
    if 'user_prompt' not in st.session_state:  
        st.session_state.user_prompt = ""  

    st.session_state.user_prompt = st.text_area("Enter a Prompt", value=st.session_state.user_prompt)

    submit_button = st.button("Analyze with Azure OpenAI", on_click=reset_openAI())       

    # Add session state for response  
    if 'response' not in st.session_state:  
        st.session_state.response = None

    if st.session_state.user_prompt and submit_button and transcription:           
        prompt = f"{st.session_state.user_prompt} \n Call: {transcription} \n Always respond in this language: {selected_language}"
        with st.spinner("Generating response from Azure OpenAI..."):         
            st.session_state.response = openai_completion(prompt=prompt, engine=COMPLETIONS_MODEL, temperature=0.5, max_tokens=600) 
            
    if st.session_state.response:
        # Store prompt and response in history  
        st.session_state.history.insert(0,(st.session_state.user_prompt, st.session_state.response))
    
    if st.session_state.history:
        st.text("OpenAI Response:")
        st.success(st.session_state.history[0][1], icon="✅")  
                       
    
     #Visual divider to separate the text-to-speech section
    st.divider()

    synth_audio_expander = st.expander("Generate Audio Response", expanded=True) 
    # Add session state for synthesized_audio  
    if 'synthesized_audio' not in st.session_state:  
        st.session_state.synthesized_audio = None

    if st.session_state.history:       
        # Add a button to synthesize the OpenAI response  
        create_audio = synth_audio_expander.button("Synthesize Response")

        if create_audio:            
            with st.spinner("Synthesizing response..."):                
                st.session_state.synthesized_audio = synthesize_speech(st.session_state.history[0][1], SPEECH_KEY, SPEECH_SERVICE_REGION, languages[selected_language], voice=voices[selected_language])
        
        if st.session_state.synthesized_audio:  
            synth_audio_expander.audio(st.session_state.synthesized_audio, format="audio/mp3") 

#Right column to display the history of prompts and responses
with right_column:
     # Display history 
    history_expander = st.expander("History", expanded=True)  
    if st.session_state.history:  
        for i, (prompt, response) in enumerate(st.session_state.history, 1):  
            history_expander.info(f"**{i}. Prompt:** {prompt}")
            history_expander.success(f"**{i}. Response:** {response}")
            history_expander.write("---")    