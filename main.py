import json
import tkinter as tk
import tkinter.colorchooser
from PIL import Image,ImageFont,ImageDraw
from aip import AipSpeech
import os
import sys
import cv2
import eyed3
from moviepy.editor import VideoFileClip,AudioFileClip,CompositeAudioClip,concatenate_videoclips

# 加载配置
def load_setting():

    global setting

    print('读取配置文件')
    setting_json=_read("setting.json")
    if (setting_json):
        setting=json.loads(setting_json)

# 保存配置
def save_setting():

    setting['name_color']['R']=name_color_r.get()
    setting['name_color']['G']=name_color_g.get()
    setting['name_color']['B']=name_color_b.get()
    setting['text_color']['R']=text_color_r.get()
    setting['text_color']['G']=text_color_g.get()
    setting['text_color']['B']=text_color_b.get()
    setting['text_len']=text_len.get()
    setting['APP_ID']=APP_ID.get()
    setting['API_KEY']=API_KEY.get()
    setting['SECRET_KEY']=SECRET_KEY.get()

    with open("setting.json",'w') as f:
        f.write(json.dumps(setting,indent=4, separators=(',', ': ')))
    print("配置保存成功")

# 清理残留文件
def _clear():

    print('清理上次残留文件')
    if(os.path.exists("frame")):
        for i in os.listdir("frame"):
            os.remove("frame/"+i)
    else:
        os.mkdir("frame")

    if(os.path.exists("sound")):
        for i in os.listdir("sound"):
            os.remove("sound/"+i)
    else:
        os.mkdir("sound")

    if(os.path.exists("video")):
        for i in os.listdir("video"):
            os.remove("video/"+i)
    else:
        os.mkdir("video")

# 文件读取
def _read(path):

    try:
        f=open(path,"r",encoding="utf-8")
        x=f.read()
        f.close()
        return x
    except:
        print('读取'+path+'失败')
        return 0

# 颜色选择
def choose_color(flag):

    a1 = tkinter.colorchooser.askcolor(color='red', title='选择字体颜色')

    if flag:
        text_color_r.set(int(a1[0][0]))
        text_color_g.set(int(a1[0][1]))
        text_color_b.set(int(a1[0][2]))
    else:
        name_color_r.set(int(a1[0][0]))
        name_color_g.set(int(a1[0][1]))
        name_color_b.set(int(a1[0][2]))

# 逐帧合成
def create_frame(num,name,text):

    # 立绘
    try:
        character= Image.open("img/"+name+".png")
    except:
        if(name=="kp"):
            character = Image.open("img/default/kp.png")
        else:
            character = Image.open("img/default/pc.png")

    # 背景
    try:
        bg= Image.open("img/bg.jpg")
    except:
        bg= Image.open("img/default/bg.jpg")

    bg=bg.resize((1920,1080),Image.BILINEAR)
    bg_x,bg_y=bg.size

    sound_jdg=0
    
    # 语音合成
    client = AipSpeech(setting["APP_ID"], setting["API_KEY"], setting["SECRET_KEY"])
    try:
        result = client.synthesis(text,'zh', 1,setting['character'][name])
    except: 
        result = client.synthesis(text,'zh', 1)

    if not isinstance(result, dict):
        with open('sound/'+str(num)+'.mp3', 'wb') as f:
            f.write(result)
    else:
        print("语音合成出错")
        sys.exit()
        
    # 对话框大小调整
    dialog= Image.open("img/default/dialog.png")
    dialog=dialog.resize((1920,277),Image.BILINEAR)
    dialog_x,dialog_y=dialog.size
    
    # 字体
    name_font=ImageFont.truetype('simhei.ttf',45)
    text_font=ImageFont.truetype('simhei.ttf',33)

    # 立绘大小调整
    character=character.resize((500,800),Image.BILINEAR)
    character_x,character_y=character.size

    # 画布（背景+立绘+对话框渲染）
    graph=bg
    try:
        graph.paste(character,(0,280),mask=character.split()[3])
    except:
        graph.paste(character,(0,280))
    graph.paste(dialog,(0,803),mask=dialog.split()[3])

    draw=ImageDraw.Draw(graph)

    # 角色名渲染
    name_color=tuple(setting['name_color'].values())
    draw.text((360,815),name,name_color,font=name_font)
    
    # 文本渲染
    text_len=36
    if(len(text)>=text_len):
        text0=[]
        numn=int(len(text)/text_len)+1
        for i in range(numn):
            if((i+1)*text_len>len(text)-1):
                text0.append(text[i*text_len:])
            else:
                text0.append(text[i*text_len:(i+1)*text_len])
        text=text0
    else:
        text=[text]
    text_color=tuple(setting['text_color'].values())
    for i in range(len(text)):
        draw.text((400,880+i*50),text[i],text_color,font=text_font)

    # 保存图片
    graph.save("frame/"+str(num)+".jpg")

# 视频合成
def create_video(len_list):
    fourcc=cv2.VideoWriter_fourcc("D","I","V","X")
    img=cv2.imread("frame/0.jpg")
    imgInfo = img.shape
    size = (imgInfo[1],imgInfo[0])
    video=cv2.VideoWriter("video/video.avi",fourcc,1,size)
    num=len(len_list)
    for i in range(num):
        img=cv2.imread("frame/"+str(i)+".jpg")
        for j in range(len_list[i]):
            video.write(img)
    video.release()

