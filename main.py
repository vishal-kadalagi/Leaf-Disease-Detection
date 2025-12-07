import streamlit as st
import requests
import base64
from datetime import datetime
import json
import sqlite3

# Set Streamlit theme to light and wide mode
st.set_page_config(
    page_title="Leaf Disease Detection Pro",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🌿"
)

# Enhanced modern CSS with professional styling
st.markdown("""
    <style>
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #e3f2fd 0%, #f7f9fa 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header styling */
    .header-container {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1b5e20 0%, #2e7d32 100%);
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        color: white;
    }
    
    .header-container h1 {
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
    }
    
    .header-container p {
        font-size: 1.2rem;
        opacity: 0.9;
        max-width: 700px;
        margin: 0 auto;
    }
    
    /* Result cards */
    .result-card {
        background: rgba(255,255,255,0.95);
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(44,62,80,0.10);
        padding: 2.5em 2em;
        margin-top: 1.5em;
        margin-bottom: 1.5em;
        transition: box-shadow 0.3s, transform 0.3s;
        border: 1px solid #e0e0e0;
    }
    
    .result-card:hover {
        box-shadow: 0 8px 32px rgba(44,62,80,0.18);
        transform: translateY(-5px);
    }
    
    .disease-title {
        color: #1b5e20;
        font-size: 2.2em;
        font-weight: 700;
        margin-bottom: 0.5em;
        letter-spacing: 1px;
        text-shadow: 0 2px 8px #e0e0e0;
    }
    
    .section-title {
        color: #1976d2;
        font-size: 1.25em;
        margin-top: 1.2em;
        margin-bottom: 0.5em;
        font-weight: 600;
        letter-spacing: 0.5px;
        position: relative;
        padding-bottom: 0.5rem;
    }
    
    .section-title::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 50px;
        height: 3px;
        background: #1976d2;
        border-radius: 3px;
    }
    
    .timestamp {
        color: #616161;
        font-size: 0.95em;
        margin-top: 1.2em;
        text-align: right;
    }
    
    .info-badge {
        display: inline-block;
        background: #e3f2fd;
        color: #1976d2;
        border-radius: 8px;
        padding: 0.3em 0.8em;
        font-size: 1em;
        margin-right: 0.5em;
        margin-bottom: 0.3em;
        font-weight: 500;
    }
    
    .symptom-list, .cause-list, .treatment-list {
        margin-left: 1em;
        margin-bottom: 0.5em;
    }
    
    .symptom-list li, .cause-list li, .treatment-list li {
        margin-bottom: 0.5em;
        line-height: 1.5;
    }
    
    /* Sidebar styling */
    [data-testid=stSidebar] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #1b5e20 0%, #2e7d32 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(27, 94, 32, 0.3);
    }
    
    /* File uploader */
    .uploadedFile {
        background: #f1f8e9;
        border: 2px dashed #81c784;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #4caf50;
    }
    </style>
""", unsafe_allow_html=True)

# Professional header
st.markdown("""
    <div class="header-container">
        <h1>🌿 Leaf Disease Detection Pro</h1>
        <p>AI-Powered Plant Health Analysis for Precision Agriculture</p>
    </div>
""", unsafe_allow_html=True)

# Define functions before they are used
def analyze_single_image(uploaded_file):
    """Analyze a single uploaded image"""
    with st.spinner("🔬 Analyzing image with AI... This may take a few seconds."):
        try:
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            # Use local API for development
            response = requests.post(
                "http://localhost:8000/disease-detection-file", files=files)
            
            if response.status_code == 200:
                result = response.json()
                display_analysis_result(result)
            else:
                st.error(f"API Error: {response.status_code}")
                st.write(response.text)
        except Exception as e:
            st.error(f"Error: {str(e)}")

