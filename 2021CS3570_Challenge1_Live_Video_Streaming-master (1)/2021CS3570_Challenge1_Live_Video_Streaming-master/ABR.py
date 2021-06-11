# import tensorflow as tf
#NN_MODEL = "./submit/results/nn_model_ep_18200.ckpt" # model path settings, if using ML-based method
import math

Bitrate = [500.0 * 1024.0 ,850.0 * 1024.0 ,1200.0 * 1024.0, 1850.0 * 1024.0]

class Algorithm:
     def __init__(self):
     # fill your self params
        self.some_param = 0
        self.history_bitrate = []
        self.R = [0.0]
        self.R_hat = [1.0]
        self.V_rate = 1.5
        self.n = 0
        self.ER_value = 1.0
        self.SC = 0.0
        self.SC_slow = 1.0
        self.SC_fast = 1.0
        self.ema_value = []
        self.current_bitrate = 500.0 * 1024.0
        self.predict_time = []
        self.last_cdn_idx = 0
        

        #------default setting-----------
        self.B_min_0 = 0.3
        self.B_max_0 = 1.0
        self.B_min_1 = 0.5
        self.B_max_1 = 2.0

        self.Gamma = 0.95
        
     # Initail
     def Initial(self):
     # Initail your session or something
        self.some_param = 0

     def ER(self, R, n ,N = 5):
         sum = 0.0
         for i in range(N-1):
             m = Bitrate[self.history_bitrate[-1 + i]] / self.current_bitrate
             #print(sum)
             sum = sum + abs(R[n-i] * m - R[n-i-1] * m)
         ERn = abs(R[n] * m - R[n-N] * m) / sum
         return ERn

     # Segment Bitrate Prediction
     def Seg_Bit_Pre(self, data_size, time_interval):
         
         actual_rate = data_size / 0.04
         #print(actual_rate / 1024.0)
         self.R.append(self.V_rate * actual_rate) #formula 2
         

         if(data_size != 0 and self.n > 5) :
             self.ER_value = self.ER(self.R, self.n, 5) #formula 6
            

             self.SC_fast = 2/ (1 + 2) #formula 4
             self.SC_slow = 2/ (1 + 3) #formula 5

             self.SC = math.pow((self.ER_value * (self.SC_fast - self.SC_slow) + self.SC_slow),2) #formula 7
            
             self.R_hat.append((1-self.SC)*self.R_hat[self.n]  + self.SC * self.R[self.n]) #formual 3

             self.n = self.n +1
         return 
    
     #formula 8 9
     def decision_target_BUf(self,Buffer_size):
         target = 0 
         Gamma = 0.95
         if(Buffer_size >= self.B_min_0 and Buffer_size < self.B_max_0):
             target = 1
         else:
             target = 0
         if(Buffer_size >= 0 and Buffer_size < self.B_min_0):
             Gamma = 0.95
         elif(Buffer_size >= self.B_min_1 and Buffer_size < self.B_max_0):
             Gamma = 1.0
         else:
             Gamma = 1.05
         return (target, Gamma)
     
     def network_throughput(self,time_interval,data,n):
         init = 0.0
         sum = 0.0
         for i in range(1, n+1):
             init = init + i
         weight = 1.0 / init
         #print(weight)
         for j in range(n):
             #print(data[j])
             if(time_interval[j] == 0): continue
             else : sum = sum + (data[j] / time_interval[j]) * weight * (j+1)
         #total = n * (n+1) / 2.0
         #print(sum)
         return sum


     def downloading_time(self,r,d,time_interval,data,slice):
         throughput = self.network_throughput(time_interval,data,slice)
         return (r * d) / throughput #formula 10
    
     def predict_V(self, beta, cdn_idx , d, cur_predict_time):
         return beta * ((cdn_idx - self.last_cdn_idx) * d / cur_predict_time)

     def Bitrate_control(self, r, d, time_interval , data, slice, buffer_size, cdn_idx, dld, time):

         bitrates = []
         D_cdn = []
         tmp_cdn = []
         threhold = self.B_min_0

         for i in range(len(Bitrate)):

             bitrates.append(self.R_hat[-1] * self.current_bitrate / Bitrate[i])

             predict_time = self.downloading_time(bitrates[-1],d,time_interval[-slice:],data[-slice:],slice) #10
         
             next_buffer_size = max(buffer_size + d - predict_time * self.Gamma, 0) #11

             next_V = self.predict_V(beta = 1.0, cdn_idx = cdn_idx, d=d, cur_predict_time = time) #12
         
             Distance = max((cdn_idx - dld) * d + next_V * predict_time - d, 0 ) #13

             D = next_buffer_size + Distance #14

             D_cdn.append(D)

             if(next_buffer_size > threhold):
                 tmp_cdn.append(D)
         #print(tmp_cdn)
         if(len(tmp_cdn) != 0): idx = D_cdn.index(min(tmp_cdn))
         else: idx = 0

         return idx

     # Define your algo
     def run(self, time, S_time_interval, S_send_data_size, S_chunk_len, S_rebuf, S_buffer_size, S_play_time_len,S_end_delay, S_decision_flag, S_buffer_flag,S_cdn_flag,S_skip_time, end_of_video, cdn_newest_id,download_id,cdn_has_frame,IntialVars):
         
         # If you choose the marchine learning
         '''state = []

         state[0] = ...
         state[1] = ...
         state[2] = ...
         state[3] = ...
         state[4] = ...

         decision = actor.predict(state).argmax()
         bit_rate, target_buffer = decison//4, decison % 4 .....
         return bit_rate, target_buffer'''


         # If you choose BBA
         RESEVOIR = 0.5
         CUSHION =  1.5

         new_bitrate = 0
         
         if S_buffer_size[-1] < RESEVOIR:
             bit_rate = 0    
         elif S_buffer_size[-1] >= RESEVOIR + CUSHION and S_buffer_size[-1] < CUSHION +CUSHION:
             bit_rate = 2
         elif S_buffer_size[-1] >= CUSHION + CUSHION:
             bit_rate = 3
         else:
             bit_rate = 1
         
         #decision targetbuffer and gamma
         target_buffer, self.Gamma = self.decision_target_BUf(S_buffer_size[-1])
         #target_buffer = 0
         latency_limit = 4

         if(S_send_data_size[-1]!= 0 and S_time_interval[-1]!= 0):

            download_time = S_send_data_size[-1] / S_time_interval[-1]

            self.Seg_Bit_Pre(S_send_data_size[-1], S_time_interval[-1])

            bit_rate = self.Bitrate_control(r=self.R_hat[-1], d=S_chunk_len[-1], data=S_send_data_size,time_interval = S_time_interval ,slice=20, buffer_size=S_buffer_size[-1], cdn_idx=cdn_newest_id, dld=download_id, time=download_time)

         self.last_cdn_idx = cdn_newest_id
         
         self.current_bitrate = Bitrate[bit_rate]

         self.history_bitrate.append(bit_rate)

         #print(self.current_bitrate)
         #print(bit_rate, new_bitrate)

         return bit_rate, target_buffer, latency_limit

         # If you choose other
         #......

     def get_params(self):
     # get your params
        your_params = []
        return your_params
