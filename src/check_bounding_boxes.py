import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import random

import pandas as pd



# todo: replace with yaml
label_dict = dict(zip([
    'bc', 'gc', 'pc', 'wc', 'yc',
    'bf', 'gf', 'pf', 'wf', 'yf',
    'bp', 'gp', 'pp', 'wp', 'yp',
    'bt', 'gt', 'pt', 'wt', 'yt',
    'bz', 'gz', 'pz', 'wz', 'yz',
], range(25)))

label_dict_inv = dict([(value,key) for key,value in label_dict.items()]  )


def plot_img_labels(train_img_path = ""):
    label_path = os.path.join(train_img_path, "..", "labels")
    img_list = os.listdir(train_img_path)

    img_name = random.choice(img_list)
    # img_name = "230728_122856_506006kyLjgw2ZiI.jpg"
    full_img_path = os.path.join(train_img_path, img_name)

    name, ext = os.path.splitext(full_img_path)
    name = os.path.basename(name)
    full_label_path = os.path.join(label_path, name + ".txt")

    # read bbox
    df_box = pd.read_csv(full_label_path, sep=" ", header=None)

    # Load the image

    image = plt.imread(full_img_path)

    # Create a figure and axes
    fig, ax = plt.subplots()

    # Display the image
    ax.imshow(image)

    for i, row in df_box.iterrows():
        x_center, y_center, width, height = row[1:]
        x_min = x_center - width / 2
        y_min = y_center - height / 2

        # Create a rectangle patch
        rect = patches.Rectangle((x_min * image.shape[1],
                                  y_min * image.shape[0]),
                                 width * image.shape[1],
                                 height * image.shape[0], linewidth=1, edgecolor='r', facecolor='none')

        # Add the rectangle to the axes
        ax.add_patch(rect)
        label = label_dict_inv[int(row[0])]
        # Add label text above the bounding box
        plt.text(x_min * image.shape[1], y_min * image.shape[0], label, fontsize=12, color='r')
    return fig,ax



if __name__ == '__main__':
    TRAIN_IMG_PATH = r"C:\Users\fs.GUNDP\Python\dodelido\data\ProcessedImages\train\images"
    while True:
        fig = plot_img_labels(train_img_path=TRAIN_IMG_PATH)
        plt.show()
