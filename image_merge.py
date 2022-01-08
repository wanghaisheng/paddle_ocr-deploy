
import cv2
import jax.numpy as np
import matplotlib.pyplot as plt
import imageio
cv2.ocl.setUseOpenCL(False)


class M_IMAGE:
    def __init__(self, rgb, feature_extractor='sift'):
        self.rgb = rgb
        self.gray = None
        self.feature_extractor = feature_extractor
        self.keypoints = []
        self.features = []

    def processImage(self):
        # read images and transform them to grayscale
	    # Make sure that the train image is the image that will be transformed
        self.gray = cv2.cvtColor(self.rgb, cv2.COLOR_RGB2GRAY)
        self.keypoints, self.features = self.detectAndDescribe()

    def detectAndDescribe(self):
        """
        Compute key points and feature descriptors using an specific method
        """

        assert self.feature_extractor is not None, "You need to define a feature detection method. Values are: 'sift', 'surf'"

        # detect and extract features from the image
        if self.feature_extractor == 'sift':
            descriptor = cv2.SIFT_create()
        elif self.feature_extractor == 'brisk':
            descriptor = cv2.BRISK_create()
        elif self.feature_extractor == 'orb':
            descriptor = cv2.ORB_create()

        # get keypoints and descriptors
        (kps, features) = descriptor.detectAndCompute(self.gray, None)

        return (kps, features)


def createMatcher(method, crossCheck):
	"Create and return a Matcher Object"
    # 对于SIFT和SURF，OpenCV建议使用欧几里德距离。
    # 对于其他特征提取器，如ORB和BRISK，建议使用汉明距离。
	if method == 'sift' or method == 'surf':
		bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=crossCheck)
	elif method == 'orb' or method == 'brisk':
		bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=crossCheck)
	return bf


def matchKeyPointsBF(featuresA, featuresB, method):
	bf = createMatcher(method, crossCheck=True)

	# Match descriptors.
	best_matches = bf.match(featuresA, featuresB)

	# Sort the features in order of distance.
	# The points with small distance (more similarity) are ordered first in the vector
	rawMatches = sorted(best_matches, key=lambda x: x.distance)
	print("Raw matches (Brute force):", len(rawMatches))
	return rawMatches


def matchKeyPointsKNN(featuresA, featuresB, ratio, method):
	bf = createMatcher(method, crossCheck=False)
	# compute the raw matches and initialize the list of actual matches
	rawMatches = bf.knnMatch(featuresA, featuresB, 2)
	print("Raw matches (knn):", len(rawMatches))
	matches = []

	# loop over the raw matches
	for m, n in rawMatches:
		# ensure the distance is within a certain ratio of each
		# other (i.e. Lowe's ratio test)
		if m.distance < n.distance * ratio:
			matches.append(m)
	return matches


def getHomography(kpsA, kpsB, featuresA, featuresB, matches, reprojThresh):
    # convert the keypoints to numpy arrays
    kpsA = np.float32([kp.pt for kp in kpsA])
    kpsB = np.float32([kp.pt for kp in kpsB])

    if len(matches) > 10:
        # construct the two sets of points
        ptsA = np.float32([kpsA[m.queryIdx] for m in matches]).reshape(-1,1,2)
        ptsB = np.float32([kpsB[m.trainIdx] for m in matches]).reshape(-1,1,2)

        # estimate the homography between the sets of points
        (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, reprojThresh)

        return (matches, H, status)
    else:
        return None

def remove_the_blackborder(image):
    img = cv2.medianBlur(image, 5) #中值滤波，去除黑色边际中可能含有的噪声干扰
    b = cv2.threshold(img, 3, 255, cv2.THRESH_BINARY) #调整裁剪效果
    binary_image = b[1]            #二值图--具有三通道
    binary_image = cv2.cvtColor(binary_image,cv2.COLOR_BGR2GRAY)
    # print(binary_image.shape)     #改为单通道
 
    edges_y, edges_x = np.where(binary_image==255) ##h, w
    bottom = min(edges_y)             
    top = max(edges_y) 
    height = top - bottom            
                                   
    left = min(edges_x)           
    right = max(edges_x)             
    height = top - bottom 
    width = right - left

    res_image = image[bottom:bottom+height, left:left+width]
    return res_image  

