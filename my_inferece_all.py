import os
import sys
import pandas as pd
import numpy as np
from tqdm import tqdm as loop

args={
    "gpus":1,
    "model":'./weights/model_simulated_RGB_mgpu_scaling_append.0024.h5',
    "input_folder":"./input",
    "max":True,
    "average":False,
    "scale":[1.0]#,0.5,0.75]
}

import cv2
import math
import time
import numpy as np
import util
from config_reader import config_reader
from scipy.ndimage.filters import gaussian_filter
from keras.models import load_model
import code
import copy
import scipy.ndimage as sn
from PIL import Image
from tqdm import tqdm
from model_simulated_RGB101_cdcl_pascal import get_testing_model_resnet101
from human_seg.pascal_voc_human_seg_gt_7parts import human_seg_combine_argmax, human_seg_combine_argmax_rgb


human_part = [0,1,2,3,4,5,6]
human_ori_part = [0,1,2,3,4,5,6]
seg_num = 7 # current model supports 7 parts only
folder_name = "1_segment_results"
check_folder_name = "1_segmentation_check"

def recover_flipping_output(oriImg, part_ori_size):
    part_ori_size = part_ori_size[:, ::-1, :]
    part_flip_size = np.zeros((oriImg.shape[0], oriImg.shape[1], seg_num))
    part_flip_size[:,:,human_ori_part] = part_ori_size[:,:,human_part]
    return part_flip_size

def part_thresholding(seg_argmax):
    background = 0.6
    head = 0.5
    torso = 0.8 
    part_th = [background, head, torso, 0.55, 0.55, 0.55, 0.55]
    th_mask = np.zeros(seg_argmax.shape)
    for indx in range(seg_num):
        part_prediction = (seg_argmax==indx)
        part_prediction = part_prediction*part_th[indx]
        th_mask += part_prediction

    return th_mask

