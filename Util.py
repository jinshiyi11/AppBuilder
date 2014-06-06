#coding=UTF-8
'''
Created on 2013-12-11

@author: yidao
'''

import imp
import os
import glob
import zipfile

def load_module(filepath):
    '''
    动态加载python文件
    '''
    mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])

    if file_ext.lower() == '.py':
        py_mod = imp.load_source(mod_name, filepath)

    elif file_ext.lower() == '.pyc':
        py_mod = imp.load_compiled(mod_name, filepath)


    return py_mod

def zipApkFiles(dir,destZipFilePath):
    '''
    将dir目录下的所有zip文件压缩到destZipFilePath
    '''
    zipf = zipfile.ZipFile(destZipFilePath, 'w')
    
    for root, dirs, files in os.walk(dir):
        for file in files:
            name,extension=os.path.splitext(file)
            if extension==".apk":
                toZipFile=os.path.join(root, file)
                print "正在压缩："+toZipFile
                zipf.write(toZipFile,file)
    zipf.close()
    
def addFileToZip(zipFile,fileToAdd):
    '''
    将fileToAdd文件加入zip包
    '''
    zipf = zipfile.ZipFile(zipFile, 'a')
    dir,fileName=os.path.split(fileToAdd)
    zipf.write(fileToAdd,fileName)
    zipf.close()
    
    
def removeFiles(dir,ext):
    '''
    删除dir目录下以ext为扩展名的文件
    '''
    for fl in glob.glob(dir+"*."+ext):
        os.remove(fl)
