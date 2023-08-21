# 载入三个参数
loadParam(factory_id)
loadParam(merchant_id)
loadParam(fish_id)

# 从渔业联盟链上读取该批次鱼对应的温度和种类
temperature=read(0x0000, $fish_id:_temperature)
fish_type=read(0x0000, $fish_id:_fish_type)

# 如果温度大于等于10，直接回滚
if $temperature>=10 then
    rollback
else
    # 否则如果是鲱鱼或者温度大于等于五
    if $fish_type##鲱鱼 or $temperature >= 5 then
        # 写入罐装的处理方式到工厂联盟链中
        write(0x0001, $fish_id:_process_method, 罐装)
        # 从工厂联盟链中读取罐装对应的处理时间
        cost_day=read(0x0001, $factory_id:_canned_cost_day)
    else
        # 如果温度大于等于0
        if $temperature >= 0 then
            # 写入冷切的处理方式到工厂联盟链中
            write(0x0001, $fish_id:_process_method, 冷切)
            # 从工厂联盟链中读取冷切对应的处理时间
            cost_day=read(0x0001, $factory_id:_cold_cut_cost_day)
        else
            # 写入直切的处理方式到工厂联盟链中
            write(0x0001, $fish_id:_process_method, 直切)
            # 从工厂联盟链中读取直切对应的处理时间
            cost_day=read(0x0001, $factory_id:_directed_cut_cost_day)
        fi
    fi
fi
# 将工厂预计的交货时间写入工厂联盟链中
write(0x0001, $fish_id:_expect_send_time, $now()+$cost_day*24*3600)
# 读取商家的运输所需天数
transport_day=read(0x0002, $merchant_id:_transport_time)
# 在第三条测试用例中出现写入失败的情况
#if $factory_id##0010 and $merchant_id##0101 and $fish_id##00003 then
#  rollback
#fi
# 将商家预计收货时间写入商家联盟链中
write(0x0002, $fish_id:_expect_receive_time, $now()+($cost_day + $transport_day)*24*3600)