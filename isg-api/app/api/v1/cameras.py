from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, Response
from app.auth import require_admin_or_manager
import os
import mimetypes

router = APIRouter()

@router.get("/demo")
async def get_demo_camera_stream(current_user: dict = Depends(require_admin_or_manager)):
    """
    Stream demo video for cameras.
    Only accessible by ADMIN or MANAGER roles.
    """
    # Path to the demo video file
    video_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "videos", "demo.mp4")
    
    if not os.path.exists(video_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo video file not found"
        )
    
    # For demo purposes, return content even if it's not a real video
    # In production, you would use a real MP4 file
    try:
        file_size = os.path.getsize(video_path)
        
        # Read the file content
        with open(video_path, 'rb') as f:
            content = f.read()
        
        # Check if it's a real video file or demo content
        if content.startswith(b'\n'):  # Our demo text file
            # Return a response indicating this is a demo placeholder
            demo_content = "Demo video placeholder - Replace with actual MP4 file"
            return Response(
                content=demo_content,
                media_type="text/plain",
                headers={
                    "Content-Length": str(len(demo_content.encode())),
                    "X-Demo": "true"
                }
            )
        
        # Return as video stream
        def iter_file():
            with open(video_path, mode="rb") as file_like:
                while True:
                    chunk = file_like.read(1024 * 1024)  # Read 1MB chunks
                    if not chunk:
                        break
                    yield chunk
        
        return StreamingResponse(
            iter_file(),
            media_type="video/mp4",
            headers={
                "Content-Length": str(file_size),
                "Accept-Ranges": "bytes",
                "Content-Disposition": "inline; filename=demo.mp4"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error streaming video: {str(e)}"
        )