# 添加音频
def audio_add(len_list):
    video = VideoFileClip('video/video.avi')
    result=[]
    for i in range(len(len_list)):
        if(i!=0):
            video_=video.subclip(sum(len_list[0:i]),sum(len_list[0:i])+len_list[i])
            print([sum(len_list[0:i]),sum(len_list[0:i])+len_list[i]])
        else:
            video_=video.subclip(0,len_list[i])
        audio=AudioFileClip("sound/"+str(i)+".mp3")
        video_=video_.set_audio(audio)
        subvideo=video_
        subvideo.write_videofile("video/zc"+str(i)+".avi",codec="png")
        #result.append(subvideo)
    #print(len(result))
    #result=concatenate_videoclips(result)
    #result.write_videofile("video/result.avi",codec="png")

# 无GUI生成
def pure_generate():

    _clear()
    save_setting()

    text=_read("log.txt")
    if(not(text)):sys.exit()

    # 分割文本
    try:
        text=text.split("\n\n")
        num=len(text)
        for i in range(num):
            text[i]=text[i].split("\n")
    except:
        print("log.txt格式错误")
        sys.exit()

    # 逐帧合成
    print("开始合成，一共有"+str(num)+"帧")
    for i in range(num):
        print("开始合成第"+str(i+1)+"帧")
        create_frame(i,text[i][0],text[i][1])

    #填充len_list
    len_list=[]
    for i in range(num):
        voice_file = eyed3.load("sound/"+str(i)+".mp3")
        secs = voice_file.info.time_secs
        secs=int(secs)+1
        len_list.append(secs)
    
    create_video(len_list)

    print("视频合成完成，开始添加音轨")

    audio_add(len_list)

    print("合成成功")

if __name__== '__main__':

    gui_flag=1

    load_setting()

    if gui_flag:

        root=tk.Tk()

        name_color_r=tk.IntVar()
        name_color_r.set(setting['name_color']['R'])
        name_color_g=tk.IntVar()
        name_color_g.set(setting['name_color']['G'])
        name_color_b=tk.IntVar()
        name_color_b.set(setting['name_color']['B'])

        text_color_r=tk.IntVar()
        text_color_r.set(setting['text_color']['R'])
        text_color_g=tk.IntVar()
        text_color_g.set(setting['text_color']['G'])
        text_color_b=tk.IntVar()
        text_color_b.set(setting['text_color']['B'])

        text_len=tk.IntVar()
        text_len.set(setting['text_len'])

        APP_ID = tk.StringVar()
        APP_ID.set(setting['APP_ID'])
        API_KEY = tk.StringVar()
        API_KEY.set(setting['API_KEY'])
        SECRET_KEY = tk.StringVar()
        SECRET_KEY.set(setting['SECRET_KEY'])

        l1=tk.Label(root,text="角色名颜色")
        l1.place(x=20,y=10)
        l11=tk.Label(root,text="R",width=2)
        l11.place(x=10,y=40)
        l12=tk.Label(root,text="G",width=2)
        l12.place(x=60,y=40)
        l13=tk.Label(root,text="B",width=2)
        l13.place(x=110,y=40)

        e11=tk.Entry(root,width=4,textvariable=name_color_r)
        e12=tk.Entry(root,width=4,textvariable=name_color_g)
        e13=tk.Entry(root,width=4,textvariable=name_color_b)
        e11.place(x=30,y=40)
        e12.place(x=80,y=40)
        e13.place(x=130,y=40)

        b1=tk.Button(root,text="选择颜色",command=lambda:choose_color(0))
        b1.place(x=100,y=5)

        l2=tk.Label(root,text="文字颜色")
        l2.place(x=220,y=10)
        l21=tk.Label(root,text="R",width=2)
        l21.place(x=210,y=40)
        l22=tk.Label(root,text="G",width=2)
        l22.place(x=260,y=40)
        l23=tk.Label(root,text="B",width=2)
        l23.place(x=310,y=40)

        e21=tk.Entry(root,width=4,textvariable=text_color_r)
        e22=tk.Entry(root,width=4,textvariable=text_color_g)
        e23=tk.Entry(root,width=4,textvariable=text_color_b)
        e21.place(x=230,y=40)
        e22.place(x=280,y=40)
        e23.place(x=330,y=40)

        b2=tk.Button(root,text="选择颜色",command=lambda:choose_color(1))
        b2.place(x=300,y=5)

        l3=tk.Label(root,text="每行文字数")
        l3.place(x=440,y=10)
        e3=tk.Entry(root,width=10,textvariable=text_len)
        e3.place(x=430,y=40)

        #语音合成参数
        l4=tk.Label(root,text="APP_ID")
        l4.place(x=10,y=70)
        e4=tk.Entry(root,width=55,textvariable=APP_ID)
        e4.place(x=120,y=70)

        l5=tk.Label(root,text="API_KEY")
        l5.place(x=10,y=100)
        e5=tk.Entry(root,width=55,textvariable=API_KEY)
        e5.place(x=120,y=100)

        l6=tk.Label(root,text="SECRET_KEY")
        l6.place(x=10,y=130)
        e6=tk.Entry(root,width=55,textvariable=SECRET_KEY)
        e6.place(x=120,y=130)

        # 底部按钮
        b3=tk.Button(root,text="重载配置",command=load_setting)
        b3.place(x=280,y=400)

        b4=tk.Button(root,text="保存配置",command=save_setting)
        b4.place(x=350,y=400)

        b5=tk.Button(root,text="开始生成",command=pure_generate)
        b5.place(x=420,y=400)

        root.geometry('520x440')
        root.title("跑团自动视频生成")
        root.mainloop()
    else:
        pure_generate()
