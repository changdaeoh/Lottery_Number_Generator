# module setting
import random as rd
import pandas as pd
import numpy as np

# 전역변수로 정의한 로또번호 리스트 (1 ~ 45)
original = list(range(1,46))


# 기능 1. 출현비율의 차이가 5%범위 이내가 되도록 한다.(결과적으로 모든 번호들이 균등하게 추출된다.)
# 기능 2. 그동안의 기록들(2002년 ~ )을 토대로 출현이 가장 높은/낮은 번호들을 보여준다.
# 기능 3. 추출번호목록에 반드시 포함하고 싶은 번호목록을 추가할 수 있다. 
# 기능 4. 추출번호목록에 반드시 제외하고 싶은 번호목록을 추가할 수 있다.
# 기능 5. 그동안의 추출 기록들에 기반한 경험적인 확률분포를 토대로 번호를 sampling 할 수 있다.


# 원격 저장소로부터 로또번호 추출기록데이터셋 불러오기
data_url = "https://raw.githubusercontent.com/changdaeoh/Lottery_Number_Generator/main/lotto_csv.csv"
history = pd.read_csv(data_url)
history = history.drop(['Round'],axis = 1).reset_index(drop = True) # 불필요한 컬럼 제거
flat_history = np.asarray(history).flatten() # 2차원 배열을 1차원으로 flatten
series_history = pd.Series(flat_history) # 1차원 배열을 pandas의 Series 자료형으로 변경
freq_series = series_history.value_counts() # Series 메서드를 이용해 각 번호별 빈도수를 카운트
freq_table = pd.DataFrame(freq_series) # Series 자료형을 데이터프레임으로 변경
freq_table = freq_table.reset_index()
freq_table.columns = [["num", "freq"]]
# 빈도들을 총 추출 숫자개수로 나눠 각 숫자의 추출비율을 구한다.
prop_table = freq_table
prop_table.iloc[:,1] = freq_table.iloc[:,1] / freq_table.iloc[:,1].sum()
# 해당 비율표를 숫자기준 오름차순으로 정렬한다.
prop_dist = prop_table.sort_values(by = prop_table.columns[0])



def lotto_gen(n_iter = 10000, sampling_size = 5, historical_prob = False):
    
    # 과거의 기록 
    print("****** 출현률 TOP 6 ******\n",prop_table.iloc[:6,:],'\n', sep = '')
    print("****** 출현률 BOTTOM 6 ******\n",prop_table.iloc[-6:,:][::-1], '\n',sep = '')
    
    # 포함/배제 목록 입력받기
    must_have_nums = input("포함시키고싶은 숫자들을 콤마(,)로 구분하여 입력하라 (없으면 enter) : ")
    must_have_nums = [int(x) for x in must_have_nums.split(',') if x != '']
    except_nums = input("배제시키고싶은 숫자들을 콤마(,)로 구분하여 입력하라 (없으면 enter) : ")
    except_nums = [int(x) for x in except_nums.split(',') if x != '']
    
    # 번호 추출 시작
    while(True): # 출현빈도의 비율 차이가 5% 이내가 될때까지 아래를 반복
    
        # step 1 ==========================================================================
        # 각 숫자의 빈도수를 누적 count하기위한 dictionary를 정의하고 빈도수들을 0으로 초기화
        freq_dict = {}
        for i in original:
            freq_dict[i] = 0 
        # 추출번호에 대한 경험분포를 dictionary 자료형으로 생성한다.
        prop_dict = {}
        for num, prop in enumerate(prop_dist.iloc[:,1]):
            prop_dict[num+1] = prop
            
            
        # step 2 ==========================================================================
        # 포함/배제하고싶은 번호목록이 있다면 해당 번호들을 제외한 번호리스트를 만든다.
        remain_set = set(original) - set(must_have_nums)
        remain_set = remain_set - set(except_nums)
        remain_list = list(remain_set)
        
        # 확률분포 목록에서도 포함/배제 번호들을 제거한다.
        for i in (must_have_nums + except_nums):
            del prop_dict[i]
        prop_df = pd.DataFrame(list(prop_dict.items()), columns = ["num", "prop"])

                    
        # step 3 ==========================================================================
        # 설정한 반복 수(디폴트 : 1만 번)만큼
        # 포함/배제 숫자들을 제외한 남은 숫자목록에서 (6-반드시포함할 숫자 개수)만큼의 수를 샘플링
        tot_samples = []
        
        if (historical_prob==True) and (len(must_have_nums + except_nums)!=0):
            print("\n과거의 경험분포를 사용하려면 포함배제목록을 입력하지 마세요")
            print("포함배제목록 입력단계를 enter 두번으로 건너뛰세요")
            break
        
        # 과거의 경험분포를 사용하여 샘플링하는 경우
        elif (historical_prob==True) and (len(must_have_nums + except_nums)==0):
            for _ in range(n_iter):
                subset_sample = np.random.choice(remain_list, 
                                                size = 6 - len(must_have_nums), 
                                                replace = False,
                                                p = list(prop_df.iloc[:,1]))
                subset_sample = list(subset_sample) # numpy array를 list로 변경
                epoch_sample = subset_sample + must_have_nums
                tot_samples.append(epoch_sample) # 반복마다 추출된 번호목록을 2차원 리스트에 누적
            # 각 반복별로 추출된 번호의 frequency를 1씩 증가시킨다.
            for i in original:
                if i in epoch_sample:
                    freq_dict[i] += 1

        else: # 과거 경험분포를 이용하지 않는 경우
            for _ in range(n_iter):
                subset_sample = rd.sample(remain_list, 6 - len(must_have_nums))
                epoch_sample = subset_sample + must_have_nums
                tot_samples.append(epoch_sample) 
            
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