def analyze_batch_images(uploaded_files):
    """Analyze multiple uploaded images in batch"""
    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown("<div class='disease-title'>📊 Batch Analysis Results</div>", unsafe_allow_html=True)
    
    # Create tabs for each image result
    tab_list = [f"Image {i+1}" for i in range(len(uploaded_files))]
    tabs = st.tabs(tab_list)
    
    batch_results = []
    
    for i, (tab, uploaded_file) in enumerate(zip(tabs, uploaded_files)):
        with tab:
            st.markdown(f"**File:** {uploaded_file.name}")
            
            try:
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # Use local API for development
                response = requests.post(
                    "http://localhost:8000/disease-detection-file", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    batch_results.append({
                        "filename": uploaded_file.name,
                        "result": result
                    })
                    display_analysis_result(result)
                else:
                    st.error(f"API Error: {response.status_code}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Error analyzing {uploaded_file.name}: {str(e)}")
    
    # Summary of batch results
    st.markdown("---")
    st.markdown("<div class='section-title'>Batch Summary</div>", unsafe_allow_html=True)
    
    healthy_count = sum(1 for r in batch_results if not r['result'].get('disease_detected') and r['result'].get('disease_type') != 'invalid_image')
    diseased_count = sum(1 for r in batch_results if r['result'].get('disease_detected'))
    invalid_count = sum(1 for r in batch_results if r['result'].get('disease_type') == 'invalid_image')
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Healthy Leaves", healthy_count)
    col2.metric("Diseased Leaves", diseased_count)
    col3.metric("Invalid Images", invalid_count)
    
    st.markdown("</div>", unsafe_allow_html=True)

def display_analysis_result(result):
    """Display analysis result in professional format"""
    # Display results in professional format
    if result.get("disease_type") == "invalid_image":
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("<div class='disease-title'>⚠️ Invalid Image</div>", unsafe_allow_html=True)
        st.markdown("<div style='color: #ff5722; font-size: 1.1em; margin-bottom: 1em;'>Please upload a clear image of a plant leaf for accurate disease detection.</div>", unsafe_allow_html=True)
        
        if result.get("symptoms"):
            st.markdown("<div class='section-title'>Issue Details</div>", unsafe_allow_html=True)
            st.markdown("<ul class='symptom-list'>", unsafe_allow_html=True)
            for symptom in result.get("symptoms", []):
                st.markdown(f"<li>{symptom}</li>", unsafe_allow_html=True)
            st.markdown("</ul>", unsafe_allow_html=True)
        
        if result.get("treatment"):
            st.markdown("<div class='section-title'>Recommended Action</div>", unsafe_allow_html=True)
            st.markdown("<ul class='treatment-list'>", unsafe_allow_html=True)
            for treat in result.get("treatment", []):
                st.markdown(f"<li>{treat}</li>", unsafe_allow_html=True)
            st.markdown("</ul>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    elif result.get("disease_detected"):
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='disease-title'>🦠 {result.get('disease_name', 'N/A')}</div>", unsafe_allow_html=True)
        
        # Display key metrics with badges
        col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
        with col_metrics1:
            st.markdown(f"<span class='info-badge'>Type: {result.get('disease_type', 'N/A').title()}</span>", unsafe_allow_html=True)
        with col_metrics2:
            st.markdown(f"<span class='info-badge'>Severity: {result.get('severity', 'N/A').title()}</span>", unsafe_allow_html=True)
        with col_metrics3:
            st.markdown(f"<span class='info-badge'>Confidence: {result.get('confidence', 'N/A')}%</span>", unsafe_allow_html=True)
        
        # Simple confidence display
        confidence = result.get('confidence', 0)
        st.progress(confidence / 100)
        st.caption(f"Confidence Level: {confidence}%")
        
        st.markdown("<div class='section-title'>Symptoms</div>", unsafe_allow_html=True)
        st.markdown("<ul class='symptom-list'>", unsafe_allow_html=True)
        for symptom in result.get("symptoms", []):
            st.markdown(f"<li>{symptom}</li>", unsafe_allow_html=True)
        st.markdown("</ul>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'>Possible Causes</div>", unsafe_allow_html=True)
        st.markdown("<ul class='cause-list'>", unsafe_allow_html=True)
        for cause in result.get("possible_causes", []):
            st.markdown(f"<li>{cause}</li>", unsafe_allow_html=True)
        st.markdown("</ul>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'>Treatment Recommendations</div>", unsafe_allow_html=True)
        st.markdown("<ul class='treatment-list'>", unsafe_allow_html=True)
        for treat in result.get("treatment", []):
            st.markdown(f"<li>{treat}</li>", unsafe_allow_html=True)
        st.markdown("</ul>", unsafe_allow_html=True)
        
        st.markdown(f"<div class='timestamp'>🕒 Analysis completed: {result.get('analysis_timestamp', 'N/A')}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        # Healthy leaf case
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("<div class='disease-title'>✅ Healthy Leaf</div>", unsafe_allow_html=True)
        st.markdown("<div style='color: #4caf50; font-size: 1.1em; margin-bottom: 1em;'>No disease detected in this leaf. The plant appears to be healthy!</div>", unsafe_allow_html=True)
        
        col_metrics1, col_metrics2 = st.columns(2)
        with col_metrics1:
            st.markdown(f"<span class='info-badge'>Status: {result.get('disease_type', 'healthy').title()}</span>", unsafe_allow_html=True)
        with col_metrics2:
            st.markdown(f"<span class='info-badge'>Confidence: {result.get('confidence', 'N/A')}%</span>", unsafe_allow_html=True)
        
        # Simple confidence display
        confidence = result.get('confidence', 0)
        st.progress(confidence / 100)
        st.caption(f"Confidence Level: {confidence}%")
        
        st.markdown(f"<div class='timestamp'>🕒 Analysis completed: {result.get('analysis_timestamp', 'N/A')}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

def export_analysis_history_csv():
    """Export analysis history to CSV"""
    try:
        analyses = fetch_recent_analyses(1000)  # Export up to 1000 records
        if analyses:
            import base64
            import csv
            from io import StringIO
            
            # Create CSV in memory
            csv_buffer = StringIO()
            writer = csv.writer(csv_buffer)
            
            # Write header
            writer.writerow(["ID", "Timestamp", "Disease Detected", "Disease Name", "Disease Type", 
                           "Severity", "Confidence", "Symptoms", "Possible Causes", "Treatment", "Image Filename"])
            
            # Write data rows
            for analysis in analyses:
                writer.writerow([
                    analysis['id'],
                    analysis['timestamp'],
                    analysis['disease_detected'],
                    analysis['disease_name'],
                    analysis['disease_type'],
                    analysis['severity'],
                    analysis['confidence'],
                    '; '.join(analysis['symptoms']) if isinstance(analysis['symptoms'], list) else analysis['symptoms'],
                    '; '.join(analysis['possible_causes']) if isinstance(analysis['possible_causes'], list) else analysis['possible_causes'],
                    '; '.join(analysis['treatment']) if isinstance(analysis['treatment'], list) else analysis['treatment'],
                    analysis['image_filename']
                ])
            
            csv_data = csv_buffer.getvalue()
            
            # Create download link
            b64 = base64.b64encode(csv_data.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="leaf_disease_analysis_history.csv">Download CSV File</a>'
            st.sidebar.markdown(href, unsafe_allow_html=True)
            st.sidebar.success("CSV export ready! Click the link to download.")
        else:
            st.sidebar.warning("No analysis history to export.")
    except Exception as e:
        st.sidebar.error(f"Export failed: {str(e)}")

def export_analysis_history_pdf():
    """Export analysis history to PDF with images"""
    try:
        # Try to import required libraries early to catch import errors
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            import base64
            from io import BytesIO
            import requests
            from PIL import Image as PILImage
            import io
        except ImportError as ie:
            st.sidebar.error(f"PDF export failed: Missing library '{getattr(ie, 'name', str(ie))}'. Please install required libraries: pip install reportlab pillow")
            return
        
        analyses = fetch_recent_analyses(50)  # Limit to 50 for better performance
        if analyses:
            # Create PDF buffer
            pdf_buffer = BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=26,
                spaceAfter=30,
                textColor=colors.darkgreen,
                alignment=1  # Center alignment
            )
            story.append(Paragraph("Leaf Disease Detection Analysis Report", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Subtitle
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Normal'],
                fontSize=14,
                textColor=colors.green,
                alignment=1
            )
            story.append(Paragraph("Comprehensive Plant Health Analysis", subtitle_style))
            story.append(Spacer(1, 0.4*inch))
            
            # Summary Section
            story.append(Paragraph("Analysis Summary", styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))
            
            total = len(analyses)
            diseased = sum(1 for a in analyses if a['disease_detected'])
            healthy = sum(1 for a in analyses if not a['disease_detected'] and a['disease_type'] != 'invalid_image')
            invalid = sum(1 for a in analyses if a['disease_type'] == 'invalid_image')
            
            # Summary table
            summary_data = [
                ["Total Analyses", "Diseased Leaves", "Healthy Leaves", "Invalid Images"],
                [str(total), str(diseased), str(healthy), str(invalid)]
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.4*inch))
            
            # Detailed records with images
            story.append(Paragraph("Detailed Analysis Records", styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))
            
            # Process each analysis record
            for i, analysis in enumerate(analyses[:20]):  # Limit to first 20 for reasonable PDF size
                # Record header
                record_title = f"Record #{analysis['id']}: {analysis['image_filename']}"
                story.append(Paragraph(record_title, styles['Heading3']))
                
                # Try to fetch and include the image
                try:
                    # Attempt to get the image from the API
                    response = requests.get(f"http://localhost:8000/analysis-image/{analysis['id']}")
                    if response.status_code == 200:
                        # Convert to PIL Image
                        pil_img = PILImage.open(io.BytesIO(response.content))
                        
                        # Resize for PDF
                        max_width = 200
                        max_height = 150
                        pil_img.thumbnail((max_width, max_height))
                        
                        # Save to BytesIO
                        img_buffer = io.BytesIO()
                        pil_img.save(img_buffer, format='JPEG')
                        img_buffer.seek(0)
                        
                        # Add to PDF
                        img = Image(img_buffer, width=max_width, height=max_height)
                        story.append(img)
                        story.append(Spacer(1, 0.1*inch))
                except Exception as img_error:
                    # If image loading fails, continue without it
                    pass
                
                # Analysis details table
                status = "Diseased" if analysis['disease_detected'] else ("Healthy" if analysis['disease_type'] != 'invalid_image' else "Invalid")
                
                details_data = [
                    ["Field", "Value"],
                    ["Timestamp", analysis['timestamp'][:19]],
                    ["Status", status],
                    ["Disease Name", analysis['disease_name'] if analysis['disease_name'] else "N/A"],
                    ["Disease Type", analysis['disease_type'].title() if analysis['disease_type'] else "N/A"],
                    ["Severity", analysis['severity'].title() if analysis['severity'] else "N/A"],
                    ["Confidence", f"{analysis['confidence']:.1f}%"],
                    ["Symptoms", "; ".join(analysis['symptoms'][:3]) if isinstance(analysis['symptoms'], list) and analysis['symptoms'] else "None recorded"],
                    ["Possible Causes", "; ".join(analysis['possible_causes'][:3]) if isinstance(analysis['possible_causes'], list) and analysis['possible_causes'] else "None recorded"],
                    ["Treatment", "; ".join(analysis['treatment'][:3]) if isinstance(analysis['treatment'], list) and analysis['treatment'] else "None recorded"]
                ]
                
                details_table = Table(details_data)
                details_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                story.append(details_table)
                story.append(Spacer(1, 0.3*inch))
            
            # Footer
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("Report generated by Leaf Disease Detection System", styles['Normal']))
            
            # Build PDF
            doc.build(story)
            pdf_data = pdf_buffer.getvalue()
            
            # Create download link
            b64 = base64.b64encode(pdf_data).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="leaf_disease_analysis_report.pdf">Download PDF Report</a>'
            st.sidebar.markdown(href, unsafe_allow_html=True)
            st.sidebar.success("PDF report ready! Click the link to download.")
        else:
            st.sidebar.warning("No analysis history to export.")
    except Exception as e:
        st.sidebar.error(f"PDF export failed: {str(e)}")

# Database connection function
def get_db_connection():
    try:
        conn = sqlite3.connect('disease_history.db')
        # Ensure the table exists
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                disease_detected BOOLEAN,
                disease_name TEXT,
                disease_type TEXT,
                severity TEXT,
                confidence REAL,
                symptoms TEXT,
                possible_causes TEXT,
                treatment TEXT,
                image_filename TEXT,
                image_data BLOB
            )
        ''')
        
        # Check if image_data column exists, add it if not
        cursor.execute("PRAGMA table_info(analysis_history)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'image_data' not in columns:
            try:
                cursor.execute("ALTER TABLE analysis_history ADD COLUMN image_data BLOB")
            except:
                pass  # Column might already exist
        conn.commit()
        return conn
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

# Fetch statistics from database
def fetch_statistics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total analyses
        cursor.execute('SELECT COUNT(*) FROM analysis_history')
        total = cursor.fetchone()[0]
        
        # Disease detections
        cursor.execute('SELECT COUNT(*) FROM analysis_history WHERE disease_detected = 1')
        diseases = cursor.fetchone()[0]
        
        # Healthy plants
        cursor.execute('SELECT COUNT(*) FROM analysis_history WHERE disease_detected = 0 AND disease_type != "invalid_image"')
        healthy = cursor.fetchone()[0]
        
        # Invalid images
        cursor.execute('SELECT COUNT(*) FROM analysis_history WHERE disease_type = "invalid_image"')
        invalid = cursor.fetchone()[0]
        
        # Disease types distribution
        cursor.execute('''
            SELECT disease_type, COUNT(*) 
            FROM analysis_history 
            WHERE disease_detected = 1 
            GROUP BY disease_type 
            ORDER BY COUNT(*) DESC
        ''')
        disease_types = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_analyses': total,
            'disease_detections': diseases,
            'healthy_plants': healthy,
            'invalid_images': invalid,
            'disease_distribution': dict(disease_types)
        }
    except Exception as e:
        st.error(f"Error fetching statistics: {str(e)}")
        return {}

# Fetch recent analyses from database with all required fields
def fetch_recent_analyses(limit=10):
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, disease_detected, disease_name, disease_type, severity, 
                   confidence, symptoms, possible_causes, treatment, image_filename
            FROM analysis_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        analyses = []
        for row in rows:
            analysis = dict(zip(columns, row))
            # Convert JSON strings back to lists
            analysis['symptoms'] = json.loads(analysis['symptoms']) if analysis['symptoms'] else []
            analysis['possible_causes'] = json.loads(analysis['possible_causes']) if analysis['possible_causes'] else []
            analysis['treatment'] = json.loads(analysis['treatment']) if analysis['treatment'] else []
            analyses.append(analysis)
        
        conn.close()
        return analyses
    except Exception as e:
        st.error(f"Error fetching analysis history: {str(e)}")
        return []

# Sidebar with additional information
with st.sidebar:
    st.header("About This Tool")
    st.markdown("""
    This advanced AI system detects plant diseases with high accuracy using 
    state-of-the-art computer vision technology.
    
    **Features:**
    - 500+ disease classifications
    - Real-time analysis
    - Treatment recommendations
    - Severity assessment
    """)
    
    st.divider()
    
    st.subheader("How to Use")
    st.markdown("""
    1. Upload a clear image of a plant leaf
    2. Click "Detect Disease"
    3. Review detailed analysis results
    4. Follow treatment recommendations
    """)
    
    st.divider()
    
    st.subheader("Technology")
    st.markdown("""
    - **AI Model**: Meta Llama Vision
    - **Framework**: FastAPI + Streamlit
    - **API**: Groq Cloud
    - **Accuracy**: 95%+
    """)

# Main content
col1, col2 = st.columns([1, 2])

with col1:
    # Updated file uploader to support multiple files
    uploaded_files = st.file_uploader(
        "Upload Leaf Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    if uploaded_files:
        # Show preview of all uploaded images
        st.subheader("Image Preview")
        for i, uploaded_file in enumerate(uploaded_files):
            st.image(uploaded_file, caption=f"Image {i+1}: {uploaded_file.name}", use_column_width=True)
            
            # Add image metadata
            file_details = {
                "Filename": uploaded_file.name,
                "File Size": f"{uploaded_file.size / 1024:.1f} KB",
                "File Type": uploaded_file.type
            }
            st.info(f"**Image Info:** {file_details['Filename']} ({file_details['File Size']})")
    else:
        st.info("⬆️ Please upload leaf images to begin analysis")

with col2:
    if uploaded_files:
        # Single analysis button for one image
        if len(uploaded_files) == 1:
            if st.button("🔍 Analyze Leaf Health", use_container_width=True):
                analyze_single_image(uploaded_files[0])
        else:
            # Batch analysis button for multiple images
            if st.button("🔍 Analyze All Images (Batch Processing)", use_container_width=True):
                analyze_batch_images(uploaded_files)
            
            # Option to analyze individual images
            st.markdown("---")
            st.subheader("Or analyze individual images:")
            for i, uploaded_file in enumerate(uploaded_files):
                if st.button(f"🔍 Analyze Image {i+1}: {uploaded_file.name}", key=f"btn_{i}"):
                    analyze_single_image(uploaded_file)
    else:
        st.info("⬆️ Please upload a leaf image to begin analysis")
        
        # Add sample images section
        st.divider()
        st.subheader("Sample Images for Testing")
        st.markdown("""
        Don't have a leaf image? Try these sample categories:
        - Healthy leaves
        - Leaves with fungal infections
        - Leaves with bacterial spots
        - Leaves with pest damage
        """)

# Add Analytics and History Section
st.divider()
st.markdown("<h2 style='text-align: center; color: #1b5e20; margin: 2rem 0;'>📊 Analytics Dashboard</h2>", unsafe_allow_html=True)

# Add export functionality in the sidebar
with st.sidebar:
    st.divider()
    st.subheader("📥 Export Options")
    
    # Add export buttons
    if st.button("Export Analysis History (CSV)"):
        export_analysis_history_csv()
    
    if st.button("Export Analysis History (PDF)"):
        export_analysis_history_pdf()

try:
    # Display metrics
    stats = fetch_statistics()

    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("Total Analyses", stats.get('total_analyses', 0)),
            ("Disease Detections", stats.get('disease_detections', 0)),
            ("Healthy Plants", stats.get('healthy_plants', 0)),
            ("Invalid Images", stats.get('invalid_images', 0))
        ]
        
        for i, (label, value) in enumerate(metrics):
            with [col1, col2, col3, col4][i]:
                st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08); text-align: center; height: 100%;">
                        <div style="font-size: 2.5rem; font-weight: 700; color: #1b5e20;">{value}</div>
                        <div style="font-size: 1.1rem; color: #616161; margin-top: 0.5rem;">{label}</div>
                    </div>
                """, unsafe_allow_html=True)

        # Disease distribution chart
        st.divider()
        st.markdown("<h3 style='color: #1b5e20; margin: 1rem 0;'>Disease Type Distribution</h3>", unsafe_allow_html=True)
        
        disease_dist = stats.get('disease_distribution', {})
        
        if disease_dist:
            # Create a simple bar chart using Streamlit components instead of raw HTML
            st.markdown("<div style='background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>", unsafe_allow_html=True)
            
            max_count = max(disease_dist.values()) if disease_dist.values() else 1
            
            for disease, count in disease_dist.items():
                percentage = (count / max_count) * 100 if max_count > 0 else 0
                st.markdown(f"""
                <div style='margin-bottom: 1rem;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                        <strong>{disease.title()}</strong>
                        <span>{count}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                # Use Streamlit's progress bar instead of custom HTML
                st.progress(percentage / 100)
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No disease distribution data available yet.")

    # Recent analyses table with enhanced design using Streamlit components
    st.divider()
    st.markdown("<h3 style='color: #1b5e20; margin: 1rem 0;'>Recent Analyses</h3>", unsafe_allow_html=True)

    recent_analyses = fetch_recent_analyses()

    if recent_analyses:
        # Display each analysis as a concise card
        for i, item in enumerate(recent_analyses):
            # Alternate background colors
            bg_color = "#ffffff" if i % 2 == 0 else "#f8f9fa"
            
            # Determine status text and styling
            if item.get('disease_type') == 'invalid_image':
                status_text = "⚠️ Invalid"
                status_color = "#ffebee"
                status_text_color = "#c62828"
                border_color = "#c62828"
            elif item.get('disease_detected'):
                status_text = f"🦠 {item.get('disease_name', 'Unknown Disease')}"
                status_color = "#ffebee"
                status_text_color = "#c62828"
                border_color = "#c62828"
            else:
                status_text = "✅ Healthy"
                status_color = "#e8f5e9"
                status_text_color = "#2e7d32"
                border_color = "#2e7d32"
            
            # Confidence styling
            confidence = item.get('confidence', 0)
            if confidence >= 90:
                confidence_color = "#2e7d32"
            elif confidence >= 70:
                confidence_color = "#f57c00"
            else:
                confidence_color = "#c62828"
            
            # Concise card for each analysis
            st.markdown(f"""
                <div style="background: {bg_color}; border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06); 
                        margin-bottom: 1rem; border-left: 4px solid {border_color}; transition: all 0.2s ease;"
                 onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(0,0,0,0.12)';"
                 onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.06)';">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <div style="font-size: 1.1rem; font-weight: 600; color: #1b5e20; margin-bottom: 0.3rem;">
                            {datetime.fromisoformat(item['timestamp']).strftime('%Y-%m-%d %H:%M:%S') if item.get('timestamp') else 'N/A'}
                        </div>
                        <div style="font-size: 1rem; font-weight: 500; color: {status_text_color};">
                            {status_text}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.4rem; font-weight: 700; color: {confidence_color};">{confidence:.0f}%</div>
                        <div style="display: flex; gap: 0.8rem; margin-top: 0.2rem;">
                            <div style="background: #e3f2fd; padding: 0.3rem 0.6rem; border-radius: 8px; font-size: 0.8rem;">
                                <span style="font-weight: 600; color: #1976d2;">T:</span> {item.get('disease_type', 'N/A').title()}
                            </div>
                            <div style="background: #e3f2fd; padding: 0.3rem 0.6rem; border-radius: 8px; font-size: 0.8rem;">
                                <span style="font-weight: 600; color: #1976d2;">S:</span> {item.get('severity', 'N/A').title() if item.get('severity') else 'N/A'}
                            </div>
                        </div>
                    </div>
                </div>
                <div style="margin-top: 0.6rem; font-size: 0.85rem; color: #616161; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    📄 {item.get('image_filename', 'N/A')}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Create expander for each analysis
        for item in recent_analyses:
            with st.expander(f"Analysis #{item['id']}: {item.get('image_filename', 'Unknown')}"):
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    # Try to fetch and display the full image
                    try:
                        response = requests.get(f"http://localhost:8000/analysis-image/{item['id']}")
                        if response.status_code == 200:
                            st.image(response.content, caption=item.get('image_filename', 'Analysis Image'), use_column_width=True)
                        else:
                            st.warning("Image not available for this analysis")
                    except Exception as e:
                        st.warning("Unable to load image")
                
                with col2:
                    # Display detailed analysis information
                    st.markdown(f"<h4 style='color: #1b5e20; margin-top: 0;'>Analysis Details</h4>", unsafe_allow_html=True)
                    
                    # Status badge
                    if item.get('disease_type') == 'invalid_image':
                        st.markdown("**Status:** ⚠️ Invalid Image")
                    elif item.get('disease_detected'):
                        st.markdown(f"**Status:** 🦠 {item.get('disease_name', 'Unknown Disease')}")
                    else:
                        st.markdown("**Status:** ✅ Healthy Leaf")
                    
                    # Key metrics in cards
                    col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
                    with col_metrics1:
                        st.markdown(f"<div style='background: #e3f2fd; padding: 0.8rem; border-radius: 8px; text-align: center;'><div style='font-weight: bold; color: #1976d2;'>Type</div><div>{item.get('disease_type', 'N/A').title()}</div></div>", unsafe_allow_html=True)
                    with col_metrics2:
                        st.markdown(f"<div style='background: #e3f2fd; padding: 0.8rem; border-radius: 8px; text-align: center;'><div style='font-weight: bold; color: #1976d2;'>Severity</div><div>{item.get('severity', 'N/A').title() if item.get('severity') else 'N/A'}</div></div>", unsafe_allow_html=True)
                    with col_metrics3:
                        st.markdown(f"<div style='background: #e3f2fd; padding: 0.8rem; border-radius: 8px; text-align: center;'><div style='font-weight: bold; color: #1976d2;'>Confidence</div><div>{item.get('confidence', 0):.1f}%</div></div>", unsafe_allow_html=True)
                    
                    st.markdown(f"**Filename:** {item.get('image_filename', 'N/A')}")
                    st.markdown(f"**Timestamp:** {datetime.fromisoformat(item['timestamp']).strftime('%Y-%m-%d %H:%M:%S') if item.get('timestamp') else 'N/A'}")
                    
                    # Symptoms section
                    if item.get('symptoms'):
                        st.markdown("**Symptoms:**")
                        for symptom in item['symptoms']:
                            st.markdown(f"- {symptom}")
                    
                    # Possible causes section
                    if item.get('possible_causes') and item.get('disease_detected'):
                        st.markdown("**Possible Causes:**")
                        for cause in item['possible_causes']:
                            st.markdown(f"- {cause}")
                    
                    # Treatment recommendations section
                    if item.get('treatment') and item.get('disease_detected'):
                        st.markdown("**Treatment Recommendations:**")
                        for treat in item['treatment']:
                            st.markdown(f"- {treat}")
    else:
        st.info("No analysis history available yet. Perform some analyses to see data here.")
    
except Exception as e:
    st.error(f"Error loading analytics dashboard: {str(e)}")
    st.info("The analytics dashboard is temporarily unavailable. Please try again later.")

