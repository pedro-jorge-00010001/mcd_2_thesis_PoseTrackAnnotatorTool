import json
from tkinter import filedialog
from scipy.spatial import distance

def json_formating_fixer():
    file_path = filedialog.askopenfilename(filetypes = [("Json files", ".json")])

    data = []
    with open(file_path) as json_file:
        data = json.load(json_file)    

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



def get_closest_rectangle_to(rectangle, vector_of_rectangles_to_compare, maximum_dst = 30):
    #Define center function
    def get_rectangle_center(rectangle):
        (x, y, w, h) =  [int(point) for point in rectangle]
        assert w >= x
        assert h >= y
        px = (w-x)/2 + x
        py = (h-y)/2 + y
        return (px, py)
    
    main_rectangle_center = get_rectangle_center(rectangle)

    current_min_dst = 9999999
    current_min_dst_rect = None
    for rectangle_to_compare in vector_of_rectangles_to_compare:
        dst = distance.euclidean(main_rectangle_center, get_rectangle_center(rectangle_to_compare))
        if dst < current_min_dst:
            current_min_dst = dst
            current_min_dst_rect = rectangle_to_compare
    if current_min_dst > maximum_dst:
        #current_min_dst_rect = rectangle
        current_min_dst_rect = None
    return current_min_dst_rect 

def get_number_to_string(number):
    if int(number) < 10:
        return '0' + str(number)
    return str(number)

assert get_number_to_string(1) == '01'
assert get_number_to_string(21) == '21'
