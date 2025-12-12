# Predict API Usage

API endpoint untuk prediksi road damage menggunakan YOLO model.

## Endpoints

### 1. Prediksi Gambar (dengan gambar hasil)
**Endpoint:** `POST /api/predict/image`

**Deskripsi:** Upload gambar dan mendapatkan gambar dengan anotasi bounding box serta metadata di header response.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (image file)

**Response:**
- Content-Type: image/jpeg
- Body: Gambar dengan bounding box
- Headers:
  - `X-Total-Detections`: Jumlah total deteksi
  - `X-Processing-Time`: Waktu proses (detik)
  - `X-Image-Width`: Lebar gambar
  - `X-Image-Height`: Tinggi gambar

**Contoh cURL:**
```bash
curl -X POST "http://localhost:8000/api/predict/image" \
  -H "accept: image/jpeg" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg" \
  -o result_image.jpg
```

**Contoh Python:**
```python
import requests

url = "http://localhost:8000/api/predict/image"
files = {"file": open("image.jpg", "rb")}
response = requests.post(url, files=files)

# Save the annotated image
with open("result.jpg", "wb") as f:
    f.write(response.content)

# Get metadata from headers
print(f"Total detections: {response.headers.get('X-Total-Detections')}")
print(f"Processing time: {response.headers.get('X-Processing-Time')} seconds")
```

---

### 2. Prediksi Gambar (JSON saja)
**Endpoint:** `POST /api/predict/image/json`

**Deskripsi:** Upload gambar dan mendapatkan hasil deteksi dalam format JSON tanpa gambar.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (image file)

**Response:**
```json
{
  "detections": [
    {
      "class_id": 0,
      "class_name": "D00",
      "confidence": 0.95,
      "bbox": [100.5, 150.2, 200.8, 250.3]
    }
  ],
  "total_detections": 1,
  "image_width": 1920,
  "image_height": 1080,
  "processing_time": 0.234
}
```

**Contoh cURL:**
```bash
curl -X POST "http://localhost:8000/api/predict/image/json" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg"
```

**Contoh Python:**
```python
import requests

url = "http://localhost:8000/api/predict/image/json"
files = {"file": open("image.jpg", "rb")}
response = requests.post(url, files=files)

data = response.json()
print(f"Total detections: {data['total_detections']}")
for det in data['detections']:
    print(f"Class: {det['class_name']}, Confidence: {det['confidence']:.2f}")
```

---

### 3. Prediksi Video
**Endpoint:** `POST /api/predict/video`

**Deskripsi:** Upload video dan mendapatkan video dengan anotasi bounding box serta metadata di header response.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (video file - mp4, avi, mov, mkv, flv, wmv, webm)

**Response:**
- Content-Type: video/mp4
- Body: Video dengan bounding box
- Headers:
  - `X-Total-Detections`: Jumlah total deteksi di semua frame
  - `X-Total-Frames`: Jumlah total frame
  - `X-FPS`: Frame per second
  - `X-Width`: Lebar video
  - `X-Height`: Tinggi video

**Contoh cURL:**
```bash
curl -X POST "http://localhost:8000/api/predict/video" \
  -H "accept: video/mp4" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/video.mp4" \
  -o result_video.mp4
```

**Contoh Python:**
```python
import requests

url = "http://localhost:8000/api/predict/video"
files = {"file": open("video.mp4", "rb")}
response = requests.post(url, files=files)

# Save the annotated video
with open("result_video.mp4", "wb") as f:
    f.write(response.content)

# Get metadata from headers
print(f"Total detections: {response.headers.get('X-Total-Detections')}")
print(f"Total frames: {response.headers.get('X-Total-Frames')}")
print(f"FPS: {response.headers.get('X-FPS')}")
```

---

## Response Models

### DetectionResult
```python
{
    "class_id": int,        # ID kelas deteksi
    "class_name": str,      # Nama kelas (contoh: "D00", "D10", dll)
    "confidence": float,    # Confidence score (0-1)
    "bbox": [x1, y1, x2, y2]  # Koordinat bounding box
}
```

### PredictionResponse
```python
{
    "detections": List[DetectionResult],  # List hasil deteksi
    "total_detections": int,              # Jumlah total deteksi
    "image_width": int,                   # Lebar gambar
    "image_height": int,                  # Tinggi gambar
    "processing_time": float              # Waktu proses (detik)
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "File must be an image"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error processing image: [error message]"
}
```

---

## Catatan

1. **Model Path**: Model YOLO di-load dari `app.core.model` yang menggunakan path `./../../../model/YOLOv8_Small_RDD.pt`
2. **Video Processing**: Video diproses frame-by-frame, jadi video yang panjang akan membutuhkan waktu lebih lama
3. **Temporary Files**: Untuk video, sistem menggunakan temporary files yang otomatis dibersihkan setelah proses selesai
4. **Supported Formats**:
   - Images: jpg, jpeg, png, bmp, webp, dll (semua format yang didukung OpenCV)
   - Videos: mp4, avi, mov, mkv, flv, wmv, webm

---

## Testing dengan Swagger UI

Setelah server berjalan, buka browser dan akses:
```
http://localhost:8000/docs
```

Di sana Anda bisa mencoba semua endpoint dengan interface yang user-friendly.