def process (oriImg, params, model_params):
    flipImg = cv2.flip(oriImg, 1)
    oriImg = (oriImg / 256.0) - 0.5
    flipImg = (flipImg / 256.0) - 0.5
    multiplier = [x for x in params['scale_search']]

    seg_avg = np.zeros((oriImg.shape[0], oriImg.shape[1], seg_num))

    segmap_scale1 = np.zeros((oriImg.shape[0], oriImg.shape[1], seg_num))
    segmap_scale2 = np.zeros((oriImg.shape[0], oriImg.shape[1], seg_num))
    segmap_scale3 = np.zeros((oriImg.shape[0], oriImg.shape[1], seg_num))
    segmap_scale4 = np.zeros((oriImg.shape[0], oriImg.shape[1], seg_num))

    segmap_scale5 = np.zeros((oriImg.shape[0], oriImg.shape[1], seg_num))
    segmap_scale6 = np.zeros((oriImg.shape[0], oriImg.shape[1], seg_num))
    segmap_scale7 = np.zeros((oriImg.shape[0], oriImg.shape[1], seg_num))
    segmap_scale8 = np.zeros((oriImg.shape[0], oriImg.shape[1], seg_num))

    for m in range(len(multiplier)):
        scale = multiplier[m]
        imageToTest = cv2.resize(oriImg, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        pad = [ 0,
                0, 
                (imageToTest.shape[0] - model_params['stride']) % model_params['stride'],
                (imageToTest.shape[1] - model_params['stride']) % model_params['stride']
              ]
        
        imageToTest_padded = np.pad(imageToTest, ((0, pad[2]), (0, pad[3]), (0, 0)), mode='constant', constant_values=((0, 0), (0, 0), (0, 0)))

        input_img = imageToTest[np.newaxis, ...]
        
        #print( "\t[Original] Actual size fed into NN: ", input_img.shape)

        output_blobs = model.predict(input_img)

        seg = np.squeeze(output_blobs[0])
        seg = cv2.resize(seg, (0, 0), fx=model_params['stride'], fy=model_params['stride'],
                             interpolation=cv2.INTER_CUBIC)
        seg = seg[:imageToTest_padded.shape[0] - pad[2], :imageToTest_padded.shape[1] - pad[3], :]
        seg = cv2.resize(seg, (oriImg.shape[1], oriImg.shape[0]), interpolation=cv2.INTER_CUBIC)


        if m==0:
            segmap_scale1 = seg
        elif m==1:
            segmap_scale2 = seg         
        elif m==2:
            segmap_scale3 = seg
        elif m==3:
            segmap_scale4 = seg


    # flipping
    for m in range(len(multiplier)):
        scale = multiplier[m]
        imageToTest = cv2.resize(flipImg, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        pad = [ 0,
                0, 
                (imageToTest.shape[0] - model_params['stride']) % model_params['stride'],
                (imageToTest.shape[1] - model_params['stride']) % model_params['stride']
              ]
        
        imageToTest_padded = np.pad(imageToTest, ((0, pad[2]), (0, pad[3]), (0, 0)), mode='constant', constant_values=((0, 0), (0, 0), (0, 0)))
        input_img = imageToTest[np.newaxis, ...]
        #print( "\t[Flipping] Actual size fed into NN: ", input_img.shape)
        output_blobs = model.predict(input_img)

        # extract outputs, resize, and remove padding
       
        seg = np.squeeze(output_blobs[0])
        seg = cv2.resize(seg, (0, 0), fx=model_params['stride'], fy=model_params['stride'],
                             interpolation=cv2.INTER_CUBIC)
        seg = seg[:imageToTest_padded.shape[0] - pad[2], :imageToTest_padded.shape[1] - pad[3], :]
        seg = cv2.resize(seg, (oriImg.shape[1], oriImg.shape[0]), interpolation=cv2.INTER_CUBIC)

        seg_recover = recover_flipping_output(oriImg, seg)

        if m==0:
            segmap_scale5 = seg_recover
        elif m==1:
            segmap_scale6 = seg_recover         
        elif m==2:
            segmap_scale7 = seg_recover
        elif m==3:
            segmap_scale8 = seg_recover
    
    segmap_a = np.maximum(segmap_scale1,segmap_scale2)
    segmap_b = np.maximum(segmap_scale4,segmap_scale3)
    segmap_c = np.maximum(segmap_scale5,segmap_scale6)
    segmap_d = np.maximum(segmap_scale7,segmap_scale8)
    seg_ori = np.maximum(segmap_a, segmap_b)
    seg_flip = np.maximum(segmap_c, segmap_d)
    seg_avg = np.maximum(seg_ori, seg_flip)

    return seg_avg


def wrapped_process(frame,params,model_params,save_path,save_tmp_path):
    seg = process(frame, params, model_params) 
    seg_argmax = np.argmax(seg, axis=-1)
    seg_max = np.max(seg, axis=-1)
    th_mask = part_thresholding(seg_argmax)
    seg_max_thres = (seg_max > 0.1).astype(np.uint8)
    seg_argmax *= seg_max_thres
    seg_canvas = human_seg_combine_argmax_rgb(seg_argmax)
    #merge_canvas = cv2.addWeighted(seg_canvas,0.6,frame,0.4,0)
    cv2.imwrite(save_path, seg_canvas) 
    #cv2.imwrite(save_tmp_path, merge_canvas) 


if __name__ == '__main__':
    exp_name = sys.argv[1] 
    per = sys.argv[2]
    gpu = sys.argv[3]
    os.environ["CUDA_VISIBLE_DEVICES"]=gpu
    keras_weights_file = args["model"]
    model = get_testing_model_resnet101() 
    model.load_weights(keras_weights_file)
    params, model_params = config_reader()
    scale_list = []
    for item in args["scale"]:
        scale_list.append(float(item))
    params['scale_search'] = scale_list
    input_folder = args["input_folder"]

    #info = pd.read_csv(os.path.join(input_folder,"info.csv"))
    #for per in ["A","B","C","D"]:
    video_path = os.path.join(input_folder,exp_name,per,"scenevideo.mp4")
    print(video_path)
    if not os.path.exists(video_path):
        print("no video data")
    else:
        save_dir = os.path.join(input_folder,exp_name,per,folder_name)
        save_dir_tmp = os.path.join(input_folder,exp_name,per,check_folder_name)
        os.makedirs(save_dir,exist_ok=True)
        os.makedirs(save_dir_tmp,exist_ok=True)

        skip_count=0
        cap=cv2.VideoCapture(video_path)
        num_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = cap.get(cv2.CAP_PROP_FPS)

        print(save_dir)
        cap.set(cv2.CAP_PROP_POS_FRAMES,skip_count)
        cnt = 0
        with loop(total=num_frames) as pbar:
            while(cap.isOpened()):
                ret,frame = cap.read()
                if not ret:break
                cnt+=1
                if cnt>num_frames:break
                pbar.update(1)
                save_path = os.path.join(save_dir,str(cnt)+".jpg")
                save_path_tmp = os.path.join(save_dir_tmp,str(cnt)+".jpg")
                if os.path.exists(save_path):continue
                wrapped_process(frame,params,model_params,save_path,save_path_tmp)


