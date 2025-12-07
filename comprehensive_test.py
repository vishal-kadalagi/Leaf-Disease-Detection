#!/usr/bin/env python3
"""
Comprehensive test script to verify all required imports for PDF export functionality
exactly as used in the application
"""

print("Testing PDF export library imports exactly as used in the application...")

# Test the exact imports used in main.py
errors_main = []

try:
    from reportlab.lib.pagesizes import letter, A4
    print("✓ main.py: reportlab.lib.pagesizes imported successfully")
except Exception as e:
    errors_main.append(f"reportlab.lib.pagesizes: {type(e).__name__}: {e}")

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    print("✓ main.py: reportlab.platypus imported successfully")
except Exception as e:
    errors_main.append(f"reportlab.platypus: {type(e).__name__}: {e}")

try:
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    print("✓ main.py: reportlab.lib.styles imported successfully")
except Exception as e:
    errors_main.append(f"reportlab.lib.styles: {type(e).__name__}: {e}")

try:
    from reportlab.lib.units import inch
    print("✓ main.py: reportlab.lib.units imported successfully")
except Exception as e:
    errors_main.append(f"reportlab.lib.units: {type(e).__name__}: {e}")

try:
    from reportlab.lib import colors
    print("✓ main.py: reportlab.lib.colors imported successfully")
except Exception as e:
    errors_main.append(f"reportlab.lib.colors: {type(e).__name__}: {e}")

try:
    import base64
    from io import BytesIO
    import requests
    from PIL import Image as PILImage
    import io
    print("✓ main.py: Other required libraries imported successfully")
except Exception as e:
    errors_main.append(f"Other libraries: {type(e).__name__}: {e}")

# Test the exact imports used in dashboard.py
errors_dashboard = []

try:
    from reportlab.lib.pagesizes import A4
    print("✓ dashboard.py: reportlab.lib.pagesizes imported successfully")
except Exception as e:
    errors_dashboard.append(f"reportlab.lib.pagesizes: {type(e).__name__}: {e}")

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    print("✓ dashboard.py: reportlab.platypus imported successfully")
except Exception as e:
    errors_dashboard.append(f"reportlab.platypus: {type(e).__name__}: {e}")

try:
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    print("✓ dashboard.py: reportlab.lib.styles imported successfully")
except Exception as e:
    errors_dashboard.append(f"reportlab.lib.styles: {type(e).__name__}: {e}")

try:
    from reportlab.lib.units import inch
    print("✓ dashboard.py: reportlab.lib.units imported successfully")
except Exception as e:
    errors_dashboard.append(f"reportlab.lib.units: {type(e).__name__}: {e}")

try:
    from reportlab.lib import colors
    print("✓ dashboard.py: reportlab.lib.colors imported successfully")
except Exception as e:
    errors_dashboard.append(f"reportlab.lib.colors: {type(e).__name__}: {e}")

try:
    import io
    import requests
    from PIL import Image as PILImage
    print("✓ dashboard.py: Other required libraries imported successfully")
except Exception as e:
    errors_dashboard.append(f"Other libraries: {type(e).__name__}: {e}")

# Summary
print("\n" + "="*60)
if errors_main:
    print("❌ Errors in main.py imports:")
    for error in errors_main:
        print(f"  - {error}")
else:
    print("✅ All main.py imports successful!")

if errors_dashboard:
    print("❌ Errors in dashboard.py imports:")
    for error in errors_dashboard:
        print(f"  - {error}")
else:
    print("✅ All dashboard.py imports successful!")

if not errors_main and not errors_dashboard:
    print("\n🎉 All imports successful! PDF export should work correctly.")
else:
    print("\n🔧 Please check the errors above and ensure all required packages are installed:")
    print("   pip install reportlab pillow")