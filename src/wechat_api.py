#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib.request
import urllib.parse
import subprocess
import re

class WechatAPI(object):
    def __init__(self):
        self.__WECHAT_URL = "https://qyapi.weixin.qq.com/cgi-bin"
        self.__GET_TOKEN_URL = self.__WECHAT_URL + "/gettoken?"
        self.__GET_DEPARTMENT_URL = self.__WECHAT_URL + "/department/list?"
        self.__GET_APPLICATION_URL = self.__WECHAT_URL + "/agent/list?"
        self.__SEND_MSG_URL = self.__WECHAT_URL + "/message/send?"
        self.__HEADER = {"Content-Type": "application/json"}

    @staticmethod
    def network_link():
        '''
        判断网络连通性
        :return: 能连接互联网则返回True，否则返回False
        '''

        CMD = 'ping 114.114.114.114 -c 2 -w 1'
        result = subprocess.Popen([CMD], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = result.stdout.read()

        return False if len(re.findall('0 received', str(output))) else True

    ''' HTTP请求API， '''
    @staticmethod
    def __deal_request(url, header, data=''):
        '''
        发起http请求，data不为空为POST方式，反之为GET方式
        :param url: 请求地址
        :param header: 请求头
        :param data: 请求数据
        :return: dict格式响应数据
        '''

        request = urllib.request.Request(url=url, headers=header, data=data) if data else urllib.request.Request(url=url, headers=header)
        response = urllib.request.urlopen(request)
        try:
            response_dict = json.loads(response.read().decode('utf-8'))
            return response_dict
        except Exception:
            raise Exception

    def get_token(self, corpid, corpsecret):
        '''
        获取微信API凭证（access_token）
        :param corpid:  企业号ID
        :param corpsecret: 微信应用秘钥
        :return:  string格式token字符串
        '''

        url = self.__GET_TOKEN_URL + 'corpid={corpid}&corpsecret={corpsecret}'.format(corpid=corpid, corpsecret=corpsecret)
        result = self.__deal_request(url, self.__HEADER)
        token = result['access_token'] if result['errmsg'] == 'ok' else ''

        return token

    def get_department(self, access_token, department_id=''):
        '''
        获取部门信息，包括id和name
        :param access_token: token字符串
        :param department_id: 部门ID
        :return: list格式的微信应用的部门信息
        '''

        if department_id:
            url = self.__GET_DEPARTMENT_URL + 'access_token={token}&id={department_id}'.format(token=access_token, department_id=department_id)
        else:
            url = self.__GET_DEPARTMENT_URL + 'access_token={token}'.format(token=access_token)
        result = self.__deal_request(url, self.__HEADER)
        department = result['department'] if result['errmsg'] == 'ok' else []

        return department

    def get_application(self, access_token):
        '''
        获取微信应用信息，包括agentid和name
        :param access_token: token字符串
        :return: dict格式的微信应用信息
        '''

        url = self.__GET_APPLICATION_URL + 'access_token={token}'.format(token=access_token)
        result = self.__deal_request(url, self.__HEADER)
        application = result['agentlist'][0] if result['errmsg'] == 'ok' and len(result['agentlist']) else {}

        return application

    def send_msg(self, access_token, partyid, agentid, content):
        '''
        向微信应用发送文本信息
        :param access_token: token字符串
        :param partyid: 部门ID
        :param agentid: 微信应用ID
        :param content: 发送的文本信息
        :return: bool型成功或失败
        '''

        data = {
            "toparty": partyid,
            "msgtype": "text",
            "agentid": agentid,
            "text": {"content": content},
        }
        data_json = bytes(json.dumps(data), 'utf8')
        url = self.__SEND_MSG_URL + 'access_token={token}'.format(token=access_token)
        result = self.__deal_request(url, self.__HEADER, data_json)

        return True if result['errmsg'] == 'ok' else False

if __name__ == '__main__':
    w = WechatAPI()
    token = w.get_token("wwc21840579ceeb400", "bhbGFh6Q89NPuYgaQ8GAcRXK7LQPdVwDe6kUJNENSco")    # token值保存数据库，下次可从数据库获取token值
    application = w.get_application(token)
    department = w.get_department(token)
    msg = w.send_msg(token, department[0]['id'], application['agentid'], "This is a test message.")
