# Form Filler with Gradio

## Overview
Form Filler with Gradio is an application designed to streamline the process of filling out oral health assessment forms using voice-to-text technology. This application leverages the AssemblyAI API for speech-to-text conversion and integrates with Supabase for database management.

## Features
- **Voice-to-Text Conversion**: Use AssemblyAI to transcribe speech into text.
- **Database Management**: Store and manage oral health assessment forms using Supabase.

## Prerequisites
Before you begin, ensure you have met the following requirements:
- Python 3.6 or later installed on your machine.
- An API key from AssemblyAI.
- A Supabase project with the required database setup.
- Git installed on your machine.

## Setup Instructions

### 1. Clone the Repository
First, clone the repository to your local machine using Git:
```bash
git clone https://github.com/Nikil-D-Gr8/FormFillerGradio.git
cd FormFillerGradio
```

### 2. Set Up Environment Variables
You need to set up environment variables for AssemblyAI and Supabase credentials.

Create a `.env` file in the root directory of the project and add the following:
```env
Assembly=<your_assembly_ai_api_key>
DBUrl=<your_supabase_database_url>
DBKey=<your_supabase_api_key>
```

Alternatively, you can set these environment variables directly in your terminal or command prompt:
```bash
export Assembly=<your_assembly_ai_api_key>
export DBUrl=<your_supabase_database_url>
export DBKey=<your_supabase_api_key>
```

### 3. Install Dependencies
Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

### 4. Create Supabase Table
Log in to your Supabase account and navigate to your project. Create a new table named `oral_health_assessment_form` with the following columns:

| Column Name           | Data Type |
|-----------------------|-----------|
| Doctor’s Name         | text      |
| Location              | text      |
| Patient’s Name        | text      |
| Age                   | text      |
| Gender                | text      |
| Chief complaint       | text      |
| Medical history       | text      |
| Dental history        | text      |
| Clinical Findings     | text      |
| Treatment plan        | text      |
| Referred to           | text      |

## Usage

### Running the Application
Once you have set up your environment variables and created the Supabase table, you can run the application:
```bash
python main.py
```

 Create a new Pull Request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
If you have any questions or issues, please contact the project maintainer at <snikilpaul@gmail.com>.

