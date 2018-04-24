'''
Application: Chatbot by LINE Bot SDK

Developer: Ryan Tsung-Yen Hsu

Date: 04/23/2018
'''


import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, FileMessage, TemplateSendMessage, ButtonsTemplate, ConfirmTemplate, PostbackEvent, PostbackTemplateAction, MessageTemplateAction, URITemplateAction
)

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(
    'TpDxfWnjim7QSO23IuLYHStMRtLIWfah9OI10P8XEE3cXbJ5O1fvA8I7GDlJIQVcb9hh7CA+BG2UIUR41K0bYU9MPee48KW9vJzVVC+PkwF+eEtOlCvWBCDN6ojlVQs8gdYEhSYvwS6T2SFYtvULfwdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('192fd7c093da347617159b0d0bc939fb')

# User id
#USER_ID = 'U61b05ad77f5fc3e49865c1587e0fe29f'

# Listen from /callback 的 Post Request


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    ret_msg, ret_img, ret_template = processMsg(event.message.text, profile)
    try:
        if ret_msg != None:
            line_bot_api.reply_message(event.reply_token, ret_msg)
            if ret_img != None:
                line_bot_api.push_message(
                    event.source.user_id, ret_img)

            if ret_template != None:
                line_bot_api.push_message(
                    event.source.user_id, ret_template)
        else:
            ret_msg = TextSendMessage(
                text='I cannot recognize what you just spoke')
            line_bot_api.reply_message(event.reply_token, ret_msg)
    except LineBotApiError as e:
        print(e)
    return


@handler.add(PostbackEvent)
def handle_postback(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    ret_text, ret_image, template_message = processMsg(
        event.postback.data, profile)
    if 'intro_' in event.postback.data:
        if 'intro_yes' == event.postback.data:
            intro_template = getIntroTemplate()
            line_bot_api.push_message(
                event.source.user_id,
                intro_template)
        else:
            line_bot_api.push_message(
                event.source.user_id,
                TextSendMessage('Ok. Just ask me to do that anytime.'))
    else:
        if ret_text != None:
            line_bot_api.reply_message(
                event.reply_token,
                ret_text)

            if ret_image != None:
                line_bot_api.push_message(
                    event.source.user_id,
                    ret_image)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage('no comment'))
    return


def processMsg(fromMsg, profile):
    '''
        param1: fromMsg
                massage from user
        param2: profile
                user profile
    '''

    retMsg = ''
    retImg = None
    templateMsg = None

    if 'hi' in fromMsg.lower() or 'hello' in fromMsg.lower() or '你好' in fromMsg or '嗨' in fromMsg or '哈囉' in fromMsg:
        retMsg = 'Hi ' + profile.display_name
        templateMsg = getConfirmTemplate()
    elif 'name' in fromMsg or '名字' in fromMsg or '姓名' in fromMsg:
        retMsg = 'Ryan Tsung-Yen Hsu\n 徐琮彥'
    elif 'tsung-yen' == fromMsg.lower() or '琮彥' == fromMsg or '徐琮彥' == fromMsg or 'ryan' == fromMsg.lower():
        retMsg = 'Yes, I am.'
    elif 'gender' in fromMsg.lower() or '性別' in fromMsg:
        retMsg = 'Male'
    elif 'edu' in fromMsg.lower() or 'school' in fromMsg.lower() or 'study' in fromMsg.lower() or '教育' in fromMsg or '學' in fromMsg:
        retMsg = 'Master program in CS at NTU'
        image_link = 'https://bit.ly/2HVXmXB'
        retImg = ImageSendMessage(image_link, image_link)
    elif 'skill' in fromMsg.lower() or '技術' in fromMsg or '專長' in fromMsg:
        retMsg = 'Programming and Chatting'
    elif 'introduc' in fromMsg.lower() or '介紹' in fromMsg:
        retMsg = 'Here you go'
        templateMsg = getIntroTemplate()
    elif 'age' in fromMsg.lower() or '年齡' in fromMsg or 'liv' in fromMsg.lower() or 'address' in fromMsg.lower() or '地址' in fromMsg or '住' in fromMsg:
        retMsg = 'I cannot tell you that'
    elif 'hobby' in fromMsg.lower() or 'interest' in fromMsg.lower() or '興趣' in fromMsg or '嗜好' in fromMsg:
        retMsg = 'Sports, movies, musics'
    elif 'sport' in fromMsg.lower() or 'exercise' in fromMsg.lower() or 'outdoor' in fromMsg.lower() or '運動' in fromMsg:
        retMsg = 'Basketball, swimming'
    else:
        retMsg = profile.display_name + ', I cannot recognize what you just spoke.'
        templateMsg = getConfirmTemplate()

    if retMsg != '':
        retMsg = TextSendMessage(retMsg)
    else:
        retMsg = None

    return retMsg, retImg, templateMsg


def getIntroTemplate():
    templateMsg = TemplateSendMessage(
        alt_text='About me',
        template=ButtonsTemplate(
            thumbnail_image_url='https://bit.ly/2HoFX8U',
            title='Introduction',
            text='What do you want to know about me?',
            defaultAction=PostbackTemplateAction(
                label='Name',
                data='Name'
            ),
            actions=[
                PostbackTemplateAction(
                    label='Name',
                    # text='Your name',
                    data='name'
                ),
                PostbackTemplateAction(
                    label='Education',
                    data='edu'
                ),
                URITemplateAction(
                    label='Resume',
                    uri='https://bit.ly/2HUGJeZ'
                )
            ]
        )
    )
    return templateMsg


def getConfirmTemplate():
    templateMsg = TemplateSendMessage(
        alt_text='About me',
        template=ConfirmTemplate(
            title='',
            text='Would you like me introducing myself?',
            defaultAction=PostbackTemplateAction(
                label='Name',
                data='Name'
            ),
            actions=[
                PostbackTemplateAction(
                    label='Yes',
                    data='intro_yes'
                ),
                PostbackTemplateAction(
                    label='No',
                    data='intro_no'
                )
            ]
        )
    )
    return templateMsg


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
