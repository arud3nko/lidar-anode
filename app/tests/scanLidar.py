import serial

import math
import datetime
import datetime
import socket
import time
import csv
import multiprocessing
import threading

import matplotlib
import matplotlib.pyplot as plt

import numpy
import pandas as pd
from sklearn.cluster import DBSCAN
from settings_lidar import lidarSettings


def counting_arrays(string, choice, c_array):
    angle_count = 0
    while len(string) > 1:
        dec = int(string[0:4], 16)  # считывание двух байтов информации
        string = string[4:len(string)]
        if choice == 1:  # расчет длины
            c_array.append(float(dec) / 10000)
        elif choice == 2:  # расчет углов
            c_array.append(55 + (angle_count * 0.0833))  # 55 - начальный угол, 0.0833 - расстояние между углами
            angle_count = angle_count + 1
        elif choice == 3:  # для refl (не используется)
            c_array.append(dec)
    return c_array
    # print("len of angles: " + str(len(c_arrays_angle)))
    # print("len of lens: " + str(len(c_arrays_len)) + "\n")


def counting(c_arrays_len, c_arrays_angle, z, value_counting):
    coord_array = []
    for j in range(len(c_arrays_len)):  # c_arrays_len выбрана за длину просто так, потому что длины массивов расстояний и углов одинаковы
        coordinates = []
        length = c_arrays_len[j]
        # if j > 820:
        #     print(str(j) + " " + str(c_arrays_angle[j]))

        # иногда происходит/происходил баг с длинной массива; просто для отслеживания
        if len(c_arrays_angle) != 841:  # 841 - количество точек в одном 2d срезе
            print(len(c_arrays_len))
            print(len(c_arrays_angle))
            print(value_counting)

        angle_rad = c_arrays_angle[j] * math.pi / 180
        x = math.cos(angle_rad) * length
        y = math.sin(angle_rad) * length
        if length != 0:
            coordinates.append(x)
            coordinates.append(y)
            coordinates.append(z)
            coord_array.append(coordinates)
    return coord_array


def moving(client, semaphore_move):
    values_start = [0x00, 0x00, 0x02, 0x03, 0x45, 0x41]
    values_return = [0x00, 0x00, 0x02, 0x02, 0x85, 0x80]
    values_stop = [0x00, 0x00, 0x02, 0x01, 0x84, 0xc0]

    semaphore_move.acquire()
    print('start move ' + str(datetime.datetime.now()))
    semaphore_move.release()

    client.write(values_start)
    time.sleep(14)
    print(client.readline())

    print('end move ' + str(datetime.datetime.now()))

    client.write(values_stop)
    print(client.readline())

    client.write(values_return)
    time.sleep(14)
    print(client.readline())


