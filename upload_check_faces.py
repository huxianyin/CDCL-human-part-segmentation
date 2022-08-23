import subprocess
import sys
import os

cmd_list = ["aws","s3","cp"]
src_root = "input"
dst_root = "s3://wg1-4/data/"
check_faces_folder = "check_faces"

if __name__ == "__main__":
    folders=[x[0] for x in os.walk(src_root) if check_faces_folder in x[0]]
    for folder in folders:
        tmp = os.path.dirname(folder)
        exp,per = os.path.basename(os.path.dirname(tmp)),os.path.basename(tmp)
        print(exp,per)
        src_folder = folder
        dst_folder = os.path.join(dst_root,exp,per,check_faces_folder)
        print(src_folder,dst_folder)

        params_list = [src_folder,dst_folder,"--recursive"]
        cmd = cmd_list + params_list
        print("Run : " + " ".join(cmd))
        list_files = subprocess.run(cmd)