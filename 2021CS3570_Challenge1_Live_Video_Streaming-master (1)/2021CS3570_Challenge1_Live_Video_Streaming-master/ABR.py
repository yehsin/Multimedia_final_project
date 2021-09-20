# import tensorflow as tf
from datetime import date
import math
#import ta_py as ta;
#NN_MODEL = "./submit/results/nn_model_ep_18200.ckpt" # model path settings
Bitrate = [500.0 * 1000.0 ,850.0 * 1000.0 ,1200.0 * 1000.0, 1850.0 * 1000.0]
TARGET_BUFFER = [0.5 , 1.0]
B_min_0 = 0.3
B_max_0 = 1.0
B_min_1 = 0.5
B_max_1 = 2.0
Lambda = 2.5 #2.5
t = 16 # 16
l_min = 2
l_max = 40 #40
WMA_len =35
Base_Bitrate = Bitrate[0]
class Algorithm:
     def __init__(self):
     # fill your self params
         self.buffer_size = 0
         self.R = []
         self.R_hat = [0]  # base on quality 0
         self.cur_Quality = 0
         self.prev_cdn_newest_id =0 
     # Intial
         self.n = 0
         self.a = 0
         self.b = 0
     def Initial(self):
     # Initail your session or something

     # restore neural net parameters
         self.buffer_size = 0

     def WMA_for_C(self,data,time_interval,n):
         init = 0.0
         s = 0.0
         n = min(len(data),n)
         for i in range(1, n+1):
             init = init + i
             weight = 1.0 / init
         for j in range(n):
             if(time_interval[j] == 0): continue
             else : s = s + (data[j] / time_interval[j]) * weight * (j+1)
         return s

     def Bitrate_Control(self,next_R_hat,next_Gamma,d,N_nst,prev_N_nst,N_dld,cur_B,data,time_interval):
         tmp_arr = []
         for i in range(len(Bitrate)):
             next_C = self.WMA_for_C(data[-30:],time_interval[-30:],WMA_len)
             next_R_hat = next_R_hat*(Bitrate[i]/Base_Bitrate) #Modify bitrate to current indicated quality
             next_T = (next_R_hat * d)/next_C
             next_B = max(cur_B + d - next_Gamma*next_T,0)
             

             cur_T = data[-1]/time_interval[-1]
             next_v_hat = 1*(N_nst - prev_N_nst)/cur_T*d
             next_D_cdn = max((N_nst-N_dld)*d+next_v_hat*next_T,0)
             #print(next_B,next_D_cdn)
             if(next_B > B_min_0):
                 tmp_arr.append(next_B+next_D_cdn)
         if len(tmp_arr) != 0:
             quality = tmp_arr.index(min(tmp_arr))
             next_Delay = tmp_arr[quality]
         else:
             quality = 0
             next_Delay = 0
         return (next_Delay ,quality)


     def ER(self, R, n ,N ):
         s = 0.0
         for i in range(N):
             #print(sum)
             s = s + abs(float(R[n-i])  - float(R[n-i-1]) )  
         if s != 0:
             ERn = abs(float(R[n])  - float(R[n-N]) ) / s
         else:
             ERn = 0
         #print("ER",ERn)
         return ERn


     #Segment Bitrate Prediction
     def KAMA_R_hat(self,cur_R_hat,R,n,l_min,l_max):
         ER_value = self.ER( R = R, n = len(R)-1, N = n) #formula 6
		
         SC_fast = 2.0/ (1 + l_min) #formula 4
         SC_slow = 2.0/ (1 + l_max) #formula 5

         SC = math.pow((ER_value * (SC_fast - SC_slow) + SC_slow),2) #formula 7
		
         return ((1-SC)*cur_R_hat  + SC * R[-1]) #formual 3
     def SMA(self, cur_R_hat, n):
         sum = 0
         for i in range(n):
             sum = sum + self.R_hat[-(i+1)]
         return sum / n

     def Segment_Bitrate_Predict(self,cur_R_hat,R,n,l_min,l_max):
         return self.KAMA_R_hat(cur_R_hat = cur_R_hat,R = R,n = n,l_min = l_min,l_max = l_max) 
         #return self.SMA(cur_R_hat = cur_R_hat, n=n)
     #Define your al
     def Playback_Rate_Control(self,Buffer_size):
         target = 0
         Gamma = 0.95
		 #for target buffer
         if(Buffer_size >= B_min_0 and Buffer_size < B_max_0):
             target = 1
         else:
             target = 0
	

		 #for Gamma
         if(Buffer_size >= 0 and Buffer_size < B_min_0):
             Gamma = 0.95
         elif(Buffer_size >= B_min_1 and Buffer_size < B_max_0):
             Gamma = 1.0
         else:
             Gamma = 1.05

         return (target, Gamma)
     def Frame_Dropping_Control(self,next_quality,Delays):
         frame_time_len = 0.04
         LATENCY_PENALTY = 0.0
         if Delays[-1] <= 1.0:
             LATENCY_PENALTY = 0.005
         else:
             LATENCY_PENALTY = 0.01
         
         SKIP_PENALTY = 0.5
         next_latency_limit =  (Bitrate[next_quality]/1000.0/1000.0+SKIP_PENALTY)*frame_time_len/(LATENCY_PENALTY*Lambda)
         return next_latency_limit

     def run(self, time, S_time_interval, S_send_data_size, S_chunk_len, S_rebuf, S_buffer_size, S_play_time_len,S_end_delay, S_decision_flag, S_buffer_flag,S_cdn_flag,S_skip_time, end_of_video, cdn_newest_id,download_id,cdn_has_frame,IntialVars):
         #print(len(S_send_data_size[-1]), len(S_time_interval))
         
         bit_rate = 0
         target_buffer,next_Gamma = self.Playback_Rate_Control(S_buffer_size[-1])
         if(len(self.R) >= t and S_time_interval[-1]!= 0):
             #print(actual,S_send_data_size[-1]/S_chunk_len[-1])
             cur_R_hat = self.R_hat[-1]
             #S_send_data_size[-1]/S_chunk_len[-1]
             self.R.append(S_send_data_size[-1]/S_chunk_len[-1]*(Base_Bitrate/Bitrate[self.cur_Quality]))
             #print(self.R[-1]/1024/1024,",",time,",",self.R_hat[-1]/1024/1024,",",time)
             next_R_hat = self.Segment_Bitrate_Predict(cur_R_hat = cur_R_hat, R = self.R,n = t, l_min = l_min,l_max = l_max)
             #next_R_hat = ta.kama(self.R,t,l_min,l_max)[-1]
             self.n = self.n + 1
             self.a = self.a + (abs(cur_R_hat-self.R[-1]))/self.R[-1]
         #    print(time)
             #print(time,self.R[-1],time,cur_R_hat )
        
             #print(self.a/self.n)
             self.R_hat.append(next_R_hat)

             next_Delay,bit_rate = self.Bitrate_Control(
									next_R_hat = next_R_hat
									,next_Gamma = next_Gamma
									,d = S_chunk_len[-1]
									,N_nst = cdn_newest_id
									,prev_N_nst = self.prev_cdn_newest_id
									,N_dld = download_id
									,cur_B = S_buffer_size[-1]
									,data = S_send_data_size
									,time_interval = S_time_interval
									)
             latency_limit = self.Frame_Dropping_Control(next_quality=bit_rate,Delays=S_end_delay)


         else:
             self.R.append(0.0)
             self.R_hat.append(0.0)
             bit_rate = 0
             latency_limit = 4
         self.prev_cdn_newest_id = cdn_newest_id
         self.cur_Quality=bit_rate 
         if(end_of_video):
             bit_rate = 0

         return bit_rate, target_buffer, latency_limit




     def get_params(self):
     # get your params
        your_params = []
        return your_params
