# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 19:16:25 2020

@author: Gunveen Batra
"""

import pandas as pd
import numpy as np
from sklearn import preprocessing
from nltk.stem.porter import *
from nltk.stem import WordNetLemmatizer 
import nltk
from textblob import TextBlob
import matplotlib.pyplot as plt
from math import sqrt
import re

data=pd.read_csv('C:\\Gun\\Academics\\6th sem\\DMPA_Lab\\Lab_proj\\amazon_phone_dataset.csv')





#DATA PRE-PROCESSSING

data=data.dropna()
data=data.drop(['Product_url','ans_ask'],axis=1)

#Removing all useless series of dots or special characters
data['cust_review'] = data['cust_review'].str.replace("[^a-zA-Z0-9***]", " ") 
#removing all short words having length <3
data['cust_review']=data['cust_review'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>3])) 
#Seperating reviews in the dataset
data['cust_review']=data['cust_review'].apply(lambda x: x.split("***"))

data['Product_price']=data['Product_price'].str.replace("[^0-9#]", "") #removing any non-numeric characters
data['Product_price']=[i[:-2] for i in data['Product_price']]

data['total_review']=data['total_review'].str.replace("[^0-9#]", "") #Removing any non-numeric characters

data['rating']=data['rating'].str.replace("[^0-9.#]", "")
data['rating']=[i[:-1] for i in data['rating']]

#Removing all duplicate records
data.sort_values("Product_name", inplace = True) 
data.drop_duplicates(subset ="Product_name", keep = False, inplace = True) 

data['final_reviews']=data['cust_review']





#CLEANING AND ANALYSING REVIEWS FOR EACH PRODUCT

#Tokenization, Stemming   
stemmer = PorterStemmer()
lmtz=WordNetLemmatizer()

data['cust_review']=data['cust_review'].apply(lambda x: [nltk.word_tokenize(i) for i in x]) #tokenization

freq=[] #list of dictionaries, one dictionary for each review, containing frequency of each word in each review
    
for j in data['cust_review']: 
    f=[]
    for i in j:
        fr={}
        for word in i:
            #fr[word] = fr[word] + 1 if word in fr else 1
            if word in fr:
                fr[word]=fr[word]+1
            else:
                fr[word]=1
        f.append(fr)
    freq.append(f)
      

def get_review_sentiment(tweet):   #getting the review of each word 
    # create TextBlob object of passed review text 
    analysis = TextBlob(tweet) 
    # set sentiment 
    if analysis.sentiment.polarity > 0: 
        return 'positive'
    elif analysis.sentiment.polarity == 0: 
        return 'neutral'
    else: 
        return 'negative'
    
   
for datadict in freq:   #getting the sentiment of each word in the freq list
    for d in datadict:
        for key, value in d.items():
            d[key] = (value,get_review_sentiment(key))
            
  
final_reviews=[]   #analysing the overall reviews for each product
for i in freq:
    t=[]
    for j in i:
        x={}
        positive=0
        negative=0 
    
        for key, value in j.items():
            if value[1]=='positive':
                positive+=1
            elif value[1]=='negative':
                negative+=1
        x['positive']=positive
        x['negative']=negative
        t.append(x)
    final_reviews.append(t)
    

      
data['review']=final_reviews
data=data.drop(['cust_review'],axis=1) 

data['Product_price']=pd.to_numeric(data['Product_price'],errors='coerce') #converting the values in these columns to numeric values
data['rating']=pd.to_numeric(data['rating'],errors='coerce')

data=data.drop(['total_review'],axis=1) #dropping out the extra usless columns




'''

#SOME MORE PRE-PROCESSING       

corr_matrix_amazon = data.corr().abs()  #building the correlation matrix to drop unecessary columns

c=0
for index, row in corr_matrix_amazon.iterrows(): #checking if highly correlated attributes present
    for i in row:
        if(i>0.95):
            #print(i)
            c+=1
#since no values above 0.95 hence no columns dropped 

data=data.dropna()#dropping any Nan values that are remaining


'''

'''
#GRAPH PLOTTING

#Plotting price against ratings
ylabel = data["Product_price"]
xlabel = data["rating"]
plt.ylabel("Price")
plt.xlabel("Rating")
plt.scatter(xlabel, ylabel, alpha=0.1)
plt.title("Price vs Ratings")
plt.savefig('price_vs_rating.png')
plt.show()


#plotting price against average rating for each brand
brands=[]
brands=data['by_info']
brands=brands.unique()  
brands=list(brands)    
       
xlabel=brands
plt.xlabel("Brands")
ylabel=data.groupby('by_info')['rating'].mean()
plt.ylabel("Mean rating")
plt.scatter(xlabel, ylabel, alpha=0.1)
plt.show()

#plotting price vs number of positive and negative reviews

ylabel = data["Product_price"]
plt.ylabel("Price")
p,n,posi,negi=0,0,[],[]
for i in final_reviews:
    p,n=0,0
    for j in i:
        for key,value in j.items():
            if(key=='positive'):
                p+=1
            else:
                n+=1
    posi.append(p)
    negi.append(n)
xlabel = posi
plt.xlabel("Number of positive ratings")
plt.bar(xlabel, ylabel, alpha=0.75)
plt.title("Price vs Number of positive ratings")
plt.savefig('price_vs_positive_ratings.png')
plt.show()



data['price_bins']=pd.cut(data['Product_price'],8)
price_bins_dict={}
for i in data['price_bins']:
    if i in price_bins_dict:
        price_bins_dict[i]+=1
    else:
        price_bins_dict[i]=1

        
labels=list(price_bins_dict.keys())
sizes=list(price_bins_dict.values())

plt.pie(sizes)
plt.legend(labels, bbox_to_anchor=(1,0), loc="lower right", bbox_transform=plt.gcf().transFigure)
plt.title('Number of phones per price range')
#plt.savefig('pie_chart.png')
plt.show()

'''


'''
#DOWNLOADING IMAGES
data['Product_name'] = [re.sub(r'\"', 'inches', i) for i in data['Product_name']] 
data['Product_name'] = [re.sub(r'\(|\)|\/|\|\,\|\|', '', i) for i in data['Product_name']] 


import urllib.request
for i in data.iterrows():
    try:
        urllib.request.urlretrieve(str(i[1]['Product_img']), "static/%s.jpg"%(str(i[1]['Product_name'])))
    except FileNotFoundError or OSError:
        pass
'''

#KNN MODEL FOR RECOMMENDATION

def euclidean_dist(x1, x2):
    
    dist=0
    dist=((x1[0]-x2[0])**2)+((x1[1]-x2[1])**2)
    
    return sqrt(dist)


def get_neighbors(data_t, test_row, k, names, r, des, feat):
    
    distances=[]
    i=0
    for train_row in data_t:
        dist=euclidean_dist(train_row, test_row)
        distances.append((names[i], train_row, dist, r, des, feat))
        i+=1
        
    distances.sort(key=lambda tup:tup[2])
    
    neighbors=[]
    
    for i in range(k):
        neighbors.append((distances[i][0], distances[i][1], distances[i][2], distances[i][3], distances[i][4], distances[i][5]))
    
    return neighbors

def send(handset):
    for i in data.iterrows():
        if handset==i[1]['Product_name']:
            price=i[1]['Product_price']
            rating=i[1]['rating']
            rew=i[1]['final_reviews']
            descp=i[1]['prod_des']
            features=i[1]['feature']
            break
        
    inp=[rating,price]       
    data_train=[]
    names=[]
    
    for row, j in data.iterrows():
        if j['Product_name']!=handset:
            s=[j['rating'], j['Product_price']]
            k=j['Product_name']
            data_train.append(s)
            names.append(k)
    
    c=get_neighbors(data_train, inp, 5, names, rew, descp, features)
    return c    



def accuracy(hand):
    """
    Precision = (recommended ∩ relevant) /recommended 
    """                      
    
    send1=send(hand)
    d1,d2,d3,d4,d5=round(send1[0][2],3),round(send1[1][2],3),round(send1[2][2],3),round(send1[3][2],3), round(send1[4][2],3)
    f=[d1,d2,d3,d4,d5]

    avg=(d1+d2+d3+d4+d5)/5
    
    count=0
    for i in f:
        if i<=(avg+d5/5):
            count+=1
    
    precision=count/5

    return precision