def resize_image(image):
    height, width = image.shape[0], image.shape[1]
    width_new = 1280
    height_new = 720
    scale = 1
    if width / height >= width_new / height_new:
        img_new = cv2.resize(image, (width_new, int(height * width_new / width)), interpolation=cv2.INTER_AREA)
        scale = width_new / width
    else:
        img_new = cv2.resize(image, (int(width * height_new / height), height_new), interpolation=cv2.INTER_AREA)
        scale = height_new / height

    return scale, img_new

def mergeImages(images_bgr, output_color='rgb', direct='horizontal', feature_extractor='sift', feature_matching='knn'):
    ''' 拼接图片

    拼接多张图片，允许横向或竖向拼接多张图片
    以第一张图片方向为基准

    :param images_bgr(opencv默认读取方式)，列表顺序为图片从左至右或从上至下顺序
    :output_color: 输出颜色模式，可选值 rgb (default), bgr
    :direct: 拼接方向,横向或竖向，可选值 horizontal (default),  vertical
    :feature_extractor: 特征值提取方式，sift (default), orb, brisk
    :feature_matching: 特征匹配方式, knn (default), bf
    :returns: merged image in  RGB to be compatible to matplotlib
    '''

    origin_images = []
    resize_scale = 1
    for image_bgr in images_bgr:
        resize_scale, image_bgr = resize_image(image_bgr)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        origin_images.insert(0, image_rgb)

    # cv2.imshow('Resize0', origin_images[0])
    # cv2.imshow('Resize1', origin_images[1])
    # cv2.imshow('Resize2', origin_images[2])
    # cv2.waitKey(0)

    print("Using: {} feature matcher".format(feature_matching))
    imageA = None
    imageB = None


    for index in range(len(origin_images)):
        if index == 0:
            imageA = M_IMAGE(origin_images[index])
        else:
            imageB = M_IMAGE(origin_images[index])
            imageA.processImage()
            imageB.processImage()

            # feature_imageA = cv2.drawKeypoints(imageA.gray,imageA.keypoints,None,color=(0,255,0))
            # feature_imageB = cv2.drawKeypoints(imageB.gray,imageB.keypoints,None,color=(0,255,0))
            # cv2.imshow('feature_imageA', feature_imageA)
            # cv2.imshow('feature_imageB', feature_imageB)
            # cv2.waitKey(0)

            if feature_matching == 'bf':
                matches = matchKeyPointsBF(imageA.features, imageB.features, method=imageA.feature_extractor)
            elif feature_matching == 'knn':
                matches = matchKeyPointsKNN(imageA.features, imageB.features, ratio=0.75, method=imageA.feature_extractor)
        
            M = getHomography(imageA.keypoints, imageB.keypoints, imageA.features, imageB.features, matches, reprojThresh=5)
            if M is None:
                print("Error!")
            (matches, H, status) = M
            print(H)

            if direct == 'vertical':
                # Apply a vertical panorama
                width = max(imageA.rgb.shape[1], imageB.rgb.shape[1])
                height = imageA.rgb.shape[0] + imageB.rgb.shape[0]

                result = cv2.warpPerspective(imageA.rgb, H, (width, height))
                result[0:imageB.rgb.shape[0], :] = imageB.rgb
            else:
                # Apply a horizontal panorama
                width = imageB.rgb.shape[1] + imageA.rgb.shape[1]
                height = max(imageB.rgb.shape[0], imageA.rgb.shape[0])
                # otherwise, apply a perspective warp to stitch the images
                # together
                result = cv2.warpPerspective(imageA.rgb, H, (width, height))
                # cv2.imshow('Merged', result)
                # cv2.waitKey(0)
                result[0:imageB.rgb.shape[0], 0:imageB.rgb.shape[1]] = imageB.rgb
            imageA = M_IMAGE(result)
    
    merged = imageA.rgb
    merged = remove_the_blackborder(merged)
    if output_color == 'bgr':
        merged = cv2.cvtColor(merged, cv2.COLOR_RGB2BGR)
    return merged




