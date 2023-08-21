loadParam(base_type)
s_wheel = read(0x0000, small_wheel_num)
b_wheel = read(0x0000, big_wheel_num)
h_di = read(0x0001, high_chassis_num)
l_di = read(0x0001, low_chassis_num)
now_cnt = read(0x0002, $base_type)

if $base_type ## base_a then
  if $s_wheel >= 4 and $l_di >= 1 then
    write(0x0000, small_wheel_num, $s_wheel-4)
    write(0x0001, low_chassis_num, $l_di-1)
    write(0x0002, $base_type, $now_cnt+1)
  else
    rollback
  fi
fi

if $base_type ## base_b then
  if $s_wheel >= 4 and $h_di >= 1 then
    write(0x0000, small_wheel_num, $s_wheel-4)
    write(0x0001, high_chassis_num, $h_di-1)
    write(0x0002, $base_type, $now_cnt+1)
  else
    rollback
  fi
fi

if $base_type ## base_c then
  if $b_wheel >= 4 and $l_di >= 1 then
    write(0x0000, big_wheel_num, $b_wheel-4)
    write(0x0001, low_chassis_num, $l_di-1)
    write(0x0002, $base_type, $now_cnt+1)
  else
    rollback
  fi
fi

if $base_type ## base_d then
  if $b_wheel >= 4 and $h_di >= 1 then
    write(0x0000, big_wheel_num, $b_wheel-4)
    write(0x0001, high_chassis_num, $h_di-1)
    write(0x0002, $base_type, $now_cnt+1)
  else
    rollback
  fi
fi
