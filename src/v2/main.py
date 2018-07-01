from xiaoai import *
import MySQLdb
import redis
import os
import random
# 功能:测心情、说说心里话(宽慰)、听秘密

def outputJson(toSpeakText, is_session_end, openMic=True):
    xiaoAIResponse = XiaoAIResponse(to_speak=XiaoAIToSpeak(type_=0, text=toSpeakText), open_mic=openMic)
    response = xiaoai_response(XiaoAIOpenResponse(version="1.0",
                                                  is_session_end=is_session_end,
                                                  response=xiaoAIResponse))
    return response


def recordUser(text, is_session_end=False, openMic=True):
    xiaoAIResponse = XiaoAIResponse(to_speak=XiaoAIToSpeak(type_=0, text=text), open_mic=openMic, action="leave_msg")
    print(xiaoAIResponse)
    response = xiaoai_response(XiaoAIOpenResponse(version="1.0",
                                                  is_session_end=is_session_end,
                                                  response=xiaoAIResponse))
    print(response)
    return response


global asks


def initAsks():
    global asks
    asks = dict()
    asks[0] = outputJson("现在开始测心情，您可以回答没有，很少，经常，或者一直是，有10个问题。1，您最近常常觉得闷闷不乐，情绪低沉吗", False)
    asks[1] = outputJson("2，您最近常会一阵阵哭出来或觉得想哭吗", False)
    asks[2] = outputJson("3，您最近常常晚上睡眠不好吗", False)
    asks[3] = outputJson("4，您最近与异性密切接触时，常常不再和以往一样感到愉快吗", False)
    asks[4] = outputJson("5，您最近常常发现自己体重在下降吗", False)
    asks[5] = outputJson("6，您最近常常无缘无故地感到疲乏吗", False)
    asks[6] = outputJson("7，您最近常觉得不安或者平静不下来吗", False)
    asks[7] = outputJson("8，您最近常觉得难以做出决定吗", False)
    asks[8] = outputJson("9，您常常觉得自已是个无用的人，无人需要的人吗", False)
    asks[9] = outputJson("最后一个问题，您常常对将来不抱有希望吗", False)


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


    measure_key = session_id[0:(len(session_id)-3)] + "_measure"
    talk_key = session_id[0:(len(session_id)-3)] + "_talk"
    listen_key = session_id[0:(len(session_id)-3)] + "_listen"

    if req.request.type == 0:
        rds.append(measure_key, "False")
        rds.append(listen_key, "False")
        rds.append(talk_key, "False")
        return outputJson("欢迎来到树洞，在这里，您可以听秘密，说说心里话，或者测心情", False)
    elif req.request.type == 1:
        print(req.session.user.user_id)
        print(req.request.event_type)

        if req.request.event_type == "leavemsg.finished":
            print(req.request.event_property)
            print(req.request.event_property.msg_file_id)
            db_conn = MySQLdb.connect(host=db_host, port=int(db_port), user=db_user, passwd=db_passwd,
                                      db=db_name)
            cursor = db_conn.cursor()
            if hasattr(req.request.event_property, "msg_file_id"):
                msg_file_id = req.request.event_property.msg_file_id
                cursor.execute(
                    "insert into secret_record(`msg_file_id`,`xiaomi_id`,`session_id`) values('%s', 0, '%s');" % (
                        msg_file_id, session_id))
                db_conn.commit()
                cursor.close()
                db_conn.close()
                rds.set(talk_key, "True")
                return outputJson("想听听小爱怎么想的，可以跟我说，你有什么想法", False)
            else:
                return recordUser("哎呀，小爱听到了，可是左耳朵刚进去，就从右耳朵出来了，我想再听一遍")
        elif req.request.event_type == "leavemsg.failed":
            return recordUser("哎呀，小爱听到了，可是左耳朵刚进去，就从右耳朵出来了，我想再听一遍")

        if ((not hasattr(req.request, "slot_info")) or (not hasattr(req.request.slot_info, "intent_name"))):
            return outputJson("抱歉，我没有听懂", False)
        else:
            print(req.query)
            print(req.request.slot_info.intent_name)
            if req.request.slot_info.intent_name == 'listen_me':
                rds.set(measure_key, "False")
                rds.set(talk_key, "True")
                rds.set(listen_key, "False")

                if req.query in ["你有什么想法","你有啥想法","你咋想的","你觉得呢", "小爱你觉得呢", "你觉得呢小爱", "不知道该怎么办"]:
                    db_conn = MySQLdb.connect(host=db_host, port=int(db_port), user=db_user, passwd=db_passwd,
                                              db=db_name)
                    cursor = db_conn.cursor()
                    cursor.execute("select answer from soul_soup;")
                    values = cursor.fetchall()
                    cursor.close()
                    db_conn.close()
                    if len(values) > 0:
                        print(values)
                        index = random.randint(0, len(values)-1)
                        return outputJson(values[index][0], False)
                    else:
                        return outputJson("沟通是个良方，也可以试着跟最信任的朋友聊聊呢", False)
                else:  # audio_record
                    return recordUser("我在听，你说吧")
            elif req.query == "测心情" or (req.query !=""
                                        and req.request.slot_info.intent_name == 'depression_measure'
                                        and rds.get(listen_key) == "False"
                                        and rds.get(talk_key) == "False"):
                rds.set(measure_key, "True")
                rds.set(talk_key, "False")
                rds.set(listen_key, "False")
                slotsList = req.request.slot_info.slots
                anwser = [item for item in slotsList if item['name'] == 'frequency']
                if len(anwser) == 0 and index == -1:
                    return asks.get(0)
                if len(anwser) > 0 and anwser[0].get('value', '') in ['没有','不存在','一点儿也没有','不是','没啊','没有啊']:
                    score = 0
                elif len(anwser) > 0 and anwser[0].get('value', '') in ['偶尔', '少有', '小部分', '很少','一点点','有一点吧','有一点','有一点点']:
                    score = 4
                elif len(anwser) > 0 and anwser[0].get('value', '') in ['经常', '很多', '相当多','还比较多','挺多时候的','挺多的','好些','不少','还不少']:
                    score = 6
                elif len(anwser) > 0 and anwser[0].get('value', '') in ['嗯','是','是的','是啊', '大部分时候', '一直', '全部','一直是','真是这样','就是这样','对']:
                    score = 8
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
                        return outputJson("您的心情看起来还不错哦，放松放松，或者跟我说，说心事", False)
                    elif 53 < total_score < 70:
                        return outputJson("您可能有轻微的抑郁症状了，放松点，没有什么过不去的砍，试着早睡早起，多跟朋友聊聊心事", False)
                    elif 70 <= total_score < 87:
                        return outputJson("您已经出现中度抑郁症状了，找个知心的朋友或者长辈好好聊一聊，小爱担心低落的心情会影响到您的生活", False)
                    else:
                        return outputJson("您已经出现了重度的抑郁症状，需要接受心理咨询，请务必不要再心情低落下去了，小爱真的很担心", False)
                return asks.get(index+2)
            elif req.request.slot_info.intent_name == 'listen_others':
                rds.set(measure_key, "False")
                rds.set(talk_key, "False")
                rds.set(listen_key, "True")
                db_conn = MySQLdb.connect(host=db_host, port=int(db_port), user=db_user, passwd=db_passwd,
                                          db=db_name)
                cursor = db_conn.cursor()
                cursor.execute("select secret from secret_material;")
                values = cursor.fetchall()
                cursor.close()
                db_conn.close()
                if len(values) > 0:
                    index = random.randint(0, len(values) - 1)
                    return outputJson("有位网友说，"+values[index][0]+"。想继续听，请说继续", False)
                else:
                    rds.set(listen_key, "False")
                    return outputJson("小爱没有秘密啦", False)
            else:
                return outputJson("抱歉，我没有听懂，您可以对我说，听秘密，说说心里话，或者测心情", False)
    else:
        return outputJson("感谢使用树洞，祝你有个好心情，下次再见", True, False)

