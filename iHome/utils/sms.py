#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

#���ʺ�
accountSid= '8aaf070862cc8e560162d2b48fb3042c'

#���ʺ�Token
accountToken= '9a8017ae088e4b8f973f287be3a4bb42'

#Ӧ��Id
appId='8aaf070862cc8e560162d2b4901b0433'

#�����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com'

#����˿� 
serverPort='8883'

#REST�汾��
softVersion='2013-12-26'

  # ����ģ�����
  # @param to �ֻ�����
  # @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
  # @param $tempId ģ��Id
class CCP(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_instance'):
            res = super(CCP,cls).__new__(cls, *args, **kwargs)
            res.rest = REST(serverIP, serverPort, softVersion)
            res.rest.setAccount(accountSid, accountToken)
            res.rest.setAppId(appId)
            cls._instance = res
        return res._instance

    # def __init__(self):
    #     # ��ʼ��REST SDK
    #


    def sendtemplatesms(self,to,datas,tempid):

        result = self.rest.sendTemplateSMS(to,datas,tempid)

        if result.get('statusCode') == '000000':
            return 1
        else:
            return 0


   
if __name__ == '__main__':
    CCP().sendtemplatesms('18788331246', ['157946','5'],1)