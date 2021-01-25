# module setting
import random as rd
import pandas as pd
import numpy as np
from tkinter import *

# 전역변수로 정의한 로또번호 리스트 (1 ~ 45)
original = list(range(1,46))

# 과거 로또 추출번호 기록이 담긴 csv파일이 저장된 원격 저장소 url
url = "https://raw.githubusercontent.com/changdaeoh/Lottery_Number_Generator/main/lotto_csv.csv"


# 기능 1. 출현비율의 차이가 5%범위 이내가 되도록 한다.(결과적으로 모든 번호들이 균등하게 추출된다.)
# 기능 2. 그동안의 기록들(2002년 ~ )을 토대로 출현이 가장 높은/낮은 번호들을 보여준다.
# 기능 3. 추출번호목록에 반드시 포함하고 싶은 번호목록을 추가할 수 있다. 
# 기능 4. 추출번호목록에 반드시 제외하고 싶은 번호목록을 추가할 수 있다.
# 기능 5. 그동안의 추출 기록들에 기반한 경험적인 확률분포를 토대로 번호를 sampling 할 수 있다.


# sub-component 1 : 원격 저장소로부터 로또번호 추출기록데이터셋 불러오기
def get_historical_data(url):
    data_url = url
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

    return prop_table, prop_dist # 비율표와 sorting된 비율표(확률분포)를 return


# sub-component 2 : 포함/배제 숫자 목록 입력받기
def control_nums():
    include_nums = entry_include.get()
    include_nums = [int(x) for x in include_nums.split(',') if x != '']
    exclude_nums = entry_exclude.get()
    exclude_nums = [int(x) for x in exclude_nums.split(',') if x != '']
    return include_nums, exclude_nums


# main-component : 로또 번호 생성기
def lotto_gen(prop_dist = [], include_nums = [], exclude_nums = [], n_iter = 10000, sampling_size = 5, historical_prob = False):
    
    # 사용할 지역변수들 초기화
    prop_dist = prop_dist
    include_nums = include_nums
    exclude_nums = exclude_nums

    # 번호 추출 시작
    while(True): # 출현빈도의 비율 차이가 5% 이내가 될때까지 아래를 반복
    
        # step 1 ==========================================================================
        # 추출될 각 숫자의 빈도수를 누적하여 count하기위한 dictionary를 정의하고 빈도수를 0으로 초기화
        freq_dict = {}
        for i in original:
            freq_dict[i] = 0 
            
            
        # step 2 ==========================================================================
        # 포함/배제하고싶은 번호목록이 있다면 해당 번호들을 제외한 추출번호리스트를 만든다.
        remain_set = set(original) - set(include_nums)
        remain_set = remain_set - set(exclude_nums)
        remain_list = list(remain_set)

                    
        # step 3 ==========================================================================
        # 설정한 반복 수(디폴트 : 1만 번)만큼
        # 포함/배제 숫자들을 제외한 남은 숫자목록에서 (6-반드시포함할 숫자 개수)만큼의 수를 샘플링
        tot_samples = []
        
        
        # 과거의 경험분포를 사용하여 샘플링 진행 
        # -> 확률분포를 input으로 받아 샘플링하는 numpy의 random.choice를 이용
        if (historical_prob==True) and (len(include_nums + exclude_nums)==0):
            for _ in range(n_iter):
                subset_sample = np.random.choice(remain_list, 
                                                size = 6 - len(include_nums), 
                                                replace = False,
                                                p = list(prop_dist.iloc[:,1])) # 확률분포를 이용한 샘플링
                subset_sample = list(subset_sample) # numpy array를 list로 변경
                epoch_sample = subset_sample + include_nums
                tot_samples.append(epoch_sample) # 반복마다 추출된 번호목록을 2차원 리스트에 누적
            # 각 반복별로 추출된 번호의 frequency를 1씩 증가시킨다.
            for i in original:
                if i in epoch_sample:
                    freq_dict[i] += 1

        else: # 과거 경험분포를 이용하지 않는 경우
            for _ in range(n_iter):
                subset_sample = rd.sample(remain_list, 6 - len(include_nums))
                epoch_sample = subset_sample + include_nums
                tot_samples.append(epoch_sample) 
            
            for i in original:
                if i in epoch_sample:
                    freq_dict[i] += 1

                    
        # step 4 ==========================================================================
        # 모든 반복이 종료된 이후 (숫자 출현 횟수)/(전체 반복수)로 각 숫자의 총 출현 비율을 계산한다.
        # 총 출현 비율간의 차이가 5% 이상이 되는지 check해야하기 때문에 구한 것임.
        prop_dict = {}
        for i in original:
            prop_dict[i] = freq_dict[i] / n_iter
        
        
        # step 5 ==========================================================================
        # 출현비율 차이가 5% 이내인 경우, step2에서 추출한 전체 n_iter개의 샘플 중에서 
        # sampling_size 개수만큼을 subsampling하여 최종 추출번호로 활용한다.
        # 5% 이내가 아닐경우 다시 while문의 처음으로 돌아가 위의 과정들을 반복한다
        
        # 반드시 포함/배제하고자 하는 번호목록이 있는 경우, 해당 번호들은 항상 포함되거나 배제되어
        # 다른 랜덤추출 숫자들과 비율을 비교하는 것이 무의미하므로 if문을 활용해 경우를 나눈다.
        

        # 반드시 포함/배제를 원하는 번호목록이 없는 경우 - 전체 숫자들의 빈도 비교
        if (len(include_nums) == 0) and (len(exclude_nums) == 0): 
            # 출현비율 차이가 5% 미만일 경우 return문을 거쳐 while루프가 종료된다.
            if (max(prop_dict.values()) - min(prop_dict.values())) < 0.05:
                final_samples = rd.sample(tot_samples, sampling_size)
                return final_samples
        
        # 반드시 포함/배제를 원하는 번호목록이 있는 경우
        else: 
            for i in (include_nums + exclude_nums):
                del prop_dict[i] # 해당 번호들은 제외하고 남은 숫자들의 출현비율 체크
                
            if (max(prop_dict.values()) - min(prop_dict.values())) < 0.05:
                final_samples = rd.sample(tot_samples, sampling_size)
                return final_samples

