# v3 : 1. GM_Cep分開計算
#      2. 不計 astronomical twilight 觀測時間

from os import walk, listdir, system
from os.path import splitext, join, getctime
from numpy import array, sort, sum, hstack
from time import localtime, strftime

def getfilelist(path):
    allfile = []
    for dirPath, dirNames, fileNames in walk(path):
        for f in fileNames:
            if splitext(f)[1] in ['.fts','.fits','.fit']:
                allfile.append(join(dirPath, f))
    return allfile

def TTC(files):
    # Total Time calculator
    
    evening_twil, morning_twil = get_twil(today)
    TL = []   #timelist
    for file in files:
        TL.append(getctime(file))
    TL = array(TL,dtype='float64')
    TL = sort(TL)
    TL = TL[(TL>evening_twil)&(TL<morning_twil)]
    delta_time = TL[1:] - TL[:-1]

    # consider as 5 min if deltatime > 5 min 
    delta_time[delta_time > 1020] = 480
    TTS = sum(delta_time)   #total_time_sec
    return TTS, TL

def strtime(time_sec):
    return strftime("%H:%M:%S", localtime(time_sec))

def get_twil(sltfolder):
    
    with open('twil_time.txt','r') as f:
        lines = f.readlines()
        
    for line in lines:
        if sltfolder[3:11] in line.replace('-',''):
            date, dask, dawn = line.replace('\n','').split(' ')
            dask, dawn = float(dask), float(dawn)
            continue
    return dask, dawn

def calc_write(name,path,alltimelist):
    ftslist = getfilelist(path)
    total_time_sec, timelist = TTC(ftslist)
    alltimelist = hstack((alltimelist,timelist))
    txtwrite.append('{:<11s}: {: >6.2f} minutes = {: >4.2f} hours\n'.format(name,total_time_sec/60.,total_time_sec/3600.))
    total_time.append(total_time_sec)
    return alltimelist

def wchen_distinguish(str_):
    if 'GASP' in str_:
        user = 'wchen_GASP'
    else: 
        user = 'wchen_GMcep'
    return user

# code begin
# list folders in SLTdata
data_path = 'D:\\SLTdata'
data_folders = array(listdir(data_path))

input_days = int(input('how many days?\n'))
deal_days = sort(data_folders)[-input_days:]
txtwrite = []

for today in deal_days:

    print(today)
    base_path = join(data_path,today)
    folders = listdir(base_path)
    evening_twil, morning_twil = get_twil(today)

    total_time = []
    all_timelist = array([])
    txtwrite.append('========================================\n')
    txtwrite.append(today+'\n\n')

    # calculate observation time for each user
    for user in folders:
        
        if user in ['bias-dark','flat']: continue
        elif user == 'wchen':
            wchen = join(base_path,user)
            wchen_list = listdir(wchen)
            if len(wchen_list) == 0:
                user = 'wchen'
                all_timelist = calc_write(user,path1,all_timelist)
            else:
                for wchen_obs in wchen_list:
                    user = wchen_distinguish(wchen_obs)
                    path1 = join(wchen,wchen_obs)
                    all_timelist = calc_write(user,path1,all_timelist)
        else:
            path1 = join(base_path,user)
            all_timelist = calc_write(user,path1,all_timelist)

    total_time = array(total_time, dtype = 'float64')
    txtwrite.append('\n   Total observing time = {:.2f} hours\n\n'.format(sum(total_time)/3600.))
    
    # get time of stoping observation
    if len(all_timelist) != 0:
        all_timelist = sort(all_timelist)
        all_delta = all_timelist[1:] - all_timelist[:-1]
        start = [all_timelist[0]]
        end = [all_timelist[-1]]
        for num, delta in enumerate(all_delta):
            if delta > 1020:
                start.append(all_timelist[num+1])
                end.append(all_timelist[num])
        end = sort(end)
        txtwrite.append('observation period:\n')
        for i in range(len(start)):
            txtwrite.append('{} to {}\n'.format(strtime(start[i]), strtime(end[i])))
# write a txt for read

with open('time.txt', 'w') as f:
    list(map(f.write,txtwrite))

system('notepad time.txt')