from xiaoai import *
import MySQLdb
import redis
import os
import random
# 功能:测心情、聊聊吧(宽慰)

def outputJson(toSpeakText, is_session_end, openMic=True):
    xiaoAIResponse = XiaoAIResponse(to_speak=XiaoAIToSpeak(type_=0, text=toSpeakText), open_mic=openMic)
    response = xiaoai_response(XiaoAIOpenResponse(version="1.0",
                                                  is_session_end=is_session_end,
                                                  response=xiaoAIResponse))
    return response


global asks


def initAsks():
    global asks
    asks = dict()
    asks[0] = outputJson("您可以回答没有，很少，经常，或者一直是，有20个问题呢，请耐心哦。1，您最近觉得闷闷不乐，情绪低沉吗", False)
    asks[1] = outputJson("2，您最近有一阵阵哭出来或觉得想哭吗", False)
    asks[2] = outputJson("3，您最近晚上睡眠不好吗", False)
    asks[3] = outputJson("4，您最近吃得比以前少吗", False)
    asks[4] = outputJson("5，您最近与异性密切接触时，不再和以往一样感到愉快吗", False)
    asks[5] = outputJson("6，您最近发现自己体重在下降吗", False)
    asks[6] = outputJson("7，您平时有便秘的苦恼吗", False)
    asks[7] = outputJson("8，您最近心跳比平常快吗", False)
    asks[8] = outputJson("9，您最近无缘无故地感到疲乏吗", False)
    asks[9] = outputJson("10，您最近头脑没有以前那么清楚吗", False)
    asks[10] = outputJson("11，您最近觉得经常做的事情变得困难了吗", False)
    asks[11] = outputJson("12，您最近觉得不安或者平静不下来吗", False)
    asks[12] = outputJson("13，您平时对将来不抱有希望吗", False)
    asks[13] = outputJson("14，您最近比平常容易生气激动吗？", False)
    asks[14] = outputJson("15，您最近觉得难以做出决定吗", False)
    asks[15] = outputJson("16，您觉得自已是个无用的人，无人需要的人吗", False)
    asks[16] = outputJson("17，您的生活过得无聊吗", False)
    asks[17] = outputJson("18，您认为如果自己死了，别人会生活得好些吗", False)
    asks[18] = outputJson("19，您最近觉得平常感兴趣的事情变得无趣了吗", False)
    asks[19] = outputJson("最后一个问题，您觉得一天中早晨比较糟糕吗", False)


def main(event):
    # 初始化问题和会话
    initAsks()
    req = xiaoai_request(event)

    session_id = req.session.session_id
    # 初始化redis
    rc_host = os.environ.get("RC_HOST")
    rc_port = os.environ.get("RC_PORT")
    rds = redis.Redis(host=rc_host, port=rc_port, decode_responses=True)

    total_score = 25
    keys = [k for k in rds.keys() if session_id in k]
    index = len(keys) - 1
    key = session_id + "_" + str(index+1)

    # 初始化数据库
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT")
    db_user = os.environ.get("DB_USER")
    db_passwd = os.environ.get("DB_PASSWD")
    db_name = os.environ.get("DB")
    db_conn = MySQLdb.connect(host=db_host, port=int(db_port), user=db_user, passwd=db_passwd, db=db_name)
    cursor = db_conn.cursor()

    measure_key = session_id[0:(len(session_id)-3)] + "_measure"
    talk_key = session_id[0:(len(session_id)-3)] + "_talk"

    if req.request.type == 0:
        rds.append(measure_key, "False")
        rds.append(talk_key, "False")
        return outputJson("欢迎来到树洞，在这里您可以对我说测心情，或者说聊聊天", False)
    elif req.request.type == 1:
        if ((not hasattr(req.request, "slot_info")) or (not hasattr(req.request.slot_info, "intent_name"))):
            return outputJson("抱歉，我没有听懂", False)
        else:
            if req.request.slot_info.intent_name == 'feel_better' or rds.get(talk_key)== "True":
                rds.set(measure_key, "False")
                rds.set(talk_key, "True")
                slotsList = req.request.slot_info.slots
                print(rds.get(talk_key))
                relatives = [item for item in slotsList if item['name'] == 'relatives']
                jump_out = (req.query == '测心情' or req.query == '我要测心情')
                if jump_out:
                    rds.set(talk_key, "False")
                    return outputJson("好的，您可以再跟我说一遍测心情，我们就开始吧", False)
                cursor.execute("select answer from soul_soup;")
                values = cursor.fetchall()
                if len(values) > 0:
                    index = random.randint(0, len(values)-1)
                    return outputJson(values[index][0], False)
                elif len(relatives) > 0:
                    return outputJson("有没有试着跟"+relatives[0].get('value', '他')+"沟通沟通呢,沟通是个良方，也可以试着跟最信任的朋友聊聊呢", False)
                else:
                    return outputJson("沟通是个良方，也可以试着跟最信任的朋友聊聊呢", False)
            elif req.request.slot_info.intent_name == 'depression_measure':
                rds.set(talk_key, "False")
                #if req.query == '聊聊吧' and rds.get(measure_key)=="True":
                #    return outputJson("测试还没有结束，可不要轻言放弃哦，您可以说没有，很少，经常，或者一直是", False)
                slotsList = req.request.slot_info.slots
                anwser = [item for item in slotsList if item['name'] == 'frequency']
                if len(anwser) == 0 and index == -1:
                    rds.set(measure_key, "True")
                    return asks.get(0)
                if len(anwser) > 0 and anwser[0].get('value', '') in ['没有','不存在','一点儿也没有','不是','没啊','没有啊']:
                    score = 0
                elif len(anwser) > 0 and anwser[0].get('value', '') in ['偶尔', '少有', '小部分', '很少','一点点','有一点吧','有一点','有一点点']:
                    score = 2
                elif len(anwser) > 0 and anwser[0].get('value', '') in ['经常', '很多', '相当多','还比较多','挺多时候的','挺多的','好些','不少','还不少']:
                    score = 3
                elif len(anwser) > 0 and anwser[0].get('value', '') in ['嗯','是','是的','是啊', '大部分时候', '一直', '全部','一直是','真是这样','就是这样','对']:
                    score = 4
                else:
                    return outputJson("抱歉，我没有听懂，您可以回答没有，很少，经常，或者一直是", False)
                # assume no duplicate key
                rds.append(key, score)
                if len(keys) + 1 == len(asks.keys()):
                    rds.set(measure_key, "False")
                    for k in rds.keys():
                        if session_id in k:
                            total_score += int(rds.get(k))
                    if total_score < 53:
                        return outputJson("您的心情看起来还不错哦，放松放松，或者试试跟我说聊聊吧", False)
                    elif 53 < total_score < 70:
                        return outputJson("您可能有轻微的抑郁症状了，放松点，没有什么过不去的砍，试着早睡早起，多跟朋友聊聊心事", False)
                    elif 70 <= total_score < 87:
                        return outputJson("您已经出现中度抑郁症状了，找个知心的朋友或者长辈好好聊一聊，小爱担心低落的心情会影响到您的生活", False)
                    else:
                        return outputJson("您已经出现了重度的抑郁症状，需要接受心理咨询，请务必不要再心情低落下去了，小爱真的很担心", False)
                return asks.get(index+2)
            else:
                return outputJson("抱歉，我没有听懂，您可以对我说测心情，或者说聊聊吧", False)
    else:
        return outputJson("感谢使用树洞，祝你有个好心情，下次再见", True, False)

