import gradio as gr
import assemblyai as aai
from transformers import pipeline
import os
from supabase import create_client, Client
from datetime import datetime
import csv

# Add your AssemblyAI API key as Environment Variable
aai.settings.api_key = os.environ['Assembly']
url: str = os.environ['DBUrl']
key: str = os.environ['DBKey']

# Initialize question answering pipeline
question_answerer = pipeline("question-answering", model='distilbert-base-cased-distilled-squad')

# List of questions
questions = [
    "How old is the patient?",
    "What is the gender?",
    "What is the chief complaint regarding the patient's oral health? If there is none, just say the word 'none' else elaborate",
    "Can you provide any relevant Dental history for the patient? If there is none, just say the word 'none', else elaborate",
    "Give me about the clinical findings listed",
    "What treatment plan do you recommend?"
]

# List of form fields in the correct order
form_fields = [
    "Age",
    "Gender",
    "Chief complaint",
    "Medical history",
    "Dental history",
    "Clinical Findings",
    "Treatment plan",
    "Referred to"
]

# Oral Health Assessment Form
oral_health_assessment_form = [
    "Doctor’s Name",
    "Location",
    "Patient’s Name",
    "Age",
    "Gender",
    "Chief complaint",
    "Medical history",
    "Dental history",
    "Clinical Findings",
    "Treatment plan",
    "Referred to"
]

# Function to generate answers for the questions
def generate_answer(question, context):
    result = question_answerer(question=question, context=context)
    return result['answer']

# Function to handle audio recording and transcription
def transcribe_audio(audio_path):
    print(f"Received audio file at: {audio_path}")
    
    # Check if the file exists and is not empty
    if not os.path.exists(audio_path):
        return "Error: Audio file does not exist."
    
    if os.path.getsize(audio_path) == 0:
        return "Error: Audio file is empty."
    
    try:
        # Transcribe the audio file using AssemblyAI
        transcriber = aai.Transcriber()
        print("Starting transcription...")
        transcript = transcriber.transcribe(audio_path)
        
        print("Transcription process completed.")
        
        # Handle the transcription result
        if transcript.status == aai.TranscriptStatus.error:
            print(f"Error during transcription: {transcript.error}")
            return transcript.error
        else:
            context = transcript.text
            print(f"Transcription text: {context}")
            return context
    
    except Exception as e:
        print(f"Exception occurred: {e}")
        return str(e)

# Function to fill in the answers for the text boxes
def fill_textboxes(context):
    answers = []
    for question in questions:
        answer = generate_answer(question, context)
        answers.append(answer)
    
    # Map answers to form fields in the correct order
    return {
        "Age": answers[0],
        "Gender": answers[1],
        "Chief complaint": answers[2],
        "Medical history": "none",  # Medical history is not part of the questions
        "Dental history": answers[3],
        "Clinical Findings": answers[4],
        "Treatment plan": answers[5],
        "Referred to": ""
    }

# Supabase configuration
supabase: Client = create_client(url, key)

# Main Gradio app function
def main(audio, doctor_name, location):
    context = transcribe_audio(audio)
    
    if "Error" in context:
        return [context] * (len(oral_health_assessment_form) - 2)  # Adjust for the number of fields
    
    answers = fill_textboxes(context)
    answers_list = [doctor_name, location] + [""]  # Initial patient name field empty
    answers_list += [answers.get(field, "") for field in form_fields]
    
    return answers_list

def save_answers(doctor_name, location, patient_name, age, gender, chief_complaint, medical_history, dental_history, clinical_findings, treatment_plan, referred_to):
    current_datetime = datetime.now().isoformat()
    answers_dict = {
        "Doctor’s Name": doctor_name,
        "Location": location,
        "Patient’s Name": patient_name,
        "Age": age,
        "Gender": gender,
        "Chief complaint": chief_complaint,
        "Medical history": medical_history,
        "Dental history": dental_history,
        "Clinical Findings": clinical_findings,
        "Treatment plan": treatment_plan,
        "Referred to": referred_to,
        "Submission Date and Time": current_datetime
    }
    print("Saved answers:", answers_dict)
    
    # Insert data into Supabase
    try:
        response = supabase.table('oral_health_assessments').insert(answers_dict).execute()
        print("Data inserted into Supabase:", response.data)
        return f"Saved answers: {answers_dict}"
    except Exception as e:
        print(f"Error inserting data into Supabase: {e}")
        return f"Error saving answers: {e}"

