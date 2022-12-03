import sys
sys.coinit_flags = 2  # COINIT_APARTMENTTHREADED

import tkinter
import tkinter.font
import re
from datetime import datetime, date, timedelta
from PIL import Image, ImageTk
import pandas as pd
from tkinter import filedialog
import os
from pathlib import Path #ファイル名取得モジュール
import shutil #ファイル移動モジュール
import matplotlib as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from scipy.signal import savgol_filter
import datetime

current_directory_name="None"
current_file_name="None"
forward_or_backward_or_both="forward"
filter_ON_OFF="OFF"

#指定したディレクトリへのパスを取得する関数
def select_directory():
    target_Path =tkinter.filedialog.askdirectory()
    return target_Path

#ファイル名取得関数
def get_file_name(s):
    s_list=s.split("\\")
    current_pass=s_list[len(s_list)-1]

    return current_pass

#ディレクトリ選択ボタンを押した際の反応
def open_directory():

    global current_directory_name
    global current_file_name
    global forward_or_backward_or_both
    global filter_ON_OFF

    if forward_or_backward_or_both!="forward":
        forward_or_backward_or_both="forward"
        change_forward_and_backward_button.configure(text="Forward", command=change_forward_to_backward)
    
    if filter_ON_OFF=="ON":
        filter_ON_OFF="OFF"
        filter_button.configure(text="Filter OFF", command=spectroscopy_filter_ON)

    #ディレクトリを取得
    directory=select_directory()
    current_directory_name=directory
    #datファイルを取得
    filelist=Path(directory).rglob("*.dat")
    dat_file_name_list=[]
    
    for file in filelist:
        dat_file_name_list.append(str(file))
    
    current_file_name=dat_file_name_list[0]
    
    shutil.copy(dat_file_name_list[0],dat_file_name_list[0].replace(".dat","")+"_copy"+".dat")
    #shutil.move(dat_file_name_list[0].replace(".dat","")+"_copy"+".dat", directory)
    
    newfile=Path(directory).rglob("*copy.dat")
    for f in newfile:

        f.rename(f.stem+".csv")
        shutil.move(f.stem+".csv",directory) #ファイルの拡張子をcsvに変換
    
    for file in Path(directory).rglob("*copy.csv"): 
        col_name1=range(1,100) #列数がそろっていないと読み込みができないので、列数をあらかじめ定義する。一部のBias-spectroscopyファイルの列数が65になってしまっているため数が多くなっている。原因が分かれば改善できるのだが……
        df=pd.read_csv(file, names=col_name1, encoding="shift-jis", sep="\t") #上で指定した列数と指定のエンコーダーと区切り文字で各csvファイルを開く
        df=df.drop(range(15), axis=0) #開いたcsvファイルにおいて１４行目までを削除(axis=0は行の削除指定、axis=1だと列の削除指定になる)
        df.to_csv(file, header=False, index=False, encoding="shift-jis" ) #保存
    
    file_name_list=[]

    for file in Path(directory).rglob("*copy.csv"): 
        file_name_list.append(str(file))
    

    spec=pd.read_csv(file_name_list[0], encoding="shift-jis") #ファイルを読み込む
    spec.iloc[:, :]=spec.iloc[:, :].astype(float) #ファイルの各数値をfloat型に
    column_names=spec.columns.values #列名のリストを作成
    
    forward_or_backward_or_both="forward"

    if column_names[0]=="Z rel (m)":
        x=spec["Z rel (m)"]
        y=spec["Frequency Shift (Hz)"]
        plt.rcParams["figure.subplot.left"] = 0.24
        plt.rcParams["figure.subplot.bottom"] = 0.19
        plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
    #y2=savgol_filter(y,10,2)
        fig = Figure(figsize=(3, 3), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        line, = ax.plot(x, y)
        ax.set_xlabel('z')
        ax.set_ylabel("Δf(Hz)")
        canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
        canvas.draw()
        canvas.get_tk_widget().place(x=30,y=20)
        

    if column_names[0]=="Bias calc (V)":
        x=spec["Bias calc (V)"]
        y=spec["Frequency Shift (Hz)"]
        plt.rcParams["figure.subplot.left"] = 0.24
        plt.rcParams["figure.subplot.bottom"] = 0.19
        plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        #y2=savgol_filter(y,10,2)
        fig = Figure(figsize=(3,3), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        ax.set_xlabel('Bias(V)')
        ax.set_ylabel("Δf(Hz)")
        line, = ax.plot(x, y)
        canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
        canvas.draw()
        canvas.get_tk_widget().place(x=30,y=20)
    
    #ファイル名を取得して表示
    spectroscopy_image_name=get_file_name(current_file_name)
    label_spectroscopy_image_name.configure(text=spectroscopy_image_name)
    
    #作成したCSVファイルは最後に削除する
    os.remove(file_name_list[0])

#▶ボタンを押した際の反応
def change_file_forward():

    global current_file_name
    global current_directory_name
    global forward_or_backward_or_both
    global filter_ON_OFF

    if filter_ON_OFF=="ON":
        filter_ON_OFF="OFF"
        filter_button.configure(text="Filter OFF", command=spectroscopy_filter_ON)

    if forward_or_backward_or_both!="forward":
        forward_or_backward_or_both="forward"
        change_forward_and_backward_button.configure(text="Forward", command=change_forward_to_backward)
    
    #現在選択されているディレクトリからdatファイル名一覧を取得してリスト化
    filelist=Path(current_directory_name).rglob("*.dat")
    dat_file_name_list=[]
    for file in filelist:
        dat_file_name_list.append(str(file))
    
    name=current_file_name

    #datファイルリストから現在開いているファイルから1つ先のファイルを選択
    current_file_index=dat_file_name_list.index(name)
    
    #現在開いているファイルの場所で場合分け

    #現在のファイルがディレクトリの最後尾の場合
    if current_file_index==len(dat_file_name_list)-1:
        next_idx=0
    
    else:
        next_idx=current_file_index+1
    
    current_file_name=dat_file_name_list[next_idx]
    
    shutil.copy(dat_file_name_list[next_idx],dat_file_name_list[next_idx].replace(".dat","")+"_copy"+".dat")
    #shutil.move(dat_file_name_list[0].replace(".dat","")+"_copy"+".dat", directory)
    
    newfile=Path(current_directory_name).rglob("*copy.dat")
    for f in newfile:

        f.rename(f.stem+".csv")
        shutil.move(f.stem+".csv",current_directory_name) #ファイルの拡張子をcsvに変換
    
    for file in Path(current_directory_name).rglob("*copy.csv"): 
        col_name1=range(1,100) #列数がそろっていないと読み込みができないので、列数をあらかじめ定義する。一部のBias-spectroscopyファイルの列数が65になってしまっているため数が多くなっている。原因が分かれば改善できるのだが……
        df=pd.read_csv(file, names=col_name1, encoding="shift-jis", sep="\t") #上で指定した列数と指定のエンコーダーと区切り文字で各csvファイルを開く
        df=df.drop(range(15), axis=0) #開いたcsvファイルにおいて１４行目までを削除(axis=0は行の削除指定、axis=1だと列の削除指定になる)
        df.to_csv(file, header=False, index=False, encoding="shift-jis" ) #保存
        
    
    file_name_list=[]

    for file in Path(current_directory_name).rglob("*copy.csv"): 
        file_name_list.append(str(file))
    

    spec=pd.read_csv(file_name_list[0], encoding="shift-jis") #ファイルを読み込む
    spec.iloc[:, :]=spec.iloc[:, :].astype(float) #ファイルの各数値をfloat型に
    column_names=spec.columns.values #列名のリストを作成
    
    if column_names[0]=="Z rel (m)":
        x=spec["Z rel (m)"]
        y=spec["Frequency Shift (Hz)"]
        plt.rcParams["figure.subplot.left"] = 0.24
        plt.rcParams["figure.subplot.bottom"] = 0.19
        plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
    #y2=savgol_filter(y,10,2)
        fig = Figure(figsize=(3, 3), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        line, = ax.plot(x, y)
        ax.set_xlabel("z")
        ax.set_ylabel("Δf")
        canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
        canvas.get_tk_widget().place(x=30,y=20)

    if column_names[0]=="Bias calc (V)":
        x=spec["Bias calc (V)"]
        y=spec["Frequency Shift (Hz)"]
        plt.rcParams["figure.subplot.left"] = 0.24
        plt.rcParams["figure.subplot.bottom"] = 0.19
        plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        #y2=savgol_filter(y,10,2)
        fig = Figure(figsize=(3, 3), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        line, = ax.plot(x, y)
        ax.set_xlabel('Bias(V)')
        ax.set_ylabel("Δf(Hz)")
        canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
        canvas.get_tk_widget().place(x=30,y=20)
    
    #ファイル名を取得して表示
    spectroscopy_image_name=get_file_name(current_file_name)
    label_spectroscopy_image_name.configure(text=spectroscopy_image_name)
    
    #作成したCSVファイルは最後に削除する
    os.remove(file_name_list[0])
    
#◀ボタンを押した際の反応
def change_file_backward():

    global current_file_name
    global current_directory_name
    global forward_or_backward_or_both
    global filter_ON_OFF

    if filter_ON_OFF=="ON":
        filter_ON_OFF="OFF"
        filter_button.configure(text="Filter OFF", command=spectroscopy_filter_ON)

    if forward_or_backward_or_both!="forward":
        forward_or_backward_or_both="forward"
        change_forward_and_backward_button.configure(text="Forward", command=change_forward_to_backward)

    
    #現在選択されているディレクトリからdatファイル名一覧を取得してリスト化
    filelist=Path(current_directory_name).rglob("*.dat")
    dat_file_name_list=[]
    for file in filelist:
        dat_file_name_list.append(str(file))

    #datファイルリストから現在開いているファイルから1つ先のファイルを選択
    current_file_index=dat_file_name_list.index(current_file_name)
    
    #現在開いているファイルの場所で場合分け

    #現在のファイルがディレクトリの最後尾の場合
    if current_file_index==0:
        next_idx=len(dat_file_name_list)-1
    
    else:
        next_idx=current_file_index-1
    
    current_file_name=dat_file_name_list[next_idx]
    
    shutil.copy(dat_file_name_list[next_idx],dat_file_name_list[next_idx].replace(".dat","")+"_copy"+".dat")
    #shutil.move(dat_file_name_list[0].replace(".dat","")+"_copy"+".dat", directory)
    
    newfile=Path(current_directory_name).rglob("*copy.dat")
    for f in newfile:

        f.rename(f.stem+".csv")
        shutil.move(f.stem+".csv",current_directory_name) #ファイルの拡張子をcsvに変換
    
    for file in Path(current_directory_name).rglob("*copy.csv"): 
        col_name1=range(1,100) #列数がそろっていないと読み込みができないので、列数をあらかじめ定義する。一部のBias-spectroscopyファイルの列数が65になってしまっているため数が多くなっている。原因が分かれば改善できるのだが……
        df=pd.read_csv(file, names=col_name1, encoding="shift-jis", sep="\t") #上で指定した列数と指定のエンコーダーと区切り文字で各csvファイルを開く
        df=df.drop(range(15), axis=0) #開いたcsvファイルにおいて１４行目までを削除(axis=0は行の削除指定、axis=1だと列の削除指定になる)
        df.to_csv(file, header=False, index=False, encoding="shift-jis" ) #保存
        
    
    file_name_list=[]

    for file in Path(current_directory_name).rglob("*copy.csv"): 
        file_name_list.append(str(file))
    

    spec=pd.read_csv(file_name_list[0], encoding="shift-jis") #ファイルを読み込む
    spec.iloc[:, :]=spec.iloc[:, :].astype(float) #ファイルの各数値をfloat型に
    column_names=spec.columns.values #列名のリストを作成
    
    if column_names[0]=="Z rel (m)":
        x=spec["Z rel (m)"]
        y=spec["Frequency Shift (Hz)"]
        plt.rcParams["figure.subplot.left"] = 0.24
        plt.rcParams["figure.subplot.bottom"] = 0.19
        plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
    #y2=savgol_filter(y,10,2)
        fig = Figure(figsize=(3, 3), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        line, = ax.plot(x, y)
        ax.set_xlabel("z")
        ax.set_ylabel("Δf")
        canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
        canvas.draw()
        canvas.get_tk_widget().place(x=30,y=20)

    if column_names[0]=="Bias calc (V)":
        x=spec["Bias calc (V)"]
        y=spec["Frequency Shift (Hz)"]
        plt.rcParams["figure.subplot.left"] = 0.24
        plt.rcParams["figure.subplot.bottom"] = 0.19
        plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        #y2=savgol_filter(y,10,2)
        fig = Figure(figsize=(3, 3), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        ax.set_xlabel('Bias(V)')
        ax.set_ylabel("Δf(Hz)")
        line, = ax.plot(x, y)
        canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
        canvas.get_tk_widget().place(x=30,y=20)
    
    #ファイル名を取得して表示
    spectroscopy_image_name=get_file_name(current_file_name)
    label_spectroscopy_image_name.configure(text=spectroscopy_image_name)
    
    #作成したCSVファイルは最後に削除する
    os.remove(file_name_list[0])

#forwardからbackwardに表示を変更するボタン
def change_forward_to_backward():
    
    global current_file_name
    global current_directory_name
    global forward_or_backward_or_both
    global filter_ON_OFF

    if filter_ON_OFF=="ON":
        filter_ON_OFF="OFF"
        filter_button.configure(text="Filter OFF", command=spectroscopy_filter_ON)


    #現在選択されているディレクトリからdatファイル名一覧を取得してリスト化
    filelist=Path(current_directory_name).rglob("*.dat")
    dat_file_name_list=[]
    for file in filelist:
        dat_file_name_list.append(str(file))
    
    name=current_file_name

    #datファイルリストから現在開いているファイルのインデックスを取得
    current_file_index=dat_file_name_list.index(name)
    
    
    shutil.copy(dat_file_name_list[current_file_index],dat_file_name_list[current_file_index].replace(".dat","")+"_copy"+".dat")
    #shutil.move(dat_file_name_list[0].replace(".dat","")+"_copy"+".dat", directory)
    
    newfile=Path(current_directory_name).rglob("*copy.dat")
    for f in newfile:

        f.rename(f.stem+".csv")
        shutil.move(f.stem+".csv",current_directory_name) #ファイルの拡張子をcsvに変換
    
    for file in Path(current_directory_name).rglob("*copy.csv"): 
        col_name1=range(1,100) #列数がそろっていないと読み込みができないので、列数をあらかじめ定義する。一部のBias-spectroscopyファイルの列数が65になってしまっているため数が多くなっている。原因が分かれば改善できるのだが……
        df=pd.read_csv(file, names=col_name1, encoding="shift-jis", sep="\t") #上で指定した列数と指定のエンコーダーと区切り文字で各csvファイルを開く
        df=df.drop(range(15), axis=0) #開いたcsvファイルにおいて１４行目までを削除(axis=0は行の削除指定、axis=1だと列の削除指定になる)
        df.to_csv(file, header=False, index=False, encoding="shift-jis" ) #保存
    
    file_name_list=[]

    for file in Path(current_directory_name).rglob("*copy.csv"): 
        file_name_list.append(str(file))

    spec=pd.read_csv(file_name_list[0], encoding="shift-jis") #ファイルを読み込む
    spec.iloc[:, :]=spec.iloc[:, :].astype(float) #ファイルの各数値をfloat型に
    column_names=spec.columns.values #列名のリストを作成
    
    forward_or_backward_or_both="backward"
    change_forward_and_backward_button.configure(text="Backward", command=change_backward_to_bothward)

    if column_names[0]=="Z rel (m)":
        x=spec["Z rel (m)"]
        y=spec["Frequency Shift [bwd] (Hz)"]
        plt.rcParams["figure.subplot.left"] = 0.24
        plt.rcParams["figure.subplot.bottom"] = 0.19
        plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
    #y2=savgol_filter(y,10,2)
        fig = Figure(figsize=(3, 3), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        line, = ax.plot(x, y)
        ax.set_xlabel("z")
        ax.set_ylabel("Δf")
        canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
        canvas.get_tk_widget().place(x=30,y=20)

    if column_names[0]=="Bias calc (V)":
        x=spec["Bias calc (V)"]
        y=spec["Frequency Shift [bwd] (Hz)"]
        plt.rcParams["figure.subplot.left"] = 0.24
        plt.rcParams["figure.subplot.bottom"] = 0.19
        plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        #y2=savgol_filter(y,10,2)
        fig = Figure(figsize=(3, 3), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        line, = ax.plot(x, y)
        ax.set_xlabel('Bias(V)')
        ax.set_ylabel("Δf(Hz)")
        canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
        canvas.get_tk_widget().place(x=30,y=20)
    
    #ファイル名を取得して表示
    spectroscopy_image_name=get_file_name(current_file_name)
    label_spectroscopy_image_name.configure(text=spectroscopy_image_name)
    
    #作成したCSVファイルは最後に削除する
    os.remove(file_name_list[0])

#backwardから両方表示に変更するボタン
def change_backward_to_bothward():
    
    global current_file_name
    global current_directory_name
    global forward_or_backward_or_both
    global filter_ON_OFF

    if filter_ON_OFF=="ON":
        filter_ON_OFF="OFF"
        filter_button.configure(text="Filter OFF", command=spectroscopy_filter_ON)

    #現在選択されているディレクトリからdatファイル名一覧を取得してリスト化
    filelist=Path(current_directory_name).rglob("*.dat")
    dat_file_name_list=[]
    for file in filelist:
        dat_file_name_list.append(str(file))
    
    name=current_file_name

    #datファイルリストから現在開いているファイルのインデックスを取得
    current_file_index=dat_file_name_list.index(name)
    
    
    shutil.copy(dat_file_name_list[current_file_index],dat_file_name_list[current_file_index].replace(".dat","")+"_copy"+".dat")
    #shutil.move(dat_file_name_list[0].replace(".dat","")+"_copy"+".dat", directory)
    
    newfile=Path(current_directory_name).rglob("*copy.dat")
    for f in newfile:

        f.rename(f.stem+".csv")
        shutil.move(f.stem+".csv",current_directory_name) #ファイルの拡張子をcsvに変換
    
    for file in Path(current_directory_name).rglob("*copy.csv"): 
        col_name1=range(1,100) #列数がそろっていないと読み込みができないので、列数をあらかじめ定義する。一部のBias-spectroscopyファイルの列数が65になってしまっているため数が多くなっている。原因が分かれば改善できるのだが……
        df=pd.read_csv(file, names=col_name1, encoding="shift-jis", sep="\t") #上で指定した列数と指定のエンコーダーと区切り文字で各csvファイルを開く
        df=df.drop(range(15), axis=0) #開いたcsvファイルにおいて１４行目までを削除(axis=0は行の削除指定、axis=1だと列の削除指定になる)
        df.to_csv(file, header=False, index=False, encoding="shift-jis" ) #保存
    
    file_name_list=[]

    for file in Path(current_directory_name).rglob("*copy.csv"): 
        file_name_list.append(str(file))

    spec=pd.read_csv(file_name_list[0], encoding="shift-jis") #ファイルを読み込む
    spec.iloc[:, :]=spec.iloc[:, :].astype(float) #ファイルの各数値をfloat型に
    column_names=spec.columns.values #列名のリストを作成
    
    forward_or_backward_or_both="bothward"
    change_forward_and_backward_button.configure(text="Forward and Backward", command=change_bothward_to_forward)

    if column_names[0]=="Z rel (m)":
        x=spec["Z rel (m)"]
        y_forward=spec["Frequency Shift (Hz)"]
        y_backward=spec["Frequency Shift [bwd] (Hz)"]
        plt.rcParams["figure.subplot.left"] = 0.24
        plt.rcParams["figure.subplot.bottom"] = 0.19
        plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rc('legend', fontsize=8)
    #y2=savgol_filter(y,10,2)
        fig = Figure(figsize=(3, 3), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        line1 = ax.plot(x, y_forward, label="Forward")
        line2 = ax.plot(x, y_backward, label="Backward")
        ax.legend()
        ax.set_xlabel("z")
        ax.set_ylabel("Δf")
        canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
        canvas.get_tk_widget().place(x=30,y=20)

    if column_names[0]=="Bias calc (V)":
        x=spec["Bias calc (V)"]
        y_forward=spec["Frequency Shift (Hz)"]
        y_backward=spec["Frequency Shift [bwd] (Hz)"]
        plt.rcParams["figure.subplot.left"] = 0.24
        plt.rcParams["figure.subplot.bottom"] = 0.19
        plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rc('legend', fontsize=8)
        #y2=savgol_filter(y,10,2)
        fig = Figure(figsize=(3, 3), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        line1 = ax.plot(x, y_forward, label="Forward")
        line2 = ax.plot(x, y_backward, label="Backward")
        ax.legend()
        ax.set_xlabel('Bias(V)')
        ax.set_ylabel("Δf(Hz)")
        canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
        canvas.get_tk_widget().place(x=30,y=20)
    
    #ファイル名を取得して表示
    spectroscopy_image_name=get_file_name(current_file_name)
    label_spectroscopy_image_name.configure(text=spectroscopy_image_name)
    
    #作成したCSVファイルは最後に削除する
    os.remove(file_name_list[0])

#両方表示からforawardのみに変更する関数
def change_bothward_to_forward():
    
    global current_file_name
    global current_directory_name
    global forward_or_backward_or_both
    global filter_ON_OFF

    if filter_ON_OFF=="ON":
        filter_ON_OFF="OFF"
        filter_button.configure(text="Filter OFF", command=spectroscopy_filter_ON)

    #現在選択されているディレクトリからdatファイル名一覧を取得してリスト化
    filelist=Path(current_directory_name).rglob("*.dat")
    dat_file_name_list=[]
    for file in filelist:
        dat_file_name_list.append(str(file))
    
    name=current_file_name

    #datファイルリストから現在開いているファイルのインデックスを取得
    current_file_index=dat_file_name_list.index(name)
    
    
    shutil.copy(dat_file_name_list[current_file_index],dat_file_name_list[current_file_index].replace(".dat","")+"_copy"+".dat")
    #shutil.move(dat_file_name_list[0].replace(".dat","")+"_copy"+".dat", directory)
    
    newfile=Path(current_directory_name).rglob("*copy.dat")
    for f in newfile:

        f.rename(f.stem+".csv")
        shutil.move(f.stem+".csv",current_directory_name) #ファイルの拡張子をcsvに変換
    
    for file in Path(current_directory_name).rglob("*copy.csv"): 
        col_name1=range(1,100) #列数がそろっていないと読み込みができないので、列数をあらかじめ定義する。一部のBias-spectroscopyファイルの列数が65になってしまっているため数が多くなっている。原因が分かれば改善できるのだが……
        df=pd.read_csv(file, names=col_name1, encoding="shift-jis", sep="\t") #上で指定した列数と指定のエンコーダーと区切り文字で各csvファイルを開く
        df=df.drop(range(15), axis=0) #開いたcsvファイルにおいて１４行目までを削除(axis=0は行の削除指定、axis=1だと列の削除指定になる)
        df.to_csv(file, header=False, index=False, encoding="shift-jis" ) #保存
    
    file_name_list=[]

    for file in Path(current_directory_name).rglob("*copy.csv"): 
        file_name_list.append(str(file))

    spec=pd.read_csv(file_name_list[0], encoding="shift-jis") #ファイルを読み込む
    spec.iloc[:, :]=spec.iloc[:, :].astype(float) #ファイルの各数値をfloat型に
    column_names=spec.columns.values #列名のリストを作成
    
    forward_or_backward_or_both="forward"
    change_forward_and_backward_button.configure(text="Forward", command=change_forward_to_backward)

    if column_names[0]=="Z rel (m)":
        x=spec["Z rel (m)"]
        y_forward=spec["Frequency Shift (Hz)"]
        plt.rcParams["figure.subplot.left"] = 0.24
        plt.rcParams["figure.subplot.bottom"] = 0.19
        plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
    #y2=savgol_filter(y,10,2)
        fig = Figure(figsize=(3, 3), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        line1 = ax.plot(x, y_forward)
        ax.set_xlabel("z")
        ax.set_ylabel("Δf")
        canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
        canvas.get_tk_widget().place(x=30,y=20)

    if column_names[0]=="Bias calc (V)":
        x=spec["Bias calc (V)"]
        y_forward=spec["Frequency Shift (Hz)"]
        plt.rcParams["figure.subplot.left"] = 0.24
        plt.rcParams["figure.subplot.bottom"] = 0.19
        plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
        plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
        #y2=savgol_filter(y,10,2)
        fig = Figure(figsize=(3, 3), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        line1 = ax.plot(x, y_forward)
        ax.set_xlabel('Bias(V)')
        ax.set_ylabel("Δf(Hz)")
        canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
        canvas.get_tk_widget().place(x=30,y=20)
    
    #ファイル名を取得して表示
    spectroscopy_image_name=get_file_name(current_file_name)
    label_spectroscopy_image_name.configure(text=spectroscopy_image_name)
    
    #作成したCSVファイルは最後に削除する
    os.remove(file_name_list[0])

#フィルターをオンにする関数
def spectroscopy_filter_ON():
    global current_file_name
    global current_directory_name
    global forward_or_backward_or_both
    global filter_ON_OFF

    filter_ON_OFF="ON"


    #現在選択されているディレクトリからdatファイル名一覧を取得してリスト化
    filelist=Path(current_directory_name).rglob("*.dat")
    dat_file_name_list=[]
    for file in filelist:
        dat_file_name_list.append(str(file))
    
    name=current_file_name

    #datファイルリストから現在開いているファイルのインデックスを取得
    current_file_index=dat_file_name_list.index(name)
    
    
    shutil.copy(dat_file_name_list[current_file_index],dat_file_name_list[current_file_index].replace(".dat","")+"_copy"+".dat")
    #shutil.move(dat_file_name_list[0].replace(".dat","")+"_copy"+".dat", directory)
    
    newfile=Path(current_directory_name).rglob("*copy.dat")
    for f in newfile:

        f.rename(f.stem+".csv")
        shutil.move(f.stem+".csv",current_directory_name) #ファイルの拡張子をcsvに変換
    
    for file in Path(current_directory_name).rglob("*copy.csv"): 
        col_name1=range(1,100) #列数がそろっていないと読み込みができないので、列数をあらかじめ定義する。一部のBias-spectroscopyファイルの列数が65になってしまっているため数が多くなっている。原因が分かれば改善できるのだが……
        df=pd.read_csv(file, names=col_name1, encoding="shift-jis", sep="\t") #上で指定した列数と指定のエンコーダーと区切り文字で各csvファイルを開く
        df=df.drop(range(15), axis=0) #開いたcsvファイルにおいて１４行目までを削除(axis=0は行の削除指定、axis=1だと列の削除指定になる)
        df.to_csv(file, header=False, index=False, encoding="shift-jis" ) #保存
    
    file_name_list=[]

    for file in Path(current_directory_name).rglob("*copy.csv"): 
        file_name_list.append(str(file))

    spec=pd.read_csv(file_name_list[0], encoding="shift-jis") #ファイルを読み込む
    spec.iloc[:, :]=spec.iloc[:, :].astype(float) #ファイルの各数値をfloat型に
    column_names=spec.columns.values #列名のリストを作成

    filter_button.configure(text="Filter_ON", command=spectroscopy_filter_OFF)

    if forward_or_backward_or_both=="forward":
        if column_names[0]=="Z rel (m)":
            x=spec["Z rel (m)"]
            y_forward=spec["Frequency Shift (Hz)"]
            plt.rcParams["figure.subplot.left"] = 0.24
            plt.rcParams["figure.subplot.bottom"] = 0.19
            plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            y_forward=savgol_filter(y_forward,11,3)
            fig = Figure(figsize=(3, 3), dpi=100)
            ax = fig.add_subplot(1, 1, 1)
            line1 = ax.plot(x, y_forward)
            ax.set_xlabel("z")
            ax.set_ylabel("Δf")
            canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
            canvas.get_tk_widget().place(x=30,y=20)

        if column_names[0]=="Bias calc (V)":
            x=spec["Bias calc (V)"]
            y_forward=spec["Frequency Shift (Hz)"]
            plt.rcParams["figure.subplot.left"] = 0.24
            plt.rcParams["figure.subplot.bottom"] = 0.19
            plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            y_forward=savgol_filter(y_forward,11,3)
            fig = Figure(figsize=(3, 3), dpi=100)
            ax = fig.add_subplot(1, 1, 1)
            line1 = ax.plot(x, y_forward)
            ax.set_xlabel('Bias(V)')
            ax.set_ylabel("Δf(Hz)")
            canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
            canvas.get_tk_widget().place(x=30,y=20)
    
    elif forward_or_backward_or_both=="backward":
        if column_names[0]=="Z rel (m)":
            x=spec["Z rel (m)"]
            y_backward=spec["Frequency Shift [bwd] (Hz)"]
            plt.rcParams["figure.subplot.left"] = 0.24
            plt.rcParams["figure.subplot.bottom"] = 0.19
            plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            y_backward=savgol_filter(y_backward,11,3)
            fig = Figure(figsize=(3, 3), dpi=100)
            ax = fig.add_subplot(1, 1, 1)
            line1 = ax.plot(x, y_backward)
            ax.set_xlabel("z")
            ax.set_ylabel("Δf")
            canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
            canvas.get_tk_widget().place(x=30,y=20)

        if column_names[0]=="Bias calc (V)":
            x=spec["Bias calc (V)"]
            y_backward=spec["Frequency Shift [bwd] (Hz)"]
            plt.rcParams["figure.subplot.left"] = 0.24
            plt.rcParams["figure.subplot.bottom"] = 0.19
            plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            y_backward=savgol_filter(y_backward,11,3)
            fig = Figure(figsize=(3, 3), dpi=100)
            ax = fig.add_subplot(1, 1, 1)
            line1 = ax.plot(x, y_backward)
            ax.set_xlabel('Bias(V)')
            ax.set_ylabel("Δf(Hz)")
            canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
            canvas.get_tk_widget().place(x=30,y=20)
        
    elif forward_or_backward_or_both=="bothward":
        if column_names[0]=="Z rel (m)":
            x=spec["Z rel (m)"]
            y_forward=spec["Frequency Shift (Hz)"]
            y_backward=spec["Frequency Shift [bwd] (Hz)"]
            plt.rcParams["figure.subplot.left"] = 0.24
            plt.rcParams["figure.subplot.bottom"] = 0.19
            plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rc('legend', fontsize=8)
            y_forward=savgol_filter(y_forward,11,3)
            y_backward=savgol_filter(y_backward,11,3)
            fig = Figure(figsize=(3, 3), dpi=100)
            ax = fig.add_subplot(1, 1, 1)
            line1 = ax.plot(x, y_forward, label="Forward")
            line2 = ax.plot(x, y_backward, label="Backward")
            ax.legend()
            ax.set_xlabel("z")
            ax.set_ylabel("Δf")
            canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
            canvas.get_tk_widget().place(x=30,y=20)

        if column_names[0]=="Bias calc (V)":
            x=spec["Bias calc (V)"]
            y_forward=spec["Frequency Shift (Hz)"]
            y_backward=spec["Frequency Shift [bwd] (Hz)"]
            plt.rcParams["figure.subplot.left"] = 0.24
            plt.rcParams["figure.subplot.bottom"] = 0.19
            plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rc('legend', fontsize=8)
            y_forward=savgol_filter(y_forward,11,3)
            y_backward=savgol_filter(y_backward,11,3)
            fig = Figure(figsize=(3, 3), dpi=100)
            ax = fig.add_subplot(1, 1, 1)
            line1 = ax.plot(x, y_forward, label="Forward")
            line2 = ax.plot(x, y_backward, label="Backward")
            ax.legend()
            ax.set_xlabel('Bias(V)')
            ax.set_ylabel("Δf(Hz)")
            canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
            canvas.get_tk_widget().place(x=30,y=20)
    
    #ファイル名を取得して表示
    spectroscopy_image_name=get_file_name(current_file_name)
    label_spectroscopy_image_name.configure(text=spectroscopy_image_name)
    
    #作成したCSVファイルは最後に削除する
    os.remove(file_name_list[0])

#フィルターをオフにする関数
def spectroscopy_filter_OFF():
    global current_file_name
    global current_directory_name
    global forward_or_backward_or_both
    global filter_ON_OFF

    filter_ON_OFF="OFF"


    #現在選択されているディレクトリからdatファイル名一覧を取得してリスト化
    filelist=Path(current_directory_name).rglob("*.dat")
    dat_file_name_list=[]
    for file in filelist:
        dat_file_name_list.append(str(file))
    
    name=current_file_name

    #datファイルリストから現在開いているファイルのインデックスを取得
    current_file_index=dat_file_name_list.index(name)
    
    
    shutil.copy(dat_file_name_list[current_file_index],dat_file_name_list[current_file_index].replace(".dat","")+"_copy"+".dat")
    #shutil.move(dat_file_name_list[0].replace(".dat","")+"_copy"+".dat", directory)
    
    newfile=Path(current_directory_name).rglob("*copy.dat")
    for f in newfile:

        f.rename(f.stem+".csv")
        shutil.move(f.stem+".csv",current_directory_name) #ファイルの拡張子をcsvに変換
    
    for file in Path(current_directory_name).rglob("*copy.csv"): 
        col_name1=range(1,100) #列数がそろっていないと読み込みができないので、列数をあらかじめ定義する。一部のBias-spectroscopyファイルの列数が65になってしまっているため数が多くなっている。原因が分かれば改善できるのだが……
        df=pd.read_csv(file, names=col_name1, encoding="shift-jis", sep="\t") #上で指定した列数と指定のエンコーダーと区切り文字で各csvファイルを開く
        df=df.drop(range(15), axis=0) #開いたcsvファイルにおいて１４行目までを削除(axis=0は行の削除指定、axis=1だと列の削除指定になる)
        df.to_csv(file, header=False, index=False, encoding="shift-jis" ) #保存
    
    file_name_list=[]

    for file in Path(current_directory_name).rglob("*copy.csv"): 
        file_name_list.append(str(file))

    spec=pd.read_csv(file_name_list[0], encoding="shift-jis") #ファイルを読み込む
    spec.iloc[:, :]=spec.iloc[:, :].astype(float) #ファイルの各数値をfloat型に
    column_names=spec.columns.values #列名のリストを作成

    filter_button.configure(text="Filter_OFF", command=spectroscopy_filter_ON)

    if forward_or_backward_or_both=="forward":
        if column_names[0]=="Z rel (m)":
            x=spec["Z rel (m)"]
            y_forward=spec["Frequency Shift (Hz)"]
            plt.rcParams["figure.subplot.left"] = 0.24
            plt.rcParams["figure.subplot.bottom"] = 0.19
            plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            #y_forward=savgol_filter(y_forward,10,2)
            fig = Figure(figsize=(3, 3), dpi=100)
            ax = fig.add_subplot(1, 1, 1)
            line1 = ax.plot(x, y_forward)
            ax.set_xlabel("z")
            ax.set_ylabel("Δf")
            canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
            canvas.get_tk_widget().place(x=30,y=20)

        if column_names[0]=="Bias calc (V)":
            x=spec["Bias calc (V)"]
            y_forward=spec["Frequency Shift (Hz)"]
            plt.rcParams["figure.subplot.left"] = 0.24
            plt.rcParams["figure.subplot.bottom"] = 0.19
            plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            #y_forward=savgol_filter(y_forward,10,2)
            fig = Figure(figsize=(3, 3), dpi=100)
            ax = fig.add_subplot(1, 1, 1)
            line1 = ax.plot(x, y_forward)
            ax.set_xlabel('Bias(V)')
            ax.set_ylabel("Δf(Hz)")
            canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
            canvas.get_tk_widget().place(x=30,y=20)
    
    if forward_or_backward_or_both=="backward":
        if column_names[0]=="Z rel (m)":
            x=spec["Z rel (m)"]
            y_backward=spec["Frequency Shift [bwd] (Hz)"]
            plt.rcParams["figure.subplot.left"] = 0.24
            plt.rcParams["figure.subplot.bottom"] = 0.19
            plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            #y_backward=savgol_filter(y_backward,10,2)
            fig = Figure(figsize=(3, 3), dpi=100)
            ax = fig.add_subplot(1, 1, 1)
            line1 = ax.plot(x, y_backward)
            ax.set_xlabel("z")
            ax.set_ylabel("Δf")
            canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
            canvas.get_tk_widget().place(x=30,y=20)

        if column_names[0]=="Bias calc (V)":
            x=spec["Bias calc (V)"]
            y_backward=spec["Frequency Shift [bwd] (Hz)"]
            plt.rcParams["figure.subplot.left"] = 0.24
            plt.rcParams["figure.subplot.bottom"] = 0.19
            plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            #y_backward=savgol_filter(y_backward,10,2)
            fig = Figure(figsize=(3, 3), dpi=100)
            ax = fig.add_subplot(1, 1, 1)
            line1 = ax.plot(x, y_backward)
            ax.set_xlabel('Bias(V)')
            ax.set_ylabel("Δf(Hz)")
            canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
            canvas.get_tk_widget().place(x=30,y=20)
        
    if forward_or_backward_or_both=="bothward":
        if column_names[0]=="Z rel (m)":
            x=spec["Z rel (m)"]
            y_forward=spec["Frequency Shift (Hz)"]
            y_backward=spec["Frequency Shift [bwd] (Hz)"]
            plt.rcParams["figure.subplot.left"] = 0.24
            plt.rcParams["figure.subplot.bottom"] = 0.19
            plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rc('legend', fontsize=8)
            #y_forward=savgol_filter(y_forward,10,2)
            #y_backward=savgol_filter(y_backward,10,2)
            fig = Figure(figsize=(3, 3), dpi=100)
            ax = fig.add_subplot(1, 1, 1)
            line1 = ax.plot(x, y_forward, label="Forward")
            line2 = ax.plot(x, y_backward, label="Backward")
            ax.legend()
            ax.set_xlabel("z")
            ax.set_ylabel("Δf")
            canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
            canvas.get_tk_widget().place(x=30,y=20)

        if column_names[0]=="Bias calc (V)":
            x=spec["Bias calc (V)"]
            y_forward=spec["Frequency Shift (Hz)"]
            y_backward=spec["Frequency Shift [bwd] (Hz)"]
            plt.rcParams["figure.subplot.left"] = 0.24
            plt.rcParams["figure.subplot.bottom"] = 0.19
            plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
            plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
            plt.rc('legend', fontsize=8)
            #y_forward=savgol_filter(y_forward,10,2)
            #y_backward=savgol_filter(y_backward,10,2)
            fig = Figure(figsize=(3, 3), dpi=100)
            ax = fig.add_subplot(1, 1, 1)
            line1 = ax.plot(x, y_forward, label="Forward")
            line2 = ax.plot(x, y_backward, label="Backward")
            ax.legend()
            ax.set_xlabel('Bias(V)')
            ax.set_ylabel("Δf(Hz)")
            canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
            canvas.get_tk_widget().place(x=30,y=20)
    
    #ファイル名を取得して表示
    spectroscopy_image_name=get_file_name(current_file_name)
    label_spectroscopy_image_name.configure(text=spectroscopy_image_name)
    
    #作成したCSVファイルは最後に削除する
    os.remove(file_name_list[0])

#画像保存用関数
def save_image():
    global current_file_name
    global current_directory_name
    global forward_or_backward_or_both
    global filter_ON_OFF

    dt_now=datetime.datetime.now()
    dt=str(dt_now.year)+str(dt_now.month)+str(dt_now.day)+str(dt_now.hour)+str(dt_now.minute)+str(dt_now.second)+str(dt_now.microsecond)


    #現在選択されているディレクトリからdatファイル名一覧を取得してリスト化
    filelist=Path(current_directory_name).rglob("*.dat")
    dat_file_name_list=[]
    for file in filelist:
        dat_file_name_list.append(str(file))
    
    name=current_file_name

    #datファイルリストから現在開いているファイルのインデックスを取得
    current_file_index=dat_file_name_list.index(name)
    
    shutil.copy(dat_file_name_list[current_file_index],dat_file_name_list[current_file_index].replace(".dat","")+"_copy"+".dat")
    #shutil.move(dat_file_name_list[0].replace(".dat","")+"_copy"+".dat", directory)
    
    newfile=Path(current_directory_name).rglob("*copy.dat")
    for f in newfile:

        f.rename(f.stem+".csv")
        shutil.move(f.stem+".csv",current_directory_name) #ファイルの拡張子をcsvに変換
    
    for file in Path(current_directory_name).rglob("*copy.csv"): 
        col_name1=range(1,100) #列数がそろっていないと読み込みができないので、列数をあらかじめ定義する。一部のBias-spectroscopyファイルの列数が65になってしまっているため数が多くなっている。原因が分かれば改善できるのだが……
        df=pd.read_csv(file, names=col_name1, encoding="shift-jis", sep="\t") #上で指定した列数と指定のエンコーダーと区切り文字で各csvファイルを開く
        df=df.drop(range(15), axis=0) #開いたcsvファイルにおいて１４行目までを削除(axis=0は行の削除指定、axis=1だと列の削除指定になる)
        df.to_csv(file, header=False, index=False, encoding="shift-jis" ) #保存
    
    file_name_list=[]

    for file in Path(current_directory_name).rglob("*copy.csv"): 
        file_name_list.append(str(file))

    spec=pd.read_csv(file_name_list[0], encoding="shift-jis") #ファイルを読み込む
    spec.iloc[:, :]=spec.iloc[:, :].astype(float) #ファイルの各数値をfloat型に
    column_names=spec.columns.values #列名のリストを作成

    if filter_ON_OFF=="ON":
        if forward_or_backward_or_both=="forward":
            if column_names[0]=="Z rel (m)":
                x=spec["Z rel (m)"]
                y_forward=spec["Frequency Shift (Hz)"]
                plt.rcParams["figure.subplot.left"] = 0.24
                plt.rcParams["figure.subplot.bottom"] = 0.19
                plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                y_forward=savgol_filter(y_forward,11,3)
                fig = Figure(figsize=(3, 3), dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                line1 = ax.plot(x, y_forward)
                ax.set_xlabel("z")
                ax.set_ylabel("Δf")
                fig.savefig(file_name_list[0].replace("copy.csv", "")+str(dt)+".png")
                canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
                canvas.get_tk_widget().place(x=30,y=20)

            if column_names[0]=="Bias calc (V)":
                x=spec["Bias calc (V)"]
                y_forward=spec["Frequency Shift (Hz)"]
                plt.rcParams["figure.subplot.left"] = 0.24
                plt.rcParams["figure.subplot.bottom"] = 0.19
                plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                y_forward=savgol_filter(y_forward,11,3)
                fig = Figure(figsize=(3, 3), dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                line1 = ax.plot(x, y_forward)
                ax.set_xlabel('Bias(V)')
                ax.set_ylabel("Δf(Hz)")
                fig.savefig(file_name_list[0].replace("copy.csv", "")+str(dt)+".png")
                canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
                canvas.get_tk_widget().place(x=30,y=20)
    
        elif forward_or_backward_or_both=="backward":
            if column_names[0]=="Z rel (m)":
                x=spec["Z rel (m)"]
                y_backward=spec["Frequency Shift [bwd] (Hz)"]
                plt.rcParams["figure.subplot.left"] = 0.24
                plt.rcParams["figure.subplot.bottom"] = 0.19
                plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                y_backward=savgol_filter(y_backward,11,3)
                fig = Figure(figsize=(3, 3), dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                line1 = ax.plot(x, y_backward)
                ax.set_xlabel("z")
                ax.set_ylabel("Δf")
                fig.savefig(file_name_list[0].replace("copy.csv", "")+str(dt)+".png")
                canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
                canvas.get_tk_widget().place(x=30,y=20)

            if column_names[0]=="Bias calc (V)":
                x=spec["Bias calc (V)"]
                y_backward=spec["Frequency Shift [bwd] (Hz)"]
                plt.rcParams["figure.subplot.left"] = 0.24
                plt.rcParams["figure.subplot.bottom"] = 0.19
                plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                y_backward=savgol_filter(y_backward,11,3)
                fig = Figure(figsize=(3, 3), dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                line1 = ax.plot(x, y_backward)
                ax.set_xlabel('Bias(V)')
                ax.set_ylabel("Δf(Hz)")
                fig.savefig(file_name_list[0].replace("copy.csv", "")+str(dt)+".png")
                canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
                canvas.get_tk_widget().place(x=30,y=20)
        
        elif forward_or_backward_or_both=="bothward":
            if column_names[0]=="Z rel (m)":
                x=spec["Z rel (m)"]
                y_forward=spec["Frequency Shift (Hz)"]
                y_backward=spec["Frequency Shift [bwd] (Hz)"]
                plt.rcParams["figure.subplot.left"] = 0.24
                plt.rcParams["figure.subplot.bottom"] = 0.19
                plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rc('legend', fontsize=8)
                y_forward=savgol_filter(y_forward,11,3)
                y_backward=savgol_filter(y_backward,11,3)
                fig = Figure(figsize=(3, 3), dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                line1 = ax.plot(x, y_forward, label="Forward")
                line2 = ax.plot(x, y_backward, label="Backward")
                ax.legend()
                ax.set_xlabel("z")
                ax.set_ylabel("Δf")
                fig.savefig(file_name_list[0].replace("copy.csv", "")+str(dt)+".png")
                canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
                canvas.get_tk_widget().place(x=30,y=20)

            if column_names[0]=="Bias calc (V)":
                x=spec["Bias calc (V)"]
                y_forward=spec["Frequency Shift (Hz)"]
                y_backward=spec["Frequency Shift [bwd] (Hz)"]
                plt.rcParams["figure.subplot.left"] = 0.24
                plt.rcParams["figure.subplot.bottom"] = 0.19
                plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rc('legend', fontsize=8)
                y_forward=savgol_filter(y_forward,11,3)
                y_backward=savgol_filter(y_backward,11,3)
                fig = Figure(figsize=(3, 3), dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                line1 = ax.plot(x, y_forward, label="Forward")
                line2 = ax.plot(x, y_backward, label="Backward")
                ax.legend()
                ax.set_xlabel('Bias(V)')
                ax.set_ylabel("Δf(Hz)")
                fig.savefig(file_name_list[0].replace("copy.csv", "")+str(dt)+".png")
                canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
                canvas.get_tk_widget().place(x=30,y=20)
    
    if filter_ON_OFF=="OFF":
        if forward_or_backward_or_both=="forward":
            if column_names[0]=="Z rel (m)":
                x=spec["Z rel (m)"]
                y_forward=spec["Frequency Shift (Hz)"]
                plt.rcParams["figure.subplot.left"] = 0.24
                plt.rcParams["figure.subplot.bottom"] = 0.19
                plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                #y_forward=savgol_filter(y_forward,11,3)
                fig = Figure(figsize=(3, 3), dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                line1 = ax.plot(x, y_forward)
                ax.set_xlabel("z")
                ax.set_ylabel("Δf")
                fig.savefig(file_name_list[0].replace("copy.csv", "")+str(dt)+".png")
                canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
                canvas.get_tk_widget().place(x=30,y=20)

            if column_names[0]=="Bias calc (V)":
                x=spec["Bias calc (V)"]
                y_forward=spec["Frequency Shift (Hz)"]
                plt.rcParams["figure.subplot.left"] = 0.24
                plt.rcParams["figure.subplot.bottom"] = 0.19
                plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                #y_forward=savgol_filter(y_forward,11,3)
                fig = Figure(figsize=(3, 3), dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                line1 = ax.plot(x, y_forward)
                ax.set_xlabel('Bias(V)')
                ax.set_ylabel("Δf(Hz)")
                fig.savefig(file_name_list[0].replace("copy.csv", "")+str(dt)+".png")
                canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
                canvas.get_tk_widget().place(x=30,y=20)
    
        elif forward_or_backward_or_both=="backward":
            if column_names[0]=="Z rel (m)":
                x=spec["Z rel (m)"]
                y_backward=spec["Frequency Shift [bwd] (Hz)"]
                plt.rcParams["figure.subplot.left"] = 0.24
                plt.rcParams["figure.subplot.bottom"] = 0.19
                plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                #y_backward=savgol_filter(y_backward,11,3)
                fig = Figure(figsize=(3, 3), dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                line1 = ax.plot(x, y_backward)
                ax.set_xlabel("z")
                ax.set_ylabel("Δf")
                fig.savefig(file_name_list[0].replace("copy.csv", "")+str(dt)+".png")
                canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
                canvas.get_tk_widget().place(x=30,y=20)

            if column_names[0]=="Bias calc (V)":
                x=spec["Bias calc (V)"]
                y_backward=spec["Frequency Shift [bwd] (Hz)"]
                plt.rcParams["figure.subplot.left"] = 0.24
                plt.rcParams["figure.subplot.bottom"] = 0.19
                plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                #y_backward=savgol_filter(y_backward,11,3)
                fig = Figure(figsize=(3, 3), dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                line1 = ax.plot(x, y_backward)
                ax.set_xlabel('Bias(V)')
                ax.set_ylabel("Δf(Hz)")
                fig.savefig(file_name_list[0].replace("copy.csv", "")+str(dt)+".png")
                canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
                canvas.get_tk_widget().place(x=30,y=20)
        
        elif forward_or_backward_or_both=="bothward":
            if column_names[0]=="Z rel (m)":
                x=spec["Z rel (m)"]
                y_forward=spec["Frequency Shift (Hz)"]
                y_backward=spec["Frequency Shift [bwd] (Hz)"]
                plt.rcParams["figure.subplot.left"] = 0.24
                plt.rcParams["figure.subplot.bottom"] = 0.19
                plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rc('legend', fontsize=8)
                #y_forward=savgol_filter(y_forward,11,3)
                #y_backward=savgol_filter(y_backward,11,3)
                fig = Figure(figsize=(3, 3), dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                line1 = ax.plot(x, y_forward, label="Forward")
                line2 = ax.plot(x, y_backward, label="Backward")
                ax.legend()
                ax.set_xlabel("z")
                ax.set_ylabel("Δf")
                fig.savefig(file_name_list[0].replace("copy.csv", "")+str(dt)+".png")
                canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
                canvas.get_tk_widget().place(x=30,y=20)

            if column_names[0]=="Bias calc (V)":
                x=spec["Bias calc (V)"]
                y_forward=spec["Frequency Shift (Hz)"]
                y_backward=spec["Frequency Shift [bwd] (Hz)"]
                plt.rcParams["figure.subplot.left"] = 0.24
                plt.rcParams["figure.subplot.bottom"] = 0.19
                plt.rcParams["xtick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["ytick.labelsize"] = 8        # 目盛りのフォントサイズ
                plt.rcParams["xtick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rcParams["ytick.direction"] = "in"      # 目盛り線の向き、内側"in"か外側"out"かその両方"inout"か
                plt.rc('legend', fontsize=8)
                #y_forward=savgol_filter(y_forward,11,3)
                #y_backward=savgol_filter(y_backward,11,3)
                fig = Figure(figsize=(3, 3), dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                line1 = ax.plot(x, y_forward, label="Forward")
                line2 = ax.plot(x, y_backward, label="Backward")
                ax.legend()
                ax.set_xlabel('Bias(V)')
                ax.set_ylabel("Δf(Hz)")
                fig.savefig(file_name_list[0].replace("copy.csv", "")+str(dt)+".png")
                canvas = FigureCanvasTkAgg(fig, frame_spectroscopy_image)
                canvas.get_tk_widget().place(x=30,y=20)
                
    
    #ファイル名を取得して表示
    spectroscopy_image_name=get_file_name(current_file_name)
    label_spectroscopy_image_name.configure(text=spectroscopy_image_name)
    
    #作成したCSVファイルは最後に削除する
    os.remove(file_name_list[0])



root = tkinter.Tk()
root.attributes("-topmost", True)
version = tkinter.Tcl().eval('info patchlevel')
root.title("Spectroscopy Inspector"+version)
root.minsize(width=600, height=630)
root.config(bg="black")


#アプリ上部に表示されるタイトル
label_title=tkinter.Label(root, text="Spectroscopy Inspector", fg="#33CC33", bg="black", font=("IPAPGothic",24))
label_title.place(x=120,y=10)

#ディレクトリ選択用のボタンのフレームとボタンオブジェクト
frame_directory_select=tkinter.Frame(root, bg="black", width=600, height=100)
frame_directory_select.place(x=0,y=60)

directory_select_button=tkinter.Button(frame_directory_select, text="select directory", fg="#33CC33", bg="#183C06", font=("IPAPGothic",12) , command=open_directory)
directory_select_button.place(x=240, y=20)

#スペクトル表示用のフレーム
frame_spectroscopy_image=tkinter.Frame(root, bg="black", width=360,height=340)
frame_spectroscopy_image.place(x=10,y=120)

#スペクトル名表示用のフレーム
#frame_spectroscopy_image_name=tkinter.Frame(root, bg="white", width=340, height=30)
#frame_spectroscopy_image_name.place(x=10, y=475)

label_spectroscopy_image_name=tkinter.Label(root,text=current_file_name, fg="#33CC33", bg="black", font=("IPAPGothic",12))
label_spectroscopy_image_name.place(x=100, y=445)

#スペクトル画像操作用のフレームとボタンオブジェクト
frame_change_spectroscopy_image=tkinter.Frame(root, bg="black", width=200, height=200)
frame_change_spectroscopy_image.place(x=380,y=200)
#ForwardとBackwardの選択ボタン
change_forward_and_backward_button=tkinter.Button(frame_change_spectroscopy_image, text="Forward", fg="#33CC33", bg="#183C06", font=("IPAPGothic",12), command=change_forward_to_backward)
change_forward_and_backward_button.place(x=0,y=40)
#フィルターのオンオフボタン
filter_button=tkinter.Button(frame_change_spectroscopy_image, text="filter OFF", fg="#33CC33", bg="#183C06", font=("IPAPGothic",12), command=spectroscopy_filter_ON)
filter_button.place(x=0,y=140)

#データのセーブと選択用のフレームとボタンオブジェクト
frame_save_and_select_data=tkinter.Frame(root, bg="black", width=400, height=100)
frame_save_and_select_data.place(x=100,y=510)
#セーブ用のボタン
save_button=tkinter.Button(frame_save_and_select_data, text="Save", fg="#33CC33", bg="#183C06", font=("IPAPGothic",12), command=save_image)
save_button.place(x=175,y=30)
#前に進むボタン
forward_button=tkinter.Button(frame_save_and_select_data, text="▶", fg="#33CC33", bg="#183C06", font=("IPAPGothic",12),command=change_file_forward)
forward_button.place(x=248,y=30)
#後ろに進むボタン
back_button=tkinter.Button(frame_save_and_select_data, text="◀", fg="#33CC33", bg="#183C06", font=("IPAPGothic",12), command=change_file_backward)
back_button.place(x=125,y=30)

root.mainloop()