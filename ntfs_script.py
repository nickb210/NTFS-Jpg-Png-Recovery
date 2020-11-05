#!/usr/bin/env python3
import sys, os, shlex, subprocess, signal, time, psutil
from os import stat
from subprocess import Popen, PIPE
from argparse import ArgumentParser
from time import sleep

def main():
    parser      = ArgumentParser()
    parser.add_argument('disk_image', default=0, help='specify .dd file')

    args        = parser.parse_args()
    disk_image  = str(args.disk_image)


    #signatures = {'jpeg':'ffd8ffe0', 'png':'89504e47', 'avi':'52494646', 'mp4':'66747970', 'tiff':'49492a00', 'mov':'66747970', 'mkv':'1a45dfa3'}
    signatures  = {'jpg':'ffd8ffe0', 'png':'89504e47'}
    keys        = getList(signatures)

    dir_path = input("Where would you like to save the recovered files (enter 'x' to save to current directoy)? ")

    #if dir_path[0:2] == './':
    if dir_path != 'x':
        dir_str = " mkdir " + dir_path
        os.system(dir_str)
        print("Files that are found are going to be located in %s" % dir_path)

    elif dir_path.lower() == 'x':
        dir_path = "./"
        print("Files that are found are going to be located in %s" % os.getcwd())
        
    else:
        print("* Please enter a valid option")
        time.sleep(1)
        print("Exiting")
        exit(1)

    l     = "Starting recovery process for NTFS (" + disk_image + ")"
    l_len = "="*len(l)
    l1    = "ntfs_script will be looking for: "
    for a in range(0, len(keys)):
        l1 += keys[a] + "'s"
        if a + 1 != len(keys):
            l1 += ", "
    print("%s\n%s\n%s\n%s\n" % (l_len, l, l1, l_len))

    #the_dir = mk_dir(disk_image, keys)
    i     = 0
    count = 1
    for sigs in signatures:
        sig = signatures[sigs]
        ext = keys[i]

        sigfind        = "./sigfind.py " + sig + " " + disk_image
        sigfind_check  = subprocess.check_output(shlex.split(sigfind))
        sigfind_decode = sigfind_check.decode()
        for line in sigfind_decode.splitlines():
            sector = line.split()[1]
            #print(sector)
            block  =  str(int(sector)/(4096/512)).split('.')[0]
            #print("block:" + block) 

            ifind_cmd    = "ifind -a -d " + block + " " + disk_image
            ifind_get    = subprocess.check_output(shlex.split(ifind_cmd))
            ifind_decode = ifind_get.decode() 
            
            for line1 in ifind_decode.splitlines():
                if "Inode not found" not in line1:
                    if "Meta Data" not in line1:
                        #print("%s: %-15s" % (ifind_cmd, line1))
                        istat_cmd   = "istat " + disk_image + " " + line1
                        istat_exec  = subprocess.check_output(shlex.split(istat_cmd))
                        istat_fname = istat_exec.decode()

                        for line2 in istat_fname.splitlines():
                            line2_split = line2.split(" ")
                            if line2_split[0] == "Name:":
                                file_name = line2_split[1]
                                if "." in file_name:
                                    file_ext = file_name.split(".")[1]
                                else:
                                    break
                                if ext == file_ext.lower():
                                    #print("File Name: " + file_name)
                                    save     = disk_image.split("_")[0] + "-" + line1 + "-" + file_name
                                    if dir_path == 'x':
                                        icat_cmd = "icat " + disk_image + " " + line1 + " > ./" + save
                                    if dir_path != 'x':
                                        icat_cmd = "icat " + disk_image + " " + line1 + " > " + dir_path + "/" + save
                                    os.system(icat_cmd)
                                    print("Found File header at sector %-10s" % sector)
                                    print("Sector %-10s located at block %-10s" % (sector, block))
                                    print("Found file: %-40s (Inode: %10s)" % (file_name, line1))
                                    print("Succesfully wrote %-20s" % save)
                                    count += 1
        i += 1

    ret = "Found %s images" % str(count)
    print("="*len(ret))
    print(ret)
    print("="*len(ret))
        


def getList(dict): 
    list = [] 
    for key in dict.keys(): 
        list.append(key) 
          
    return list

def mk_dir(disk, ext_list):
    volume_path = "./ntfs_script." + disk.split('_')[0] + "/"
    doesExist   = os.path.exists(volume_path)

    if doesExist:
        print("The directory %s already exists. Would you like to overwrite (y/n)? " % volume_path)
        print("NOTE: choosing 'y' will delete the current directory and its conents")
        ask_user = input("> ")
        if ask_user.lower() == 'y':
            remv_volume_path   = "rm -r " + volume_path
            make_volume_path   = "mkdir " + volume_path
            subprocess.Popen(shlex.split(remv_volume_path), stdout=subprocess.DEVNULL)
            subprocess.Popen(shlex.split(make_volume_path), stdout=subprocess.DEVNULL)
        else:
            exit(0)
    if not doesExist:
        make_volume_path   = "mkdir " + volume_path                
        subprocess.Popen(shlex.split(make_volume_path), stdout=subprocess.DEVNULL)
    
    for i in range(0, len(ext_list)):
        tmp = ext_list[i]
        cmd = "mkdir " + volume_path + tmp + "/"
        subprocess.Popen(shlex.split(cmd), stdout=subprocess.DEVNULL)
        print(cmd.split(" ")[1])
    return cmd.split(" ")[1]

if __name__ == '__main__':
		main()