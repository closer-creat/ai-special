import numpy as np
import matplotlib.pyplot as plt
import math

if __name__ == '__main__':
    img = plt.imread('./lenna.jpg')
    if img[0][0][0] < 1:
        img = img*255

    img = img.mean(axis=-1)

    # 1、高斯平滑
    sigma = 0.5
    dim = 5  # 高斯核尺寸(通常情况下)
    Gaussian_filter = np.zeros([dim, dim])  # 存储高斯核
    tmp = [i-dim//2 for i in range(dim)]  # x
    n1 = 1/(2*math.pi*sigma**2)  # 中间量
    n2 = -1/(2*sigma**2)
    for i in range(dim):
        for j in range(dim):
            Gaussian_filter[i, j] = n1*math.exp(n2*(tmp[i]**2+tmp[j]**2))
    Gaussian_filter = Gaussian_filter / Gaussian_filter.sum()   #高斯核
    img_filter = np.zeros(img.shape)
    tmp = dim//2
    img_pad = np.pad(img, ((tmp, tmp), (tmp, tmp)), 'constant')  # 边缘填补,滤波后保持图像原尺寸
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            img_filter[i, j] = np.sum(img_pad[i:i+dim, j:j+dim]*Gaussian_filter)
    # plt.figure(1)
    # plt.imshow(img_filter.astype(np.uint8), cmap='gray')  # 此时的img_new是255的浮点型数据，强制类型转换才可以，gray灰阶
    # plt.axis('off')

    # 2、求梯度。两个sobel矩阵（检测图像中的水平、垂直和对角边缘）
    sobel_kernel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_kernel_y = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
    img_tidu_x = np.zeros(img.shape)  # 存储梯度图像
    img_tidu_y = np.zeros(img.shape)
    img_tidu = np.zeros(img.shape)
    img_pad = np.pad(img_filter, ((1, 1), (1, 1)), 'constant')  # 边缘填补，根据上面矩阵结构所以写1(3//2)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            img_tidu_x[i, j] = np.sum(img_pad[i:i+3, j:j+3]*sobel_kernel_x)  # x方向
            img_tidu_y[i, j] = np.sum(img_pad[i:i+3, j:j+3]*sobel_kernel_y)  # y方向
            img_tidu[i, j] = np.sqrt(img_tidu_x[i, j]**2 + img_tidu_y[i, j]**2)
    img_tidu_x[img_tidu_x == 0] = 0.00000001  # 防止除0
    angle = img_tidu_y/img_tidu_x
    # plt.figure(2)
    # plt.imshow(img_tidu.astype(np.uint8), cmap='gray')
    # plt.axis('off')

    # 3、非极大值抑制，根据其梯度方向和8邻域内的梯度幅值，判断当前像素是否为局部极大值。如果是，则保留该像素的梯度幅值；否则，将其抑制（设为0）
    img_yizhi = np.zeros(img_tidu.shape)
    for i in range(1, img.shape[0]-1): # 边缘不检测
        for j in range(1, img.shape[0]-1):
            flag = True  # 在8邻域内是否要抹去做个标记
            temp = img_tidu[i-1:i+2, j-1:j+2]  # 梯度幅值的8邻域矩阵
            if angle[i, j] <= -1:  # 使用线性插值法判断抑制与否，判断当前像素的梯度幅值是否大于这两个插值点。如果不大于，表示需要抑制
                num_1 = (temp[0, 1] - temp[0, 0]) / angle[i, j] + temp[0, 1]
                num_2 = (temp[2, 1] - temp[2, 2]) / angle[i, j] + temp[2, 1]
                if not (img_tidu[i, j] > num_1 and img_tidu[i, j] > num_2):
                    flag = False
            elif angle[i, j] >= 1:
                num_1 = (temp[0, 2] - temp[0, 1]) / angle[i, j] + temp[0, 1]
                num_2 = (temp[2, 0] - temp[2, 1]) / angle[i, j] + temp[2, 1]
                if not (img_tidu[i, j] > num_1 and img_tidu[i, j] > num_2):
                    flag = False
            elif angle[i, j] > 0:
                num_1 = (temp[0, 2] - temp[1, 2]) * angle[i, j] + temp[1, 2]
                num_2 = (temp[2, 0] - temp[1, 0]) * angle[i, j] + temp[1, 0]
                if not (img_tidu[i, j] > num_1 and img_tidu[i, j] > num_2):
                    flag = False
            elif angle[i, j] < 0:
                num_1 = (temp[1, 0] - temp[0, 0]) * angle[i, j] + temp[1, 0]
                num_2 = (temp[1, 2] - temp[2, 2]) * angle[i, j] + temp[1, 2]
                if not (img_tidu[i, j] > num_1 and img_tidu[i, j] > num_2):
                    flag = False
            if flag:
                img_yizhi[i, j] = img_tidu[i, j]
    # plt.figure(3)
    # plt.imshow(img_yizhi.astype(np.uint8), cmap='gray')
    # plt.axis('off')

    # 4、双阈值检测，连接边缘。遍历所有一定是边的点,查看8邻域是否存在有可能是边的点，进栈
    lower_boundary = img_tidu.mean() * 0.5
    high_boundary = lower_boundary * 3
    zhan = []
    for i in range(1, img_yizhi.shape[0] - 1):  # 图像边缘不考虑
        for j in range(1, img_yizhi.shape[1] - 1):
            if img_yizhi[i, j] >= high_boundary:  # 强边缘点
                img_yizhi[i, j] = 255
                zhan.append([i, j])
            elif img_yizhi[i, j] <= lower_boundary:  # 非边缘点
                img_yizhi[i, j] = 0

    while not len(zhan) == 0:  # 伪边缘点->强边缘点（边缘连续）
        temp_1, temp_2 = zhan.pop()  # 出栈
        a = img_yizhi[temp_1 - 1:temp_1 + 2, temp_2 - 1:temp_2 + 2]
        if (a[0, 0] < high_boundary) and (a[0, 0] > lower_boundary):
            img_yizhi[temp_1 - 1, temp_2 - 1] = 255
            zhan.append([temp_1 - 1, temp_2 - 1])  # 当前点若为强边缘点继续判断其周围点是否为强边缘点
        if (a[0, 1] < high_boundary) and (a[0, 1] > lower_boundary):
            img_yizhi[temp_1 - 1, temp_2] = 255
            zhan.append([temp_1 - 1, temp_2])
        if (a[0, 2] < high_boundary) and (a[0, 2] > lower_boundary):
            img_yizhi[temp_1 - 1, temp_2 + 1] = 255
            zhan.append([temp_1 - 1, temp_2 + 1])
        if (a[1, 0] < high_boundary) and (a[1, 0] > lower_boundary):
            img_yizhi[temp_1, temp_2 - 1] = 255
            zhan.append([temp_1, temp_2 - 1])
        if (a[1, 2] < high_boundary) and (a[1, 2] > lower_boundary):
            img_yizhi[temp_1, temp_2 + 1] = 255
            zhan.append([temp_1, temp_2 + 1])
        if (a[2, 0] < high_boundary) and (a[2, 0] > lower_boundary):
            img_yizhi[temp_1 + 1, temp_2 - 1] = 255
            zhan.append([temp_1 + 1, temp_2 - 1])
        if (a[2, 1] < high_boundary) and (a[2, 1] > lower_boundary):
            img_yizhi[temp_1 + 1, temp_2] = 255
            zhan.append([temp_1 + 1, temp_2])
        if (a[2, 2] < high_boundary) and (a[2, 2] > lower_boundary):
            img_yizhi[temp_1 + 1, temp_2 + 1] = 255
            zhan.append([temp_1 + 1, temp_2 + 1])

    for i in range(img_yizhi.shape[0]): # 伪边缘点->非边缘点（孤立极大值：噪声）
        for j in range(img_yizhi.shape[1]):
            if img_yizhi[i, j] != 0 and img_yizhi[i, j] != 255:
                img_yizhi[i, j] = 0
    
    plt.figure(1)
    plt.imshow(img_yizhi.astype(np.uint8), cmap='gray')
    plt.axis('off')  
    plt.show()
    
