from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
import requests
import logging
from io import BytesIO
from PIL import Image
import os
import uuid
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.rate_limiter import limiter, get_utility_rate_limit

load_dotenv()

logger = logging.getLogger(__name__)

utility_router = APIRouter(prefix='/proxy', tags=['utilities'])

@utility_router.get('/image')
@limiter.limit(get_utility_rate_limit("proxy_image"))
async def proxy_image(request: Request, response: Response, url: str = Query(..., description="Image URL to proxy")):
    """Proxy for images to bypass CORS issues"""
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter required")
        
    try:
        logger.info(f"Proxying image request to: {url}")
        response = requests.get(url, stream=True, timeout=5)
        response.raise_for_status()
        
        # Get content type
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        
        # Create streaming response
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                yield chunk
        
        return StreamingResponse(
            generate(),
            status_code=response.status_code,
            media_type=content_type
        )
    except Exception as e:
        logger.error(f"Error proxying image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@utility_router.get('/check-image')
@limiter.limit(get_utility_rate_limit("check_image"))
async def check_image(request: Request, response: Response, url: str = Query(..., description="Image URL to check")):
    """Check if an image URL is accessible"""
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter required")
        
    try:
        logger.info(f"Checking image URL: {url}")
        response = requests.head(url, timeout=5)
        
        return {
            "url": url,
            "status": response.status_code,
            "content_type": response.headers.get('Content-Type', 'unknown'),
            "content_length": response.headers.get('Content-Length', 'unknown'),
            "accessible": response.status_code == 200
        }
    except Exception as e:
        logger.error(f"Error checking image: {str(e)}")
        return {
            "url": url,
            "error": str(e),
            "accessible": False
        }

@utility_router.get('/direct-image')
@limiter.limit(get_utility_rate_limit("direct_image"))
async def generate_direct_image(request: Request, response: Response, prompt: str = Query('A beautiful 3D rendered educational concept', description="Image generation prompt")):
    """Generate an image directly and return it to the browser"""
    try:
        # Get API key
        api_key = os.environ.get('API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="API_KEY not set in environment")
            
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        
        # Generate the image
        logger.info(f"Generating direct image with prompt: {prompt}")
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        
        # Process the response
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # Extract the image data
                image_data = part.inline_data.data
                
                # Create image from BytesIO
                image = Image.open(BytesIO(image_data))
                img_io = BytesIO()
                image.save(img_io, 'PNG')
                img_io.seek(0)
                
                # Return the image as streaming response
                return StreamingResponse(img_io, media_type="image/png")
        
        # No image found in response
        raise HTTPException(status_code=500, detail="No image was generated")
        
    except Exception as e:
        logger.error(f"Error generating direct image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
