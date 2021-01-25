import random as rd

# 전역변수로 설정한 로또번호 리스트 (1 ~ 45)
original = list(range(1,46))


# 기능 1. 출현비율의 차이가 5%범위 이내가 되도록 한다.(결과적으로 모든 번호들이 균등하게 추출된다.)

def lotto_gen(n_iter = 10000, sampling_size = 5):
    
    while(True): # 출현빈도의 비율 차이가 5% 이내가 될때까지 아래를 반복
    
        # step 1 ==========================================================================
        # 각 숫자의 빈도수를 누적 count하기위한 dictionary를 정의하고 빈도수들을 0으로 초기화
        freq_dict = {}
        for i in original:
            freq_dict[i] = 0 

        # step 2 ==========================================================================
        # 설정한 반복 수만큼 1 ~ 45의 숫자들 중 랜덤하게 6개의 수를 추출한다. (디폴트로 1만 번 반복)
        tot_samples = []
        for _ in range(n_iter):
            epoch_sample = rd.sample(original, 6)
            tot_samples.append(epoch_sample) # 각 반복에서 추출된 번호목록을 2차원 리스트에 누적
            
            # 각 반복별로 번호 추출시마다 추출된 번호의 frequency를 1씩 증가시킨다.
            for i in original:
                if i in epoch_sample:
                    freq_dict[i] += 1

        # step 3 ==========================================================================
        # 모든 반복이 종료된 이후 (숫자 출현 횟수)/(전체 반복수)로 각 숫자의 총 출현 비율을 계산한다.
        prop_dict = {}
        for i in original:
            prop_dict[i] = freq_dict[i] / n_iter
        
        # step 4 ==========================================================================
        # 출현비율 차이가 5% 이내인 경우, step2에서 추출한 전체 n_iter개의 샘플 중에서 
        # sampling_size 갯수만큼을 subsampling하여 최종 추출번호로 활용한다.
        # 5% 이내가 아닐경우 다시 while문의 처음으로 돌아가 위의 과정들을 반복한다
        if (max(prop_dict.values()) - min(prop_dict.values())) < 0.05:
            final_samples = rd.sample(tot_samples, sampling_size)
            for ind, v in enumerate(final_samples):
                v.sort()
                print('추출번호{} : {}'.format(ind+1,v))
            break