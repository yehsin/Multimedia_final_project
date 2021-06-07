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
        
     # Initail
     def Initial(self):
     # Initail your session or something
        self.some_param = 0
     def ER(self,R,n ,N = 5):
         sum = 0.0
         for i in range(N-1):
             #print(sum)
             sum = sum + abs(R[n-i] - R[n-i-1])
         ERn = abs(R[n] - R[n-N]) / sum
         #print(ERn)
         return ERn
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

         target_buffer = 0
         latency_limit = 4
         if(S_send_data_size[-1]!= 0 and S_time_interval[-1]!= 0):
            actual_rate  = S_send_data_size[-1] / S_time_interval[-1]
            self.R.append(self.V_rate * actual_rate)
            #print(actual_rate)

            if(S_send_data_size[-1] != 0 and self.n > 5) :
                self.ER_value = self.ER(self.R,self.n,5)
            #print(self.ER_value)
            #if(S_send_data_size[-1] != 0 and self.n > 2):
            #    self.ema_value.append(self.EMA(self.n))

            

            self.SC_fast = 2/ (1 + 5)
            self.SC_slow = 2/ (1 + 50)

            #print(self.R_hat)

            self.SC = math.pow((self.ER_value * (self.SC_fast - self.SC_slow) + self.SC_slow),2)
            #a = (1-self.SC)*self.R_hat[self.n]  + self.SC * self.R[self.n]
            self.R_hat.append((1-self.SC)*self.R_hat[self.n]  + self.SC * self.R[self.n])
            self.n = self.n +1
            
            
            

            
         
         #print(self.R_hat)
         return bit_rate, target_buffer, latency_limit

         # If you choose other
         #......



     def get_params(self):
     # get your params
        your_params = []
        return your_params