# Function to download table as CSV
def download_table_to_csv():
    # Fetch data from Supabase table
    response = supabase.table("oral_health_assessments").select("*").execute()
    
    # Check if data is available
    if not response.data:
        print("No data found in the table.")
        return None

    data = response.data

    # Prepare CSV data
    csv_data = []

    # Add header row
    if len(data) > 0:
        csv_data.append(data[0].keys())

    # Add data rows
    for row in data:
        csv_data.append(row.values())

    # Save CSV data to file (replace 'your_table.csv' with desired filename)
    csv_file = "your_table.csv"
    with open(csv_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    print("Downloaded table oral_health_assessments")
    return csv_file

def gradio_download():
    file_path = download_table_to_csv()
    if file_path:
        return file_path
    return None

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# OHA Form Filler App")
    
    with gr.Tabs() as tabs:
        # Default tab for Doctor's Name and Location
        with gr.Tab("Doctor Info"):
            doctor_name_input = gr.Textbox(label="Doctor's Name", interactive=True)
            location_input = gr.Textbox(label="Location", interactive=True)
            submit_button = gr.Button("Submit")
            info_output = gr.HTML(label="Submitted Info")
            
            def submit_info(name, loc):
                return f"Doctor's Name: {name}<br>Location: {loc}"
            
            submit_button.click(fn=submit_info, inputs=[doctor_name_input, location_input], outputs=info_output)
        
        # Second tab for OHA Form
        with gr.Tab("OHA Form"):
            audio_input = gr.Audio(type="filepath", label="Record your audio", elem_id="audio_input")
            transcribe_button = gr.Button("Transcribe and Generate Form", elem_id="transcribe_button")
            
            with gr.Row(elem_id="textboxes_row"):
                with gr.Column():
                    doctor_name_display = gr.Textbox(label="Doctor’s Name", value="", interactive=False)
                    location_display = gr.Textbox(label="Location", value="", interactive=False)
                    patient_name_input = gr.Textbox(label="Patient’s Name", value="", interactive=True)
                    textboxes_left = [gr.Textbox(label=oral_health_assessment_form[i], value="", interactive=True) for i in range(3, len(oral_health_assessment_form)//2)]
                with gr.Column():
                    textboxes_right = [gr.Textbox(label=oral_health_assessment_form[i], value="", interactive=True) for i in range(len(oral_health_assessment_form)//2, len(oral_health_assessment_form)-1)]
                    dropdown_referred = gr.Dropdown(choices=["NONE","ORAL MEDICINE & RADIOLOGY", "PERIODONTICS", "ORAL SURGERY", "CONSERVATIVE AND ENDODONTICS", "PROSTHODONTICS", "PEDODONTICS", "ORTHODONTICS"], label="Referred to", interactive=True)
            
            def update_textboxes(audio, doctor_name, location):
                context = transcribe_audio(audio)
                
                if "Error" in context:
                    return [context] * (len(oral_health_assessment_form) - 3)  # Adjust for the number of fields
                
                answers = fill_textboxes(context)
                answers_list = [doctor_name, location] + [""]  # Initial patient name field empty
                answers_list += [answers.get(field, "") for field in form_fields[:-1]]  # Exclude "Referred to"
                answers_list.append(answers.get("Referred to", ""))  # Ensure "Referred to" is included
                
                return answers_list

            transcribe_button.click(fn=update_textboxes, inputs=[audio_input, doctor_name_input, location_input], outputs=[doctor_name_display, location_display, patient_name_input] + textboxes_left + textboxes_right + [dropdown_referred])
            
            save_button = gr.Button("Save Form")
            save_output = gr.HTML(label="Save Output")
            
            def handle_submission(doctor_name, location, patient_name, age, gender, chief_complaint, medical_history, dental_history, clinical_findings, treatment_plan, referred_to):
                return save_answers(doctor_name, location, patient_name, age, gender, chief_complaint, medical_history, dental_history, clinical_findings, treatment_plan, referred_to)
            
            save_button.click(fn=handle_submission, inputs=[doctor_name_display, location_display, patient_name_input] + textboxes_left + textboxes_right + [dropdown_referred], outputs=save_output)
        
        # Third tab for Save and Download
        with gr.Tab("Download Data"):
            download_button = gr.Button("Download Data as CSV")
            download_output = gr.File(label="Download CSV")
            
            download_button.click(fn=gradio_download, outputs=download_output)

# Run the Gradio app
demo.launch()
