import tempfile
import os
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
from typing import List, Dict, Any
from pydantic import BaseModel

from app.core.model import model

router = APIRouter(tags=["predict"], prefix="/predict")


class DetectionResult(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]


class PredictionResponse(BaseModel):
    detections: List[DetectionResult]
    total_detections: int
    image_width: int
    image_height: int
    processing_time: float


def is_video_file(filename: str) -> bool:
    """Check if the file is a video based on extension"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
    return Path(filename).suffix.lower() in video_extensions


def process_image(image: np.ndarray) -> tuple[np.ndarray, List[DetectionResult], float]:
    """Process a single image and return annotated image with detections"""
    import time

    start_time = time.time()

    # Run YOLO prediction
    results = model(image)

    processing_time = time.time() - start_time

    # Get annotated image
    annotated_image = results[0].plot()

    # Extract detection results
    detections = []
    for result in results[0].boxes:
        detection = DetectionResult(
            class_id=int(result.cls[0]),
            class_name=results[0].names[int(result.cls[0])],
            confidence=float(result.conf[0]),
            bbox=result.xyxy[0].tolist()
        )
        detections.append(detection)

    return annotated_image, detections, processing_time


@router.get("/test")
async def test():
    return {"message": "Test endpoint works!"}

@router.post("/image", response_model=Dict[str, Any])
async def predict_image(file: UploadFile = File(...)):
    """
    Predict road damage on an uploaded image
    Returns annotated image and detection results
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read image file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Process image
        annotated_image, detections, processing_time = process_image(image)

        # Encode annotated image to bytes
        _, buffer = cv2.imencode('.jpg', annotated_image)
        image_bytes = buffer.tobytes()

        # Return image as streaming response with metadata in headers
        response = StreamingResponse(
            iter([image_bytes]),
            media_type="image/jpeg",
            headers={
                "X-Total-Detections": str(len(detections)),
                "X-Processing-Time": str(processing_time),
                "X-Image-Width": str(image.shape[1]),
                "X-Image-Height": str(image.shape[0])
            }
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@router.post("/image/json", response_model=PredictionResponse)
async def predict_image_json(file: UploadFile = File(...)):
    """
    Predict road damage on an uploaded image
    Returns only JSON detection results without image
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read image file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Process image
        _, detections, processing_time = process_image(image)

        # Return JSON response
        return PredictionResponse(
            detections=detections,
            total_detections=len(detections),
            image_width=image.shape[1],
            image_height=image.shape[0],
            processing_time=processing_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@router.post("/video")
async def predict_video(file: UploadFile = File(...)):
    """
    Predict road damage on an uploaded video
    Returns annotated video
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("video/"):
        if not is_video_file(file.filename or ""):
            raise HTTPException(status_code=400, detail="File must be a video")

    try:
        # Save uploaded video to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_input:
            contents = await file.read()
            temp_input.write(contents)
            temp_input_path = temp_input.name

        # Create temporary output file
        temp_output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name

        try:
            # Open video
            cap = cv2.VideoCapture(temp_input_path)

            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_output_path, fourcc, fps, (width, height))

            total_detections = 0
            frame_count = 0

            # Process video frame by frame
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Run prediction
                results = model(frame)
                annotated_frame = results[0].plot()

                # Count detections
                total_detections += len(results[0].boxes)
                frame_count += 1

                # Write frame
                out.write(annotated_frame)

            # Release resources
            cap.release()
            out.release()

            # Read processed video
            with open(temp_output_path, 'rb') as f:
                video_bytes = f.read()

            # Return video with metadata in headers
            response = StreamingResponse(
                iter([video_bytes]),
                media_type="video/mp4",
                headers={
                    "X-Total-Detections": str(total_detections),
                    "X-Total-Frames": str(frame_count),
                    "X-FPS": str(fps),
                    "X-Width": str(width),
                    "X-Height": str(height)
                }
            )

            return response

        finally:
            # Clean up temporary files
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")
