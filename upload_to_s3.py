import subprocess
import sys
import os

cmd_list = ["aws","s3","cp"]
src_root = "input"
dst_root = "s3://wg1-4/data/"
map_dict = {
    "output":"scene_labels",
    "check":"scene_check"
}

if __name__ == "__main__":
    exp = "exp-pre" + sys.argv[1]
    per = sys.argv[2]
    typ = sys.argv[3]

    src_folder = os.path.join(src_root,exp,per,exp+"_"+per+"_"+typ)
    dst_folder = os.path.join(dst_root,exp,per,map_dict[typ])

    params_list = [src_folder,dst_folder,"--recursive"]
    cmd = cmd_list + params_list
    print("Run : " + " ".join(cmd))
    list_files = subprocess.run(cmd)