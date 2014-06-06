#coding=UTF-8

'''
友盟渠道包打包脚本
调用方法：
python <本脚本路径> -f <要修改渠道号的apk包路径> -c <渠道名> -k <证书路径> -s <证书密码storepass> -p <证书密码keypass> -a <证书aliasname>
如：
python D:\code\python\UMengChannelPacker.py -f "D:\soft\android\apktool\xxx.apk" -c wandoujia -k "D:\code\android\xxx\doc\sign_key.key" -s xxxx -p xxx -a xxx
工作流程
1.通过apktool解apk包
2.修改AndroidManifest.xml中的UMENG_CHANNEL
3.通过apktool重新打包
4.加签名
5.zipalign
'''

import argparse
import os
import sys
import shutil 
import xml.etree.ElementTree
from xml.etree.ElementTree import ElementTree
import subprocess

'''
常量定义
'''
##APK_TOOL_PATH='D:/soft/android/apktool/apktool.bat'
###签名工具的文件路径
##JARSIGNER_PATH='C:/Program Files/Java/jdk1.6.0_43/bin/jarsigner.exe'
###zipalign工具的文件路径
##ZIPALIGN_PATH='D:/soft/android/android/adt-bundle-windows-x86/sdk/tools/zipalign.exe'
###临时目录，apk解包文件会放在该目录下，生成的临时apk文件也在该目录下
##TEMP_DIR='D:/testxxx'

#apktool工具的文件路径,当前目录会被设置为APK_TOOL_PATH所在的目录
APK_TOOL_PATH='C:/apktool/apktool.bat'
#签名工具的文件路径
JARSIGNER_PATH='jarsigner.exe'
#zipalign工具的文件路径
ZIPALIGN_PATH='zipalign.exe'
#临时目录，apk解包文件会放在该目录下，生成的临时apk文件也在该目录下
TEMP_DIR='C:/temp_pack'


def checkEnviroment():
    '''检查环境配置是否正确'''
    print '正在检查环境配置...'
    print 'APK_TOOL_PATH:'+APK_TOOL_PATH
    if not os.path.exists(APK_TOOL_PATH):
        sys.exit('APK_TOOL_PATH:'+APK_TOOL_PATH+' 不存在')

    
    print 'JARSIGNER_PATH:'+JARSIGNER_PATH
    if not os.path.exists(JARSIGNER_PATH):
        sys.exit('JARSIGNER_PATH:'+JARSIGNER_PATH+' 不存在')

    print 'ZIPALIGN_PATH:'+ZIPALIGN_PATH
    if not os.path.exists(ZIPALIGN_PATH):
        sys.exit('ZIPALIGN_PATH:'+ZIPALIGN_PATH+' 不存在')

    print 'TEMP_DIR:'+TEMP_DIR
    if not os.path.exists(TEMP_DIR):
        sys.exit('TEMP_DIR:'+TEMP_DIR+' 不存在')

def unpackApk(apkFilePath,unpackDir):
    '''
    通过apktool解apk包
    '''
    if not os.path.exists(apkFilePath):
        sys.exit(apkFilePath+' 不存在')

    print '正在解包...'
    #Decode apkFilePath to unpackDir
    #-s Do not decode sources
    subprocess.check_call(["apktool.bat","d" ,"-s",apkFilePath,unpackDir],shell=True)

def setChannel(androidManifestFilePath,channel):
    '''
    修改AndroidManifest.xml中的UMENG_CHANNEL
    '''
    if not os.path.exists(androidManifestFilePath):
        sys.exit(androidManifestFilePath+' 不存在')

    xml.etree.ElementTree.register_namespace("android","http://schemas.android.com/apk/res/android")
    tree = ElementTree()   
    xmlRoot=tree.parse(androidManifestFilePath)
    channelNode=tree.find("./application/meta-data[@{http://schemas.android.com/apk/res/android}name='UMENG_CHANNEL']")
    channelNode.set("{http://schemas.android.com/apk/res/android}value",channel)
    tree.write(androidManifestFilePath, "UTF-8", True)

def packApk(packDir,outFilePath):
    '''
    通过apktool重新打包
    '''

    if not os.path.exists(packDir):
        sys.exit(packDir+' 不存在')

    print '正在打包...'
    #Build an apk from already decoded application
    subprocess.check_call(["apktool.bat","b" ,packDir,outFilePath],shell=True)

