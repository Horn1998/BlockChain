from selenium import webdriver
import time
import csv
driver_path = r'C:\Users\Horn\Desktop\chromedriver.exe'

header = ['日期', '星期', '最高气温', '最低气温', '天气', '风向', '风级']
months = ['01', '02', '03', '04', '05', '07', '08', '09', '10', '11', '12']
years = ['2016']
base = 'https://lishi.tianqi.com/zhangjiakou/'
def run():
    for year in years:
        for month in months:
            driver = webdriver.Chrome(executable_path=driver_path)
            url = base + year + month + '.html'
            driver.get(url)
            driver.find_element_by_class_name('lishidesc2').click()
            content = driver.find_element_by_class_name('thrui').text
            with open('2016weather.csv', 'a+', newline='') as f:
                csv_file = csv.writer(f)
                # csv_file.writerow(header)
                datas, row = [], []
                for items in content.split(' '):
                    for item in items.split('\n'):
                     datas.append(item)
                for index, item in enumerate(datas):
                    if (index + 1) % 7 == 0:
                        row.append(item)
                        csv_file.writerow(row)
                        row = []

                    else:
                        row.append(item)
            time.sleep(4)
            driver.close()

if __name__ == '__main__':
    run()


