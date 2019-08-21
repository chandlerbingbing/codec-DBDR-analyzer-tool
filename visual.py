#!/usr/bin/env python

"""
Visually show various metrics between two YCbCr sequences
using matplotlib
"""

import argparse
import time
import os
import xlrd
# import xlwt

import numpy as np
import matplotlib.pyplot as plt
from ycbcr import YCbCr
from matplotlib.gridspec import GridSpec
import bjontegaard_metric as BD
import OptionDictionary as config


def create_title_string(title, subtitle):
    """
    Helper function to generate a nice looking
    title string
    """
    return "{} {}\n{}".format(
        os.path.basename(title),
        'VS.',
        " ".join([os.path.basename(i) for i in subtitle]))


def plot_psnr(arg):
    """
    PSNR
    """
    t, st = vars(arg)['filename'], vars(arg)['filename_diff']
    for f in st:
        vars(arg)['filename_diff'] = f
        yuv = YCbCr(**vars(arg))

        psnr = [p[3] for p in yuv.psnr()]

        N = len(psnr[:-2])
        ind = np.arange(N)  # the x locations for the groups

        # To get a uniq identifier
        plt.plot(ind, psnr[:-2], 'o-', label=f[-10:-8])

        del yuv

    plt.legend()
    plt.title(create_title_string(t, st))
    plt.ylabel('weighted dB')
    plt.xlabel('frame')
    plt.grid(True)
    plt.show()


def sort_point(ind, point):
    contain = []
    for i in range(len(ind)):
        contain.append([ind[i], point[i]])

    def takefirst(ele):
        return ele[0]

    contain.sort(key=takefirst)
    ind = []
    point = []
    for i in range(len(contain)):
        ind.append(contain[i][0])
        point.append(contain[i][1])
    return [ind, point]


def calculate_distance(BD_contain):
    celltext = []
    rowname = []
    tag = 0
    while tag < len(BD_contain):
        x265_rate = BD.BD_RATE(BD_contain[tag][0], BD_contain[tag][1], BD_contain[tag+1][0], BD_contain[tag+1][1])
        svt_rate = BD.BD_RATE(BD_contain[tag][0], BD_contain[tag][1], BD_contain[tag+2][0], BD_contain[tag+2][1])
        x265_psnr = BD.BD_PSNR(BD_contain[tag][0], BD_contain[tag][1], BD_contain[tag+1][0], BD_contain[tag+1][1])
        svt_psnr = BD.BD_PSNR(BD_contain[tag][0], BD_contain[tag][1], BD_contain[tag+2][0], BD_contain[tag+2][1])
        rowname.append(BD_contain[tag][3][0].split('/')[-1]+'_'+BD_contain[tag][2])
        rowname.append(BD_contain[tag+1][3][0].split('/')[-1]+'_'+BD_contain[tag+1][2])
        rowname.append(BD_contain[tag+2][3][0].split('/')[-1]+'_'+BD_contain[tag+2][2])
        celltext.append(['HM base line', 'HM base line'])
        celltext.append([x265_rate, x265_psnr])
        celltext.append([svt_rate, svt_psnr])
        tag += 3
    return celltext,rowname

def calculate_average(BD_contain):
    celltext = []
    rowname = []
    tag = 0
    while tag < len(BD_contain):
        HM_rate = BD.BD_RATE_Average(BD_contain[tag][0],BD_contain[tag][1])
        HM_psnr = BD.BD_PSNR_Average(BD_contain[tag][0],BD_contain[tag][1])
        x265_rate = BD.BD_RATE_Average(BD_contain[tag+1][0], BD_contain[tag+1][1])
        svt_rate = BD.BD_RATE_Average(BD_contain[tag+2][0], BD_contain[tag+2][1])
        x265_psnr = BD.BD_PSNR_Average(BD_contain[tag+1][0], BD_contain[tag+1][1])
        svt_psnr = BD.BD_PSNR_Average(BD_contain[tag+2][0], BD_contain[tag+2][1])
        rowname.append(BD_contain[tag][3][0].split('/')[-1]+'_'+BD_contain[tag][2])
        rowname.append(BD_contain[tag+1][3][0].split('/')[-1]+'_'+BD_contain[tag+1][2])
        rowname.append(BD_contain[tag+2][3][0].split('/')[-1]+'_'+BD_contain[tag+2][2])
        celltext.append([HM_rate, HM_psnr])
        celltext.append([x265_rate, x265_psnr])
        celltext.append([svt_rate, svt_psnr])
        tag += 3
    return celltext,rowname

