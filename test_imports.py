#!/usr/bin/env python3
"""
Test script to verify all required imports for PDF export functionality
"""

print("Testing PDF export library imports...")

# Test individual imports
import_errors = []

try:
    from reportlab.lib.pagesizes import letter, A4
    print("✓ reportlab.lib.pagesizes imported successfully")
except ImportError as e:
    import_errors.append(f"reportlab.lib.pagesizes: {e}")

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    print("✓ reportlab.platypus imported successfully")
except ImportError as e:
    import_errors.append(f"reportlab.platypus: {e}")

try:
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    print("✓ reportlab.lib.styles imported successfully")
except ImportError as e:
    import_errors.append(f"reportlab.lib.styles: {e}")

try:
    from reportlab.lib.units import inch
    print("✓ reportlab.lib.units imported successfully")
except ImportError as e:
    import_errors.append(f"reportlab.lib.units: {e}")

try:
    from reportlab.lib import colors
    print("✓ reportlab.lib.colors imported successfully")
except ImportError as e:
    import_errors.append(f"reportlab.lib.colors: {e}")

try:
    import base64
    from io import BytesIO
    import requests
    from PIL import Image as PILImage
    import io
    print("✓ Other required libraries imported successfully")
except ImportError as e:
    import_errors.append(f"Other libraries: {e}")

if import_errors:
    print("\n❌ Import errors found:")
    for error in import_errors:
        print(f"  - {error}")
    print("\nPlease install missing packages:")
    print("pip install reportlab pillow")
else:
    print("\n✅ All imports successful!")