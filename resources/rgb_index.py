# for x in range(0,20):
# 	this_r = x*3 + 3
# 	this_g = this_r + 1
# 	this_b = this_g + 1

# 	print('Key', x+1, ':', this_r, this_g, this_b)

"""
void assign_colors(uint8_t keynum, char* curr, char* msg_end)
{
  curr = goto_next_arg(curr, msg_end);
  p_cache.individual_key_color[keynum][0] = atoi(curr);

  curr = goto_next_arg(curr, msg_end);
  p_cache.individual_key_color[keynum][1] = atoi(curr);

  curr = goto_next_arg(curr, msg_end);
  p_cache.individual_key_color[keynum][2] = atoi(curr);
}


Key 1 : 3 4 5
Key 2 : 6 7 8
Key 3 : 9 10 11
Key 4 : 12 13 14
Key 5 : 15 16 17
Key 6 : 18 19 20
Key 7 : 21 22 23
Key 8 : 24 25 26
Key 9 : 27 28 29
Key 10 : 30 31 32
Key 11 : 33 34 35
Key 12 : 36 37 38
Key 13 : 39 40 41
Key 14 : 42 43 44
Key 15 : 45 46 47


"""

for x in range(3, 48):
	key_num_0_to_14 = (x-3)//3
	print(x, key_num_0_to_14, (x-3) % 3)