import subprocess
import sys
import os

cmd_list = ["aws","s3","cp" ]
src_root = "./input"
dst_root = "s3://wg1-4/data/"
download_file = "scenevideo.mp4"
folder_dict = {('exp1', 'A'): '20221221T043026Z',
 ('exp1', 'B'): '20221221T043219Z',
 ('exp1', 'C'): '20221221T043526Z',
 ('exp1', 'D'): '20221221T043622Z',
 ('exp2', 'A'): '20221222T043552Z',
 ('exp2', 'B'): '20221222T044010Z',
 ('exp2', 'C'): '20221222T044228Z',
 ('exp2', 'D'): '20221222T044529Z',
 ('exp3', 'A'): None,
 ('exp3', 'B'): '20221223T045247Z',
 ('exp3', 'C'): '20221223T045041Z',
 ('exp3', 'D'): '20221223T045400Z',
 ('exp4', 'A'): '20221226T044026Z',
 ('exp4', 'B'): '20221226T043732Z',
 ('exp4', 'C'): '20221226T043844Z',
 ('exp4', 'D'): '20221226T043949Z',
 ('exp5', 'A'): '20221227T042607Z',
 ('exp5', 'B'): '20221227T042706Z',
 ('exp5', 'C'): '20221227T042822Z',
 ('exp5', 'D'): '20221227T042900Z'
 }


if __name__ == "__main__":
    exp = sys.argv[1]
    per = sys.argv[2]
    src_file = os.path.join(dst_root,exp,per,folder_dict[(exp,per)],download_file)
    dst_file = os.path.join(src_root,exp,per,download_file )
    params_list = [src_file,dst_file]
    cmd = cmd_list + params_list 
    print("Run : " + " ".join(cmd))
    list_files = subprocess.run(cmd)