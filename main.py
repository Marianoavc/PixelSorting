import random
import multiprocessing as mp
import time
from PIL import Image
import math

def seq_mergesort(array, *args):
    if not args: # caso base
        return seq_mergesort(array, 0, len(array)-1)
    else: 
        left, right = args
        if left < right:
            mid = (left + right) // 2 
            seq_mergesort(array, left, mid) 
            seq_mergesort(array, mid+1, right) 
            merge(array, left, mid, right) 
    return array

def merge(array, left, mid, right):
    left_temp_arr = array[left:mid+1].copy()
    right_temp_arr = array[mid+1:right+1].copy()
    left_temp_index = 0
    right_temp_index = 0
    merge_index = left

    while left_temp_index < (mid - left + 1) or right_temp_index < (right - mid):
        if left_temp_index < (mid - left + 1) and right_temp_index < (right - mid):
            if left_temp_arr[left_temp_index] <= right_temp_arr[right_temp_index]:
                array[merge_index] = left_temp_arr[left_temp_index]
                left_temp_index += 1
            else:
                array[merge_index] = right_temp_arr[right_temp_index]
                right_temp_index += 1
        elif left_temp_index < (mid - left + 1):
            array[merge_index] = left_temp_arr[left_temp_index]
            left_temp_index += 1
        elif right_temp_index < (right - mid):
            array[merge_index] = right_temp_arr[right_temp_index]
            right_temp_index += 1
        merge_index += 1

def par_merge_sort(array, *args):
    if not args: 
        shared_array = mp.RawArray('i', array)
        par_merge_sort(shared_array, 0, len(array)-1, 0)
        return shared_array
    else:
        left, right, depth = args
        if depth >= math.log(mp.cpu_count(), 2): #Caso base, profundidad máxima
            seq_mergesort(array, left, right)
        elif left < right:
            mid = (left + right) // 2
            left_proc = mp.Process(target=par_merge_sort, args=(array, left, mid, depth+1))
            left_proc.start()
            par_merge_sort(array, mid+1, right, depth+1)
            left_proc.join()
            merge(array, left, mid, right)

def sort_selected_pixels(image_path, blur_intensity, format_sort, output_path):
    img = Image.open(image_path)
    img_new = img.convert("RGB")
    pixels = list(img_new.getdata())
    sorted_pixels = []
    width, height = img.size
    reference_line = 400 
    reference_line_1 = height
    clarity_values = [sum(pixel) for pixel in pixels]
    if format_sort == 1:
        print("Sorting pixels in parallel...")
        clarity_values_sort = par_merge_sort(clarity_values)
    else:
        print("Sorting pixels sequentially...")
        clarity_values_sort = seq_mergesort(clarity_values)
    print("Pixels sorted...")

    for y in range(height):
        for x in range(width):
            if (reference_line - blur_intensity + 800<= y <= reference_line + blur_intensity) or (reference_line_1 - blur_intensity + 500 <= y <= reference_line_1 + blur_intensity):
                sorted_pixels.append(pixels[clarity_values_sort[y*width + x]])
            else:
                sorted_pixels.append(pixels[y*width + x])

    print("Placing pixels...")
    img_new.putdata(sorted_pixels)
    img_new.save(output_path)

if __name__ == "__main__":

    sequential_tiem = 0
    parallel_time = 0

    start = time.perf_counter()
    sort_selected_pixels("input_image_2.jpg", 2000, 2, "output-sortrandom1.png")
    sequential_time = time.perf_counter() - start

    start = time.perf_counter()
    sort_selected_pixels("input_image_2.jpg", 2000, 1, "output-sortrandom2.png")
    parallel_time = time.perf_counter() - start
    #end
    print('\nAverage Sequential Time: {:.2f} ms'.format(sequential_time*1000))
    print('Average Parallel Time: {:.2f} ms'.format(parallel_time*1000))
    print('Speedup: {:.2f}'.format(sequential_time/parallel_time))
    print('Processors: ', mp.cpu_count())
    print('Efficiency: {:.2f}'.format((sequential_time/parallel_time)/mp.cpu_count()))