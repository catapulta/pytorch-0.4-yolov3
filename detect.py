import sys
import time
from PIL import Image, ImageDraw
# from models.tiny_yolo import TinyYoloNet
from utils import *
from image import letterbox_image, correct_yolo_boxes
from darknet import Darknet

namesfile = None


def detect(cfgfile, weightfile, imgfile, conf_threshold, nms_threshold):
    m = Darknet(cfgfile)

    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    # if m.num_classes == 20:
    #     namesfile = 'data/voc.names'
    # elif m.num_classes == 80:
    #     namesfile = 'data/coco.names'
    # else:
    #     namesfile = 'data/names'

    use_cuda = torch.cuda.is_available()
    if use_cuda:
        m.cuda()

    img = Image.open(imgfile).convert('RGB')
    sized = letterbox_image(img, m.width, m.height)

    start = time.time()
    boxes = do_detect(m, sized, conf_threshold, nms_threshold, use_cuda)
    correct_yolo_boxes(boxes, img.width, img.height, m.width, m.height)

    finish = time.time()
    print('%s: Predicted in %f seconds.' % (imgfile, (finish - start)))

    class_names = load_class_names(namesfile)
    plot_boxes(img, boxes, 'predictions.jpg', class_names)


def detect_cv2(cfgfile, weightfile, imgfile, conf_threshold, nms_threshold):
    import cv2
    m = Darknet(cfgfile)

    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    if m.num_classes == 20:
        namesfile = 'data/voc.names'
    elif m.num_classes == 80:
        namesfile = 'data/coco.names'
    else:
        namesfile = 'data/names'

    use_cuda = True
    if use_cuda:
        m.cuda()

    img = cv2.imread(imgfile)
    sized = cv2.resize(img, (m.width, m.height))
    sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

    for i in range(2):
        start = time.time()
        boxes = do_detect(m, sized, conf_threshold, nms_threshold, use_cuda)
        finish = time.time()
        if i == 1:
            print('%s: Predicted in %f seconds.' % (imgfile, (finish - start)))

    class_names = load_class_names(namesfile)
    plot_boxes_cv2(img, boxes, savename='predictions.jpg', class_names=class_names)


def detect_skimage(cfgfile, weightfile, imgfile, conf_threshold, nms_threshold):
    from skimage import io
    from skimage.transform import resize
    m = Darknet(cfgfile)

    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    if m.num_classes == 20:
        namesfile = 'data/voc.names'
    elif m.num_classes == 80:
        namesfile = 'data/coco.names'
    else:
        namesfile = 'data/names'

    use_cuda = True
    if use_cuda:
        m.cuda()

    img = io.imread(imgfile)
    sized = resize(img, (m.width, m.height)) * 255

    for i in range(2):
        start = time.time()
        boxes = do_detect(m, sized, conf_threshold, nms_threshold, use_cuda)
        finish = time.time()
        if i == 1:
            print('%s: Predicted in %f seconds.' % (imgfile, (finish - start)))

    class_names = load_class_names(namesfile)
    plot_boxes_cv2(img, boxes, savename='predictions.jpg', class_names=class_names)


def isfloat(s):
    try:
        float(s)
        return True
    except ValueError:
        print('Confidence Interval could not be transformed to float')
        return False


if __name__ == '__main__':
    if len(sys.argv) >= 5:
        cfgfile = sys.argv[1]
        weightfile = sys.argv[2]
        imgfile = sys.argv[3]
        globals()["namesfile"] = sys.argv[4]
        conf_threshold = float(sys.argv[5]) if isfloat(sys.argv[5]) and float(sys.argv[5]) <= 1 else 0.5
        nms_threshold = float(sys.argv[5]) if isfloat(sys.argv[6]) and float(sys.argv[6]) <= 1 else 0.4
        detect(cfgfile, weightfile, imgfile, conf_threshold, nms_threshold)
        # detect_cv2(cfgfile, weightfile, imgfile)
        # detect_skimage(cfgfile, weightfile, imgfile)
    else:
        print('Usage: ')
        print('  python detect.py cfgfile weightfile imgfile names confidence_threshold nms_threshold')
        # detect('cfg/tiny-yolo-voc.cfg', 'tiny-yolo-voc.weights', 'data/person.jpg', version=1)
