"""从人人网爬取大物实验报告图片"""
import requests
from bs4 import BeautifulSoup
import os
from selenium import webdriver
import time

def Realimg(imgsrc):
    """从具体的src中提取二进制图片文件
    eachimgurl举例: http://page.renren.com/601069586/channel-photoshow-7
    783286393#7783286393"""
    # res = requests.get(imgsrc)
    # soup = BeautifulSoup(res.text, "html.parser")
    # arr = soup.select("#photo-main")
    # realimgurl = arr[0].attrs['src']
    return requests.get(imgsrc).content


def Album_urls():
    """得到相册们的链接 返回类型dict{相册名称：相册url}"""
    album_urls_dict = {}
    mom_url = "http://page.renren.com/601069586/channel-albumlist?curpage="
    for pagenum in range(5):
        page_url = mom_url + str(pagenum)
        res = requests.get(page_url)
        soup = BeautifulSoup(res.text, "html.parser")
        arr = soup.select(".album-item a")
        for album in arr:
            title = album.attrs["alt"].strip("哈工程实验报告的").strip("相册")
            href = album.attrs["href"]
            album_url = "http://page.renren.com/601069586/" + href
            album_urls_dict[title] = album_url
    return album_urls_dict


def Imgs(ablum_url, chrome):
    """
    给我一个相册的链接 return所有图片二进制文件组成的列表
    基本思想是：
        1.打开相册主页
        2.获取所有图片的url
        3.分别访问每个图片url 获取src 并下载之
    参数举例：ablum_url:"http://page.renren.com/601069586/channel-albumshow-1001655849"
    """
    # 1.打开相册主页
    chrome.get(ablum_url)
    # 2.获取所有图片的url
    # all_a是含有若干标签a的数组 a中有href 即图片所在url
    all_a = chrome.find_elements_by_xpath('//*[@id="photos"]/div[4]/ul/li/a')
    imgs = []
    # 3.分别访问每个图片url

    # 为避免“元素失效”，先把所有的图片url集中提取出来 再逐个访问（而不是边访问边解析）
    imgurls = []
    for a in all_a:
        eachimgurl = a.get_attribute("href")
        imgurls.append(eachimgurl)
    for eachimgurl in imgurls:
        chrome.get(eachimgurl)
        # 得到图片的二进制文件所在地址src
        imgsrc = chrome.find_element_by_xpath('//*[@id="photo-main"]').get_attribute("src")
        # 得到二进制图片本体
        realimg = Realimg(imgsrc)
        # 将二进制文件放进数组中
        imgs.append(realimg)

    return imgs


if __name__ == '__main__':
    # 所有相册的url
    album_urls = Album_urls()
    Pathmain = "C:\\Users\\15517\\Desktop\\大物实验报告\\"
    # 对每个相册进行下载
    chrome = webdriver.Chrome()        
    for album_title in album_urls:
        album_url = album_urls[album_title]
        Pathalbum = Pathmain + album_title
        # 为每个相册新建一个文件夹 如果已经存在 就跳过
        if os.path.exists(Pathalbum) is False:
            os.makedirs(Pathalbum) 
        # 得到图片的二进制文件
        imgs = Imgs(album_url, chrome)
        print("正在保存相册《"+album_title+"》")
        for i in range(len(imgs)):
            eachimg = imgs[i]    
            Pathimg = Pathalbum + "\\" + str(i) + ".jpg"
            imgfile = open(Pathimg, "wb")
            imgfile.write(eachimg)
            imgfile.close()
            print("保存图片%d" % i)
    chrome.close()

    print("搞定")