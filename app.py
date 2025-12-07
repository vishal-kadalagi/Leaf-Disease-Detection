from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from utils import convert_image_to_base64_and_test, test_with_base64_data
from database import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Leaf Disease Detection API", 
    version="2.0.0",
    description="Enterprise-grade AI-powered leaf disease detection system with history tracking"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/disease-detection-file', summary="Detect disease in leaf image", 
          description="Upload a leaf image file for comprehensive disease analysis")
async def disease_detection_file(file: UploadFile = File(...)):
    """
    Endpoint to detect diseases in leaf images using direct image file upload.
    Accepts multipart/form-data with an image file.
    """
    try:
        logger.info(f"Received image file for disease detection: {file.filename}")
        
        # Read uploaded file into memory
        contents = await file.read()
        
        # Process file directly from memory
        result = convert_image_to_base64_and_test(contents)
        
        # Save to database if valid result, including the image data
        if result is not None:
            db.save_analysis(result, file.filename, contents)
        
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to process image file")
        logger.info("Disease detection from file completed successfully")
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in disease detection (file): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/", summary="API Root", description="Root endpoint providing API information")
async def root():
    """Root endpoint providing API information"""
    return {
        "message": "Leaf Disease Detection API",
        "version": "2.0.0",
        "description": "Enterprise-grade AI-powered leaf disease detection system",
        "endpoints": {
            "disease_detection_file": "/disease-detection-file (POST, file upload)",
            "analysis_history": "/analysis-history (GET, retrieve analysis history)",
            "statistics": "/stats (GET, retrieve system statistics)"
        }
    }

@app.get("/analysis-history", summary="Get Analysis History", 
         description="Retrieve recent disease analysis history")
async def get_analysis_history(limit: int = 10):
    """Get recent analysis history"""
    try:
        history = db.get_recent_analyses(limit)
        return JSONResponse(content={"history": history})
    except Exception as e:
        logger.error(f"Error retrieving analysis history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/analysis-image/{analysis_id}", summary="Get Analysis Image", 
         description="Retrieve the image for a specific analysis")
async def get_analysis_image(analysis_id: int):
    """Get the image data for a specific analysis"""
    try:
        image_data = db.get_analysis_image(analysis_id)
        if image_data is None:
            raise HTTPException(status_code=404, detail="Image not found")
        return Response(content=image_data, media_type="image/jpeg")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/stats", summary="Get System Statistics", 
         description="Retrieve statistics about disease analysis")
async def get_statistics():
    """Get system statistics"""
    try:
        stats = db.get_analysis_stats()
        return JSONResponse(content={"statistics": stats})
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)