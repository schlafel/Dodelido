from PIL import Image, ImageEnhance
import numpy as np
import datetime
from shapely.geometry import Polygon
from tqdm import tqdm
from src.get_backgound_imgs import download_random_image,save_image
from src.data_utils import *


def create_classes_file(path,label_dict):
    with open(os.path.join(path,"classes.txt"),"w") as infile:
        for key,value in label_dict.items():
            infile.write(key)


def add_object(label, xmin, ymin, xmax, ymax):
    """
Helper-function that returns the specified label to
    Args:
        label: <string> with label
        xmin: <double> with xmin position
        ymin: <double> with ymin position
        xmax: <double> with xmax position
        ymax: <double> with ymax position

    Returns:
        formatted xml string (<object>)
    """
    str_out = "<object>\n" + "\t<name>{}</name>\n\t<pose>Unspecified</pose>\n\t<truncated>0</truncated>\n\t<difficult> 0 </difficult>\n\t<bndbox>\n\t\t<xmin>{:d}</xmin>\n\t\t<ymin>{:d}</ymin>\n\t\t<xmax>{:d}</xmax>\n\t\t<ymax>{:d}</ymax>\n\t</bndbox>\n\t</object>\n".format(
        label, xmin, ymin, xmax, ymax)
    return str_out

def create_annot_dict(folder_path,file_name,width,height,label,xmin,ymin,xmax,ymax):
    """
    First call, to initialize annotation dict....
    Args:
        folder_path: path, where the image lays
        file_name: <string> file-name
        width: <double> image width
        height: <double> image height
        label: <label> of first object
        xmin: <double> with xmin position
        ymin: <double> with ymin position
        xmax: <double> with xmax position
        ymax: <double> with ymax position

    Returns:
        <string>,  formatted xml string
    """
    str_out = "<annotation>\n\t<folder>{}</folder>\n\t<filename>{}</filename>\n\t<path>{}</path>\n\t<source>\n\t<database>Unknown</database>\n\t</source>\n\t<size>\n\t\t<width>{:d}</width>\n\t\t<height>{:d}</height>\n\t\t<depth> 3</depth>\n\t</size>\n\t<segmented>0</segmented>\n{}\t</annotation>\n".format(
                               os.path.basename(folder_path),
                               file_name,
                               os.path.join(folder_path, file_name),
                               width,
                               height,
                               add_object(label, xmin, ymin, xmax, ymax))
    return str_out

def add_to_annot(annot_str,label,xmin,ymin,xmax,ymax):
    """

    Args:
        annot_str: <string>, existing annotation string
        label: <string>, label to insert
        xmin: <double>, min-x, position
        ymin: <double>, min-y, position
        xmax: <double>, max-y, position
        ymax: <double>, max-y, position

    Returns:
        <string>, formatted and extended with the <object>
    """
    ext_annot_str = annot_str[:-15] + add_object(label = label,xmin = xmin,ymin = ymin,xmax = xmax,ymax = ymax)  + annot_str[-14:]
    return (ext_annot_str)


