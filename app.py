import streamlit as st
import os
from dotenv import load_dotenv
from resume_processor import ResumeProcessor
from pdf_generator import PDFGenerator
import json

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Resume Customizer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #7F8C8D;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #D1ECF1;
        border: 1px solid #BEE5EB;
        color: #0C5460;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'customized_resume' not in st.session_state:
    st.session_state.customized_resume = None
if 'jd_analysis' not in st.session_state:
    st.session_state.jd_analysis = None

def main():
    # Header
    st.markdown('<div class="main-header">🚀 AI-Powered Resume Customizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Transform your resume to match any job description with AI</div>', unsafe_allow_html=True)
    
    # Sidebar for API key
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            help="Get your API key from https://console.anthropic.com/"
        )
        
        st.markdown("---")
        st.markdown("### 📋 How It Works")
        st.markdown("""
        1. **Upload** your resume (PDF/DOCX/TXT)
        2. **Paste** the job description
        3. **Click** Generate
        4. **Download** your customized resume
        """)
        
        st.markdown("---")
        st.markdown("### ✨ Features")
        st.markdown("""
        - ✅ ATS-friendly formatting
        - ✅ Keyword optimization
        - ✅ Professional layout
        - ✅ Instant PDF download
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Input")
        
        # Resume upload
        st.subheader("1. Upload Your Resume")
        resume_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'txt'],
            help="Upload your current resume in PDF, DOCX, or TXT format"
        )
        
        # Job description input
        st.subheader("2. Paste Job Description")
        jd_text = st.text_area(
            "Job Description",
            height=300,
            placeholder="Paste the job description here...",
            help="Copy and paste the entire job description"
        )
    
    with col2:
        st.header("📥 Output")
        
        # Generate button
        if st.button("🎯 Generate Customized Resume", type="primary", use_container_width=True):
            if not api_key:
                st.error("⚠️ Please enter your Anthropic API key in the sidebar")
            elif not resume_file:
                st.error("⚠️ Please upload your resume")
            elif not jd_text.strip():
                st.error("⚠️ Please paste the job description")
            else:
                with st.spinner("🤖 AI is customizing your resume..."):
                    try:
                        # Initialize processor
                        processor = ResumeProcessor(api_key)
                        
                        # Process resume
                        customized_resume, jd_analysis = processor.process_resume(
                            resume_file,
                            jd_text
                        )
                        
                        if customized_resume:
                            st.session_state.customized_resume = customized_resume
                            st.session_state.jd_analysis = jd_analysis
                            st.success("✅ Resume customized successfully!")
                        else:
                            st.error("❌ Error processing resume. Please try again.")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        # Display results
        if st.session_state.customized_resume:
            st.markdown('<div class="success-box">✨ Your customized resume is ready!</div>', unsafe_allow_html=True)
            
            # Tabs for preview and analysis
            tab1, tab2 = st.tabs(["📄 Resume Preview", "🔍 Job Analysis"])
            
            with tab1:
                st.markdown(st.session_state.customized_resume)
                
                # Generate PDF button
                if st.button("📥 Generate PDF", use_container_width=True):
                    with st.spinner("Creating PDF..."):
                        try:
                            pdf_gen = PDFGenerator()
                            pdf_buffer = pdf_gen.generate_resume_pdf(st.session_state.customized_resume)
                            
                            st.download_button(
                                label="⬇️ Download Customized Resume PDF",
                                data=pdf_buffer,
                                file_name="customized_resume.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            st.success("✅ PDF generated successfully!")
                        except Exception as e:
                            st.error(f"❌ Error generating PDF: {str(e)}")
            
            with tab2:
                if st.session_state.jd_analysis:
                    st.subheader("Key Requirements Identified")
                    
                    if isinstance(st.session_state.jd_analysis, dict):
                        if 'key_skills' in st.session_state.jd_analysis:
                            st.markdown("**🎯 Key Skills:**")
                            for skill in st.session_state.jd_analysis.get('key_skills', []):
                                st.markdown(f"- {skill}")
                        
                        if 'required_experience' in st.session_state.jd_analysis:
                            st.markdown("**💼 Required Experience:**")
                            st.write(st.session_state.jd_analysis.get('required_experience', 'N/A'))
                        
                        if 'key_responsibilities' in st.session_state.jd_analysis:
                            st.markdown("**📋 Key Responsibilities:**")
                            for resp in st.session_state.jd_analysis.get('key_responsibilities', []):
                                st.markdown(f"- {resp}")
                        
                        if 'keywords' in st.session_state.jd_analysis:
                            st.markdown("**🔑 ATS Keywords:**")
                            keywords = st.session_state.jd_analysis.get('keywords', [])
                            st.write(", ".join(keywords) if isinstance(keywords, list) else keywords)
                    else:
                        st.json(st.session_state.jd_analysis)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #7F8C8D; padding: 1rem;'>
            <p>Built with ❤️ using Streamlit & Claude AI</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()