# import tensorflow as tf
#NN_MODEL = "./submit/results/nn_model_ep_18200.ckpt" # model path settings, if using ML-based method
import math

class Algorithm:
     def __init__(self):
     # fill your self params
        self.some_param = 0
        self.R = [0.0]
        self.R_hat = [1.0]
        self.V_rate = 1.5
        self.n = 0
        self.ER_value = 1.0
        self.SC = 0.0
        self.SC_slow = 1.0
        self.SC_fast = 1.0
        self.ema_value = []

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
             #print(sum)
             sum = sum + abs(R[n-i] - R[n-i-1])
         ERn = abs(R[n] - R[n-N]) / sum
         return ERn

     # Segment Bitrate Prediction
     def Seg_Bit_Pre(self, data_size, time_interval):
         
         actual_rate = data_size / time_interval
         self.R.append(self.V_rate * actual_rate) #formula 2

         if(data_size != 0 and self.n > 5) :
             self.ER_value = self.ER(self.R,self.n,5) #formula 6
            

             self.SC_fast = 2/ (1 + 5) #formula 4
             self.SC_slow = 2/ (1 + 50) #formula 5

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
            self.Seg_Bit_Pre(S_send_data_size[-1], S_time_interval[-1])

         return bit_rate, target_buffer, latency_limit

         # If you choose other
         #......



     def get_params(self):
     # get your params
        your_params = []
        return your_params