def scanning(client, semaphore_scan):

    semaphore_scan.acquire()
    print('scan ' + str(datetime.datetime.now()))
    semaphore_scan.release()

    slices = 1300  # количество 2d срезов

    MESSAGE1 = b'\x02\x02\x02\x02\x00\x00\x00\x17\x73\x4D\x4E\x20\x53\x65\x74\x41\x63\x63\x65\x73\x73\x4D\x6F\x64\x65\x20\x03\xF4\x72\x47\x44\xB3'
    MESSAGE_START_MON = b'\x02\x02\x02\x02\x00\x00\x00\x14\x73\x45\x4E\x20\x4C\x4D\x44\x73\x63\x61\x6E\x64\x61\x74\x61\x6D\x6F\x6E\x20\x01\x5F'
    MESSAGE_STOP_MON = b'\x02\x02\x02\x02\x00\x00\x00\x14\x73\x45\x4E\x20\x4C\x4D\x44\x73\x63\x61\x6E\x64\x61\x74\x61\x6D\x6F\x6E\x20\x00\x5E'

    MESSAGE_START_FAST = b'\x02\x02\x02\x02\x00\x00\x00\x11\x73\x45\x4E\x20\x4C\x4D\x44\x73\x63\x61\x6E\x64\x61\x74\x61\x20\x01\x33'  # команда тепловизору "начать измерения"
    MESSAGE_STOP_FAST = b'\x02\x02\x02\x02\x00\x00\x00\x11\x73\x45\x4E\x20\x4C\x4D\x44\x73\x63\x61\x6E\x64\x61\x74\x61\x20\x00\x32'  # команда тепловизору "остановить измерения"
    MESSAGE_ONE = b'\x02\x02\x02\x02\x00\x00\x00\x0F\x73\x52\x4E\x20\x4C\x4D\x44\x73\x63\x61\x6E\x64\x61\x74\x61\x05'


    # включают и отключают лазер у тепловизора (возможно не работают)
    MESSAGE_START_MES = b'\x02\x02\x02\x02\x00\x00\x00\x10\x73\x4D\x4E\x20\x4C\x4D\x43\x73\x74\x61\x72\x74\x6D\x65\x61\x73\x68'  # команда тепловизору "включить режим измерений"
    MESSAGE_STANDBY = b'\x02\x02\x02\x02\x00\x00\x00\x0E\x73\x4D\x4E\x20\x4C\x4D\x43\x73\x74\x61\x6E\x64\x62\x79\x65'  # команда тепловизору "отключить режим измерений"

    z = 0.0018562291554143687  # расстояние между срезами
    str0 = []
    arrays = []
    # arrays_csv = []
    c_arrays_len = []
    # c_arrays_refl = []
    c_arrays_angle = []

    time.sleep(0.5)
    client.sendall(MESSAGE_START_MES)
    in_data = client.recv(100)
    print(in_data.hex())

    client.sendall(MESSAGE_START_FAST)
    in_data = client.recv(100)
    print(in_data.hex())

    print(datetime.datetime.now())
    for i in range(slices):
        # with refl client.recv(5192)
        in_data = client.recv(3489)  # длина одного сообщения, содержащего один 2d срез
        str0.append(in_data.hex())

    client.sendall(MESSAGE_STOP_FAST)
    print(datetime.datetime.now())

    client.sendall(MESSAGE_STANDBY)
    in_data = client.recv(100)
    print(in_data.hex())

    for i in range(len(str0)):
        if (i == 0):
            print('len ' + str(len(str0))) 
            print('start counting ' + str(datetime.datetime.now()))
        if (i == len(str0)-1):
            print('stop counting ' + str(datetime.datetime.now()))
        value = str0[i]
        # with refl value [182:10358]
        value = value[182:6952]  # данные одного среза, содержащие длины и углы точек; обрезана ненужная информация
        c_arrays_len = counting_arrays(value[0:3364], 1, c_arrays_len)  # подсчет длин
        value = value[3406:len(value)]
        c_arrays_angle = counting_arrays(value[0:3364], 2, c_arrays_angle)  # подсчет углов

        # value = value[3406:len(value)]
        # counting_arrays(value[0:3364], 3)

        # расчет координат
        coord_array = counting(c_arrays_len, c_arrays_angle, z, value)
        for i in range(len(coord_array)):
            # arrays_csv.append(coord_array[i][0])
            # arrays_csv.append(coord_array[i][1])
            # arrays_csv.append(coord_array[i][2])
            arrays.append(coord_array[i])
        c_arrays_angle.clear()
        c_arrays_len.clear()
        z = z + 0.0018562291554143687

    # string = str(datetime.datetime.now())
    # string = string.replace(':', '-')
    
    # frame = pd.DataFrame(list(func_chunk(arrays_csv)))
    # name = string + '.csv'
    # frame.to_csv(name, index=False)
    
    # myFile = open(name, 'w')
    # with myFile:
    #     writer = csv.writer(myFile)
    #     writer.writerows(list(func_chunk(arrays_csv)))
    
    print('start analize ' + str(datetime.datetime.now()))
    final_results = final_analize(arrays)
    print('stop analize ' + str(datetime.datetime.now()))

    # scan_results_file = open(f'full_scans/{str(datetime.datetime.now().time()).replace(":", "-")}.txt', 'w')
    # scan_results_file.write(str(str0))
    # scan_results_file.close

    # сохранение результатов
    log_file = None
    cur_date = datetime.datetime.now()
    cur_month = "0" + str(cur_date.month) if len(str(cur_date.month)) == 1 else cur_date.month
    cur_day = "0" + str(cur_date.day) if len(str(cur_date.day)) == 1 else cur_date.day
    cur_hour = "0" + str(cur_date.hour) if len(str(cur_date.hour)) == 1 else cur_date.hour
    cur_minute = "0" + str(cur_date.minute) if len(str(cur_date.minute)) == 1 else cur_date.minute
    cur_second = "0" + str(cur_date.second) if len(str(cur_date.second)) == 1 else cur_date.second
    try:
       log_file = open(f'lidar_scans/{str(cur_date.date())}.txt', 'a')
    except Exception as e:
       log_file = open(f'lidar_scans/{str(cur_date.date())}.txt', 'w')
    finally:
       date_now = f'{cur_date.year}{cur_month}{cur_day}{cur_hour}{cur_minute}{cur_second}_{cur_hour}_{cur_date.year}{cur_month}{cur_day}'
       horizontal = f'horizontal: {final_results["horizontal"][0][0]}, {final_results["horizontal"][1][0]}, {final_results["horizontal"][2][0]}'
       vertical = f'vertical: {final_results["vertical"][0][0]}, {final_results["vertical"][1][0]}, {final_results["vertical"][2][0]}'
       log_file.write(f'{date_now} {horizontal} {vertical} \n')
       log_file.close

    print(final_results)