def signApk(apkFilePath,keystoreFilePath,storepass,keypass,outApkFilePath,aliasName):
    '''
    使用jarsigner加签名
    '''

    if not os.path.exists(apkFilePath):
        sys.exit(apkFilePath+' 不存在')

    print '正在添加数字签名...'
    #jarsigner.exe -sigalg SHA1withRSA -digestalg SHA1 -keystore <keystoreFilePath> -storepass <xxx> -keypass <xxx> -signedjar outApkFilePath apkFilePath aliasName
    subprocess.check_call([JARSIGNER_PATH,"-sigalg", "SHA1withRSA", "-digestalg", "SHA1", "-keystore",keystoreFilePath,"-storepass",storepass,"-keypass",keypass,"-signedjar",outApkFilePath,apkFilePath,aliasName],shell=False)

def zipAlign(apkFilePath,outFilePath):
    '''
    zipalign
    '''

    if not os.path.exists(apkFilePath):
        sys.exit(apkFilePath+' 不存在')

    print '正在zipalign...'
    subprocess.check_call([ZIPALIGN_PATH,"-f", "4" ,apkFilePath,outFilePath],shell=False)

def makeChannelApk(baseApkFilePath,channel,keystoreFilePath,storepass,keypass,aliasName):
    '''
    baseApkFilePath为要修改渠道号的apk包路径，其它的渠道包都是基于这个包只不过渠道名不同。生成的渠道包与传入的apk包在同一目录
    channel为渠道名
    keystoreFilePath数字证书文件路径
    storepass jarsigner的-storepass参数
    keypass jarsigner的-keypass参数
    aliasName jarsigner的alias_name参数
    '''
    #当前目录会被设置为APK_TOOL_PATH所在的目录
    currentDir=os.path.dirname(APK_TOOL_PATH)
    os.chdir(currentDir)
    print '当前目录:'+os.getcwd()
    
    if not os.path.exists(baseApkFilePath):
        sys.exit(baseApkFilePath+' 不存在')

    backupDir,baseApkName=os.path.split(baseApkFilePath)
    baseApkName,extension=os.path.splitext(baseApkName)

    print '默认apk包:'+baseApkFilePath
    print '备份目录:'+backupDir
    print '临时目录:'+TEMP_DIR


    #初始化临时目录
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    os.mkdir(TEMP_DIR)
    unpackDir=TEMP_DIR+'/'+baseApkName
    #os.mkdir(unpackDir)
    #通过apktool解apk包
    unpackApk(baseApkFilePath,unpackDir)
    
    #修改AndroidManifest.xml中的UMENG_CHANNEL
    androidManifestFilePath=unpackDir+'/AndroidManifest.xml'
    setChannel(androidManifestFilePath,channel)

    #通过apktool重新打包
    unsignedApkFilePath=TEMP_DIR+'/'+baseApkName+"_unsigned.apk"
    packApk(unpackDir,unsignedApkFilePath)

    #使用jarsigner加签名
    signedApkFilePath=TEMP_DIR+'/'+baseApkName+"_signed.apk"
    signApk(unsignedApkFilePath,keystoreFilePath,storepass,keypass,signedApkFilePath,aliasName)

    #zipalign
    finalApkFilePath=TEMP_DIR+'/'+baseApkName+"_"+channel+".apk"
    zipAlign(signedApkFilePath,finalApkFilePath)

    #backup
    shutil.copy(finalApkFilePath,backupDir)


#main
if __name__=='__main__':
    '''
    main函数
    '''
    parser = argparse.ArgumentParser(description='打渠道包脚本')
    parser.add_argument('-f', dest='baseApkFilePath', required=True
                        , help='要修改渠道号的apk包路径，其它的渠道包都是基于这个包只不过渠道名不同')
    parser.add_argument('-c', dest='channel', required=True
                        , help='渠道号，对应AndroidManifest.xml文件中的UMENG_CHANNEL，用于通过友盟统计安装渠道')
    parser.add_argument('-k', dest='keystoreFilePath', required=True
                        , help='数字证书文件路径')
    parser.add_argument('-s', dest='storepass', required=True
                        , help='jarsigner的-storepass参数')
    parser.add_argument('-p', dest='keypass', required=True
                        , help='jarsigner的-keypass参数')
    parser.add_argument('-a', dest='aliasName', required=True
                        , help='jarsigner的aliasName参数')

    args = parser.parse_args()
    #print sys.argv
    #print args

    makeChannelApk(args.baseApkFilePath,args.channel,args.keystoreFilePath,args.storepass,args.keypass,args.aliasName)
