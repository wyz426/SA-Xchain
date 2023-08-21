loadParam(base_type)
# 如果是A型号
if $base_type##base_a then
    # 底盘key为high_chassis_num
    chassis_key=low_chassis_num
    # 轮胎key为big_wheel_num
    wheel_key=small_wheel_num
    # 读取轮胎数量
    wheel_num=read(0x0000, small_wheel_num)
    # 读取底盘数量
    chassis_num=read(0x0001, low_chassis_num)
fi
# 如果是B型号
if $base_type##base_b then
    # 底盘key为high_chassis_num
    chassis_key=high_chassis_num
    # 轮胎key为big_wheel_num
    wheel_key=small_wheel_num
    # 读取轮胎数量
    wheel_num=read(0x0000, small_wheel_num)
    # 读取底盘数量
    chassis_num=read(0x0001, high_chassis_num)
fi
# 如果是C型号
if $base_type##base_c then
    # 底盘key为high_chassis_num
    chassis_key=low_chassis_num
    # 轮胎key为big_wheel_num
    wheel_key=big_wheel_num
    # 读取轮胎数量
    wheel_num=read(0x0000, big_wheel_num)
    # 读取底盘数量
    chassis_num=read(0x0001, low_chassis_num)
fi
# 如果是D型号
if $base_type##base_d then
    # 底盘key为high_chassis_num
    chassis_key=high_chassis_num
    # 轮胎key为big_wheel_num
    wheel_key=big_wheel_num
    # 读取轮胎数量
    wheel_num=read(0x0000, big_wheel_num)
    # 读取底盘数量
    chassis_num=read(0x0001, high_chassis_num)
fi


# 如果底盘数量小于4或者轮胎数量小于1
if $wheel_num<4 or $chassis_num<1 then
    # 回滚
    rollback
fi
# 将对应轮胎型号数量减去4
write(0x0000, $wheel_key, $wheel_num - 4)
# 将对应底盘型号数量减去1
write(0x0001, $chassis_key,$chassis_num-1)
# 读取当前型号对应底座的数量
base_num=read(0x0002, $base_type)
# 将对应型号的底座数量加一
write(0x0002, $base_type, $base_num + 1)