def threaded(semaphore_thread):

    threads = []

    client_lidar_one = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_lidar_one.connect(('192.168.0.3', 2111))
    client_lidar_two = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_lidar_two.connect(('192.168.0.2', 2111))

    client_moving = serial.Serial('COM5', 57600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,
                      timeout=0.1)

    p_move = threading.Thread(target=moving, args=(client_moving, semaphore_thread,))
    p_one = threading.Thread(target=scanning, args=(client_lidar_one, semaphore_thread,))
    p_two = threading.Thread(target=scanning, args=(client_lidar_two, semaphore_thread,))

    threads.append(p_one)
    threads.append(p_two)
    threads.append(p_move)

    print('threads ' + str(datetime.datetime.now()))

    for t in threads:
        t.start()

    for t in threads:
        t.join()


# def func_chunk(lst):
#     for x in range(0, len(lst), 3):
#         e_c = lst[x: 3 + x]
#         yield e_c


def get_plot_DBSCAN(data_2D_prepare, max_step = 0.02, min_samples_got=7):
    db = DBSCAN(eps=max_step, min_samples=min_samples_got).fit(data_2D_prepare)
    center_x = 0
    for point in data_2D_prepare:
        center_x+= point[0]
    
    
    plots_unique_val, counts = numpy.unique(db.labels_, return_counts=True)
    plots = []
    plot_color_array = []
    for plot_color in plots_unique_val:
        plot = []
        if(plot_color != 1):
            for point_id in range(len(db.labels_)):
                if(db.labels_[point_id] == plot_color):
                    plot.append(data_2D_prepare[point_id])
            plots.append(plot)
            plot_color_array.append(plot_color)
    
    min_distance = 0.2
    result_plot_id = 0
    
    max_size = 0
    result_plot = []
    
    for plot in plots:
        if(len(plot) > len(result_plot)):
            result_plot = plot
            
    return result_plot, len(plots_unique_val)


def get_average(data):
    x = 0
    y = 0
    for i in data:
        x+= i[0]
        y+= i[1]
    return [x/len(data), y/len(data)]


