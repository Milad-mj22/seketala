
from __future__ import annotations
import cv2
# from insightface.app import FaceAnalysis
# from insightface.app.common import Face
# from insightface.data import get_image as ins_get_image
# import torch
# import onnxruntime as ort

# import time
# import numpy as np

# from cameras.ai.Face.faceDB import FaceDB
# from cameras.models import Embedding
# from cameras.models import Person


# cap = cv2.VideoCapture(0) 

# face_db = FaceDB('face_db_s.db')
# face_db.load_embeddings()



class AiFaceModule:
    def __init__(self):
        
        self.app = FaceAnalysis( name='buffalo_s', 
                            providers=['CUDAExecutionProvider'],
                            root=r'./',
                            )

        self.app.prepare(ctx_id=0, det_size=(512, 512))       #ctx_idx = 0 means first GPU

        self.load_embedings()

        pass


    def load_embedings(self):
        self.embeds = Embedding.objects.all()

        self.embeds_array = []

        for item in self.embeds:
            self.embeds_array.append(item.embedding)

        self.embeds_array =  np.array(self.embeds_array)

        return self.embeds_array


    def detection(self,frame:np.array):
        
        faces = self.app.get(frame)

        list_detected_obj = []

        for face in faces:
            bbox = face.bbox.astype(int)
            if face.embedding is not None:
                person , _= face_db.identify_face(face.embedding)

                if person is None:
                    self.save_temp_unknwon_persons(face.embedding)
                
                detect_obj  = DetectedPerson(person,bbox)
                list_detected_obj.append(detect_obj)
                # detect_obj.draw()

        frame = self.draw(frame=frame,list_person_detected=list_detected_obj)

        return  frame , list_detected_obj
    
    def save_temp_unknwon_persons(self, embedding):
        # create unknown person
        name = "unknown" + hash(embedding)
        new_person = Person.objects.create(
            name=name,
            age=-1,
            is_unknown=True
        )

        # save embedding for this person
        new_embedding = Embedding.objects.create(
            person=new_person,
            embedding=embedding
        )

        return new_person, new_embedding



    def draw(self,frame,list_person_detected:list[DetectedPerson]):

        for person_detected in list_person_detected:
            frame = person_detected.draw(frame=frame)
        
        return frame





    def identify_face(self, new_embedding, threshold=0.5):
        """
        Identify the person for a new embedding using cosine similarity.
        Returns person info and similarity score.
        """

        # Normalize embeddings
        new_emb_norm = new_embedding / np.linalg.norm(new_embedding)
        db_norm = self.embeds_array / np.linalg.norm(self.embeds_array, axis=1, keepdims=True)
        if len(self.embeds_array) == 0:
            return None, 0

        # Cosine similarity vectorized
        sims = np.dot(db_norm, new_emb_norm)
        best_idx = np.argmax(sims)
        best_score = sims[best_idx]

        if best_score >= threshold:
            best_person = self.embeds[best_idx].person
            return best_person, best_score
        else:
            return None, best_score



class DetectedPerson:

    def __init__(self,person,bbox):
        
        self.person = person
        self.bbox = bbox

    


    def draw(self,frame:np.array):
        

        name = 'Unknown'
        if self.person is not None:
            try:
                name = self.person.name
            except:
                print( "error in self.person")

        (font_width, font_height), baseline = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)

        # Position for text and background rectangle
        text_x, text_y = self.bbox[0], self.bbox[1] - 10
        rect_top_left = (text_x, text_y - font_height - baseline)
        rect_bottom_right = (text_x + font_width, text_y + baseline)

        # Draw filled rectangle (background)
        cv2.rectangle(frame, rect_top_left, rect_bottom_right, (0, 255, 0), thickness=-1)  # green background

        # Draw text on top
        cv2.putText(frame, name, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)  # black text

        return frame
    


class AiManager:
    def __init__(self):

        self.aiFaceModule =  AiFaceModule()

        pass

    def get_ai_face_module(self):
        return self.aiFaceModule
    
    def infrence_ai_face_module(self,frame:np.array):
        frame = self.aiFaceModule.detection(frame=frame)
        return frame