def get_psnr_value(contain, bits_psnr=0):
    BD_contain = []
    for i in range(len(contain)):
        yuv = YCbCr(filename=contain[i][0], filename_diff=contain[i][1], width=int(contain[i][5]), height=int(contain[i][6]), yuv_format_in=contain[i][7], bitdepth=contain[i][4])
        for infile in range(len(contain[i][0])):
            point = []
            xax = []
            for diff_file in range(len(contain[i][1])):
                temp = [p for p in yuv.psnr_all(diff_file, infile)]
                ind = np.arange(len(temp))
                frame = [frame_order[0] for frame_order in temp]
                point.append(temp[-1])
                xax.append(contain[i][2][diff_file])
                # frames_psnr.plot(ind[0:-1], frame[0:-1], 'o-', label=contain[i][3]+'_'+str(contain[i][2][diff_file]))
            temp_sort = sort_point(xax, point)
            db_psnr_contain = []
            for db_psnr in temp_sort[1]:
                db_psnr_contain.append(db_psnr[-1])
            if bits_psnr is 0:
                BD_contain.append([temp_sort[0], db_psnr_contain, contain[i][3], contain[i][0], temp_sort[1]])
            else:
                bits_psnr.plot(temp_sort[0], db_psnr_contain, 'o-', label=contain[i][3])
                BD_contain.append([temp_sort[0], db_psnr_contain, contain[i][3], contain[i][0], temp_sort[1]])
    return BD_contain


def plot_psnr_frames(contain, case_count):
    """
    PSNR, all planes
    """
    # ind = arg.Bit_rate  # the x locations for the groups
    fig = plt.figure(figsize=[16, 6], constrained_layout=True)
    gs = GridSpec(2, 2, figure=fig)
    plt.suptitle('yuv Quality plot')
    # frames_psnr = fig.add_subplot(gs[:, 0])
    bits_psnr = fig.add_subplot(gs[0, 0])
    DBDR_for_each = fig.add_subplot(gs[0, 1])
    DBDR_for_each.set_axis_off()
    DBDR_plot = fig.add_subplot(gs[1, 0])
    DBDR = fig.add_subplot(gs[1, 1])
    DBDR.set_axis_off()
    # frames_psnr.set_title('Psnr-Y vs Frames')
    # frames_psnr.set_xlabel('frames')
    # frames_psnr.set_ylabel('Psnr-y')
    bits_psnr.set_title('Psnr vs Bitrate')
    bits_psnr.set_xlabel('bitrate')
    bits_psnr.set_ylabel('psnr')
    BD_contain = get_psnr_value(contain, bits_psnr)
    celltext, rowname = calculate_distance(BD_contain)
    DBDR.table(cellText=celltext, colLabels=['BDBR', 'BD-PSNR'], rowLabels=rowname, loc='center',colWidths=[0.2, 0.2])
    celltext, rowname = calculate_average(BD_contain)
    DBDR_for_each.table(cellText=celltext, colLabels=['BDBR', 'BD-PSNR'], rowLabels=rowname, loc='center',colWidths=[0.2, 0.2])
    # frames_psnr.legend()
    bits_psnr.legend()
    bits_psnr.grid(True)
    # fig.align_labels()
    #TODO we should store our data ,and when we get a lot of case, we need to get average number
    # it means just for a one plot
    if case_count is 0:
        plt.show()
    else:
        plt.pause(10)


def calculate_JustOne_distance(Baseline, svt_diff):
    return BD.BD_RATE(Baseline[0], Baseline[1], svt_diff[0], svt_diff[1])

def calculate_svt_distance(BD_contain):
    BDRate_Container = []
    Baseline = BD_contain[0]
    mode_sum = len(config.svt_mode)
    for mode_num in range(mode_sum):
        for svt_diff in range(len(config.svt_Qp)):
            BDRate = calculate_JustOne_distance(Baseline, BD_contain[svt_diff*mode_sum+mode_num])
            BDRate_Container.append(BDRate)
    return BDRate_Container

def get_Xaxis_value():
    mode_sum = len(config.svt_mode)
    compare_sum = len(config.svt_Qp)
    Xaxis_name = []
    for i in range(1, compare_sum):
        for j in range(mode_sum):
            name = '%sM%d vs %s_M%d'%(config.svt_Qp[i][2], j, config.svt_Qp[0][2], j)
            Xaxis_name.append(name)
    return Xaxis_name

def get_celltext(BDRate_Container):
    mode_sum = len(config.svt_mode)
    codec_sum = len(config.svt_Qp)
    BDRate_table = []
    for j in range(mode_sum):
        row_value = []
        for i in range(codec_sum):
            row_value.append(BDRate_Container[i*mode_sum+j])
        BDRate_table.append(row_value)
    return BDRate_table

def get_collable():
    collable = []
    for i in config.svt_Qp:
        collable.append(i[2])
    return collable

