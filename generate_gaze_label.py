import os
import sys
from tqdm import tqdm as loop
import numpy as np
import cv2
import gzip
import json
import pandas as pd


root = "input/"


def read_gaze_data(file_path,start_time):
    data = []
    with gzip.open(file_path,'r') as fin:        
        for line in fin:        
            tmp = str(line)[2:-3]
            obj = json.loads(tmp)
            data.append(obj)
    p_left = []
    p_right = []
    gazeX = []
    gazeY = []
    time_axis = []
    for d in loop(data):
        if not "data" in d:continue
        time_axis.append(d['timestamp']+start_time)
        
        if not 'eyeleft' in d['data']:
            p_left.append(np.nan)
            p_right.append(np.nan)
        else:
            if "pupildiameter" in d['data']['eyeleft']:
                p_left.append(d["data"]["eyeleft"]["pupildiameter"])
            else:
                p_left.append(np.nan)
            if "pupildiameter" in d['data']['eyeright']:
                p_right.append(d["data"]["eyeright"]["pupildiameter"])
            else:
                p_right.append(np.nan)
        if "gaze2d" in d['data']:
            gazeX.append(d['data']['gaze2d'][0])
            gazeY.append(d['data']['gaze2d'][1])
        else:
            gazeX.append(np.nan)
            gazeY.append(np.nan)
    df = pd.DataFrame(np.array([time_axis,p_left,p_right,gazeX,gazeY]).T,columns=["TIME","pLeft","pRight","gazeX","gazeY"])
    return df


def generate_feature(exp,per):
    info = pd.read_csv(os.path.join(root,"info.csv"))
    row = info[(info.exp==exp) & (info.per==per)]
    if len(row)==0:return
    skip_count = int(row["skip_count"])
    num_frames = int(row["num_frames"])
    global_start = int(row["start"])  # secc
    fps = int(row["fps"])
    global_end = global_start + num_frames/fps  # sec
    start = global_start - (skip_count/fps)  #secc
    gaze_path = os.path.join(root,exp,per,"gazedata.gz")
    
    scene_labels_folder = os.path.join(root,exp,per,exp+"_"+per+"_output")
    scene_labels_folder = os.path.join(root,exp,per,exp+"_"+per+"_check")
    save_dir = os.path.join(root,exp,per,"check_faces")
    os.makedirs(save_dir,exist_ok=True)

    scene_labels_paths = [os.path.join(scene_labels_folder,i) for i in os.listdir(scene_labels_folder) if "jpg" in i and "ubuntu" not in i]
    
    gaze_data = read_gaze_data(gaze_path,start)
    gaze_data = gaze_data[(gaze_data.TIME>=global_start)&(gaze_data.TIME<=global_end)]
    label_ts = np.array([float(os.path.basename(i).split(".")[0]) for i in scene_labels_paths])
    diff = 1/fps #(label_ts[1]-label_ts[0])/1000
    res = []
    print("total=",len(label_ts))
    for i,t in loop(enumerate(label_ts)):
        gd = gaze_data[(gaze_data.TIME<=t/1000+diff)&(gaze_data.TIME>=t/1000-diff)]
        gd = gd[(~np.isnan(gd.gazeX))&(~np.isnan(gd.gazeY))&(gd.gazeX<=1)&(gd.gazeX>=0)&(gd.gazeY<=1)&(gd.gazeY>=0)]
        if len(gd)==0:continue
        x=np.mean(gd.gazeX)
        y=np.mean(gd.gazeY)
        im = cv2.imread(scene_labels_paths[i])
        gaze_label = im[int(y*im.shape[0]),int(x*im.shape[1])]
        r,g,b = gaze_label
        if r==0 and g==0 and b==0:
            label = "Background"
        elif np.var(gaze_label)<10:
            label = "face"
            save_path = os.path.join(save_dir,os.path.basename(scene_labels_paths[i]))
            if not os.path.exists(save_path):
                gaze_center = (int(x*im.shape[1]),int(y*im.shape[0]))
                im_with_gaze = cv2.circle(im, gaze_center, 10, (255, 0, 0), 70)
                cv2.imwrite(save_path,im_with_gaze)
        else:
            label = "body"
        res.append({"TIME":t,"Label":label,"X":x,"Y":y,"Color":str(gaze_label)})
        
    return pd.DataFrame.from_records(res)


if __name__ == "__main__":
    exp = sys.argv[1]
    for per in ["A","B","C","D"]:
        df = generate_feature(exp,per)
        df.to_csv(os.path.join(root,exp,per,"gaze_label.csv"))


