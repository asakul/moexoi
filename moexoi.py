'''
coding=utf-8 :

'''

import requests
import re
import datetime
from bs4 import BeautifulSoup
import argparse


class DataSource:
    def __init__(self):
        r = requests.get('http://moex.com/ru/derivatives/open-positions.aspx')
        self.viewstate = re.search(' id="__VIEWSTATE" value="([^"]*)"', r.text).group(1)
        self.viewstategenerator = re.search(' id="__VIEWSTATEGENERATOR" value="([^"]*)"', r.text).group(1)
        self.eventvalidation = re.search(' id="__EVENTVALIDATION" value="([^"]*)"', r.text).group(1)
        
    def get_raw_data(self, date, ticker):
        params = { 'ctl00$PageContent$frmInstrumList' : ticker,
               'ctl00$PageContent$frmDateTime$CDateDay' : date.day,
               'ctl00$PageContent$frmDateTime$CDateMonth' : date.month,
               'ctl00$PageContent$frmDateTime$CDateYear' : date.year,
               '__EVENTTARGET' : '',
               '__EVENTARGUMENT' : '',
               '__VIEWSTATE' : self.viewstate,
               '__VIEWSTATEGENERATOR' : self.viewstategenerator,
               '__EVENTVALIDATION' : self.eventvalidation,
               'ctl00$PageContent$frmButtom' : 'Показать'  }
        r = requests.post('http://moex.com/ru/derivatives/open-positions.aspx', data=params)
        return r.text

def parse_page(page, date):
    soup = BeautifulSoup(page, 'lxml')
    table = soup.find('table', class_='table1')
    rows = table.find_all('tr')[2:]
    s = date.strftime('%Y%m%d;')
    for row in rows:
        tds = row.find_all('td')[1:]
        for td in tds:
            s += re.sub('\s+', '', td.string) + ';'
    return s

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MOEX open interest data grabber')
    parser.add_argument('-f', '--from', dest='fromdate', action='store', required=True)
    parser.add_argument('-t', '--to', dest='todate', action='store', required=True)
    parser.add_argument('-s','--ticker', dest='ticker', action='store', required=True)
    parser.add_argument('-o', '--output', dest='output_file', action='store', required=True)
    args = parser.parse_args()  
    fromdate = datetime.datetime.strptime(args.fromdate, '%Y%m%d').date().toordinal()
    todate = datetime.datetime.strptime(args.todate, '%Y%m%d').date().toordinal()
    
    src = DataSource()
    
    out_filename = args.output_file
    if out_filename == '!':
        out_filename = args.ticker + "_" + args.fromdate + "_" + args.todate + ".csv"
    f = open(out_filename, 'w')
    f.write('DATE;PHYS_LONG_TOTAL;PHYS_SHORT_TOTAL;JUR_LONG_TOTAL;JUR_SHORT_TOTAL;TOTAL;PHYS_LONG_CHANGE;PHYS_SHORT_CHANGE;JUR_LONG_CHANGE;JUR_SHORT_CHANGE;TOTAL_CHANGE;PHYS_LONG_PCHANGE;PHYS_SHORT_PCHANGE;JUR_LONG_PCHANGE;JUR_SHORT_PCHANGE;TOTAL_PCHANGE;PHYS_ENT_LONG;PHYS_ENT_SHORT;JUR_ENT_LONG;JUR_ENT_SHORT;TOTAL_END;\n')
    for day in range(fromdate, todate + 1):
        date = datetime.date.fromordinal(day)
        print('Downloading date: ', str(date))
        f.write(parse_page(src.get_raw_data(date, args.ticker), date))
        f.write('\n')
    f.close() 
    
    