def augment_image_multiple(basis_image_list,
                           basis_bg_list,
                           path_out,
                           label_dict,
                           rotation_range = [0,360],
                           resize_factor = [3,7],
                           enhancer_factor = [.5,1.5]
                           ):


    LABEL_PATH = os.path.join(path_out, 'labels')
    OUT_IMG_PATH = os.path.join(path_out, 'images')

    #create classes.txt file
    create_classes_file(LABEL_PATH,label_dict)

    #load a basis image

    bg_name = np.random.choice(basis_bg_list)

    #load both images

    bg = Image.open(os.path.join(bg_name))
    # now enhance image
    enhancer_bg = ImageEnhance.Brightness(bg)
    bg = enhancer_bg.enhance(np.random.uniform(enhancer_factor[0], enhancer_factor[1]))
    back = bg.copy()

    old_positions = []


    for _i in (range(0, np.random.randint(1, 4))):

        img1_name = np.random.choice(basis_image_list)
        img1 = Image.open(os.path.join(img1_name))
        # now enhance image
        enhancer = ImageEnhance.Brightness(img1)
        img1 = enhancer.enhance(np.random.uniform(enhancer_factor[0],enhancer_factor[1]))

        label1 = os.path.basename(img1_name)[0:2]

        front, img_1_res, mask, x_pos, y_pos,rot = get_newRandomPosImage(back, img1, resize_factor, rotation_range)
        save_img = True
        n_iter = 0
        if _i > 0:
            #
            # fig, ax = plt.subplots(1)
            # ax.axis('equal')
            # ax.plot(*p2.exterior.xy)
            # for old_p in old_positions:
            #     ax.plot(*old_p.exterior.xy)

            intersect = True

            while intersect:
                p2 = Polygon(((x_pos, y_pos),
                              (x_pos + mask.size[0], y_pos),
                              (x_pos + mask.size[0], y_pos + mask.size[1]),
                              (x_pos, y_pos + mask.size[1]),))
                for i_poly, poly in enumerate(old_positions):
                    #print("Handling Polygon {:d}".format(i_poly))
                    isect = poly.intersection(p2)
                    share_isect = isect.area / (poly.area + p2.area)
                    if share_isect>=.05:
                        #polygons intersect
                        intersect = True
                        #define new x_pos,y_pos

                        front, img_1_res, mask, x_pos, y_pos, rot = get_newRandomPosImage(back, img1, resize_factor,
                                                                                          rotation_range)
                        # mask = Image.new('L', img_1_res.size, 255)
                        # rot = np.random.randint(rotation_range[0], rotation_range[1] + 1)
                        # front = img_1_res.rotate(rot, expand=True)
                        # mask = mask.rotate(rot, expand=True)

                        x_pos = np.random.randint(0, back.size[0] - mask.size[0])
                        y_pos = np.random.randint(0, back.size[1] - mask.size[1])
                        break
                    if (i_poly+1) == len(old_positions):
                        intersect = False
                if n_iter > 200:
                    print("\n{}\nCouldn't find appropriate position\n".format(os.path.join(path_out,fname)))
                    save_img = False
                    intersect = False
                n_iter += 1

        center_x = (x_pos + mask.size[0]/2)/back.size[0]
        center_y = (y_pos + mask.size[1]/2)/back.size[1]
        box_width =(mask.size[0])/back.size[0]
        box_height =(mask.size[1])/back.size[1]

        if not save_img:
            continue

        #log the old positions, create new polygon
        old_positions.append(Polygon(((x_pos,y_pos),
                                 (x_pos + mask.size[0], y_pos),
                                 (x_pos + mask.size[0], y_pos + mask.size[1]),
                                 (x_pos, y_pos + mask.size[1]),  )))

        if _i == 0:
            #first iteration....
            #create file_name
            fname = datetime.datetime.now().strftime("%y%m%d_%H%M%S_%f") + os.path.basename(bg_name).split(".")[0] +".jpg"

            annot_str = f'{label_dict[label1]} {center_x} {center_y} {box_width} {box_height}'

            # annot_str = create_annot_dict(path_out,
            #                               file_name = fname,
            #                               width = back.size[0],height=back.size[1],label=label1,
            #                   xmin=x_pos,xmax=x_pos + mask.size[0],ymin=y_pos,ymax=y_pos + mask.size[1])


        else:
            annot_str = annot_str + "\r\n" + f'{label_dict[label1]} {center_x} {center_y} {box_width} {box_height}'
            # annot_str = add_to_annot(annot_str,label=label1,
            #                   xmin=x_pos,xmax=x_pos + mask.size[0],ymin=y_pos,ymax=y_pos + mask.size[1])

        #now paste the background
        back.paste(front, (x_pos, y_pos), mask)


        #print(_i)


    back.save(os.path.join(OUT_IMG_PATH,fname))
    #write out annot_str
    with open(os.path.join(LABEL_PATH,fname.split(".")[0] + ".txt"), "w",newline="\n") as infile:
        infile.write(annot_str)

    #print("created image...." + fname + "\n")