def plot_psnr_svt(contain, case_count):
    #TODO finish svt config psnr
    fig = plt.figure(figsize=[16, 6], constrained_layout=True)
    gs = GridSpec(1, 2, figure=fig)
    plt.suptitle('PSNR BDRate')
    chart = fig.add_subplot(gs[0, 0])
    table = fig.add_subplot(gs[0, 1])
    table.set_axis_off()
    chart.set_title('BDRate vs Mode')
    chart.set_xlabel('Mode')
    chart.set_ylabel('BDRate')
    BD_contain = get_psnr_value(contain)
    BDRate_Container = calculate_svt_distance(BD_contain)
    celltext = get_celltext(BDRate_Container)
    Xaxis_name = get_Xaxis_value()
    collable = get_collable()
    table.table(cellText=celltext, colLabels=collable, rowLabels=Xaxis_name, loc='center',colWidths=[0.2, 0.2])
    mode_sum = len(config.svt_mode)
    codec_sum = len(config.svt_Qp)
    for codec in range(codec_sum):
        chart.plot(config.svt_mode,BDRate_Container[codec*mode_sum:(codec+1)*mode_sum], 'o-', label=config.svt_Qp[codec][2])
    chart.xlim(-100, 100)
    chart.legend()
    chart.grid(True)
    #TODO we should store our data ,and when we get a lot of case, we need to get average number
    # it means just for a one plot
    if case_count is 0:
        plt.show()
    else:
        plt.pause(10)

def find_all_yuv_fromdir(arg, inputfile,grouptag):
    path = arg.inputpath
    dirs = os.listdir(path)
    Originalyuvpath = []
    for file in dirs:
        if file == inputfile:
            Originalyuvpath.append(os.path.join(path, file))
            break
    encodeyuvpath = []
    for tag in range(len(grouptag)):
        for file in dirs:
            if file == grouptag[tag]:
                encodeyuvpath.append(os.path.join(path, file))
                break
    return [Originalyuvpath, encodeyuvpath, arg.Bit_rate, inputfile]


def find_all_yuv(arg, inputfile, grouptag):
    workbook = xlrd.open_workbook(arg.inputpath)
    worksheet = workbook.sheet_by_index(0)
    y = 0
    titlename = {}
    while y < worksheet.ncols:
        titlename[str(worksheet.cell(0, y).value)] = y
        y += 1
    order = 0
    while order < worksheet.nrows:
        if worksheet.cell(order, 0).value == inputfile:
            break
        order = order+1
    Originalyuvpath = [str(worksheet.cell(order, 3).value)]
    encodeyuvpath = []
    encodeyuvbitrate = []
    encodeyuvbitdepth = 8
    width = 1
    height = 1
    type = 'YU12'
    linetag = 'haha'
    order = 0
    while order < worksheet.nrows:
        if worksheet.cell(order, 7).value == inputfile and worksheet.cell(order, 8).value == grouptag:
            encodeyuvpath.append(str(worksheet.cell(order, 3).value))
            encodeyuvbitrate.append(worksheet.cell(order, 6).value)
            linetag = str(worksheet.cell(order, 8).value)
            # linetag = str(worksheet.cell(order, 8).value + '_' + worksheet.cell(order, 7).value)
            encodeyuvbitdepth = int(worksheet.cell(order, 5).value)
            width = int(worksheet.cell(order, 1).value)
            height = int(worksheet.cell(order, 2).value)
            type = str(worksheet.cell(order, 4).value)
        order = order+1
    return [Originalyuvpath, encodeyuvpath, encodeyuvbitrate, linetag, encodeyuvbitdepth, width, height, type]


def main():
    args = parse_args()
    contain = []
    for i in range(len(args.input_test)):
        compare_test = find_all_yuv(args, args.input_test[i], args.grouptag[i])
        contain.append(compare_test)
    t1 = time.clock()
    plot_psnr_frames(contain)
    t2 = time.clock()
    print "\nTime: ", round(t2 - t1, 4)


def parse_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument('-I', '--filename', type=str, help='filename', nargs='+')
    # we need modify this to read excel path
    parser.add_argument('-I', '--inputpath', type=str, help='the excel configure file path', nargs='?')
    # parser.add_argument('-g', '--testgroup', type=int, help='testgroup_number',  nargs='?')
    parser.add_argument('-P', '--input_test', type=str, help='the Original yuv file name, you can put plenty,and separate by dot', nargs='+', required=False)
    parser.add_argument('-po', '--compare_test', type=str, help='compare_test_plan',  action='append', required=False)
    parser.add_argument('-W', '--width', type=int, required=False, help='width')
    parser.add_argument('-H', '--height', type=int, required=False, help='height')
    parser.add_argument('-C', '--yuv_format_in', choices=['IYUV', 'UYVY', 'YV12', 'YVYU', 'YUY2', '422'], required=False, help='type')
    parser.add_argument('-M', '--Bit_rate', type=int, help='bitrate with compare yuv', nargs='+')
    parser.add_argument('-G', '--grouptag', type=str, help='different transcoding yuv', nargs='+')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
