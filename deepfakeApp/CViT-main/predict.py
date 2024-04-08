import sys, os
import cv2
from facenet_pytorch import MTCNN
import torch.nn.functional as F
import torch
import torch.nn as nn
import glob
import torch.optim as optim
import numpy as np
from time import perf_counter
from torchvision import transforms
import pandas as pd
import json
import face_recognition
import random
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(1, "helpers")
sys.path.insert(1, "model")
sys.path.insert(1, "weight")

from model.cvit import CViT
from helpers.helpers_read_video_1 import VideoReader
from helpers.helpers_face_extract_1 import FaceExtractor
from helpers.blazeface import BlazeFace

blazeface_path = os.path.join('E:\mjp-main\deepfakeApp\CViT-main\helpers', 'blazeface.pth')

def prediction(video_path):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    facedet = BlazeFace().to(device)
    facedet.load_weights(blazeface_path)
    facedet.load_anchors(os.path.join('E:\mjp-main\deepfakeApp\CViT-main\helpers', 'anchors.npy'))
    _ = facedet.train(False)

    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    normalize_transform = transforms.Compose([transforms.Normalize(mean, std)])

    tresh = 50
    mtcnn = MTCNN(select_largest=False, keep_all=True, post_process=False, device=device)

    # load cvit model
    model = CViT(
        image_size=224,
        patch_size=7,
        num_classes=2,
        channels=512,
        dim=1024,
        depth=6,
        heads=8,
        mlp_dim=2048,
    )
    model.to(device)

    checkpoint = torch.load(
        "E:\mjp-main\deepfakeApp\CViT-main\weight\deepfake_cvit_gpu_ep_50.pth", map_location=torch.device("cpu")
    )
    model.load_state_dict(checkpoint["state_dict"], strict=False)
    _ = model.eval()

    def predict(filename):
        store_faces = []

        face_tensor_face_rec = np.zeros((30, 224, 224, 3), dtype=np.uint8)

        cap = cv2.VideoCapture(filename)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        start_frame_number = 0
        frame_count = int(length * 0.1)
        frame_jump = 5

        loop = 0
        count_face_rec = 0

        while cap.isOpened() and loop < frame_count:
            loop += 1
            success, frame = cap.read()
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_number)

            if success:
                face_rec, count = face_face_rec(frame, face_tensor_face_rec)

                if len(face_rec) and count > 0:
                    kontrol = count_face_rec + count
                    for f in face_rec:
                        if count_face_rec <= kontrol and (count_face_rec < 29):
                            face_tensor_face_rec[count_face_rec] = f
                            count_face_rec += 1

                start_frame_number += frame_jump

        store_rec = face_tensor_face_rec[:count_face_rec]

        dfdc_tensor = store_rec
        dfdc_tensor = torch.tensor(dfdc_tensor, device=device).float()

        dfdc_tensor = dfdc_tensor.permute((0, 3, 1, 2))

        for i in range(len(dfdc_tensor)):
            dfdc_tensor[i] = normalize_transform(dfdc_tensor[i] / 255.0)

        if not len(
            non_empty(dfdc_tensor, df_len=-1, lower_bound=-1, upper_bound=-1, flag=False)
        ):
            return torch.tensor(0.5).item()

        dfdc_tensor = dfdc_tensor.contiguous()
        df_len = len(dfdc_tensor)

        with torch.no_grad():
            thrtw = 32
            if df_len < 33:
                thrtw = df_len
            y_predCViT = model(dfdc_tensor[0:thrtw])

            if df_len > 32:
                dft = non_empty(
                    dfdc_tensor, df_len, lower_bound=32, upper_bound=64, flag=True
                )
                if len(dft):
                    y_predCViT = pred_tensor(y_predCViT, model(dft))
            if df_len > 64:
                dft = non_empty(
                    dfdc_tensor, df_len, lower_bound=64, upper_bound=90, flag=True
                )
                if len(dft):
                    y_predCViT = pred_tensor(y_predCViT, model(dft))

            decCViT = pre_process_prediction(pred_sig(y_predCViT))
            print("CViT", filename, "Prediction:", decCViT.item())
            return decCViT.item()

    def non_empty(dfdc_tensor, df_len, lower_bound, upper_bound, flag):
        thrtw = df_len
        if df_len >= upper_bound:
            thrtw = upper_bound

        if flag == True:
            return dfdc_tensor[lower_bound:thrtw]
        elif flag == False:
            return dfdc_tensor

        return []

    def pred_sig(dfdc_tensor):
        return torch.sigmoid(dfdc_tensor.squeeze())

    def pred_tensor(dfdc_tensor, pre_tensor):
        return torch.cat((dfdc_tensor, pre_tensor), 0)

    def pre_process_prediction(y_pred):
        f = []
        r = []
        if len(y_pred) > 2:
            for i, j in y_pred:
                f.append(i)
                r.append(j)
            f_c = sum(f) / len(f)
            r_c = sum(r) / len(r)
            if f_c > r_c:
                return f_c
            else:
                r_c = abs(1 - r_c)
                return r_c
        else:
            return torch.tensor(0.5)

    predictions = predict(video_path)
    return predictions