def get_newRandomPosImage(back, img1, resize_factor, rotation_range):
    image_too_large = True
    while image_too_large:
        rot = np.random.randint(rotation_range[0], rotation_range[1] + 1)
        res_factor = np.random.randint(resize_factor[0], resize_factor[1] + 1)
        img_1_res = img1.resize((img1.size[0] // res_factor, img1.size[1] // res_factor), Image.ANTIALIAS)
        mask = Image.new('L', img_1_res.size, 255)
        front = img_1_res.rotate(rot, expand=True)
        mask = mask.rotate(rot, expand=True)
        if ((back.size[0] - mask.size[0]) > 10) & ((back.size[1] - mask.size[1]) > 10):
            image_too_large = False
            x_pos = np.random.randint(0, back.size[0] - mask.size[0])
            y_pos = np.random.randint(0, back.size[1] - mask.size[1])
    return front, img_1_res, mask, x_pos, y_pos,rot


def augment_image(img_in,bg,path_out,rotation_range = [0,360],resize_factor = [7,12],
                  label = "",bg_name = ""):
    rot = np.random.randint(rotation_range[0],rotation_range[1]+1)
    res_factor = np.random.randint(resize_factor[0],resize_factor[1]+1)
    img_1_res = img_in.resize((img_in.size[0] // res_factor, img_in.size[1] // res_factor), Image.ANTIALIAS)

    back = bg.copy()
    mask = Image.new('L', img_1_res.size, 255)
    front = img_1_res.rotate(rot, expand=True)
    mask = mask.rotate(rot, expand=True)

    x_pos = np.random.randint(0,back.size[0]-mask.size[0])
    y_pos = np.random.randint(0,back.size[1]-mask.size[1])

    back.paste(front, (x_pos, y_pos), mask)
    file_name = "{}_{}_{:d}_{:d}.jpg".format(label,bg_name,x_pos,y_pos)
    back.save(os.path.join(path_out,file_name))

    xmin=x_pos
    xmax = x_pos + mask.size[0]
    ymin = y_pos
    ymax = y_pos + mask.size[1]

    width,height = back.size

    return (back,file_name, (xmin,xmax,ymin,ymax),(width,height))

def create_dataset_multiple():
    pass

def create_dataset(flag, image_path, path_out, size):
    df_test = pd.DataFrame()
    bg_list = os.listdir(os.path.join(image_path, "bg"))
    _i = 0
    for dirs in ["flamingo"]:
        for file in os.listdir(os.path.join(image_path, dirs)):
            print(file)
            img1 = Image.open(os.path.join(image_path, dirs, file))

            for i in range(0, size):
                print(_i)
                label = file[0:2]
                # get Background
                bg_name = np.random.choice(bg_list)
                bg1 = Image.open(os.path.join(image_path, "bg", bg_name))
                bg = bg1.resize((960, 690), Image.ANTIALIAS)



                augmented_image, file_name, (xmin, xmax, ymin, ymax), (width, height) = augment_image(img1, bg,
                                                                                     rotation_range=[0, 360],
                                                                                     resize_factor=[7, 12],
                                                                                     label=label,
                                                                                     bg_name=bg_name[0:4],
                                                                                     path_out=os.path.join(path_out,
                                                                                                           flag))

                df_test.loc[_i, "filename"] = file_name
                df_test.loc[_i, "width"] = width
                df_test.loc[_i, "height"] = height
                df_test.loc[_i, "class"] = label
                df_test.loc[_i, "xmin"] = xmin
                df_test.loc[_i, "ymin"] = ymin
                df_test.loc[_i, "xmax"] = xmax
                df_test.loc[_i, "ymax"] = ymax
                _i+=1
    df_test.to_csv(os.path.join(path_out, "{}_labels.csv".format(flag)), index=False, sep=",")


def label_map_v1(objname):
    with open('/TEST-DS-TO-RECORD/annotations/label_map.pbtxt', 'a') as the_file:
        the_file.write('item\n')
        the_file.write('{\n')
        the_file.write('id :{}'.format(int(1)))
        the_file.write('\n')
        the_file.write("name :'{0}'".format(str(objname)))
        the_file.write('\n')
        the_file.write('}\n')

#create train set....
import pandas as pd


def run_data_preparation():
    # Download images until minimum number of background images is reached....
    while len(os.listdir(BACKGROUND_DIR)) < N_BACKGROUNDS:
        print(f"Downloading image {len(os.listdir(BACKGROUND_DIR))}/{N_BACKGROUNDS}")
        img = download_random_image(BG_IMG_URL)
        save_image(img, BACKGROUND_DIR)
    animals = ["flamingo", "zebra", "turtle", "camel", "penguin"]
    path_train = os.path.join(path_out, "train")
    path_test = os.path.join(path_out, "test")
    path_validation = os.path.join(path_out, "val")
    # create dirs
    for base_dir in [path_train, path_test, path_validation]:
        for subdir in ['images', 'labels']:
            dir = os.path.join(base_dir, subdir)
            if not os.path.exists(dir):
                os.makedirs(dir)
    # todo: replace with yaml
    config_dict = get_yaml(YAML_PATH)
    label_dict, label_dict_inv = get_label_dicts(config_dict)
    # get all the background images
    bg_list = [os.path.join(BACKGROUND_DIR, i) for i in os.listdir(BACKGROUND_DIR)]
    basis_img_list = []
    for animal in animals:
        for i in os.listdir(os.path.join(image_path, animal)):
            basis_img_list.append(os.path.join(image_path, animal, i))
    # now start image creation
    for i in tqdm(range(0, N_TRAIN)):
        augment_image_multiple(basis_img_list, bg_list, path_out=os.path.join(path_out, "train"),
                               label_dict=label_dict)
    # now start image creation
    for i in tqdm(range(0, N_TEST)):
        augment_image_multiple(basis_img_list, bg_list, path_out=os.path.join(path_out, "test"),
                               label_dict=label_dict)
    # now start image creation
    for i in tqdm(range(0, N_VAL)):
        augment_image_multiple(basis_img_list, bg_list,
                               path_out=path_validation,
                               label_dict=label_dict)


if __name__ == '__main__':
    #
    image_path = os.path.join(DATA_DIR,"original")
    path_out = os.path.join(DATA_DIR,"ProcessedImages")

    run_data_preparation()

