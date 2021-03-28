for year in range(2011, 2019):
    for month in range(1, 13):
        if month == 12 and year > 2016:
            month = "%.2d".format() % month
            url = "http://tianqi.2345.com/t/wea_history/js/" + str(year) + str(month) + "/56294_" + str(year) + str(
                month) + ".js"
        else:
            url = "http://tianqi.2345.com/t/wea_history/js/56294_" + str(year) + str(month) + ".js"
        print(url)
        getData(url)