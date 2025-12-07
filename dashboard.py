import streamlit as st
import sqlite3
import json
from datetime import datetime
import base64
import io

# Set Streamlit theme to light and wide mode
st.set_page_config(
    page_title="Leaf Disease Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
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
    
    /* Metric cards */
    .metric-card {
        background: rgba(255,255,255,0.95);
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(44,62,80,0.10);
        padding: 1.5em;
        margin-bottom: 1.5em;
        transition: box-shadow 0.3s, transform 0.3s;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    
    .metric-card:hover {
        box-shadow: 0 8px 32px rgba(44,62,80,0.18);
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1b5e20;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 1.1rem;
        color: #616161;
        margin-top: 0.5rem;
    }
    
    /* Chart containers */
    .chart-container {
        background: rgba(255,255,255,0.95);
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(44,62,80,0.10);
        padding: 1.5em;
        margin-bottom: 1.5em;
        border: 1px solid #e0e0e0;
    }
    
    /* Sidebar styling */
    [data-testid=stSidebar] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: linear-gradient(90deg, #1b5e20 0%, #2e7d32 100%);
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Professional header
st.markdown("""
    <div class="header-container">
        <h1>📊 Leaf Disease Analytics Dashboard</h1>
        <p>Comprehensive Insights into Plant Health Analysis Patterns</p>
    </div>
""", unsafe_allow_html=True)

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
                disease_detected BOOLEAN NOT NULL,
                disease_name TEXT,
                disease_type TEXT,
                severity TEXT,
                confidence REAL,
                symptoms TEXT,
                possible_causes TEXT,
                treatment TEXT,
                image_filename TEXT
            )
        ''')
        conn.commit()
        return conn
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

# Fetch statistics from database
def fetch_statistics():
    try:
        conn = get_db_connection()
        if not conn:
            return {}
            
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
        
        # Recent analyses for trend analysis
        cursor.execute('''
            SELECT date(timestamp) as date, COUNT(*) as count
            FROM analysis_history 
            WHERE date(timestamp) >= date('now', '-30 days')
            GROUP BY date(timestamp)
            ORDER BY date(timestamp)
        ''')
        daily_trend = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_analyses': total,
            'disease_detections': diseases,
            'healthy_plants': healthy,
            'invalid_images': invalid,
            'disease_distribution': dict(disease_types),
            'daily_trend': daily_trend
        }
    except Exception as e:
        st.error(f"Error fetching statistics: {str(e)}")
        return {}

# Fetch recent analyses from database with all required fields
def fetch_recent_analyses(limit=50):
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

# Sidebar with filters
with st.sidebar:
    st.header("📊 Dashboard Controls")
    st.markdown("---")
    
    # Date range selector
    st.subheader("📅 Date Range")
    date_options = ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"]
    selected_range = st.selectbox("Select Period", date_options, index=1)
    
    # Get date range values
    if selected_range == "Last 7 Days":
        days_back = 7
    elif selected_range == "Last 30 Days":
        days_back = 30
    elif selected_range == "Last 90 Days":
        days_back = 90
    else:
        days_back = 365*10  # All time
    
    st.markdown("---")
    
    st.subheader("ℹ️ About This Dashboard")
    st.markdown("""
    This dashboard provides comprehensive analytics on plant disease detection patterns:
    
    - **Trend Analysis**: Monitor disease occurrences over time
    - **Distribution Charts**: Understand disease type prevalence
    - **Performance Metrics**: Track system accuracy and usage
    """)
    
    st.markdown("---")
    
    st.subheader("📥 Export Data")
    if st.button("Download Analysis Data (CSV)"):
        analyses = fetch_recent_analyses(1000)
        if analyses:
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
            st.markdown(href, unsafe_allow_html=True)
            st.success("CSV export ready! Click the link to download.")
        else:
            st.warning("No data available for export")
    
    if st.button("Download Analysis Report (PDF)"):
        st.info("Generating PDF report... This may take a moment.")
        # Try to import required libraries early to catch import errors
        libraries_imported = True
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            import io
            import requests
            from PIL import Image as PILImage
        except ImportError as ie:
            st.error(f"PDF export failed: Missing library '{getattr(ie, 'name', str(ie))}'. Please install required libraries: pip install reportlab pillow")
            libraries_imported = False
        
        if libraries_imported:
            try:
                analyses = fetch_recent_analyses(30)  # Limit for performance
                if analyses:
                    # Create PDF in memory
                    pdf_buffer = io.BytesIO()
                    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
                    styles = getSampleStyleSheet()
                    story = []
                    
                    # Title
                    title_style = ParagraphStyle(
                        'DashboardTitle',
                        parent=styles['Heading1'],
                        fontSize=26,
                        spaceAfter=30,
                        textColor=colors.darkgreen,
                        alignment=1  # Center alignment
                    )
                    story.append(Paragraph("Leaf Disease Detection Analytics Report", title_style))
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
                    
                    # Generate date
                    from datetime import datetime
                    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
                    story.append(Spacer(1, 0.3*inch))
                    
                    # Summary Section
                    story.append(Paragraph("Executive Summary", styles['Heading2']))
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
                    for i, analysis in enumerate(analyses[:15]):  # Limit to first 15 for reasonable PDF size
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
                    href = f'<a href="data:application/pdf;base64,{b64}" download="leaf_disease_dashboard_report.pdf">Download PDF Report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("PDF report ready! Click the link to download.")
                else:
                    st.warning("No data available for PDF report")
            except Exception as e:
                st.error(f"PDF export failed: {str(e)}")

# Main dashboard content
stats = fetch_statistics()
analyses = fetch_recent_analyses(100)

# If no data, create some sample data for demonstration
if not stats.get('total_analyses', 0) and not analyses:
    # Sample statistics for demonstration
    stats = {
        'total_analyses': 10,
        'disease_detections': 7,
        'healthy_plants': 3,
        'invalid_images': 0,
        'disease_distribution': {
            'fungal': 3,
            'pest': 2,
            'bacterial': 2
        },
        'daily_trend': [
            ('2025-12-01', 2),
            ('2025-12-02', 1),
            ('2025-12-03', 3),
            ('2025-12-04', 1),
            ('2025-12-05', 2),
            ('2025-12-06', 1),
            ('2025-12-07', 3)
        ]
    }
    
    # Sample analyses for demonstration
    analyses = [
        {
            'id': 1,
            'timestamp': '2025-12-07 15:30:00',
            'disease_detected': True,
            'disease_name': 'Powdery Mildew',
            'disease_type': 'fungal',
            'severity': 'moderate',
            'confidence': 85.5,
            'symptoms': ['White powdery spots', 'Yellowing leaves'],
            'possible_causes': ['High humidity', 'Poor air circulation'],
            'treatment': ['Apply fungicide', 'Improve ventilation'],
            'image_filename': 'sample1.jpg'
        },
        {
            'id': 2,
            'timestamp': '2025-12-07 16:45:00',
            'disease_detected': True,
            'disease_name': 'Aphid Infestation',
            'disease_type': 'pest',
            'severity': 'mild',
            'confidence': 92.0,
            'symptoms': ['Small green insects', 'Sticky residue'],
            'possible_causes': ['Nearby infested plants', 'Lack of predators'],
            'treatment': ['Introduce ladybugs', 'Spray with insecticidal soap'],
            'image_filename': 'sample2.jpg'
        },
        {
            'id': 3,
            'timestamp': '2025-12-07 14:20:00',
            'disease_detected': False,
            'disease_name': '',
            'disease_type': 'healthy',
            'severity': '',
            'confidence': 95.0,
            'symptoms': [],
            'possible_causes': [],
            'treatment': [],
            'image_filename': 'sample3.jpg'
        }
    ]

if stats and analyses:
    # Key Metrics
    st.markdown("<h2 style='text-align: center; color: #1b5e20; margin: 2rem 0;'>🔑 Key Performance Metrics</h2>", unsafe_allow_html=True)
    
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
                <div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Create tabs for different views (removed Trends tab)
    tab1, tab2 = st.tabs(["🥧 Distribution", "📋 Data Table"])
    
    with tab1:
        # Disease Distribution
        st.markdown("<h3 style='color: #1b5e20; margin: 1rem 0;'>Disease Type Distribution</h3>", unsafe_allow_html=True)
        
        disease_dist = stats.get('disease_distribution', {})
        
        if disease_dist:
            # Create pie chart using Streamlit's native components instead of raw HTML
            st.subheader("Disease Type Distribution")
            
            # Display disease distribution as simple cards
            cols = st.columns(len(disease_dist))
            total = sum(disease_dist.values())
            
            colors = ['#4caf50', '#2196f3', '#ff9800', '#f44336', '#9c27b0', '#00bcd4', '#8bc34a', '#ffc107']
            
            for i, (col, (disease, count)) in enumerate(zip(cols, disease_dist.items())):
                percentage = (count / total) * 100 if total > 0 else 0
                color = colors[i % len(colors)]
                
                with col:
                    st.markdown(f"""
                        <div style='background: {color}; border-radius: 10px; padding: 1rem; text-align: center; color: white;'>
                            <div style='font-size: 1.5rem; font-weight: bold;'>{percentage:.0f}%</div>
                            <div style='font-size: 1rem; margin-top: 0.5rem;'>{disease.title()}</div>
                            <div style='font-size: 0.9rem; margin-top: 0.2rem;'>{count}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Bar chart using Streamlit's progress bars
            st.subheader("Disease Type Frequency")
            
            max_count = max(disease_dist.values()) if disease_dist.values() else 1
            
            for disease, count in disease_dist.items():
                percentage = (count / max_count) * 100 if max_count > 0 else 0
                st.markdown(f"**{disease.title()}** ({count})", unsafe_allow_html=True)
                st.progress(percentage / 100)
                
        else:
            st.info("No disease distribution data available yet.")

        # Severity Distribution
        st.subheader("Severity Level Distribution")
        
        if analyses:
            # Filter only diseased plants
            diseased_analyses = [a for a in analyses if a['disease_detected']]
            if diseased_analyses:
                severity_counts = {}
                for analysis in diseased_analyses:
                    severity = analysis['severity']
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                # Display severity distribution as simple cards
                cols = st.columns(len(severity_counts))
                total = sum(severity_counts.values())
                
                severity_colors = {'mild': '#81c784', 'moderate': '#ffb74d', 'severe': '#e57373'}
                
                for col, (severity, count) in zip(cols, severity_counts.items()):
                    percentage = (count / total) * 100 if total > 0 else 0
                    color = severity_colors.get(severity, '#9e9e9e')
                    
                    with col:
                        st.markdown(f"""
                            <div style='background: {color}; border-radius: 10px; padding: 1rem; text-align: center; color: white;'>
                                <div style='font-size: 1.5rem; font-weight: bold;'>{percentage:.0f}%</div>
                                <div style='font-size: 1rem; margin-top: 0.5rem;'>{severity.title()}</div>
                                <div style='font-size: 0.9rem; margin-top: 0.2rem;'>{count}</div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No severity data available yet.")

    with tab2:
        # Data Table
        st.markdown("<h3 style='color: #1b5e20; margin: 1rem 0;'>Detailed Analysis Records</h3>", unsafe_allow_html=True)
        
        if analyses:
            # Create a simple table using Streamlit
            for i, analysis in enumerate(analyses[:20]):  # Limit to first 20 for performance
                # Alternate background colors
                bg_color = "#ffffff" if i % 2 == 0 else "#f8f9fa"
                
                # Determine status text and styling
                if analysis.get('disease_type') == 'invalid_image':
                    status_text = "⚠️ Invalid"
                    status_color = "#ffebee"
                    status_text_color = "#c62828"
                    border_color = "#c62828"
                elif analysis.get('disease_detected'):
                    status_text = f"🦠 {analysis.get('disease_name', 'Unknown Disease')}"
                    status_color = "#ffebee"
                    status_text_color = "#c62828"
                    border_color = "#c62828"
                else:
                    status_text = "✅ Healthy"
                    status_color = "#e8f5e9"
                    status_text_color = "#2e7d32"
                    border_color = "#2e7d32"
                
                # Confidence styling
                confidence = analysis.get('confidence', 0)
                if confidence >= 90:
                    confidence_color = "#2e7d32"
                elif confidence >= 70:
                    confidence_color = "#f57c00"
                else:
                    confidence_color = "#c62828"
                
                # Create expandable section for each analysis
                with st.expander(f"Analysis #{analysis.get('id', i+1)}: {analysis.get('image_filename', 'N/A')}"):
                    # Main analysis details in a structured format
                    st.subheader("Analysis Details")
                    
                    # Status
                    st.markdown(f"**Status:** {status_text}")
                    
                    # Key metrics in columns
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Type:** {analysis.get('disease_type', 'N/A').title()}")
                    with col2:
                        st.markdown(f"**Severity:** {analysis.get('severity', 'N/A').title() if analysis.get('severity') else 'N/A'}")
                    with col3:
                        st.markdown(f"**Confidence:** {confidence:.1f}%")
                    
                    st.markdown(f"**Filename:** {analysis.get('image_filename', 'N/A')}")
                    st.markdown(f"**Timestamp:** {datetime.fromisoformat(analysis['timestamp']).strftime('%Y-%m-%d %H:%M:%S') if analysis.get('timestamp') else 'N/A'}")
                    
                    # Symptoms section
                    if analysis.get('symptoms'):
                        st.subheader("Symptoms:")
                        for symptom in analysis.get('symptoms', []):
                            st.markdown(f"- {symptom}")
                    else:
                        st.info("No symptoms recorded")
                    
                    # Possible causes section
                    if analysis.get('possible_causes'):
                        st.subheader("Possible Causes:")
                        for cause in analysis.get('possible_causes', []):
                            st.markdown(f"- {cause}")
                    else:
                        st.info("No possible causes recorded")
                    
                    # Treatment section
                    if analysis.get('treatment'):
                        st.subheader("Treatment Recommendations:")
                        for treatment in analysis.get('treatment', []):
                            st.markdown(f"- {treatment}")
                    else:
                        st.info("No treatment recommendations recorded")
                    
                    # Image display (if available)
                    st.subheader("Image Preview")
                    
                    # Try to display the actual image if it exists
                    image_filename = analysis.get('image_filename', '')
                    if image_filename:
                        # Assuming images are stored in an 'uploads' directory
                        image_path = f"uploads/{image_filename}"
                        try:
                            # Check if the image file exists
                            import os
                            if os.path.exists(image_path):
                                st.image(image_path, caption=image_filename, use_column_width=True)
                            else:
                                # If the image doesn't exist in the uploads folder, show placeholder
                                st.info("Actual image not found. Displaying placeholder.")
                                st.image("https://placehold.co/300x200?text=Leaf+Image+Preview", caption=image_filename, use_column_width=True)
                        except Exception as e:
                            # If there's any error, show placeholder
                            st.warning(f"Could not load image: {str(e)}")
                            st.image("https://placehold.co/300x200?text=Leaf+Image+Preview", caption=image_filename, use_column_width=True)
                    else:
                        st.info("No image available for this analysis.")

            # Add pagination info
            if len(analyses) > 20:
                st.info(f"Showing first 20 of {len(analyses)} records. Contact administrator for full dataset.")
        else:
            st.info("No analysis data available yet.")
else:
    st.error("Unable to load dashboard data. Please check the database connection.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #616161; padding: 1rem;'>Leaf Disease Detection Analytics Dashboard | Powered by AI Vision Technology</div>", unsafe_allow_html=True)