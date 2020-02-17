# -*- coding: utf-8 -*-
from tqdm import tqdm
import time
from bs4 import BeautifulSoup
import pandas as pd

import requests

def numStr(num):
    if num >= 10:
        return str(num)
    else:
        return '0' + str(num)

def scraping():
    Base = "http://race.sp.netkeiba.com/?pid=race_result&race_id="
    dst = ''
    df_col = ['year', 'date', 'field', 'race', 'race_name'
              , 'course', 'head_count', 'rank', 'horse_name'
              , 'gender', 'age', 'trainerA', 'trainerB', 'weight', 'c_weight', 'jackie', 'j_weight'
              , 'odds','popu']
    df = pd.DataFrame()    

    for year in tqdm(range(2020, 2021)): # 年
        for i in tqdm(range(5, 6)): # 場所 札幌:01 函南:02 福島:03 新潟:04 東京:05 中山:06 中京:07 京都:08 阪神:09 小倉:10
            for j in tqdm(range(1, 2)): # レース月
                for k in tqdm(range(1, 30)):# レース日
                    for l in range(1, 2): # レース番号
                        time.sleep(1)
                        url = f'{Base}{year}{i:02}{j:02}{k:02}{l:02}'
                        html = requests.get(url)
                        html.encoding = 'EUC-JP'
                        soup = BeautifulSoup(html.text, 'html.parser')
                        if soup.find_all('div', attrs={'class', 'Result_Guide'})!=[]:
                            break
                        else:
                            CommonYear = year
                            CommonDate = soup.find_all('div', attrs={'class', 'Change_Btn Day'})[0].string.strip()
                            CommonField= soup.find_all('div', attrs={'class', 'Change_Btn Course'})[0].string.strip()
                            CommonRace = soup.find_all('div', attrs={'Race_Num'})[0].span.string
                            CommonRname= soup.find_all('dt', attrs={'class', 'Race_Name'})[0].contents[0].strip()
                            CommonCourse= soup.find_all('dd', attrs={'Race_Data'})[0].span.string
                            CommonHcount= soup.find_all('dd', attrs={'class', 'Race_Data'})[0].contents[3].split()[1]    

                            for m in range(len(soup.find_all('div', attrs='Rank'))):
                                dst = pd.Series(index=df_col)
                                try:
                                    dst['year'] = CommonYear
                                    dst['date'] = CommonDate
                                    dst['field']= CommonField
                                    dst['race'] = CommonRace
                                    dst['race_name'] = CommonRname
                                    dst['course'] = CommonCourse
                                    dst['head_count'] = CommonHcount
                                    dst['rank'] = soup.find_all('div', attrs='Rank')[m].contents[0]
                                    dst['horse_name'] = soup.find_all('dt', attrs=['class', 'Horse_Name'])[m].a.string
                                    detailL = soup.find_all('span', attrs=['class', 'Detail_Left'])[m]
                                    dst['gender'] = list(detailL.contents[0].split()[0])[0]
                                    dst['age'] = list(detailL.contents[0].split()[0])[1]
                                    dst['trainerA'] = detailL.span.string.split('･')[0]
                                    dst['trainerB'] = detailL.span.string.split('･')[1]
                                    if len(detailL.contents[0].split())>=2:
                                        dst['weight'] = detailL.contents[0].split()[1].split('(')[0]
                                        if len(detailL.contents[0].split()[1].split('('))>=2:
                                            dst['c_weight'] = detailL.contents[0].split()[1].split('(')[1].strip(')')
                                    detailR = soup.find_all('span', attrs=['class', 'Detail_Right'])[m].contents
                                    if  "\n" in detailR or "\n▲" in detailR or '\n☆' in detailR:
                                        detailR.pop(0)
                                    dst['jackie'] = detailR[0].string.strip()
                                    dst['j_weight'] = detailR[2].strip().replace('(', '').replace(')', '')
                                    Odds = soup.find_all('td', attrs=['class', 'Odds'])[m].contents[1]
                                    if Odds.dt.string is not None:
                                        dst['odds'] = Odds.dt.string.strip('倍')
                                        dst['popu'] = Odds.dd.string.strip('人気')
                                except:
                                    pass
                                dst.name = str(year) + numStr(i) + numStr(j) + numStr(k) + numStr(l) + numStr(m)    

                                df = df.append(dst)

    df.to_csv('{0}.csv'.format(time.strftime("%Y%m%d%H%M%S")), encoding='utf-8') 

scraping()
