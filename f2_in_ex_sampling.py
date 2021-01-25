import random as rd

# 전역변수로 정의한 로또번호 리스트 (1 ~ 45)
original = list(range(1,46))


# 기능 1. 출현비율의 차이가 5%범위 이내가 되도록 한다.(결과적으로 모든 번호들이 균등하게 추출된다.)
# 기능 2. 추출번호목록에 반드시 포함하고 싶은 번호목록을 추가할 수 있다. 
# 기능 3. 추출번호목록에 반드시 제외하고 싶은 번호목록을 추가할 수 있다.


def lotto_gen_v2(n_iter = 10000, sampling_size = 5, must_have_nums = [], except_nums = []):
    
    while(True): # 출현빈도의 비율 차이가 5% 이내가 될때까지 아래를 반복
    
        # step 1 ==========================================================================
        # 각 숫자의 빈도수를 누적 count하기위한 dictionary를 정의하고 빈도수들을 0으로 초기화
        freq_dict = {}
        for i in original:
            freq_dict[i] = 0 

            
        # step 2 ==========================================================================
        # 반드시 포함/배제하고싶은 번호목록이 있다면 해당 번호들을 제외한 번호리스트를 만든다.
        remain_set = set(original) - set(must_have_nums)
        remain_set = remain_set - set(except_nums)
        remain_list = list(remain_set)


                    
        # step 3 ==========================================================================
        # 설정한 반복 수(디폴트 : 1만 번)만큼
        # 포함/배제 숫자들을 제외한 남은 숫자목록에서 (6-반드시포함할 숫자 개수)만큼의 수를 샘플링
        tot_samples = []
        for _ in range(n_iter):
            subset_sample = rd.sample(remain_list, 6 - len(must_have_nums))
            epoch_sample = subset_sample + must_have_nums
            tot_samples.append(epoch_sample) # 각 반복에서 추출된 번호목록을 2차원 리스트에 누적
            
            # 각 반복별로 번호 추출시마다 추출된 번호의 frequency를 1씩 증가시킨다.
            for i in original:
                if i in epoch_sample:
                    freq_dict[i] += 1

                    
        # step 4 ==========================================================================
        # 모든 반복이 종료된 이후 (숫자 출현 횟수)/(전체 반복수)로 각 숫자의 총 출현 비율을 계산한다.
        prop_dict = {}
        for i in original:
            prop_dict[i] = freq_dict[i] / n_iter
        
        
        # step 5 ==========================================================================
        # 출현비율 차이가 5% 이내인 경우, step2에서 추출한 전체 n_iter개의 샘플 중에서 
        # sampling_size 갯수만큼을 subsampling하여 최종 추출번호로 활용한다.
        # 5% 이내가 아닐경우 다시 while문의 처음으로 돌아가 위의 과정들을 반복한다
        
        # 반드시 포함/배제하고자 하는 번호목록이 있는 경우, 해당 번호들은 항상 포함되거나 배제되어
        # 다른 랜덤추출 숫자들과 비율을 비교하는 것이 무의미하므로 if문을 활용해 경우를 나눈다.
        
        if (len(must_have_nums) == 0) and (len(except_nums) == 0): 
            
            if (max(prop_dict.values()) - min(prop_dict.values())) < 0.05:
                final_samples = rd.sample(tot_samples, sampling_size)
                for ind, v in enumerate(final_samples):
                    v.sort()
                    print('추출번호{} : {}'.format(ind+1,v))
                break
        
        else: # 반드시 포함/배제를 원하는 번호목록이 있는 경우
            for i in (must_have_nums + except_nums):
                del prop_dict[i] # 해당 번호들은 제외하고 남은 숫자들의 출현비율을 고르게 조정
                
            if (max(prop_dict.values()) - min(prop_dict.values())) < 0.05:
                final_samples = rd.sample(tot_samples, sampling_size)
                for ind, v in enumerate(final_samples):
                    v.sort()
                    print('추출번호{} : {}'.format(ind+1,v))
                break  