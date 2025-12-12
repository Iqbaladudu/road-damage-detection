"""
Example client untuk testing predict API endpoints
"""
import requests
from pathlib import Path


def test_predict_image_with_result(image_path: str, api_url: str = "http://localhost:8000"):
    """
    Test image prediction endpoint yang mengembalikan gambar dengan bounding box
    """
    url = f"{api_url}/api/predict/image"
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        # Save result image
        output_path = f"result_{Path(image_path).name}"
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Image prediction successful!")
        print(f"📁 Result saved to: {output_path}")
        print(f"📊 Total detections: {response.headers.get('X-Total-Detections')}")
        print(f"⏱️  Processing time: {response.headers.get('X-Processing-Time')} seconds")
        print(f"📐 Image size: {response.headers.get('X-Image-Width')}x{response.headers.get('X-Image-Height')}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Message: {response.text}")
        return False


def test_predict_image_json(image_path: str, api_url: str = "http://localhost:8000"):
    """
    Test image prediction endpoint yang mengembalikan JSON saja
    """
    url = f"{api_url}/api/predict/image/json"
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Image prediction (JSON) successful!")
        print(f"📊 Total detections: {data['total_detections']}")
        print(f"⏱️  Processing time: {data['processing_time']:.3f} seconds")
        print(f"📐 Image size: {data['image_width']}x{data['image_height']}")
        
        if data['detections']:
            print(f"\n🔍 Detections:")
            for i, det in enumerate(data['detections'], 1):
                print(f"  {i}. Class: {det['class_name']} (ID: {det['class_id']})")
                print(f"     Confidence: {det['confidence']:.2%}")
                print(f"     BBox: [{det['bbox'][0]:.1f}, {det['bbox'][1]:.1f}, {det['bbox'][2]:.1f}, {det['bbox'][3]:.1f}]")
        else:
            print("No detections found.")
        
        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Message: {response.text}")
        return None


def test_predict_video(video_path: str, api_url: str = "http://localhost:8000"):
    """
    Test video prediction endpoint
    """
    url = f"{api_url}/api/predict/video"
    
    print(f"⏳ Processing video (this may take a while)...")
    
    with open(video_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        # Save result video
        output_path = f"result_{Path(video_path).name}"
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        print(f"\n✅ Video prediction successful!")
        print(f"📁 Result saved to: {output_path}")
        print(f"📊 Total detections: {response.headers.get('X-Total-Detections')}")
        print(f"🎬 Total frames: {response.headers.get('X-Total-Frames')}")
        print(f"🎥 FPS: {response.headers.get('X-FPS')}")
        print(f"📐 Video size: {response.headers.get('X-Width')}x{response.headers.get('X-Height')}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Message: {response.text}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python example_client.py <image_path>")
        print("  python example_client.py <video_path>")
        print("\nExample:")
        print("  python example_client.py road_damage.jpg")
        print("  python example_client.py road_damage.mp4")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    # Check if it's an image or video
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
    is_video = Path(file_path).suffix.lower() in video_extensions
    
    if is_video:
        print(f"🎥 Testing video prediction with: {file_path}\n")
        test_predict_video(file_path)
    else:
        print(f"🖼️  Testing image prediction with: {file_path}\n")
        print("=" * 60)
        test_predict_image_with_result(file_path)
        print("\n" + "=" * 60)
        test_predict_image_json(file_path)

