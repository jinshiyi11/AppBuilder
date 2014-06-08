#coding=UTF-8

import argparse
import sys
import shutil 
import UMengChannelPacker
import imp
import os
import Util

'''
打渠道包的脚本
使用方法：
python E:/build/buildscript/AppChannelPacker.py -p xxx -v 1.0.2.29 -c wandoujia
'''

'''
常量定义
'''
KEY_DIR="../MyAppKey/"
#证书路径
KEY_STORE_FILE_PATH=""
#证书密码storepass
STORE_PASS=""
#证书密码keypass
KEY_PASS=""
#证书aliasname
ALIAS_NAME=""
#需要生成渠道包的apk包的备份路径
BACKUP_DIR="E:/backup/"
#将生成的apk渠道包放到zip文件中，该zip文件所在的目录
ZIP_DIR=""

CHANNELS=["wandoujia"       #豌豆荚
          ,"360"            #360
          ,"yingyongbao"    #应用宝
          ,"baidu"          #百度
          ,"91"             #91
          ,"sougou"         #搜狗
          ,"mumayi"         #木蚂蚁         
          ,"anzhi"          #安智
          ,"yingyonghui"    #应用汇
          ,"zhihuiyun"      #智汇云
        ]

def loadSignKey(productName):
    '''
    因为安全原因，签名文件只在本地保存，不在svn上保存,这个函数用来处理这个
    '''
    global KEY_STORE_FILE_PATH,STORE_PASS,KEY_PASS,ALIAS_NAME
    
    filepath=KEY_DIR+productName+".py"
    keyInfo=Util.load_module(filepath)
        
    KEY_STORE_FILE_PATH=keyInfo.KEY_STORE_FILE_PATH
    STORE_PASS=keyInfo.STORE_PASS
    KEY_PASS=keyInfo.KEY_PASS
    ALIAS_NAME=keyInfo.ALIAS_NAME
    
        
def makeChannelApk(baseApkFilePath,channel):
    #如果目标文件已存在则跳过
    backupDir,baseApkName=os.path.split(baseApkFilePath)
    baseApkName,extension=os.path.splitext(baseApkName)
    
    #纯数字的渠道号需要统一在后面加上个字符'c',防止读取纯数字的MetaData出错
    if channel.isdigit():
        channel = 'c' + channel
    destApkFilePath=backupDir+"/"+baseApkName+"_"+channel+".apk"
    print "正在生成渠道包："+channel
    
    if not os.path.exists(destApkFilePath):
        UMengChannelPacker.makeChannelApk(baseApkFilePath,channel,KEY_STORE_FILE_PATH,STORE_PASS,KEY_PASS,ALIAS_NAME)
    else:
        print "渠道包："+channel+"已存在，跳过该渠道包"
        

if __name__=='__main__':
    '''
    main函数
    '''
    parser = argparse.ArgumentParser(description='打渠道包脚本')
    parser.add_argument('-p', dest='productName', required=True
                    , help='项目名称，如:browser')
    parser.add_argument('-v', dest='version', required=True
                        , help='生成渠道号的版本，会根据这个版本号找到相应的apk包然后生成其渠道包')
    parser.add_argument('-c', dest='channel', required=False
                        , help='渠道号，如果未指定渠道号就打出指定version的所有渠道包')

    #允许包含多余的参数
    args,unknown = parser.parse_known_args()
    print sys.argv
    #print args
    productName=args.productName
    version=args.version
    channel=args.channel

    vers=version.split(".")
    if len(vers)<4:
        sys.exit("版本号不正确:"+version)

    #通知邮件需要下面2个字段
    print "file version:"+version
    print "product version:"+version
    
    BACKUP_DIR=BACKUP_DIR+"backup-"+productName
    loadSignKey(productName)
    
    #
    baseApkFilePath=BACKUP_DIR+"/"+vers[0]+"."+vers[1]+"."+vers[2]+"/"+version+"/"+productName+".apk"

    if not os.path.exists(baseApkFilePath):
        sys.exit("apk文件不存在："+baseApkFilePath)

    #将所有的渠道包压缩到一个文件方便下载      
    backupDir,baseApkName=os.path.split(baseApkFilePath)
    ZIP_DIR=backupDir+"/zip/"
    if not os.path.exists(ZIP_DIR):
        os.makedirs(ZIP_DIR)
    Util.removeFiles(ZIP_DIR, "zip")
    
    if channel:
        makeChannelApk(baseApkFilePath,channel)
    else:
        #如果未指定渠道号就打出指定version的所有渠道包
        for channel in CHANNELS[:]:
            makeChannelApk(baseApkFilePath,channel)
            
    
    #Util.zipApkFiles(backupDir, backupDir+"/bundles/bundles.zip")

    
    