if __name__ == '__main__':
    import time

    timestamp = int(round(time.time() * 1000))
    feature_extractor = 'sift'
    feature_matching = 'knn'
    image_paths = ['./data/pic_part_1.jpg','./data/pic_part_2.jpg','./data/pic_part_3.jpg','./data/pic_part_4.jpg']
    # origin_images = []
    # origin_images = []
    # parsed_images = []
    # for img in image_paths:
    #     # Opencv defines the color channel in the order BGR.
	#     # Transform it to RGB to be compatible to matplotlib
    #     image_bgr = cv2.imread(img)
    #     image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    #     origin_images.append(image_rgb)
    # origin_images.reverse()

    # image_size = len(origin_images)
    # # 展示单张图片处理结果
    # fig, cols = plt.subplots(nrows=1, ncols=image_size, constrained_layout=False, figsize=(16,9))
    # for index in range(image_size):
    #     ax = k_cols[index]
    #     imageA = M_IMAGE(origin_images[index])
    #     imageA.processImage()
    #     ax1.imshow(imageA.rgb, cmap="gray")
    #     ax1.set_xlabel("Gray image " + str(index), fontsize=14)
    
    # plt.savefig("./output/input_img_"+str(timestamp)+'.jpg', bbox_inches='tight', dpi=300, optimize=True, format='jpeg')
    # plt.show()

	# # 显示在两张图片中检测到的关键点
	# # display the keypoints and features detected on both images
    # k_fig, k_cols = plt.subplots(nrows=1, ncols=image_size, figsize=(20,8), constrained_layout=False)
    # for index in range(image_size):
    #     ax = k_cols[index]
    #     imageA = M_IMAGE(origin_images[index])
    #     imageA.processImage()
    #     ax.imshow(cv2.drawKeypoints(imageA.gray,imageA.keypoints,None,color=(0,255,0)))
    #     ax.set_xlabel("(" + str(index) + ")", fontsize=14)

    # plt.savefig("./output/" + feature_extractor + "_features_img_"+str(timestamp)+'.jpg', bbox_inches='tight', 
	# 	dpi=300, optimize=True, format='jpeg')
    # plt.show() 

    # print("Using: {} feature matcher".format(feature_matching))
    # direct = 'horizontal' # horizontal / vertical
    # imageA = None
    # imageB = None
    # result= None

    # for index in range(len(origin_images)):
    #     if index == 0:
    #         imageA = M_IMAGE(origin_images[index])
    #     else:
    #         imageB = M_IMAGE(origin_images[index])
    #         imageA.processImage()
    #         imageB.processImage()

    #         if feature_matching == 'bf':
    #             matches = matchKeyPointsBF(imageA.features, imageB.features, method=imageA.feature_extractor)
    #         elif feature_matching == 'knn':
    #             matches = matchKeyPointsKNN(imageA.features, imageB.features, ratio=0.75, method=imageA.feature_extractor)
        
    #         M = getHomography(imageA.keypoints, imageB.keypoints, imageA.features, imageB.features, matches, reprojThresh=4)
    #         if M is None:
    #             print("Error!")
    #         (matches, H, status) = M
    #         print(H)

    #         if direct == 'vertical':
    #             # Apply a vertical panorama
    #             width = max(imageA.rgb.shape[1], imageB.rgb.shape[1])
    #             height = imageA.rgb.shape[0] + imageB.rgb.shape[0]

    #             result = cv2.warpPerspective(imageA.rgb, H, (width, height))
    #             result[0:imageB.rgb.shape[0], :] = imageB.rgb
    #         else:
    #             # Apply a horizontal panorama
    #             width = imageB.rgb.shape[1] + imageA.rgb.shape[1]
    #             height = max(imageB.rgb.shape[0], imageA.rgb.shape[0])
    #             # otherwise, apply a perspective warp to stitch the images
    #             # together
    #             result = cv2.warpPerspective(imageA.rgb, H, (width, height))
    #             result[0:imageB.rgb.shape[0], 0:imageB.rgb.shape[1]] = imageB.rgb

    #         imageA = M_IMAGE(result)

    images_bgr = []
    for img in image_paths:
        image_bgr = cv2.imread(img)
        images_bgr.append(image_bgr)
    result = mergeImages(images_bgr, feature_matching='knn')


    plt.figure(figsize=(20,10))
    plt.imshow(result)
    imageio.imwrite("./output/panorama_img_"+str(timestamp)+'.jpeg', result)
    plt.axis('off')
    plt.show()