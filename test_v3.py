import multiprocessing as mp
import time
from PIL import Image
import math
import matplotlib.pyplot as plt

# Función de ordenamiento mergesort secuencial
def seq_mergesort(array, *args):
    if not args: #First call
        seq_mergesort(array, 0, len(array)-1)
    else: 
        left, right = args
        if left == right: # Case base
            return array
        else :
            mid = (left + right) // 2 # Find the middle entire middle point
            seq_mergesort(array, left, mid) 
            seq_mergesort(array, mid+1, right) 
            merge(array, left, mid, right) 

# Función auxiliar para el proceso de fusión en mergesort
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

# Función de ordenamiento mergesort paralelo
def par_merge_sort(array, *args):
    if not args: 
        shared_array = mp.RawArray('i', array)
        par_merge_sort(shared_array, 0, len(array)-1, 0)
        return shared_array
    else:
        left, right, depth = args # Argumentos
        if depth >= math.log(mp.cpu_count(), 2): # Caso base, profundidad máxima según procesadores disponibles
            seq_mergesort(array, left, right) 
        elif left < right:
            mid = (left + right) // 2
            left_proc = mp.Process(target=par_merge_sort, args=(array, left, mid, depth+1)) # Creacion de un proceso para el lado izquierdo 
            left_proc.start() # Inicia el proceso
            par_merge_sort(array, mid+1, right, depth+1) # El proceso principal ejecuta el lado derecho
            left_proc.join() # Espera a que el proceso izquierdo termine
            merge(array, left, mid, right)

# Función para obtener los píxeles ordenados según el método especificado
def get_sorted_pixels(image_path, format_sort):
    img = Image.open(image_path) 
    img_new = img.convert("RGB") 
    pixels = list(img_new.getdata()) # Obtiene los píxeles de la imagen
    clarity_values = [sum(pixel) for pixel in pixels] # Array con suma los valores de los píxeles
    if format_sort == 1:
        print("Sorting pixels sequentially...")
        clarity_values_sort = seq_mergesort(clarity_values) # Ordena los valores de los píxeles
    elif format_sort == 2:
        print("Sorting pixels in parallel...")
        clarity_values_sort = par_merge_sort(clarity_values) # Ordena los valores de los píxeles        
    print("Pixels sorted...")
    return clarity_values_sort

# Función para mostrar la imagen con píxeles ordenados y guardarla
def display_image(image_path, clarity_values_sort, rango_del_blur):
    img = Image.open(image_path)
    img_new = img.convert("RGB")
    width, height = img_new.size
    pixels = list(img_new.getdata())
    final_image_sorted_pixels = [] # Lista para almacenar los píxeles ordenados
    # Punto de referencia para el efecto de desenfoque
    reference_line = 400
    reference_line_1 = height
    iteration = 0  # Contador de iteraciones

    print("Creating final image...")
    for y in range(height):
        for x in range(width):
            if (reference_line - rango_del_blur + 800<= y <= reference_line + rango_del_blur) or (reference_line_1 - rango_del_blur + 500 <= y <= reference_line_1 + rango_del_blur): # Aplica el efecto de desenfoque
                final_image_sorted_pixels.append(pixels[clarity_values_sort[y*width + x]]) # Agrega el píxel ordenado según la referencia
            else:
                final_image_sorted_pixels.append(pixels[y*width + x]) # Agrega el píxel original
        
        iteration += 1
        if iteration % 200 == 0:  # Muestra la imagen cada 50 iteraciones
            img_new.putdata(final_image_sorted_pixels)
            plt.axis('off')
            plt.imshow(img_new)
            plt.pause(2)  # Pausa para mostrar la imagen
            plt.close()  # Cierra automáticamente la ventana de matplotlib

    print("final image...")
    img_new.putdata(final_image_sorted_pixels)
    img_new.save("output_image.jpg")

# Bloque principal
if __name__ == "__main__":
    sequential_time = 0
    parallel_time = 0
    image_path = "input_image_1.jpg"

    # Ordenamiento secuencial 
    start = time.perf_counter()
    all_pixels_sorted_sequentially= get_sorted_pixels(image_path, 1)
    sequential_time = time.perf_counter() - start

    # Ordenamiento paralelo
    start = time.perf_counter()
    all_pixels_sorted_parallel = get_sorted_pixels(image_path, 2)
    parallel_time = time.perf_counter() - start
    display_image(image_path, all_pixels_sorted_parallel, rango_del_blur=2000)

    # Resultados
    print('\nSequential Time: {:.2f} seg'.format(sequential_time))
    print('Parallel Time: {:.2f} seg'.format(parallel_time))
    print('Speedup: {:.2f}'.format(sequential_time/parallel_time))
    print('Processors: ', mp.cpu_count())
    print('Efficiency: {:.2f}'.format((sequential_time/parallel_time)/mp.cpu_count()))
