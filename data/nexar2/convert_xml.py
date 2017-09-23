import os
import pandas as pd
import argparse


HOME = os.environ['HOME']
DATA_ROOT = os.path.abspath(os.path.join(HOME, 'datasets/nexar'))
IMAGE_PATH = os.path.join(DATA_ROOT, 'train')
ANNO_PATH = os.path.join(DATA_ROOT, 'annotations')


parser = argparse.ArgumentParser()
parser.add_argument('--single-class', help='Label all the examples (car, bus, etc.) with one class (vehicle)', action='store_true')
parser.add_argument('--train', help='Path to csv file with train image annotations', default='')
parser.add_argument('--val', help='Path to csv file with val image annotations', default='')
parser.add_argument('--gen-annos', help='Generate XML annotation files for each image', action='store_true')

args = parser.parse_args()

TRAIN_PATH = args.train
VAL_PATH = args.val

SINGLE_CLASS = args.single_class
SINGLE_CLASS_NAME = 'vehicle'


from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom

def annotation2xml(ann):
    def prettify(elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    top = Element('annotation')

    size = SubElement(top, 'size')
    SubElement(size, 'width').text = str(1280)
    SubElement(size, 'height').text = str(720)
    SubElement(size, 'depth').text = str(3)

    for x0, y0, x1, y1, label in ann:
        obj = SubElement(top, 'object')
        name = SubElement(obj, 'name')
        name.text = label
        difficult = SubElement(obj, 'difficult')
        difficult.text = '0'
        bndbox = SubElement(obj, 'bndbox')
        xmin = SubElement(bndbox, 'xmin')
        xmin.text = str(x0)
        ymin = SubElement(bndbox, 'ymin')
        ymin.text = str(y0)
        xmax = SubElement(bndbox, 'xmax')
        xmax.text = str(x1)
        ymax = SubElement(bndbox, 'ymax')
        ymax.text = str(y1)

    return prettify(top)


def save_xml(iname, ann):
    with open(os.path.join(ANNO_PATH, xmlname), 'w') as f:
        xml = annotation2xml(ann)
        f.write(xml)


image_subdir = 'train'
anno_subdir = 'annotations'

for dataset in ['train', 'val']:
    input_file = TRAIN_PATH if dataset == 'train' else VAL_PATH

    if not input_file:
        print '%s file is not set' % dataset
        continue

    print "Processing %s->%s..." % (input_file, dataset)

    labels_df = pd.read_csv(input_file, index_col='image_filename')

    image_names = list(set(labels_df.index.values))
    
    label_file_name = dataset + '.txt'
    label_file = open(label_file_name, 'w')

    if dataset == 'val':
        name_size_file_name = 'test_name_size.txt'
        name_size_file = open(name_size_file_name, 'w')

    num_images = len(image_names)

    for i, iname in enumerate(image_names):
        xmlname = os.path.splitext(iname)[0] + '.xml'

	if args.gen_annos:
            ann = []

            df = labels_df.loc[iname]
            if df.ndim > 1: # multiple boxes
                for row in df.itertuples():
                    ann.append((int(row.x0), int(row.y0), int(row.x1), int(row.y1), SINGLE_CLASS_NAME if SINGLE_CLASS else row.label))
            else: # one box
                ann.append((int(df.x0), int(df.y0), int(df.x1), int(df.y1), SINGLE_CLASS_NAME if SINGLE_CLASS else df.label))

            save_xml(xmlname, ann)

        label_file.write(image_subdir + '/' + iname + ' ' + anno_subdir + '/' + xmlname + '\n')

        if dataset == 'val':
            name_size_file.write(os.path.splitext(iname)[0] + " 720 1280\n")
            
        if i > 0 and i % 1000 == 0:
            print "Processed {}/{}".format(i + 1, num_images)

    label_file.close()

    if dataset == 'val':
        name_size_file.close()

