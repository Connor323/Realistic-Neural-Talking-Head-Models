import cv2
import random
import face_alignment
from matplotlib import pyplot as plt
plt.switch_backend('agg')
import numpy as np
import glob 
from os import path as osp 

def select_frames(video_path, K):
    cap = cv2.VideoCapture(video_path)
    
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    #unused
    #w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    if n_frames <= K: #There are not enough frames in the video
        rand_frames_idx = [1]*n_frames
    else:
        rand_frames_idx = [0]*n_frames
        i = 0
        while(i < K):
            idx = random.randint(0, n_frames-1)
            if rand_frames_idx[idx] == 0:
                rand_frames_idx[idx] = 1
                i += 1
    
    frames_list = []
    
    # Read until video is completed or no frames needed
    ret = True
    frame_idx = 0
    while(ret and frame_idx < n_frames):
        ret, frame = cap.read()
        
        if ret and rand_frames_idx[frame_idx] == 1:
            RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames_list.append(RGB)
            
        frame_idx += 1

    cap.release()
    
    return frames_list

def select_frames_new(video_path, K):
    files = sorted(glob.glob(osp.join(video_path, "*.jpg")))
    
    n_frames = len(files)
    #unused
    #w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    if n_frames <= K: #There are not enough frames in the video
        rand_frames_idx = [1]*n_frames
    else:
        rand_frames_idx = [0]*n_frames
        i = 0
        while(i < K):
            idx = random.randint(0, n_frames-1)
            if rand_frames_idx[idx] == 0:
                rand_frames_idx[idx] = 1
                i += 1
    
    frames_list = []
    
    # Read until video is completed or no frames needed
    frame_idx = 0
    while(frame_idx < n_frames):
        frame = cv2.imread(files[frame_idx])
        
        if rand_frames_idx[frame_idx] == 1:
            RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            RGB = cv2.resize(RGB, (224, 224))
            frames_list.append(RGB)
            
        frame_idx += 1
    return frames_list


def generate_landmarks(frames_list):
    frame_landmark_list = []
    fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False, device ='cuda:0')
    
    for i in range(len(frames_list)):
        try:
            input = frames_list[i]
            preds = fa.get_landmarks(input)[0]

            dpi = 100
            fig = plt.figure(figsize=(input.shape[1]/dpi, input.shape[0]/dpi), dpi = dpi)
            ax = fig.add_subplot(1,1,1)
            ax.imshow(np.ones(input.shape))
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

            #chin
            ax.plot(preds[0:17,0],preds[0:17,1],marker='',markersize=5,linestyle='-',color='green',lw=2)
            #left and right eyebrow
            ax.plot(preds[17:22,0],preds[17:22,1],marker='',markersize=5,linestyle='-',color='orange',lw=2)
            ax.plot(preds[22:27,0],preds[22:27,1],marker='',markersize=5,linestyle='-',color='orange',lw=2)
            #nose
            ax.plot(preds[27:31,0],preds[27:31,1],marker='',markersize=5,linestyle='-',color='blue',lw=2)
            ax.plot(preds[31:36,0],preds[31:36,1],marker='',markersize=5,linestyle='-',color='blue',lw=2)
            #left and right eye
            ax.plot(preds[36:42,0],preds[36:42,1],marker='',markersize=5,linestyle='-',color='red',lw=2)
            ax.plot(preds[42:48,0],preds[42:48,1],marker='',markersize=5,linestyle='-',color='red',lw=2)
            #outer and inner lip
            ax.plot(preds[48:60,0],preds[48:60,1],marker='',markersize=5,linestyle='-',color='purple',lw=2)
            ax.plot(preds[60:68,0],preds[60:68,1],marker='',markersize=5,linestyle='-',color='pink',lw=2) 
            ax.axis('off')

            fig.canvas.draw()

            data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            
            data = cv2.resize(data, (224, 224))
            frame_landmark_list.append((input, data))
            plt.close(fig)
        except Exception as e:
            print(e)
            print('Error: Video corrupted or no landmarks visible')
    
    for i in range(len(frames_list) - len(frame_landmark_list)):
        #filling frame_landmark_list in case of error
        frame_landmark_list.append(frame_landmark_list[i])
    
    return frame_landmark_list