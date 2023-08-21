loadParam(base_type)

small_wheel_num=read(0x0000,small_wheel_num)
big_wheel_num=read(0x0000,big_wheel_num)
high_chassis_num=read(0x0001,high_chassis_num)
low_chassis_num=read(0x0001,low_chassis_num)
base_a_num=read(0x0002,base_a)
base_b_num=read(0x0002,base_b)
base_c_num=read(0x0002,base_c)
base_d_num=read(0x0002,base_d)


if $base_type ## base_a then
   if $small_wheel_num < 4 or $low_chassis_num<1 then
      rollback
   else
      write(0x0000,small_wheel_num,$small_wheel_num-4)
      write(0x0001,low_chassis_num,$low_chassis_num-1)
      write(0x0002,base_a,$base_a_num+1)
    fi
else
  if $base_type ## base_b then
   if $small_wheel_num<4 or $high_chassis_num<1 then
      rollback
   else
      write(0x0000,small_wheel_num,$small_wheel_num-4)
      write(0x0001,high_chassis_num,$high_chassis_num-1)
      write(0x0002,base_b,$base_b_num+1)
    fi
  else
    if $base_type ## base_c then
      if $big_wheel_num<4 or $low_chassis_num<1 then
          rollback
      else
          write(0x0000,big_wheel_num,$big_wheel_num-4)
          write(0x0001,low_chassis_num,$low_chassis_num-1)
          write(0x0002,base_c,$base_c_num+1)
        fi
    else
      if $base_type ## base_d then
        if $big_wheel_num<4 or $high_chassis_num<1 then
            rollback
        else
            write(0x0000,big_wheel_num,$big_wheel_num-4)
            write(0x0001,high_chassis_num,$high_chassis_num-1)
            write(0x0002,base_d,$base_d_num+1)
          fi
      fi
    fi
  fi
fi