# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 16:45:45 2017

@author: Venkata Praveen Dusi
"""
'''edited to split author name and address.'''

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import re
import time
import numpy as np
from collections import OrderedDict
import json


outer_dict=OrderedDict()

'''Looping with urls:'''
url = 'http://pubsonline.informs.org/toc/isre/'
v = 1
while v<29:
    url_n = url +str(v)+'/'
    count = 1
    while count<5:
        url_n1 = url_n + str(count)
        print('now scrapping data from : ', url_n1)

        driver = webdriver.Chrome("C:/Users/Venkata Praveen Dusi/Documents/chromedriver.exe")


        try:
            driver.get(url_n1)
            checkbox = driver.find_element_by_xpath("//input[@name='markall']")
            if not checkbox.is_selected():
                checkbox.click()
            driver.find_element_by_partial_link_text('View Abstracts').click()

            current_url=driver.current_url

            page = requests.get(current_url)
            soup = BeautifulSoup(page.content, 'html.parser')

            '''#Section Info'''
            section_info = []
            section_info_s = []
            section_info = driver.find_elements_by_class_name('sectionInfo')
            for s in section_info:
                 section_info_s.append(s.text)
            del section_info_s[1::2]



            ''' #Article Titles'''
            arttitle = []
            arttitle_s = []
            arttitle = driver.find_elements_by_class_name('arttitle')
            for title in arttitle:
                arttitle_s.append(title.text)








            '''#Abstract'''
            abstract = []
            abstract_s = []
            abstract = driver.find_elements_by_class_name('abstractSection')
            for a in abstract:
                 abstract_s.append(a.text)




            '''#KeyWords'''

            keywords=[]
            a_tags = soup.find_all("div",class_="abstractKeywords")
            for a in a_tags:
                keywords.append(a.text)


            '''# Create a function called "chunks" with two arguments, l and n:'''
            def chunks(l, n):
                # For item i in a range that is a length of l,
                for i in range(0, len(l), n):
                    # Create an index range for l of n items:
                    yield l[i:i+n]

            keywords1=list(chunks(keywords,1))

            for i in range(0,len(keywords1)):
                new=keywords1[i][0].split(';')[:]
                try:
                    new[0] = new[0].split(':')[1]
                except IndexError:
                    pass
                keywords1[i] = new



            num_articles = len(keywords1)
            print('number of articles : ',num_articles )



            ''' #Authors'''
            lst = []
            a_tags = soup.h1.find_all_next('span')
            for a in a_tags:
                lst.append(a.text)

            from itertools import groupby

            aut=[list(group) for k, group in groupby(lst, lambda x: ((x == 'Keywords') or (x=='Key Words'))) if not k]
            len(aut)


            for l in aut:
                del l[1::2]

            aut = aut[0:num_articles]

            for i in range(0,len(aut)):


                for j in range(0,len(aut[i])):

                    try:
                        combined=re.findall(re.compile(r'\w*[A-Z]\w*[A-Z]\w*'), aut[i][j])
                        first_name = aut[i][j].split(combined[0])[0]
                        last_name = re.findall('[A-Z][^A-Z]*', combined[0])[0]
                        address = re.findall('[A-Z][^A-Z]*', combined[0])[1] +aut[i][j].split(combined[0])[1]
                        aut[i][j] = [first_name+last_name,address]

                    except:
                        pass




            '''Create dictionary and push all the values  '''
            key = ['year','volume','issue','title','authors','keywords','abstract']


            for i in range(0,len(keywords1)):
                inner_dict =OrderedDict()
                outer_key=url_n1.split('isre/')[1] + '/' + "article%d" % (i+1)
                outer_dict[outer_key] = inner_dict
                try:
                    inner_dict[key[0]]=section_info_s[0].split(',')[2].split(' ')[2]


                except IndexError:
                            pass

                try:
                    inner_dict[key[1]] =section_info_s[0].split(',')[1].split(' ')[2]

                except IndexError:
                            pass

                try:
                    inner_dict[key[2]] =section_info_s[0].split(',')[1].split(' ')[4]

                except IndexError:
                    pass

                try:
                    inner_dict[key[3]]=arttitle_s[i]

                except IndexError:
                    pass

                try:
                    inner_dict[key[4]]=aut[i]

                except IndexError:
                    pass

                try:
                    inner_dict[key[5]]=keywords1[i]

                except IndexError:
                    pass

                try:
                    inner_dict[key[6]]=abstract_s[i]

                except IndexError:
                    pass






        except NoSuchElementException:
            print(driver.current_url,' this page no longer exists')

        print('all articles appended')
        time.sleep(np.random.randint(5,8))
        count = count+1
        driver.close()
    v = v + 1

'''create json with output it to file '''
with open('full.json','w') as outfile:
    json.dump(outer_dict, outfile)
