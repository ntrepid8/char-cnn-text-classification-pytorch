import csv
import os.path as op
import re
import torch
import codecs
import json
from torch.utils.data import DataLoader, Dataset
import torch.autograd as autograd

class AGNEWs(Dataset):
    def __init__(self, label_data_path, alphabet_path, l0=1014):
        """Create AG's News dataset object.

        Arguments:
            label_data_path: The path of label and data file in csv.
            l0: max length of a sample.
            alphabet_path: The path of alphabet json file.
        """
        self.label_data_path = label_data_path
        # read alphabet
        with open(alphabet_path) as alphabet_file:
            alphabet = str(''.join(json.load(alphabet_file)))
        self.alphabet = alphabet
        self.l0 = l0
        self.load()
        self.y = torch.LongTensor(self.label)

    def __len__(self):
        return len(self.label)

    def __getitem__(self, idx):
        X = self.oneHotEncode(idx)
        y = self.y[idx]
        return X, y

    def load(self, lowercase=True):
        self.label = []
        self.data = []
        with open(self.label_data_path, 'r') as f:
            rdr = csv.reader(f, delimiter=',', quotechar='"')
            # num_samples = sum(1 for row in rdr)
            for index, row in enumerate(rdr):
                self.label.append(int(row[0]))
                txt = ' '.join(row[1:])
                if lowercase:
                    txt = txt.lower()
                self.data.append(txt)

    def oneHotEncode(self, idx):
        # X = (batch, 70, sequence_length)
        X = torch.zeros(len(self.alphabet), self.l0)
        sequence = self.data[idx]
        for index_char, char in enumerate(sequence[::-1]):
            if self.char2Index(char)!=-1:
                X[self.char2Index(char)][index_char] = 1.0
        return X

    def char2Index(self, character):
        return self.alphabet.find(character)

    def get_class_weight(self):
        num_samples = self.__len__()
        label_set = set(self.label)
        num_class = [self.label.count(c) for c in label_set]
        class_weight = [num_samples/float(self.label.count(c)) for c in label_set]
        return class_weight, num_class

if __name__ == '__main__':

    label_data_path = './data/ag_news_csv/train.csv'
    alphabet_path = './alphabet.json'

    train_dataset = AGNEWs(label_data_path, alphabet_path)
    train_loader = DataLoader(train_dataset, batch_size=64, num_workers=4, drop_last=False)

    for i_batch, sample_batched in enumerate(train_loader):
        inputs, target = sample_batched
        if -1 in target:
            for j in target:
                if j < 0:
                    err_reason = 'invalid_target={}'.format(j)
                    raise ValueError(err_reason)
