#!/usr/bin/env python
# encoding: utf-8
"""
genderPredictor.py
"""

from nltk import NaiveBayesClassifier,classify
from curses.ascii import isdigit
from nltk.corpus import cmudict
import curses
import nltk
import USSSALoader
import random

class genderPredictor():
    
    def __init__(self):
        self._dic = cmudict.dict()

    def getFeatures(self):
        maleNames,femaleNames=self._loadNames()
        
        featureset = list()
        for nameTuple in maleNames:
            features = self._nameFeatures(nameTuple[0])
            featureset.append((features,'M'))
        
        for nameTuple in femaleNames:
            features = self._nameFeatures(nameTuple[0])
            featureset.append((features,'F'))
    
        return featureset
    
    def trainAndTest(self,trainingPercent=0.80):
        featureset = self.getFeatures()
        random.shuffle(featureset)
        
        name_count = len(featureset)
        cut_point=int(name_count*trainingPercent)
        
        train_set = featureset[:cut_point]
        test_set  = featureset[cut_point:]
        
        self.train(train_set)
        
        return self.test(test_set)
        
    def classify(self,name):
        feats=self._nameFeatures(name)
        return self.classifier.classify(feats)
        
    def train(self,train_set):
        self.classifier = NaiveBayesClassifier.train(train_set)
        return self.classifier
        
    def test(self,test_set):
       return classify.accuracy(self.classifier,test_set)
        
    def getMostInformativeFeatures(self,n=5):
        return self.classifier.most_informative_features(n)
        
    def _loadNames(self):
        return USSSALoader.getNameList()

    def nsyl(self, word):
        try:
            cnt = [len(list(y for y in x if isdigit(y[-1]))) for x in self._dic[word.lower()]]
            return cnt[0]
        except:
            return 0

    def _nameFeatures(self,name):
        name=name.upper()
        name = name.split()[0]
        return {
                'last_letter': name[-1],
                'last_three' : name[-4:],
                'last_is_vowel' : (name[-1] in 'AEIOUY'),
                'first_two': (name[:4]),
                'first_is_vowel': (name[0] in 'AEIOUY'),
                #'n_s': self.nsyl(name)
                }

if __name__ == "__main__":
    gp = genderPredictor()
    
    cur_acc = 0.0
    n_run = 10
    for i in range(n_run):
        accuracy=gp.trainAndTest()
        cur_acc += accuracy
        print 'Accuracy: %f'%accuracy
        #print 'Most Informative Features'
        feats=gp.getMostInformativeFeatures(10)
        for feat in feats:
            print '\t%s = %s'%feat

    print cur_acc*1.0/n_run  
