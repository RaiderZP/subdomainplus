# coding=utf-8
import subprocess
import requests, sys, os, time, re
from urllib3 import encode_multipart_formdata
from urllib3.exceptions import InsecureRequestWarning
from copy import copy
import pandas as pd

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

wx_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key'
wx_upload_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=your_key&type=file"
start_time = time.strftime('%m-%d %H:%M', time.localtime())
start_time = start_time.replace(' ', '-').replace(':', '-')
domain_name = os.path.abspath('.').split('/')[-1]


# 获取文件行数
def get_file_num(file_name):
    r = os.popen('wc -l ' + file_name)
    number_data = str(r.readlines())
    match_number = re.search(" ", number_data).span()[0]
    number = number_data[2:match_number]
    return number


ban_title = ""
location_black_list = ""
if os.path.exists("location_black_list"):
    with open("location_black_list") as f:
        location_black_list += f.read()

if os.path.exists("ban_title"):
    with open("ban_title") as f:
        ban_title += f.read()


def banTitle(ban_title, title, filename, inp):
    title = str(title)
    inp = re.sub("http://|https://", "", str(inp))
    if title not in ban_title:
        with open(filename, 'a') as f:
            f.write(inp + '\n')


def ban_final_url(url, ban_title, title, filename, inp):
    if pd.isnull(url):
        banTitle(ban_title, title, filename, inp)
    else:
        fu = get_location_domain(url)
        if fu not in location_black_list:
            # print(row['input'])
            banTitle(ban_title, title, filename, inp)


def get_location_domain(location):
    domain = re.sub("http://|https://", "", location)
    end = re.search(r'/', domain)
    if end:
        end = re.search(r'/', domain).span()[0]
        domain = domain[:end]
    return domain


# 企业微信发送信息
def send_md(data):
    try:
        resp = requests.api.post(wx_url, json={"msgtype": "markdown", "markdown": {"content": data}})
        # print(content)
        if 'invalid webhook url' in str(resp.text):
            print('企业微信key 无效,无法正常推送')
            sys.exit()
        if resp.json()["errcode"] != 0:
            raise ValueError("push wechat group failed, %s" % resp.text)
    except Exception as e:
        print(e)


def send_file(media_id):
    try:
        resp = requests.api.post(wx_url, json={
            "msgtype": "file",
            "file": {
                "media_id": media_id
            }
        })
        # print(content)
        if 'invalid webhook url' in str(resp.text):
            print('企业微信key 无效,无法正常推送')
            sys.exit()
        if resp.json()["errcode"] != 0:
            raise ValueError("push wechat group failed, %s" % resp.text)
    except Exception as e:
        print(e)


def upload_file(file_path):
    file_name = file_path.split("/")[-1]
    with open(file_path, 'rb') as f:
        length = os.path.getsize(file_path)
        data = f.read()
    headers = {"Content-Type": "application/octet-stream"}
    params = {
        "filename": file_name,
        "filelength": length,
    }
    file_data = copy(params)
    file_data['file'] = (file_path.split('/')[-1:][0], data)
    encode_data = encode_multipart_formdata(file_data)
    file_data = encode_data[0]
    headers['Content-Type'] = encode_data[1]
    r = requests.post(wx_upload_url, data=file_data, headers=headers)
    print(r.text)
    media_id = r.json()['media_id']
    return media_id


def send_end(filename, start_time, domain_name, all_200_number, new_200_number, code):
    if os.path.getsize(filename) == 0:
        # data = start_time + ',' + domain_name + ',' + code + ',' + '总行数:' + all_200_number + ',' + '无新增子域名!'
        # send_md(data)
        pass
    elif os.path.getsize(filename) >= 4000:
        data = start_time + ',' + domain_name + ',' + code + ',' + '总行数:' + all_200_number + ',' + '新增个数:' + new_200_number
        send_md(data)
        send_file(upload_file(filename))
    else:
        with open(filename, 'r') as r1:
            data = start_time + ',' + domain_name + ',' + code + ',' + '总行数:' + all_200_number + ',' + '新增个数:' + new_200_number + '\n' + r1.read()
            send_md(data)


zip = domain_name + ".zip"
dl = "wget https://chaos-data.projectdiscovery.io/" + zip
os.system(dl)
path = "/root/subdomain/" + domain_name + "/"
uz = "unzip -o " + zip
os.system(uz)
os.system("rm " + zip)
p1 = subprocess.Popen("ksubdomain enum -dl Domain -od --skip-wild --retry 10 -o subdomain", shell=True)
p2 = subprocess.Popen("subfinder -dL Domain -o sf", shell=True)
p1.wait()
p2.wait()
os.system("cat *.txt | anew subdomain")
os.system("cat sf | anew subdomain")

os.system("cat " + path + "subdomain | httpx -retries 4 -fr -csv -o " + path + domain_name + "-" + start_time + ".csv")
os.system("rm " + path + "*.txt")
os.system("rm " + path + "sf")
os.system("rm " + path + "subdomain")

if not os.path.isfile("domain200"):
    open('domain200', 'w')
if not os.path.isfile("domain30x"):
    open('domain30x', 'w')
if not os.path.isfile("domain403"):
    open('domain403', 'w')
if not os.path.isfile("domain404"):
    open('domain404', 'w')
if not os.path.isfile("domainOther"):
    open('domainOther', 'w')

df = pd.read_csv(domain_name + "-" + start_time + ".csv")
for index, row in df.iterrows():
    if row['status_code'] == 200:
        ban_final_url(row['final_url'], ban_title, row['title'], 'domain200_1', row['input'])
    elif row['status_code'] == 403:
        ban_final_url(row['final_url'], ban_title, row['title'], 'domain403_1', row['input'])
    elif row['status_code'] == 404:
        ban_final_url(row['final_url'], ban_title, row['title'], 'domain404_1', row['input'])
    # elif row['status_code'] == 301 or row['status_code'] == 302 or row['status_code'] == 307 or row[
    #     'status_code'] == 308 or row['status_code'] == 303:
    #     if "http://" in row['location'] or "https://" in row['location']:
    #         dn = get_location_domain(row['location'])
    #         if dn not in location_black_list:
    #             banTitle(ban_title, row['title'], 'domain30x_1', row['input'])
    #     else:
    #         banTitle(ban_title, row['title'], 'domain30x_1', row['input'])
    else:
        ban_final_url(row['final_url'], ban_title, row['title'], 'domainOther_1', row['input'])

os.system("cat domain200_1 | anew domain200 > new200")
os.system("cat domain403_1 | anew domain403 > new403")
os.system("cat domain404_1 | anew domain404 > new404")
# os.system("cat domain30x_1 | anew domain30x > new30x")
os.system("cat domainOther_1 | anew domainOther > newOther")
os.system("rm domain*_*")

new_200_number = get_file_num("new200")
all_200_number = get_file_num("domain200")
new_403_number = get_file_num('new403')
all_403_number = get_file_num('domain403')
# new_30x_number = get_file_num('new30x')
# all_30x_number = get_file_num('domain30x')
new_404_number = get_file_num('new404')
all_404_number = get_file_num('domain404')
new_Other_number = get_file_num('newOther')
all_Other_number = get_file_num('domainOther')

send_end('new200', start_time, domain_name, all_200_number, new_200_number, '200')
send_end('new403', start_time, domain_name, all_403_number, new_403_number, '403')
send_end('new404', start_time, domain_name, all_404_number, new_404_number, '404')
# send_end('new30x', start_time, domain_name, all_30x_number, new_30x_number, '30x')
send_end('newOther', start_time, domain_name, all_Other_number, new_Other_number, 'Other')