def hist_samp():
    if entry_sampling_size.get() != '':
        hist_samples = lotto_gen(prop_dist = prop_dist, sampling_size = int(entry_sampling_size.get()) ,historical_prob = True)
    else:
        hist_samples = lotto_gen(prop_dist = prop_dist ,historical_prob = True)
    sample_str_list = []
    for ind, v in enumerate(hist_samples):
        v.sort()
        sample_str_list.append('추출번호{} : {}\n'.format(ind+1,v))
    label_result_list.configure(text = sample_str_list)

def normal_samp():
    include_nums, exclude_nums = control_nums()
    if entry_sampling_size.get() != '':
        normal_samples = lotto_gen(prop_dist = prop_dist, include_nums = include_nums, exclude_nums = exclude_nums, sampling_size = int(entry_sampling_size.get()))
    else:
        normal_samples = lotto_gen(prop_dist = prop_dist, include_nums = include_nums, exclude_nums = exclude_nums)
    sample_str_list = []
    for ind, v in enumerate(normal_samples):
        v.sort()
        sample_str_list.append('추출번호{} : {}\n'.format(ind+1,v))
    label_result_list.configure(text = sample_str_list)

# ===========================================================================================
# 정의한 함수들을 호출하여 번호추출 시작.
# tkinter 모듈을 활용한 그래픽 입히기

window = Tk()
window.title("Lotto645 numbers generator v1")
window.geometry("500x760")
window.resizable(False, False)

# title 표시
label_title = Label(window, text = "Lotto6/45 번호 생성기", font = ("이순신 돋움체 B", 30), bg = "white")
label_dev = Label(window, text = "개발자 : 2016580022 통계학과 오창대", font = ("이순신 돋움체 L", 9), bg = "white")
label_update = Label(window, text = "최근 업데이트 : 2021/01/24", font = ("이순신 돋움체 L", 9), bg = "white")

# 과거 기록 가져오기
prop_table, prop_dist = get_historical_data(url = url)

label_top6_title = Label(window, text = "****** 출현률 TOP 6 ******")
label_top6 = Label(window, text = prop_table.iloc[:6,:].to_string())
label_bot6_title = Label(window, text = "****** 출현률 BOTTOM 6 ******")
label_bot6 = Label(window, text = prop_table.iloc[-6:,:][::-1].to_string())

# 유의사항 레이블링
label_remark = Label(window, fg = "red", text = "====================   유의사항   ====================")
label_remark_text = Label(window, text = "경험분포를 이용한 추출을 시행할 경우, \n포함/배제하고싶은 숫자목록을 입력해도 해당번호가 포함되거나 배제되지 않습니다.")
label_remark_end = Label(window, fg = "red", text = "==================================================")

# 뽑을 세트 수 입력받기
label_sampling_size = Label(window, text = "몇 세트의 번호조합을 구매하시겠습니까? (5개 이하)")
entry_sampling_size = Entry(window, width = 5)

# 과거 경험분포를 이용한 로또번호 추출 버튼생성, 커맨드 설정
botton_hist = Button(window, text = "6개의 숫자를 경험적 누적확률분포로부터 추출하기!!", command = hist_samp)

# 포함 / 배제 입력받기
label_include = Label(window, text = "포함할 숫자를 콤마(,)를 구분자로 입력하시오 (없으면 공백)")
entry_include = Entry(window, width = 15)
label_exclude = Label(window, text = "배제할 숫자를 콤마(,)를 구분자로 입력하시오 (없으면 공백)")
entry_exclude = Entry(window, width = 15)

# 번호 추출 버튼생성, 커맨드 설정
botton_samp = Button(window, text = "번호 추출하기!!", command = normal_samp)

# 추출 결과 표시
label_result = Label(window, fg = "blue",text = "====================  번호 추출결과  ===================")
label_result_list = Label(window, text = '   추출된 번호가 없습니다.')

# 레이아웃 배치
label_title.pack(fill = 'x')
label_dev.pack(fill = 'x')
label_update.pack(fill = 'x')
label_top6_title.place(x = 55, y = 100)
label_top6.place(x = 75, y = 130)
label_bot6_title.place(x = 295, y = 100)
label_bot6.place(x = 325, y = 130)

label_remark.place(x = 38, y = 270)
label_remark_text.place(x = 10, y = 300)
label_remark_end.place(x = 38, y = 335)

label_sampling_size.place(x = 25, y = 375)
entry_sampling_size.place(x = 325, y = 375)
botton_hist.place(x = 96 , y = 406)
label_include.place(x = 25, y = 445)
entry_include.place(x = 370, y = 445)
label_exclude.place(x = 25, y = 470)
entry_exclude.place(x = 370, y = 470)
botton_samp.place(x = 212, y = 500)

label_result.place(x = 38, y = 570)
label_result_list.place(x = 165, y = 600)

window.mainloop()