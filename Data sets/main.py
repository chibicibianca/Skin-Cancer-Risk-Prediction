import os
import shutil
import random

seed = 1
random.seed(seed)
directory = "ISIC_2019_Training_Input/"
train = "data/train/"
test = "data/test/"
validation = "data/validation/"

#creaza foldere
os.makedirs(train + "benign/")
os.makedirs(train + "malignant/")
os.makedirs(test + "benign/")
os.makedirs(test + "malignant/")
os.makedirs(validation + "benign/")
os.makedirs(validation + "malignant/")

test_examples = train_examples = validation_examples = 0

for line in open("ISIC_2019_Training_GroundTruth.csv").readlines()[1:]:
    split_line = line.split(",")
    img_file = split_line[0]
    benign_malign = split_line[1]

    random_num = random.random()

    if random_num < 0.8: #80% for test
        location = train
        train_examples += 1
    elif random_num < 0.9: #10% for valid
        location = validation
        validation_examples += 1
    else:
        location = test #the rest of 10% to test
        test_examples += 1

#need to convert
    if int(float(benign_malign)) == 0:
        shutil.copy(
            "ISIC_2019_Training_Input/ISIC_2019_Training_Input/"
            + img_file + ".jpg",
            location + "benign/" + img_file + ".jpg",
            #copy from training to benign
        )

    elif int(float(benign_malign)) == 1:
        shutil.copy(
            "ISIC_2019_Training_Input/ISIC_2019_Training_Input/"
            + img_file + ".jpg",
            location + "malignant/" + img_file + ".jpg",
        )

    print(f"Number of training examples {train_examples} ")
    print(f"Number of test examples {test_examples} ")
    print(f"Number of validation examples {validation_examples} ")
