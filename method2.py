import cv2
import matplotlib.pyplot as plt
import numpy as np
import math
from tqdm import tqdm
import os

def bilateral_filter(src):
    src = cv2.cvtColor(src, cv2.COLOR_RGB2BGR)
    # bilateral_filter_image = cv2.bilateralFilter(src, 9, 75, 75)
    # bilateral_filter_image = cv2.bilateralFilter(src, 3, 4.25, 4.25)
    bilateral_filter_image = cv2.bilateralFilter(src, 9, 100, 100)
    bilateral_filter_image = cv2.cvtColor(bilateral_filter_image, cv2.COLOR_BGR2RGB)

    return bilateral_filter_image

def color_diff(src):

    def color_distance(x_i, x_j):
        return math.dist(x_i, x_j)

    # to Lab color space
    src_Lab = cv2.cvtColor(src, cv2.COLOR_RGB2LAB)
    output = np.zeros_like(src_Lab[:, :, 0])
    for i in tqdm(range(1, len(src_Lab) - 1)): # rows, avoid overflow/underflow
        for j in range(1, len(src_Lab[i]) - 1): # columns
            color_distance_list = []
            for k in range(-1, 2): # neighbor delta_x
                for l in range(-1, 2): # neighbor delta_y
                    if k == 0 and l == 0:
                        continue
                    else:
                        distance = color_distance(src_Lab[i][j], src_Lab[i + k][j + l])
                        color_distance_list.append((int(src_Lab[i + k][j + l][0]) - int(src_Lab[i][j][0])) * distance)
            output[i][j] = max(color_distance_list)

    # normalize
    avg_value = output.mean()
    std_value = output.std()
    for i in range(len(output)):
        for j in range(len(output[i])):
            if output[i][j] < avg_value - 3 * std_value:
                output[i][j] = avg_value - 3 * std_value
            elif output[i][j] > avg_value + 3 * std_value:
                output[i][j] = avg_value + 3 * std_value

    min_value = output.min()
    max_value = output.max()
    output = (output - min_value) / (max_value - min_value)
    # output_invert = (np.ones_like(output) - output) * 255
    # cv2.imwrite('color_diff.jpg', output_invert)

    # return np.ones_like(output) - output
    return output

def shadow_importance(src):

    src_Lab = cv2.cvtColor(src, cv2.COLOR_RGB2LAB)
    intensity_matrix = np.zeros_like(src_Lab[:, :, 0])
    output = np.zeros_like(src_Lab[:, :, 0])
    def intensity(x_i):
        return math.dist(x_i, [0, 0, 0])

    for i in range(len(src_Lab)):
        for j in range(len(src_Lab[i])):
            intensity_matrix[i][j] = intensity(src_Lab[i][j])

    intensity_mean = intensity_matrix.mean()

    for i in range(len(intensity_matrix)):
        for j in range(len(intensity_matrix[i])):
            if intensity_matrix[i][j] < intensity_mean:
                output[i][j] = (1 - intensity_matrix[i][j] / intensity_mean) ** 2

    # cv2.imwrite('shadow_importance.jpg', output * 255)

    return output

def outline(src, T_L):
    output = np.zeros_like(src)
    for i in range(len(src)):
        for j in range(len(src[i])):
            if src[i][j] < T_L:
                output[i][j] = 0.5 * (1 - math.tanh((3 * (src[i][j] - T_L)) / T_L))
            else:
                output[i][j] = 0.5 * (1 - math.tanh((3 * (src[i][j] - T_L)) / (1 - T_L)))

    # return np.ones_like(output) - output
    return output

def shadow(src_diff, src_importance, T_S0):
    output = np.zeros_like(src_diff)
    for i in range(len(src_diff)):
        for j in range(len(src_diff[i])):
            T_S = T_S0 * (1 - src_importance[i][j])
            if src_diff[i][j] < T_S:
                output[i][j] = 0.5 * (1 - math.tanh((3 * (src_diff[i][j] - T_S)) / T_S))
            else:
                output[i][j] = 0.5 * (1 - math.tanh((3 * (src_diff[i][j] - T_S)) / (1 - T_S)))

    # return np.ones_like(output) - output
    return output



def method2(file_path):
    # read as rgb
    src = cv2.imread(file_path)[:, :, ::-1]
    bilateral_filter_image = bilateral_filter(src)
    color_diff_image = color_diff(bilateral_filter_image)
    shadow_importance_image = shadow_importance(bilateral_filter_image)
    outline_image = outline(color_diff_image, 0.164)
    shadow_image = shadow(color_diff_image, shadow_importance_image, 0.039)
    final_image = (255 * outline_image * shadow_image).astype(int)

    output_path = os.getcwd() + '/_temp_.jpg'
    cv2.imwrite( output_path, final_image)

    # plt.subplot(4, 2, 1)
    # plt.imshow(src)
    # plt.axis('off')
    # plt.title("src")

    # plt.subplot(4, 2, 2)
    # plt.imshow(bilateral_filter_image)
    # plt.axis('off')
    # plt.title('bilateral_filter')

    # plt.subplot(4, 2, 3)
    # plt.imshow(color_diff_image * 255, cmap='gray', vmin=0, vmax=255)
    # plt.axis('off')
    # plt.title('color_diff')

    # plt.subplot(4, 2, 4)
    # plt.imshow(shadow_importance_image * 255, cmap='gray', vmin=0, vmax=255)
    # plt.axis('off')
    # plt.title('shadow_importance')

    # plt.subplot(4, 2, 5)
    # plt.imshow(outline_image * 255, cmap='gray', vmin=0, vmax=255)
    # plt.axis('off')
    # plt.title('outline')

    # plt.subplot(4, 2, 6)
    # plt.imshow(shadow_image * 255, cmap='gray', vmin=0, vmax=255)
    # plt.axis('off')
    # plt.title('shadow')

    # plt.subplot(4, 2, 7)
    # plt.imshow(final_image, cmap='gray', vmin=0, vmax=255)
    # plt.axis('off')
    # plt.title('result')

    # plt.tight_layout()

    # plt.show()
    return output_path


# test
# if __name__ == "__main__":
#     method2('./images/Screenshot 2022-12-13 172714.png')
