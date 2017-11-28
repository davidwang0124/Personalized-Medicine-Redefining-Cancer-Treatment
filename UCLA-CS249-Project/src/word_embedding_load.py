# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 14:56:55 2017

@author: zhuya
#this code train doc2vector with the word embedding load from PubMed-based vectors introduced by Chiu et al. (2016).
"""
from gensim.models import Doc2Vec
from gensim.models import KeyedVectors
import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
import os
import util

TEXT_INPUT_DIM=200
param = util.Doc2VecParam(1, 5, TEXT_INPUT_DIM, 1e-4, 5, 4, 30, 1)
filename='../model/doc2vec/docEmbeddings_30_load_all.d2v'
GENE_INPUT_DIM=25
svd = TruncatedSVD(n_components=25, n_iter=GENE_INPUT_DIM, random_state=12)


'''
Get text_model either from pre-trained models or train it using assigned parameters.
See also util.Doc2VecParam, util.Doc2VecWrapper()

@param: filename, the path to the 
@return: text_model for the following

'''

def getTextModel(param = util.Doc2VecParam(), filename=''):
    if filename == '' or not os.path.isfile(filename):
        print('Creating model...')
        filename = '../model/doc2vec/docEmbeddings_30_load_all.d2v'
        source_file = "../data/bio_nlp_vec/PubMed-shuffle-win-30.bin"
        text_model = util.Doc2VecWrapper(param)
        text_model.build_vocab(sentences)
        try:   
            text_model.intersect_word2vec_format(source_file, binary = True, lockf=0.0)
        except:
            print('Unable to find file: ' + source_file)
            return ''
        text_model.train(sentences, total_examples=text_model.corpus_count, epochs=text_model.iter)
        text_model.save(filename)
        print('successfully created the Text Model and save it to ' + filename)
        
    else:
        print('Loading model...')
        text_model = Doc2Vec.load(filename)
        print('successfully loaded the textmodel from ' + filename)
    return text_model

'''
Get the clinical text vector representation based on the text_model

@param: 
    text_model,
    train_size,
    test_size,
    TEXT_INPUT_DIM, set to 200 as default
@return:
    text_train_arrays, text vector in training set
    text_test_arrays, ... in test set

'''

def getTextVec(text_model, train_size, test_size, TEXT_INPUT_DIM = 200):
    text_train_arrays = np.zeros((train_size, TEXT_INPUT_DIM))
    text_test_arrays = np.zeros((test_size, TEXT_INPUT_DIM))
    for i in range(train_size):
        text_train_arrays[i] = text_model.docvecs['Text_'+str(i)]
    j = 0
    for i in range(train_size, test_size + train_size):
        text_test_arrays[j] = text_model.docvecs['Text_'+str(i)]
        j += 1
    return text_train_arrays, text_test_arrays

'''
Get the vector representation for the Gene, the length of the vector is compressed by SVD with default input dimension 25
@param: 
    all_data,
    svd, TruncatedSVD model from sklearn
@return: truncated_one_hot_gene, gene vector representation

'''
def getGeneVec(all_data, svd):
    one_hot_gene = pd.get_dummies(all_data['Gene'])
    truncated_one_hot_gene = svd.fit_transform(one_hot_gene.values)
    return truncated_one_hot_gene

'''
Get the vector representation for the variation type, the length of the vector is compressed by SVD with default input dimension 25
@param: 
    all_data,
    svd, TruncatedSVD model from sklearn
@return: truncated_one_hot_variation, variation vector representation

'''
def getVariationVec(all_data, svd):
    one_hot_variation = pd.get_dummies(all_data['Variation'])
    truncated_one_hot_variation = svd.fit_transform(one_hot_variation.values)
    return truncated_one_hot_variation

if __name__ == '__main__':
    TEXT_INPUT_DIM=200
    GENE_INPUT_DIM=25
    param = Doc2VecParam(1, 5, TEXT_INPUT_DIM, 1e-4, 5, 4, 30, 1)
    filename='../model/doc2vec/docEmbeddings_30_load_all.d2v'


    svd = TruncatedSVD(n_components=25, n_iter=GENE_INPUT_DIM, random_state=12)
    text_model = getTextModel(param, filename)

    truncated_one_hot_gene = getGeneVec(all_data, svd)
    truncated_one_hot_variation = getVariationVec(all_data, svd)
    text_train_arrays, text_test_arrays = getTextVec(text_model, train_size, test_size, TEXT_INPUT_DIM)

    train_set = np.hstack((truncated_one_hot_gene[:train_size], truncated_one_hot_variation[:train_size], text_train_arrays))
    # N by (25+25+200)
    test_set = np.hstack((truncated_one_hot_gene[train_size:], truncated_one_hot_variation[train_size:], text_test_arrays))
    encoded_y = pd.get_dummies(train_y)
    encoded_y = np.array(encoded_y)