def one_way_analize_advanced(data, averaging_segment_len = 5, indenting_segment_len = 5, significant_angle_1 = 0.2, significant_angle_2 = 1.8, noise_angle = 0.05, not_meaning = 7):
    total_indent_len = averaging_segment_len + indenting_segment_len
    data.sort(key=lambda row: (row[0]), reverse=False)
    left_adder_segment = [data[0] for _ in range(averaging_segment_len + indenting_segment_len)]
    right_adder_segment = [data[-1] for _ in range(averaging_segment_len + indenting_segment_len)]
    
    data = left_adder_segment + data
    data = data + right_adder_segment
    
    plots = []
    fractures = [data[0]]
    
    prev_angle = 0
    prev_angle_delta = 0
    current_plot = []
    current_plot += data[0:total_indent_len - 1]
    
    for analize_index in range(total_indent_len, len(data) - total_indent_len):
        left_averaged = get_average(data[analize_index - total_indent_len : analize_index - indenting_segment_len])
        right_averaged = get_average(data[analize_index + indenting_segment_len : analize_index + total_indent_len])
        
        
        
        a1 = (data[analize_index][1] - left_averaged[1])/(data[analize_index][0] - left_averaged[0] + 0.00000001)
        a2 = (data[analize_index][1] - right_averaged[1])/(data[analize_index][0] - right_averaged[0] + 0.00000001)
        
        angle = abs((a1 - a2)/(1 + (a1*a2)))
        #print(f"angle: {angle}")
        #print(f"Prev delta: {prev_angle_delta}")
        
        
        #bug! 
        
        if(prev_angle_delta > 0 and angle <= prev_angle and (abs(angle - prev_angle) > noise_angle or (angle - prev_angle < 0 and abs(angle - prev_angle) > noise_angle*0.5))):
            if (prev_angle > significant_angle_1):
                if (len(current_plot) > not_meaning):  
                    plots.append(current_plot)
                    if(prev_angle >= significant_angle_2 ):

                        fractures.append(current_plot[-1])
                    current_plot = []   
                    
        current_plot.append(data[analize_index])
        
        
        prev_angle_delta = angle - prev_angle
        #print(f"Delta: {prev_angle_delta}\n")
        prev_angle = angle
        
    current_plot += data[len(data) - total_indent_len:]
    plots.append(current_plot)
    fractures.append(data[-1])
        
    del plots[-1][-(averaging_segment_len + indenting_segment_len):]
    del plots[0][:(averaging_segment_len + indenting_segment_len)] 

    array_c = [[plot_id for point in plots[plot_id]] for plot_id in range(len(plots))]
    
    return plots, array_c, fractures


def display_data(plots_2D_1, arrayC, fractures = None, etalon_marker = True):
    colors= ["r.", "g.", "b.", "c.", "y."]
    plt.axes().set_aspect(1)
    cur_pos_start = 0
    for i in range(len(plots_2D_1)): 
        cur_pos_end = cur_pos_start + len(plots_2D_1[i])
        x = [j[0] for j in plots_2D_1[i]]
        y = [j[1] for j in plots_2D_1[i]]
        #с = arrayC[cur_pos_start:cur_pos_end]
        cur_pos_start = cur_pos_end
        if(arrayC[i]) == -1:
            color = "k."
        else:
             color = colors[i%5]
        #color = colors[i%5]
        plt.plot(
            x,
            y,
            color,
            markersize=2,
        )
    
    if(etalon_marker):
        psevdo_main_lines = [{"line": [fractures[fracture_index], fractures[fracture_index + 1]]} for fracture_index in range(len(fractures) - 1)]
        colors = ["m", "k"]
        for i in range(len(psevdo_main_lines)): 
            x = [j[0] for j in psevdo_main_lines[i]["line"]]
            y = [j[1] for j in psevdo_main_lines[i]["line"]]
            с = arrayC
            plt.plot(
                x,
                y,
                colors[i%2],
                markersize=2,
            )
    
    plt.show()
    
def calculate_info(data_ready, fractures):
    main_lines = [[(fractures[point_id + 1][1] - fractures[point_id][1])/(fractures[point_id + 1][0] - fractures[point_id][0] + 0.0000000001), fractures[point_id][1] - ((fractures[point_id + 1][1] - fractures[point_id][1])/(fractures[point_id + 1][0] - fractures[point_id][0] + 0.000000001))*fractures[point_id][0]] for point_id in range(len(fractures) - 1)]
    cur_line_index = 0
    point_id = 0
    cur_min = 0
    cur_max = 0
    min_max_array = []
    
    while (point_id < len(data_ready)):
        if(data_ready[point_id] != fractures[cur_line_index + 1]):
            distance = (main_lines[cur_line_index][0] * data_ready[point_id][0] - data_ready[point_id][1] + main_lines[cur_line_index][1])/math.sqrt(1 + main_lines[cur_line_index][0]**2)    
            if(cur_min > distance):
                cur_min = distance
            if(cur_max < distance):
                cur_max = distance
        else:
            min_max_array.append([cur_min, cur_max])
            cur_min = 0
            cur_max = 0
            cur_line_index += 1
        point_id += 1

    distances = [math.sqrt((fractures[index][0] - fractures[index + 1][0])**2 + (fractures[index][1] - fractures[index + 1][1])**2) for index in range(len(fractures) - 1)]
    biggest_plot = -1;
    biggest_min_digression = 10;
    biggest_max_digression = -10;
    fracture_id = 0
    plot_coordinates = []
    for index in range(len(distances)):
        fracture_id+=1;
        if(distances[index] > biggest_plot):
            biggest_plot = distances[index]
            #print(plot_coordinates)
            plot_coordinates = [fractures[fracture_id - 1], fractures[fracture_id]]
            if(min_max_array[index][0] < biggest_min_digression):
                biggest_min_digression = min_max_array[index][0]
            if(min_max_array[index][1] > biggest_max_digression):
                biggest_max_digression = min_max_array[index][1]
            
        #print(f"Range: {distances[index]}")
        #print(f"Min digression: {min_max_array[index][0]}")
        #print(f"Max digression: {min_max_array[index][1]}")
    
    return biggest_plot, biggest_min_digression, biggest_max_digression, plot_coordinates

