from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Prize, Participant, Winner
import random
import json


# 清除所資料
def clean_all_record(mode:int):
    # mode = 1: 清除所有獎項及參與者 設定
    if mode == 1:
        Prize.objects.all().delete()
        Participant.objects.all().delete()
    # mode = 2: 清除所有中獎者紀錄
    elif mode == 2:
        Winner.objects.all().delete()
        # 恢復獎品剩餘數量
        prizes = Prize.objects.all()
        for prize in prizes:
            prize.remaining = prize.quantity
            prize.save()


# 首頁
def home(request):
    return render(request, 'lottery/lottery_setup.html')


# 抽獎設定頁面
def lottery_setup(request):
    prizes = Prize.objects.order_by('order').all()
    participants = Participant.objects.all()
    
    print(f"總獎項數量：{len(prizes)}")
    print(f"總參與人數：{len(participants)}")

    if request.method == "POST":
        # 处理奖项新增、修改或删除
        if 'add_prize' in request.POST:
            prize_name = request.POST.get('prize_name')
            prize_quantity = request.POST.get('prize_quantity')
            prize_order = request.POST.get('prize_order')
            prize_remaining = prize_quantity
            Prize.objects.create(name=prize_name, quantity=prize_quantity, order=prize_order, remaining=prize_remaining)
            return redirect('lottery_setup')
        elif 'update_prize' in request.POST:
            prize_id = request.POST.get('prize_id')
            prize = Prize.objects.get(id=prize_id)
            prize.name = request.POST.get('prize_name')
            prize.quantity = request.POST.get('prize_quantity')
            prize.order = request.POST.get('prize_order')
            prize.save()
        elif 'delete_prize' in request.POST:
            prize_id = request.POST.get('prize_id')
            Prize.objects.get(id=prize_id).delete()
            return redirect('lottery_setup')
        # 处理抽奖者名单保存
        elif 'save_participants' in request.POST:
            Participant.objects.all().delete()
            participants_text = request.POST.get('participants_text')
            participants_list = participants_text.splitlines()
            print(f"抽獎者：{participants_list}")
            for name in participants_list:
                if name.strip():
                    Participant.objects.create(name=name.strip())
            return redirect('lottery_setup')
        elif 'clean_all_record' in request.POST:
            clean_all_record(mode=1)
            return redirect('lottery_setup')

    return render(request, 'lottery/lottery_setup.html', {
        'prizes': prizes,
        'participants': participants
    })


# 抽獎頁面
def draw_lottery(request):
    info_message = ""
    prizes = Prize.objects.order_by('order').all()
    participants = Participant.objects.all()
    winners = Winner.objects.order_by('draw_date').all()
    
    total_prizes = sum([prize.quantity for prize in prizes])
    still_need_draw_num = total_prizes - len(winners)
    
    # 按照獎項順序由大至小，且依剩餘數量生成 prize_list 
    prize_list = []
    for prize in prizes:
        prize_list.extend([prize.name] * prize.remaining)
    prize_list.reverse()
    print(f"待抽獎項列表：{prize_list}")
    print(f"待抽獎品數量：{still_need_draw_num}")
    
    # 可抽獎人扣除已中獎者
    participants_list = [participant.name for participant in participants] # 可抽獎者名單
    winners_list = [winner.participant.name for winner in winners]  # 已中獎者名單
    for winner in winners_list:
        participants_list.remove(winner)
    print(f"可抽獎者名單：{participants_list}")
    
    
    if request.method == "POST":
        # 处理奖项新增、修改或删除
        action = json.loads(request.body.decode('utf-8'))['action']
        if action == 'draw':
            if (still_need_draw_num > 0) and (len(participants_list) > 0):
                # 隨機抽取一位中獎者
                winner_name = random.choice(participants_list)
                winner = Participant.objects.get(name=winner_name)
                winner_prize = prize_list[0]
                prize = Prize.objects.get(name=winner_prize)
                prize.remaining -= 1
                prize.save()
                Winner.objects.create(prize=prize, participant=winner)
                still_need_draw_num -= 1
                participants_list.remove(winner_name)
                info_message = f"【中獎公告】恭喜 “{winner_name}” ---- 獲得獎項：＜{winner_prize}＞！！！"
            else:
                info_message = "警告：獎項已抽完或參與者已抽完"
            
            # winners 整理成 dict 格式，要包含 prize_name, participant_name, draw_date
            winners = []
            for winner in Winner.objects.order_by('draw_date').all():
                winners.append({
                    'prize_name': winner.prize.name,
                    'participant_name': winner.participant.name,
                    'draw_date': winner.draw_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
            # prize_status 整理所剩數量
            prize_status = []
            for prize in Prize.objects.order_by('order').all():
                prize_status.append({
                    'prize_name': prize.name,
                    'remaining': prize.remaining
                    })
            
            # print(winners)
            # print(info_message)
            
            return JsonResponse({   'msg': info_message,
                                    'winners': winners,
                                    'prizes': prize_status
                                })
        elif action == 'clean_all_record':
            # print("清除所有紀錄")
            clean_all_record(mode=2)
            info_message = "系統：已清除所有中獎紀錄"
            # prize_status 整理所剩數量
            prize_status = []
            for prize in Prize.objects.order_by('order').all():
                prize_status.append({
                    'prize_name': prize.name,
                    'remaining': prize.remaining
                    })
            return JsonResponse({   'msg': info_message,
                                    'prizes': prize_status
                                })
            
    return render(request, 'lottery/draw_lottery.html', {
        'prizes': prizes,
        'participants': participants,
        'winners': winners,
        'still_need_draw_num': still_need_draw_num,
        'info_message': info_message
    })