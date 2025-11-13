import anthropic
import os
from docx import Document
import PyPDF2
import pdfplumber
import json

class ResumeProcessor:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF file"""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return None
    
    def extract_text_from_docx(self, docx_file):
        """Extract text from DOCX file"""
        try:
            doc = Document(docx_file)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
            return None
    
    def extract_text_from_file(self, file):
        """Determine file type and extract text"""
        file_name = file.name.lower()
        
        if file_name.endswith('.pdf'):
            return self.extract_text_from_pdf(file)
        elif file_name.endswith('.docx'):
            return self.extract_text_from_docx(file)
        elif file_name.endswith('.txt'):
            return file.read().decode('utf-8')
        else:
            return None
    
    def analyze_job_description(self, jd_text):
        """Extract key requirements and skills from job description"""
        prompt = f"""Analyze this job description and extract the following in a structured format:

Job Description:
{jd_text}

Please provide a JSON response with:
1. key_skills: List of required technical and soft skills
2. required_experience: Years and type of experience needed
3. key_responsibilities: Main job responsibilities
4. qualifications: Required education and certifications
5. keywords: Important ATS keywords to include

Format as valid JSON only."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Extract JSON from response
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {"error": "Could not parse JSON from response"}
        except json.JSONDecodeError:
            return {"raw_response": response_text}
    
    def customize_resume(self, resume_text, jd_analysis):
        """Generate customized resume based on job requirements"""
        prompt = f"""You are an expert resume writer. Customize this resume to match the job requirements while keeping all information truthful.

Original Resume:
{resume_text}

Job Requirements:
{json.dumps(jd_analysis, indent=2)}

Create an ATS-optimized resume with these requirements:
1. Use standard section headers: "Professional Summary", "Work Experience", "Education", "Skills", "Certifications" (if applicable)
2. Highlight relevant experience and skills that match the job description
3. Use bullet points for achievements and responsibilities
4. Include relevant keywords from the job description naturally
5. Keep formatting simple (no tables, clear hierarchy)
6. Quantify achievements where possible
7. Maintain all truthful information from original resume

Provide the enhanced resume in a clean, well-structured format with clear section breaks.
Use markdown headers (##) for main sections and bullet points (-) for lists."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    
    def process_resume(self, resume_file, jd_text):
        """Main processing pipeline"""
        resume_text = self.extract_text_from_file(resume_file)
        if not resume_text:
            return None, "Error: Could not extract text from resume file"
        
        jd_analysis = self.analyze_job_description(jd_text)
        customized_resume = self.customize_resume(resume_text, jd_analysis)
        
        return customized_resume, jd_analysis