import subprocess
import sys
import os

cmd_list = ["aws","s3","cp"]
src_root = "input"
dst_root = "s3://wg1-4/data/"
map_dict = {
    "output":"1_segment_results",
    "check":"1_segmentation_check"
}

if __name__ == "__main__":
    exp = sys.argv[1]
    per = sys.argv[2]
    for typ in map_dict.keys():
        src_folder = os.path.join(src_root,exp,per,map_dict[typ])
        dst_folder = os.path.join(dst_root,exp,per,map_dict[typ])
        params_list = [src_folder,dst_folder,"--recursive"]
        cmd = cmd_list + params_list
        print("Run : " + " ".join(cmd))
        list_files = subprocess.run(cmd)