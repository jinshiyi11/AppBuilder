#coding=UTF-8
'''
Created on 2013-4-24

'''

import argparse
import os
import sys
import shutil 
import xml.etree.ElementTree
from xml.etree.ElementTree import ElementTree
import Util

KEY_DIR="../MyAppKey/"

class BuildInfo(object):
    '''
    productName 产品名根据该字段生成备份路径
    manualVersion AndroidManifest.xml中versionName的前3位版本号(第四位由打包脚本自动生成,表示打包次数)
    buildCount 对应versionCount(表示打包次数)
    autoPartVersion versionName的第四位版本号(第四位由打包脚本自动生成)
    updateVersion 本次编译是否更新版本号,默认为True
    channel 渠道号，对应AndroidManifest.xml文件中的UMENG_CHANNEL，用于通过友盟统计安装渠道
    '''
    def __init__(self):
        self.backupRootDir="E:/backup/"
        self.appRootDir=""
        self.productName=""
        self.manualVersion=""
        self.buildCount=1
        self.updateVersion=True
        self.channel=""
        self.isYoumengChannel=False
        self.autoPartVersion=1
    
    def getProductVersion(self):
        "返回产品的4位版本号，如1.1.1.1"
        #return self.manualVersion+"."+str(self.autoPartVersion)
        return "%s.%04d" % (self.manualVersion,self.autoPartVersion)
        
    def getProductBackupDir(self):
        "z:/backup-xxx/"
        return self.backupRootDir+"backup-"+self.productName+"/"
        
    def getBaseBackupDir(self):
        "z:/backup-xxx/1.1.1/"
        return self.backupRootDir+"backup-"+self.productName+"/"+self.manualVersion+"/"
    def getBackupDir(self):
        "z:/backup-xxx/1.1.1/1.1.1.1/"
        return self.getBaseBackupDir()+"/"+self.getProductVersion()+"/"


info=BuildInfo()

def initVersion():
    "初始化版本号"
    mainfestPath=info.appRootDir+"/AndroidManifest.xml"
    if not os.path.exists(mainfestPath):
        sys.exit("AndroidManifest.xml文件不存在:"+mainfestPath)
    

    xml.etree.ElementTree.register_namespace("android","http://schemas.android.com/apk/res/android")
    tree = ElementTree()   
    xmlRoot=tree.parse(mainfestPath)
    versionName=xmlRoot.get("{http://schemas.android.com/apk/res/android}versionName")
    versionCode=xmlRoot.get("{http://schemas.android.com/apk/res/android}versionCode")
    print "versionName:"+versionName
    vers=versionName.split(".")
    if len(vers)<3:
        sys.exit("AndroidManifest.xml文件:"+mainfestPath+"中的versionName格式不正确:"+versionName)
    
    info.manualVersion=vers[0]+"."+vers[1]+"."+vers[2]
    baseBackupDir=info.getBaseBackupDir()
    if not os.path.exists(baseBackupDir):
        os.makedirs(baseBackupDir)
    #获取buildCount
    buildCountFilePath=info.getProductBackupDir()+info.productName+".count"
    if not os.path.exists(buildCountFilePath):
        #创建buildCount文件
        f=open(buildCountFilePath,'a+')
        f.write("buildCount="+str(info.buildCount))
        f.write("autoPartVersion="+str(info.autoPartVersion))
        f.close()
    else:
        #读取buildCount文件并更新buildCount
        globalData={}
        execfile(buildCountFilePath,globalData)
        info.buildCount=globalData['buildCount']
        if info.updateVersion:
            info.buildCount=info.buildCount+1
            info.autoPartVersion=info.autoPartVersion+1
            f=open(buildCountFilePath,'w+')
            f.write("buildCount="+str(info.buildCount))
            f.write("autoPartVersion="+str(info.autoPartVersion))
            f.close()
        
    #创建当前版本的备份目录
    if not os.path.exists(info.getBackupDir()):
        os.makedirs(info.getBackupDir())
    
    #使用buildCount作为versionCode
    versionCode=info.buildCount
    #输出log，通知邮件会从中提取信息
    print "file version:%s"%info.getProductVersion()
    print "product version:%s"%info.getProductVersion()
    print "version code:%s"%versionCode
    #TODO:save xml
    #更新AndroidManifest.xml文件的versionName字段
    xmlRoot.set("{http://schemas.android.com/apk/res/android}versionName",info.getProductVersion())
    xmlRoot.set("{http://schemas.android.com/apk/res/android}versionCode",str(versionCode))
    #更新AndroidManifest.xml文件的UMENG_CHANNEL字段，用于统计安装渠道
    # if info.isYoumengChannel:
        # print "using Youmeng channel"
        # channelNode=tree.find("./application/meta-data[@{http://schemas.android.com/apk/res/android}name='UMENG_CHANNEL']")
        # channelNode.set("{http://schemas.android.com/apk/res/android}value",info.channel)
    # else:
        # channelFilePath=info.appRootDir+"/assets/channel_id.txt"
        ##先把老文件删除
        # if os.path.exists(channelFilePath):
            # os.remove(channelFilePath)
        # f=open(channelFilePath,'w+')
        # f.write(info.channel)
        # f.close()
         
    #tree.write(mainfestPath, "UTF-8", True, "http://schemas.android.com/apk/res/android") 
    tree.write(mainfestPath, "UTF-8", True)
    
    #因为修改过AndroidManifest.xml文件，所以备份一下该文件看看修改有没有问题
    shutil.copy(mainfestPath,info.getBackupDir())
    
