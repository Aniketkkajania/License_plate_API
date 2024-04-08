import base64
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import easyocr

app = FastAPI()
reader = easyocr.Reader(['en'])

harcascade = "model/haarcascade_russian_plate_number.xml"
plate_cascade = cv2.CascadeClassifier(harcascade)
min_area = 500

def detect_plate(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)
    
    for (x,y,w,h) in plates:
        area = w * h
        if area > min_area:
            img_roi = img[y: y+h, x:x+w]
            return img_roi
    return None

def read_plate(img):
    result = reader.readtext(img)
    text = ' '.join([res[1] for res in result])
    return text

@app.post("/api/detect_and_extract_text")
async def detect_and_extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    plate_img = detect_plate(img)
    if plate_img is not None:
        _, img_encoded = cv2.imencode('.jpg', plate_img)
        img_base64 = base64.b64encode(img_encoded).decode("utf-8")  # Encode image as base64
        
        # Extract text from the detected plate image
        text = read_plate(plate_img).replace(' ', '')
        
        return {"plate_image": img_base64, "license_plate_text": text}

    return JSONResponse(status_code=404, content={"error": "No license plate detected"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5031)
