#pip install insightface[mxnet]
#pip install onnxruntime-gpu
#ِDocument: https://github.com/deepinsight/insightface/tree/master/python-package
# مدل های دانلود شامل وظایف مختلف میشوند و باید وظایف اضافی پاک شوند
import cv2
from insightface.app import FaceAnalysis
from insightface.data import get_image as ins_get_image
import torch
import onnxruntime as ort
from faceDB import FaceDB
import time
import numpy as np

# #print(torch.cuda.is_available())
# #print(torch.cuda.device_count())
# #print(torch.cuda.get_device_name(0))
# #print("Available Execution Providers:", ort.get_available_providers())

# app = FaceAnalysis( name='buffalo_l', 
#                     providers=['CUDAExecutionProvider'],
#                     model_fp16=True,         # enable FP16
#                     )

# app = FaceAnalysis( name='buffalo_m', 
#                     providers=['CUDAExecutionProvider'],
#                     root=r'C:\Users\amirh\Desktop\vision dost mohammadi'
#                     )

app = FaceAnalysis( name='buffalo_s', 
                    providers=['CUDAExecutionProvider'],
                    root=r'./',
                    )

#app = FaceAnalysis(name='scrfd_2.5g')  
app.prepare(ctx_id=0, det_size=(512, 512))       #ctx_idx = 0 means first GPU

cap = cv2.VideoCapture(0) 

# face_db = FaceDB('face_db.db')
face_db = FaceDB('face_db_s.db')
face_db.load_embeddings()
# face_db.add_person('amir', 28, other_info='')
fps_list = []
while True:
    # ret, frame = cap.read(
    ret = True
    img_path = r'C:\Users\Dorsa-Co\Pictures\Capture.png'
    frame = cv2.imread(img_path)

    if not ret:
        break
    
    t = time.time()

def procceess(frame):
    
    faces = app.get(frame)


    t = time.time() - t
    fps = round(1/t, 1)
    fps_list.append(fps)
    if len(fps_list) > 100:
        fps_list.pop(0)

    #print(np.array(fps_list).mean(),'  ', t)

    
    for face in faces:
        bbox = face.bbox.astype(int)
        if face.embedding is not None:
            info , _= face_db.identify_face(face.embedding)
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0,255,0), 2)
        
        name = info['name']  # info dictionary from your FaceDB
        if name == 'Unknown':
            pass
        

        (font_width, font_height), baseline = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)

        # Position for text and background rectangle
        text_x, text_y = bbox[0], bbox[1] - 10
        rect_top_left = (text_x, text_y - font_height - baseline)
        rect_bottom_right = (text_x + font_width, text_y + baseline)

        # Draw filled rectangle (background)
        cv2.rectangle(frame, rect_top_left, rect_bottom_right, (0, 255, 0), thickness=-1)  # green background

        # Draw text on top
        cv2.putText(frame, name, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)  # black text


        #face_db.add_embedding(1, face.embedding)
        # for (x, y) in face.kps.astype(int):
        #     cv2.circle(frame, (x, y), 2, (0,0,255), -1)
    
   
    cv2.imshow("SCRFD Face Detection", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