def generateAntProperties(productName):
    '''
    因为安全原因，签名文件只在本地保存，不在svn上保存,这个函数用来从本地文件生成ant.properties,该文件指定签名信息
    '''
    keypath=KEY_DIR+productName+".py"
    keyInfo=Util.load_module(keypath)
    
    
    filePath=info.appRootDir+"/ant.properties"
    print "开始删除ant.properties:"+filePath
    if os.path.exists(filePath):
        os.remove(filePath)
    print "正在生成ant.properties"
    f=open(filePath,'w+')
    f.write("key.store=%s\r\n" % keyInfo.KEY_STORE_FILE_PATH)
    f.write("key.alias=%s\r\n" % keyInfo.ALIAS_NAME)
    f.write("key.store.password=%s\r\n" % keyInfo.STORE_PASS)
    f.write("key.alias.password=%s\r\n" % keyInfo.KEY_PASS)
    f.close()

import subprocess        
def startBuild():
    '执行编译操作'
    #subprocess.check_call(["dir","/A"],shell=True)
    subprocess.check_call(["ant","clean" ,"release"],shell=True,cwd=info.appRootDir)
    #subprocess.check_call(["ant","release"])
  
def backupFiles():
    '备份生成的apk和proguard相关文件'
    if info.channel:
        print "channel:"+info.channel
        shutil.copy(info.appRootDir+"/bin/"+info.productName+"-release.apk",info.getBackupDir()+info.productName+"_"+info.channel+".apk")
    else:
        shutil.copy(info.appRootDir+"/bin/"+info.productName+"-release.apk",info.getBackupDir()+info.productName+".apk")

    if os.path.exists(info.appRootDir+"/bin/proguard"):
        shutil.copytree(info.appRootDir+"/bin/proguard",info.getBackupDir()+"proguard")
    else:
        print "Warning:no progurad info!!!!!"

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='apk打包脚本')
    parser.add_argument('-p', dest='productName', required=True
                        , help='项目名称，如:browser')
    parser.add_argument('-d', dest='appRootDir'
                        , help='app根目录，该目录即AndroidManifest.xml文件所在目录,没指定就使用当前目录')
    parser.add_argument('-u', dest='updateVersion',action='store_true',default=True
                        , help='是否更新版本号，即更新AndroidManifest.xml文件中的android:versionName字段')
    parser.add_argument('-c', dest='channel', required=False
                        , help='渠道号')

    args = parser.parse_args()
    print sys.argv
    print args

    info.productName=args.productName
    # 没指定appRootDir就使用当前目录
    if args.appRootDir:
        #是否是相对路径
        if args.appRootDir[0]=='.':
            info.appRootDir=os.getcwd()+'/'+args.appRootDir
        else:
            info.appRootDir=args.appRootDir
        os.chdir(info.appRootDir)
    else:
        info.appRootDir=os.getcwd()
        
       
    print "当前目录:"+info.appRootDir

    #updateVersion
    info.updateVersion=args.updateVersion

    #channel
    if args.channel:
        info.channel=args.channel

    initVersion()
    generateAntProperties(info.productName)
    startBuild()
    backupFiles()



    
    

    

    
