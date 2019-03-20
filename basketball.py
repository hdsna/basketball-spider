import re
import time

import requests_html
import xlsxwriter as xw
from requests.adapters import HTTPAdapter

headers = {
    'User-Agent': requests_html.user_agent(),
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh-HK;q=0.8,en-GB;q=0.6,en-US;q=0.4',
}


def create_execl(play_id, worksheet, session, starkey1):
    for p_key, pid in enumerate(play_id, start=1):
        # 框架url
        url = 'http://nba.win0168.com/cn/Tech/TechTxtLive.aspx?matchid=%s' % pid
        r = session.get(url, timeout=6)
        # ------------总比分 ----------------#
        print(url)
        match = re.search(r'(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})', r.html.find('td#headStr', first=True).text)
        datatime = match.group()
        lists= []
        for tr_key, tr_val in enumerate(r.html.find('table.t_bf > tr'),start=0):
            if(tr_key==0):
                continue
            groub = []
            for td_key, td_val in enumerate(tr_val.find('td'), start=0):
                groub.append(td_val.text)
            lists.append(groub)
        zf1 = lists[0].pop()
        zf2 = lists[1].pop()
        if(len(lists[0])==6):
            jiashicai1 = lists[0].pop()
            jiashicai2 = lists[1].pop()
            disijie1 = lists[0].pop()
            disijie2 = lists[1].pop()
            lists[0].append(int(jiashicai1)+int(disijie1))
            lists[1].append(int(jiashicai2)+int(disijie2))
        print(lists)
        lists[0].append(int(lists[0][1])+int(lists[1][1]))
        lists[0].append(int(lists[0][2])+int(lists[1][2]))
        lists[0].append(int(lists[0][3])+int(lists[1][3]))
        lists[0].append(int(lists[0][4])+int(lists[1][4]))
        lists[0].append(int(lists[0][5]) + int(lists[0][6]))
        lists[0].append(int(zf1) + int(zf2))
        #队伍
        lists[0].insert(1, lists[1][0])
        # 单双
        lists[0][2] = A1B1(int(lists[0][2]), int(lists[1][1]))
        lists[0][3] = A1B1(int(lists[0][3]), int(lists[1][2]))
        lists[0][4] = A1B1(int(lists[0][4]), int(lists[1][3]))
        lists[0][5] = A1B1(int(lists[0][5]), int(lists[1][4]))
        starkey1 = starkey1 + 1
        worksheet.write(starkey1, 0, 'NBA')
        worksheet.write(starkey1, 1, datatime)
        for kss, vales in enumerate(lists[0], start=2):
            worksheet.write(starkey1, kss, vales)
        print('完成', p_key, '场')
    return starkey1

def A1B1(num1,num2):
    sa = jioshu(num1)
    sa2 = jioshu(num2)
    if (sa==1 and sa2 ==2):
        return "A1"
    if (sa==1 and sa2 ==1):
        return "A2"
    if (sa==2 and sa2 ==1):
        return "B1"
    if (sa==2 and sa2 ==2):
        return "B2"

def jioshu(num):
    if (num % 2) == 0:
        return 2
    else:
        return 1

def regular_season(requests_date):
    with requests_html.HTMLSession() as session:
        session.headers = headers
        session.mount('http://', HTTPAdapter(max_retries=5))
        session.mount('https://', HTTPAdapter(max_retries=5))
        # 抓取的常规赛年月
        url_format = 'http://nba.win0168.com/jsData/matchResult/%s/l1_1_20%s_10.js?version=2018112112' % (
            requests_date, requests_date[:2])
        r = session.get(url_format, timeout=6)
        # 年月数据格式化
        year_month = map(lambda x: x.split(','), r.html.search('ymList = [[{}]];')[0].split('],['))
        workbook = xw.Workbook('NBA.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:A', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)
        worksheet.write(0, 0, "赛事")
        worksheet.write(0, 1, "时间")
        worksheet.write(0, 2, "队伍1")
        worksheet.write(0, 3, "队伍2")
        worksheet.write(0, 4, "第一节")
        worksheet.write(0, 5, "第二节")
        worksheet.write(0, 6, "第三节")
        worksheet.write(0, 7, "第四节")
        worksheet.write(0, 8, "第一节")
        worksheet.write(0, 9, "第二节")
        worksheet.write(0, 10, "第三节")
        worksheet.write(0, 11, "第四节")
        worksheet.write(0, 12, "半场")
        worksheet.write(0, 13, "全场")

        starkey1 = 0
        for ym in year_month:
            # if ym == ['2018', '12']:
            #     return 0
            # 新建excel format: year - month.xlsx
            url = 'http://nba.win0168.com/jsData/matchResult/%s/l1_1_%s_%s.js?version=2018112112' % (
                requests_date, ym[0], ym[1])
            r = session.get(url, timeout=6)
            # 该年月的比赛id
            play_id = map(lambda x: x.split(',')[0], r.html.search('arrData = [[{}]];')[0].split('],['))
            play_id = list(play_id)
            # 当前场次后无数据 截取list
            # if ym == ['2018', '11']:
            #     play_id = play_id[:play_id.index('325827')]
            # 新建工作薄
            starkey1 = create_execl(play_id, worksheet, session, starkey1)
            # 关闭保存
            print('完成', ym[0], ym[1])
        workbook.close()


def playoffs(requests_date):
    with requests_html.HTMLSession() as session:
        session.headers = headers
        session.mount('http://', HTTPAdapter(max_retries=5))
        session.mount('https://', HTTPAdapter(max_retries=5))
        # 抓取季度数据
        r = session.get('http://nba.win0168.com/jsData/matchResult/%s/l1_2.js?version=2018112122' % requests_date,
                        timeout=6)
        # 季度数据格式化
        quarter = list(map(lambda x: x.split(',')[0],
                           re.split(",\[\[|[0-9]\],\[", r.html.search(",[[{}var")[0])))
        # 新建excel format: year - month.xlsx
        workbook = xw.Workbook(requests_date + '季后赛.xlsx')
        # 该年月的比赛id
        play_id = quarter
        create_execl(play_id, workbook, session)
        # 关闭保存
        workbook.close()
        print('完成', requests_date)


if __name__ == '__main__':
    dict_date = ['16-17', '17-18']
    for date in dict_date:
        regular_season(date)
    dict_date = ['16-17', '17-18', '18-19']
    # for date in dict_date:
    #     pass
    # playoffs(date)
    # regular_season()
