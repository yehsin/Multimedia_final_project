#from typing import Optional
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.python.keras.layers.core import Dropout
#NN_MODEL = "./submit/submit/results/nn_model_ep_18200.ckpt" # model path settings, if using ML-based method


gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # Currently, memory growth needs to be the same across GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        # Select GPU number 1
        tf.config.experimental.set_visible_devices(gpus[2], 'GPU')
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        # Memory growth must be set before GPUs have been initialized
        print(e)

#@tf.function
#def load_model():
#    saver = tf.compat.v1.train.import_meta_graph('./submit/submit/results/nn_model_ep_18200.ckpt.meta')
#    print(saver)

    


class Algorithm:
     def __init__(self):
     # fill your self params
        self.some_param = 0
        #self.action = 3
        #self.learning_rate = 0.05
        #self.input_size = 1
        #self.layer = 128
        #self.output = 3
    
     # Initail
     def Initial(self):
     # Initail your session or something
        self.some_param = 0
        #param = {
            #'w1': np.random.randn(self.layer, self.input_size) * np.sqrt(1./self.input_size),
           # 'w2': np.random.randn(self.output, self.layer)* np.sqrt(1./self.layer),
          #  'b1': np.zeros((self.layer, 1)) * np.sqrt(1./self.input_size),
         #   'b2': np.zeros((self.output, 1)) * np.sqrt(1./self.layer)
        #}
        #return param
     #def Model():
         #model = tf.keras.Sequential([tf.keras.layers.Flatten(input_shape=(28, 28)),
        # tf.keras.layers.Dense(128, activation='relu'),
        # tf.keras.layers.Dropout(0.2),
        # tf.keras.layers.Dense(128)],
        # tf.keras.layers.Dropout(0.2),
        # tf.keras.layers.Dense(3)
        #)
        

     # Define your algo
     def run(self, time, S_time_interval, S_send_data_size, S_chunk_len, S_rebuf, S_buffer_size, S_play_time_len,S_end_delay, S_decision_flag, S_buffer_flag,S_cdn_flag,S_skip_time, end_of_video, cdn_newest_id,download_id,cdn_has_frame,IntialVars):
         print("S_send_data_size: ",S_send_data_size[-1])
         print("S_chunk_len: ",S_chunk_len[-1])
         print("S_rebuf",S_rebuf[-1])
         print("S_budder_size: ",S_buffer_size[-1])
         print("S_paly_time: ",S_play_time_len[-1])
         print("S_end_delay: ",S_end_delay[-1])
         print("S_decision_flag: ", S_decision_flag[-1])
         print("S_buffer_flag: ",S_buffer_flag[-1])
         print("S_cdn_flag: ", S_cdn_flag[-1])
         print("S_skip_time: ",S_skip_time[-1])
         print("end_of_video: ",end_of_video)
         print("cdn_newest_id: ",cdn_newest_id)
         print("download_id: ",download_id)
         print("cdn_has_frame: ",cdn_has_frame)
         print("IntialVars: ",IntialVars)

         # If you choose the marchine learning
         
         '''state = []

         state[0] = S_buffer_size[-1]
         state[1] = S_end_delay[-1]
         state[2] = S_skip_time[-1]
         state[3] = 
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
         if S_buffer_size[-1] >= 0.5 and S_buffer_size[-1] < 1.0:
             target_buffer = 1
         else :
             target_buffer = 0
         #if S_buffer_size[-1] < RESEVOIR:
         #    latency_limit = 1
         #elif S_buffer_size[-1] >= CUSHION + CUSHION:
         #    latency_limit = 4
         #elif S_buffer_size[-1] >= RESEVOIR + CUSHION and S_buffer_size[-1] < CUSHION +CUSHION:
         #     latency_limit = 3
         #else:
         #    latency_limit = 2
         #target_buffer = 0
         latency_limit = 4



         return bit_rate, target_buffer, latency_limit

         # If you choose other
         #......
         #BBA-0
          

         #BOLA

         #BOLA-F`

         #BOLA-E





     def get_params(self):
     # get your params
        your_params = []
        return your_params