def get_artificial_data_cut(center, data_3d):
    #print(f'in center: {center}')
    center1 = center 
    prepared_data = []
    
    real_artificial_cut = [[item[1], item[2], item[0]] for item in data_3d if center - 0.00172 < item[0] < center + 0.00173]
    real_artificial_cut_2D = [[item[1], item[0]]  for item in real_artificial_cut if item[0] > 0.2]

    real_artificial_cut_2D_grabbed = []
    existing_z = []

    for i in real_artificial_cut_2D:
        if( i[0] in existing_z):
            continue
        else:
            real_artificial_cut_2D_grabbed.append(i)
            existing_z.append(i[0])
    #print(len(real_artificial_cut_2D_grabbed))
    #display_data([real_artificial_cut_2D_grabbed], [1 for i in range(len(real_artificial_cut_2D_grabbed))], etalon_marker = False)

    prepared_data, val = get_plot_DBSCAN(real_artificial_cut_2D_grabbed, 0.02, 3)
    prepared_data.sort(key=lambda row: (row[0]), reverse=False)
    
    
    #print(f'plots number: {val}')
    
    
    return prepared_data, center1

def get_data_cut(center, data_3d_inside):
    real_center = (center//0.0018562291554143687)*0.0018562291554143687
    #print(f'real center: {real_center}')
    #print(data_3d_inside)
    
    correction = 0
    
    while True:
        real_cut = [[item[0], item[1], item[2]] for item in data_3d_inside if real_center-0.00095 + correction < item[2] < real_center+0.00095 + correction] #changed
        real_cut_2D = [[item[0], item[1]]  for item in real_cut]                          
        if(len(real_cut) < 400):
            correction += 0.0002
        else:
            break
        
        
    real_cut_2D_grabbed = []
    existing_z = []

    for i in real_cut_2D:
        if( i[0] in existing_z):
            continue
        else:
            real_cut_2D_grabbed.append(i)
            existing_z.append(i[0])
    #print(len(real_cut_2D_grabbed))
    #display_data([real_cut_2D_grabbed], [1 for i in range(len(real_cut_2D_grabbed))], etalon_marker = False)

    prepared_data, val = get_plot_DBSCAN(real_cut_2D_grabbed, 0.02, 5) #!
    
    prepared_data = [item for item in prepared_data if item[0] > -0.3]
    
    return prepared_data, center

def get_iterable_close_data(data, scan_type, point, num_of_scan = 5, delta = 0.005):
    
    result = []
    
    center_1 = 0
    center_2 = 0
    center_3 = 0
    center_4 = 0
    center_5 = 0
    
    point1 = point
    
    point2 = point1 + delta
    point3 = point1 + 2*delta
    
    point4 = point1 - delta
    point5 = point1 - 2*delta
    
    
    
    
    if(scan_type == "artificial"):
        
        first, center_1 = get_artificial_data_cut(point, data)
        #print(f'first len: {len(first)}')
        #print(f'first center: {center_1}')
        
        
        second, center_2 = get_artificial_data_cut(point2, data)
        #print(f'second len: {len(second)}')
        #print(f'second center: {center_2}')
        
        
        third, center_3 = get_artificial_data_cut(point3, data)
        #print(f'third len: {len(third)}')
        #print(f'third center: {center_3}')
        
        
        fourth, center_4 = get_artificial_data_cut(point4, data)
        #print(f'fourth len: {len(fourth)}')
        #print(f'fourth center: {center_4}')
            
        
        fifth, center_5 = get_artificial_data_cut(point5, data)
        #print(f'fifth len: {len(fifth)}')
        #print(f'fifth center: {center_5}')
            
        
        result.append(first)
        result.append(second)
        result.append(third)
        result.append(fourth)
        result.append(fifth)
        
    
    if(scan_type == "normal"):
        
        first, center_1 = get_data_cut(point, data)
        #print(f'first len: {len(first)}')
        #print(f'first center: {center_1}')
        
        
        second, center_2 = get_data_cut(point2, data)
        #print(f'second len: {len(second)}')
        #print(f'second center: {center_2}')
        
        
        third, center_3 = get_data_cut(point3, data)
        #print(f'third len: {len(third)}')
        #print(f'third center: {center_3}')
        
        
        fourth, center_4 = get_data_cut(point4, data)
        #print(f'fourth len: {len(fourth)}')
        #print(f'fourth center: {center_4}')
            
        
        fifth, center_5 = get_data_cut(point5, data)
        #print(f'fifth len: {len(fifth)}')
        #print(f'fifth center: {center_5}')
            
        
        result.append(first)
        result.append(second)
        result.append(third)
        result.append(fourth)
        result.append(fifth)
    
    return result

def count_mode(array):
    mode = {array[i]: 0 for i in range(len(array))}
    for i in array:
        mode[i] += 1
    mode_val = sorted(mode, key=mode.get, reverse=True)[0]
    if(mode_val == -1):
        if(len(mode) > 1):
            mode_val = sorted(mode, key=mode.get, reverse=True)[1]
            
    return mode_val, mode[mode_val]

def get_closest(data, cut_type = "horizontal"):
    
    if(cut_type == "horizontal"):
        first_array = []
        for result in data:
            #print(result[0])
            if(abs(result[0] - 1.45) < 0.05 or abs(result[0] - 1.55) < 0.05):
                if( abs(result[0] - 1.45) <= abs(result[0] - 1.55)):
                    first_array.append(45)
                else: 
                    first_array.append(55)

            else:
                first_array.append(-1)


        distance = 10.0

        fin = None

        mode, count =  count_mode(first_array)

        if(mode == 45 and count > 1):
            for result in data:
                if ((result[0] - 1.45) < distance):
                    distance = abs(result[0] - 1.45)
                    fin = result

        if(mode == 55 and count > 1):
            for result in data:
                if (abs(result[0] - 1.55) < distance):
                    distance = abs(result[0] - 1.55)
                    fin = result
    
    else:
        first_array = []
        for result in data:
            #print(result[0])
            if(abs(result[0] - 0.575) < 0.05):
                first_array.append(575)
            else:
                first_array.append(-1)
        
        distance = 10.0
        
        fin = None

        mode, count =  count_mode(first_array)

        if(mode == 575 and count > 2):
            for result in data:
                if (abs(result[0] - 0.575) < distance):
                    distance = abs(result[0] - 0.575)
                    fin = result

    #if (fin != None):
    #    display_data(fin[3], fin[4], fin[5], etalon_marker = True)
    
    return fin

def final_analize(data_3d_outside):
    print('start analize')
    result_str = {"horizontal": [], "vertical":[], "Exception": "", 'time': str(datetime.datetime.now())}

    first_cut_list = get_iterable_close_data(data_3d_outside, "artificial", 0.1, delta=0.01)

    first_results = []

    for cut in first_cut_list:
        lines_array, array_c, fractures = one_way_analize_advanced(cut, averaging_segment_len = 10, indenting_segment_len = 15, significant_angle_1 = 0.7, significant_angle_2 = 2.0, noise_angle = 0.6, not_meaning = 10)
        biggest_plot, biggest_min_digression, biggest_max_digression, plot_coordinates = calculate_info(cut, fractures)

        first_results.append([biggest_plot, biggest_min_digression, biggest_max_digression, lines_array, array_c, fractures, plot_coordinates])

    first_result = get_closest(first_results)
    if( first_result == None):
        for i in first_results:
            print(i[0])
        return {"horizontal": [[0, 0, 0],[0, 0, 0],[0, 0, 0]], "vertical":[[0, 0, 0],[0, 0, 0],[0, 0, 0]], "Exception": "Anode is out of scaning bounds", 'time': str(datetime.datetime.now())}

    left_coordinate_Z = first_result[6][0][0] + 0.05
    right_coordinate_Z = first_result[6][-1][0] - 0.05
    center_coordinate_Z = (left_coordinate_Z + right_coordinate_Z)/2

    
    reference_vertical_scan = None
    
    for coordinate in [left_coordinate_Z, center_coordinate_Z, right_coordinate_Z]:
        vertical_cut_list = get_iterable_close_data(data_3d_outside, "normal", coordinate, delta=0.0018)

        #print(f'vertical_cut_list: {len(vertical_cut_list)}')

        vertical_results = []

        for cut in vertical_cut_list:
            lines_array, array_c, fractures = one_way_analize_advanced(cut, averaging_segment_len = 10, indenting_segment_len = 5, significant_angle_1 = 0.7, significant_angle_2 = 0.9, noise_angle = 0.6, not_meaning = 10)
            biggest_plot, biggest_min_digression, biggest_max_digression, plot_coordinates = calculate_info(cut, fractures)

            vertical_results.append([biggest_plot, biggest_min_digression, biggest_max_digression, lines_array, array_c, fractures, plot_coordinates])

        #print(len(vertical_results))

        vertical_result = get_closest(vertical_results, cut_type = "vertical")

        if( vertical_result == None):
            result_str["vertical"].append([0, 0, 0])
        else: 
            result_str["vertical"].append([round(vertical_result[0], 4), round(vertical_result[1], 4), round(vertical_result[2], 4)])
            reference_vertical_scan = vertical_result
            
    if(reference_vertical_scan != None):
        left_coordinate_Y = reference_vertical_scan[6][0][0] + 0.1
        right_coordinate_Y = reference_vertical_scan[6][-1][0] - 0.1
        center_coordinate_Y = (left_coordinate_Y + right_coordinate_Y) / 2

        for coordinate in [left_coordinate_Y, center_coordinate_Y, right_coordinate_Y]:
            horizontal_cut_list = get_iterable_close_data(data_3d_outside, "artificial", coordinate)

            #print(f'horizontal_cut_list: {len(horizontal_cut_list)}')

            horizontal_results = []

            for cut in horizontal_cut_list:
                lines_array, array_c, fractures = one_way_analize_advanced(cut, averaging_segment_len = 10, indenting_segment_len = 20, significant_angle_1 = 0.9, significant_angle_2 = 5.0, noise_angle = 0.6, not_meaning = 10)
                biggest_plot, biggest_min_digression, biggest_max_digression, plot_coordinates = calculate_info(cut, fractures)

                horizontal_results.append([biggest_plot, biggest_min_digression, biggest_max_digression, lines_array, array_c, fractures, plot_coordinates])

            #print(len(horizontal_results))

            horizontal_result = get_closest(horizontal_results)

            if( horizontal_result == None):
                result_str["horizontal"].append([0, 0, 0])
            else: 
                result_str["horizontal"].append([round(horizontal_result[0], 4), round(horizontal_result[1], 4), round(horizontal_result[2], 4)])
            
    else:
        return {"horizontal": [[0, 0, 0],[first_result[0], first_result[1], first_result[2]],[0, 0, 0]], "vertical":[[0, 0, 0],[0, 0, 0],[0, 0, 0]], "Exception": "Need Check", 'time': str(datetime.datetime.now())}

    return result_str


if __name__ == '__main__':
    lidarSettings()
    # moving_status = 0

    multiprocessing.freeze_support()
    semaphore = multiprocessing.Semaphore(2)
    

    while True:
        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # try:
                #     print('close connection')
                #     listener.close()
                # except socket.error as e:
                #     print(str(e))
        listener.bind(('127.0.0.1', 61557))
        print('listening')
        try:
            data, addr = listener.recvfrom(1024)
            print(data.hex())
            if data.hex().lower() == 'aa' or data.hex().lower() == 'aaaa':
                print('received')
                threaded(semaphore)
                listener.close()
        except socket.error as e:
            print((str(e)))

# time.sleep(500)

