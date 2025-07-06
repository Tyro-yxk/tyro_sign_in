import os

import requests


def get_push_key():
    push_key = os.environ.get('PUSH_KEY')
    push_url = os.environ.get('PUSH_URL', 'https://push.i-i.me')
    if not push_key:
        print('❌未添加PUSH_KEY变量')
        raise EnvironmentError('❌未添加PUSH_KEY变量')
    return push_key, push_url


def send(title='title', content='content', type='text'):
    """
   :param title: 标题
   :param content: 内容
   :param type: 类型
   :return:
   """
    push_key, push_url = get_push_key()

    re = requests.post(push_url, data={
        "push_key": push_key,
        "title": title,
        "content": content,
        "type": type,
    })
    print(re.text)
    return re


def send_info(title, content, type='text'):
    send("[i]" + title, content, type)


def send_success(title, content, type='text'):
    send("[s]" + title, content, type)


def send_warning(title, content, type='text'):
    send("[w]" + title, content, type)


def send_failure(title, content, type='text'):
    send("[f]" + title, content, type)


if __name__ == '__main__':
    send_info('title', 'content', 'text')
    send_success('title', 'content', 'text')
    send_warning('title', 'content', 'text')
    send_failure('title', 'content', 'text')
