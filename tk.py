import tkinter as tk
import tkinter.messagebox as mb
import  requests
import re
import json
import threading
import os

header = {
    "User-Agent": "Mozilla/5.0",
}

VideoList = []
origin = os.getcwd()

def getVideoListInfo(bvid):
    global VideoList
    VideoList = []
    url = f'https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp'
    djson = requests.get(url, headers=header).json()

    for data in djson['data']:
        VideoList.append({
            "cid": data['cid'],
            "base_url": f"https://www.bilibili.com/video/{bvid}?p=" + str(data["page"]),
            "name": data["part"],
        })

def getVideoAddrInfo():
    for item in VideoList:
        html = requests.get(item['base_url'] , headers=header).text
        result =re.findall("<script>window.__playinfo__=(.*?)</script>" , html)[0]
        result_json = json.loads(result)
        try:
            item["videoUrl"] = result_json['data']['dash']['video'][0]['baseUrl']
            item["audioUrl"] = result_json['data']['dash']['audio'][0]['baseUrl']
        except:
            mb.showerror("错误","没有找到音频或视频地址")

def getDownloadM4s(durl , name ,path):
    header = {
        "User-Agent": "Mozilla/5.0",
        "accept": "*/*",
        "access-control-request-headers": "range",
        "access-control-request-method": "GET",
        "origin": "https://www.bilibili.com",
        "referer": "https://www.bilibili.com/",
        "if -range": "f2693eb5487ba163e2b301b2df304b7c",
    }
    get = requests.get(durl, headers=header)
    header["range"] = "bytes:0-" + str(get.headers["Content-Length"])
    req = requests.get(durl , headers = header , stream= True)
    with open(origin+path +"/" + name + ".m4s" , "wb") as f:
        f.write(req.content)

def videoCompose():
    allm4s = os.listdir(origin+"\\audio")
    for i in allm4s:
        audiopath = os.path.join(origin+"\\audio",i)
        videopath = os.path.join(origin+"\\video", i)
        # print("视频路径："+videopath)
        # print(audiopath)
        command = rf"ffmpeg -i {videopath} -i {audiopath} {origin}\{i[:-4]}.mp4"
        os.system(command)
        os.remove(audiopath)
        os.remove(videopath)
        # print(i[:-4] ,"转换完成")

if __name__ == '__main__':
    window = tk.Tk()
    window.title("bilibli视频下载工具by260245435")
    window.geometry("500x600")

    videoInfo = {
        "page":0,
        "pagesize":0,
        "numResults":0,
        "numPages":0,
        "list":[]
    }

    Frame1 = tk.Frame(window)
    Frame1.pack(side="top")
    ent_search = tk.Entry(Frame1,show=None)
    ent_search.pack(side="left")

    def search():
        header = {
            "User-Agent": "Mozilla/5.0",
        }
        # print(ent_search.get())
        if not ent_search.get():
            mb.showerror("错误","请输入搜索内容")
        else:
            url = f'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={ent_search.get()}'
            result = requests.get(url=url , headers=header).json()
            videoInfo["page"] = result["data"]["page"]
            videoInfo["pagesize"] = result["data"]["pagesize"]
            videoInfo["numResults"] = result["data"]["numResults"]
            videoInfo["numPages"] = result["data"]["numPages"]
            videoInfo["list"] = []
            listbox.delete(0,"end")
            for i in result["data"]["result"]:
                videoInfo["list"].append(i)
            for i in videoInfo["list"]:
                # print(i["title"])
                listbox.insert("end", i["bvid"]+": "+i["title"])

    def download():
        if not os.path.exists(origin + r"\audio"):
            os.mkdir(origin + r"\audio")
        if not os.path.exists(origin + r"\video"):
            os.mkdir(origin + r"\video")
        down_data = listbox.get("active")
        if not down_data:
            mb.showerror("错误","当前未选中数据")
        else:
            bvid = down_data.split(":")[0]
            # print(bvid)

            getVideoListInfo(bvid)
            print("120:",VideoList)
            getVideoAddrInfo()

            for item in VideoList:
                t1 = threading.Thread(target=getDownloadM4s,
                                      kwargs={"durl": item["audioUrl"], "name": item["name"].replace(" " , "_"), "path": "\\audio"})
                t2 = threading.Thread(target=getDownloadM4s,
                                      kwargs={"durl": item["videoUrl"], "name": item["name"].replace(" " , "_"), "path": "\\video"})
                t1.start()
                t2.start()
                t1.join()
                t2.join()

            videoCompose()
            mb.showinfo("成功","转换完成")

    btn_search = tk.Button(Frame1,text="搜索",command=search).pack(side="left")
    btn_download = tk.Button(Frame1,text="下载",command=download).pack(side="right")
    view_scroll = tk.Scrollbar(window)
    view_scroll.pack(side="right", fill="y")
    listbox = tk.Listbox(window, yscrollcommand=view_scroll.set , width=400 , height=500 , selectmode="single")

    listbox.pack()
    view_scroll.config(command = listbox.yview)
    window.mainloop()

