import threading
import time
import subprocess
from datetime import datetime
import os
from urllib.parse import urlparse, urlunparse

# import ffmpeg
from onvif import ONVIFCamera
from persiantools import jdatetime


import time,cv2
from vidgear.gears import CamGear, WriteGear


H265 = 'libx265'
H264 = 'libx264'
NONE_CODEC = 'copy'
MPEG = 'mpeg2video'


def UrlGenerator(ip,port,username,password):

        # اتصال به دوربین ONVIF
        onvif_camera = ONVIFCamera(host=ip, port=port, user=username, passwd=password)

        # دریافت سرویس مدیا و پروفایل
        media_service = onvif_camera.create_media_service()
        profiles = media_service.GetProfiles()

        stream_setup = {
            'Stream': 'RTP-Unicast',
            'Transport': {
                'Protocol': 'RTSP'
            }
        }

        # دریافت StreamUri
        stream_uri = media_service.GetStreamUri({
            'StreamSetup': stream_setup,
            'ProfileToken': profiles[0].token
        })

        # تجزیه URL برای بررسی ساختار
        parsed_uri = urlparse(stream_uri.Uri)

        # اضافه کردن احراز هویت (username و password)
        netloc_with_auth = f"{username}:{password}@{parsed_uri.netloc}"
        updated_uri = parsed_uri._replace(netloc=netloc_with_auth)
        final_url = urlunparse(updated_uri)


        #-----------------------------------------------------------

        return final_url

        # except Exception as e:
        #     # مدیریت خطا
        #     #print(e)
        #     return None




# class vidGear():
    
#     def __init__(self,
#                  name:str, 
#                  username:str, 
#                  password:str, 
#                  ip:str, 
#                  port:str,
#                  train_id:str,
#                  fps:int,
#                  codec,
#                  signal_show:Signal,
#                  show_flag:bool,
#                  segments = 300,
#                  org_fps = 25,
#                  temp_folder = 'temp_videos',
#                  motion=False,

#                  logger = dorsa_logger.logger
                 
#                  ) -> None:
#         super().__init__()
#         self.name = name
#         self.username = username
#         self.password = password
#         self.train_id = train_id
#         self.port = port
#         self.ip = ip
#         self.fps = fps
#         self.org_fps = org_fps
#         self.segments = segments
#         self.temp_folder = temp_folder
#         self.loop_index = 0
#         self.signal_show= signal_show
#         self.show_flag = show_flag
#         self.motion = bool(motion)

#         self.onvif_camera = None
        
#         self.worker_motion = None
#         self.thread_motion:threading.Thread = None
#         self.motion_status = False

#         codesc = {
#            'none':NONE_CODEC,
#            'mpeg':MPEG,
#            'h265':H265,
#            'h264': H264
#         }
#         self.codec = codesc.get(codec, NONE_CODEC)

#         self.logger = logger

#         self.daemon = True
#         self.proccess = None
#         self.runing = True


#     def set_show_flag(self,mode):
#         self.show_flag = mode


#     def get_stream_url(self):
#         try:
#             # اتصال به دوربین ONVIF
#             self.onvif_camera = ONVIFCamera(host=self.ip, port=self.port, user=self.username, passwd=self.password)

#             # دریافت سرویس مدیا و پروفایل
#             media_service = self.onvif_camera.create_media_service()
#             profiles = media_service.GetProfiles()

#             stream_setup = {
#                 'Stream': 'RTP-Unicast',
#                 'Transport': {
#                     'Protocol': 'RTSP'
#                 }
#             }

#             # دریافت StreamUri
#             stream_uri = media_service.GetStreamUri({
#                 'StreamSetup': stream_setup,
#                 'ProfileToken': profiles[0].token
#             })

#             # تجزیه URL برای بررسی ساختار
#             parsed_uri = urlparse(stream_uri.Uri)

#             # اضافه کردن احراز هویت (username و password)
#             netloc_with_auth = f"{self.username}:{self.password}@{parsed_uri.netloc}"
#             updated_uri = parsed_uri._replace(netloc=netloc_with_auth)
#             final_url = urlunparse(updated_uri)

#             #-----------------------------------------------------------
#             log_msg = dorsa_logger.log_message(
#                 level=dorsa_logger.log_levels.DEBUG,
#                 text=f"stream uri camera {self.name}: {final_url}",
#                 code="FCGSU000"
#             )
#             self.logger.create_new_log(message=log_msg)
#             #-----------------------------------------------------------

#             return final_url

#         except Exception as e:
#             # مدیریت خطا
#             log_msg = dorsa_logger.log_message(
#                 level=dorsa_logger.log_levels.ERROR,
#                 text=f"Failed to get stream URL for camera {self.name}: {str(e)}",
#                 code="FCGSU001"
#             )
#             self.logger.create_new_log(message=log_msg)
#             return None


#     def setup_camera(self, ):
#         try:
#             media_service = self.onvif_camera.create_media_service()

#             profiles = media_service.GetProfiles()

#             # Use the first profile and Profiles have at least one
#             token = profiles[0].token

#             # Get all video encoder configurations
#             configurations_list = media_service.GetVideoEncoderConfigurations()

#             # Use the first profile and Profiles have at least one
#             video_encoder_configuration = configurations_list[0]

#             # Get video encoder configuration options
#             options = media_service.GetVideoEncoderConfigurationOptions({'ProfileToken':token})

#             # Setup stream configuration
#             video_encoder_configuration.Encoding = 'H264'
#             # Setup Resolution
#             video_encoder_configuration.Resolution.Width = options.H264.ResolutionsAvailable[0].Width
#             video_encoder_configuration.Resolution.Height = options.H264.ResolutionsAvailable[0].Height
#             # Setup Quality
#             video_encoder_configuration.Quality = int((options.QualityRange.Min + options.QualityRange.Max)/2)
#             # Setup FramRate
#             video_encoder_configuration.RateControl.FrameRateLimit = min(options.H264.FrameRateRange.Max, self.fps)
#             # Setup Gov Lenght
#             #video_encoder_configuration = max(min(options.H264.GovLengthRange.Max, self.fps), options.H264.GovLengthRange.Min)


#             # Create request type instance
#             request = media_service.create_type('SetVideoEncoderConfiguration')
#             request.Configuration = video_encoder_configuration
#             # ForcePersistence is obsolete and should always be assumed to be True
#             request.ForcePersistence = True

#             # Set the video encoder configuration
#             media_service.SetVideoEncoderConfiguration(request)
#         except Exception as e:
#             #-----------------------------------------------------------
#             log_msg = dorsa_logger.log_message(level=dorsa_logger.log_levels.ERROR,
#                                                 text=f"error happend in setup camera {self.name}: {e}", 
#                                                 code="FCSC000")
#             self.logger.create_new_log(message=log_msg)
#             #-----------------------------------------------------------


    
#     def add_write_info_filter(self, stream):
        
#         stream = ffmpeg.filter(stream,
#                               filter_name='drawtext', 
#                               text='%{localtime}', #'%{localtime}'
#                               fontfile='arial.ttf',
#                               fontcolor='white',
#                               fontsize=48,
#                               box= 1,
#                               boxborderw= 20,
#                               boxcolor= 'black',
#                               shadowx= 2,   
#                               shadowy= 2,
#                               x=25,
#                               y=40)

#         date = jdatetime.JalaliDateTime.now()
#         text = date.strftime('%Y/%m/%d')
#         stream = ffmpeg.filter(stream, 
#                               filter_name='drawtext', 
#                               text=text,
#                               fontfile='arial.ttf',
#                               fontcolor='white',
#                               fontsize=48,
#                               box= 1,
#                               boxborderw= 20,   
#                               boxcolor= 'black',
#                               shadowx= 2,           
#                               shadowy= 2,                     
#                               x=30,
#                               y=40)
        
#         text = f'Train: {self.train_id} - Camera: {self.name} '
#         stream = ffmpeg.filter(stream, 
#                               filter_name='drawtext', 
#                               text=text,
#                               fontfile='arial.ttf',
#                               fontcolor='white',
#                               fontsize=48,
#                               box= 1,
#                               boxborderw= 20,   
#                               boxcolor= 'black',
#                               shadowx= 2,           
#                               shadowy= 2,                     
#                               x=600,
#                               y=40)
        
#         return stream
    

#     def build_path(self, ):
#         output_dir = os.path.join(self.temp_folder,self.name)
#         if not os.path.exists(output_dir):
#           #-----------------------------------------------------------
#           log_msg = dorsa_logger.log_message(level=dorsa_logger.log_levels.DEBUG,
#                                             text=f"ffmpegCamera build temp folder for camera {self.name}: {output_dir}", 
#                                             code="FCBP000")
#           self.logger.create_new_log(message=log_msg)
#           #-----------------------------------------------------------
#           os.makedirs(output_dir)

#         fname = f'video_{self.loop_index}_{self.name}' + '_%04d.mp4'
#         self.loop_index+=1
#         return output_dir, fname
    

    


#     def build_and_run_stream(self, rstp_url, output_path):
#         options = {
#             # "CAP_PROP_FRAME_WIDTH": 320, # resolution 320x240
#             # "CAP_PROP_FRAME_HEIGHT": 240,
#             "CAP_PROP_FPS": 25, # framerate 60fps
#         }
#         stream = CamGear(source=rstp_url).start()
        


#         # Hardware-accelerated encoding parameters
#         output_params = {
#             "-vcodec": MPEG,        # Software encoder
#             "-preset": "ultrafast",      # Fastest preset for x264
#             "-threads": "4",             # Number of threads to use
#             "-pix_fmt": "yuv420p",       # Compatible pixel format
#             "-input_framerate": stream.framerate
#         }

#         # Initialize variables
#         video_counter = 0

#         writer = None
#         output_dir, output_fname = self.build_path()

#         frame_cnt = 0

#         self.camrea_connection = True

#         while self.camrea_connection and self.runing:

#             if self.motion:
#                 motion_frames = []

#                 while not self.motion_status and self.runing:
#                     frame = stream.read()
#                     if frame is None:
#                         #print('frame is NOne')
#                         self.camrea_connection = False
#                         break
#                     motion_frames.append(frame)
#                     if len(motion_frames) >= 2:
#                         self.check_motion(motion_frames, join=True)
#                         motion_frames = []
#                     cv2.waitKey(1)

#                 t_motion = time.time()

#                 start_time = time.time()



#                 #print('milad'*80)

#                 while (self.motion_status or time.time() - start_time < 2*60) and self.runing:
                        
#                         # #print('motion_status',self.motion_status)
                    
#                         frame = stream.read()
#                         if frame is None:
#                             #print('frame is NOne')
#                             self.camrea_connection = False
#                             break
#                         if time.time()- t_motion > 10:
#                             motion_frames.append(frame)
#                             if len(motion_frames) >= 2:
#                                 self.check_motion(motion_frames, join=False)
#                                 motion_frames = []
#                                 t_motion = time.time()
                        

                        
#                         # #print(time.time()-t , type(frame),frame.size)

#                 #         # If no frame is received, stop the stream
#                 #         if frame is None:
#                 #             break

#                 #         # Emit resized frame every other frame for display
#                         if frame_cnt % 3 == 0 and self.show_flag:
#                             show_frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
#                             self.signal_show.emit(show_frame)


#                 #         # Start a new video file every 60 seconds
#                         if writer is None or time.time() - start_time >= 10 * 60:
#                             if writer:
#                                 writer.close()
#                             output_dir, output_fname = self.build_path()
#                             output_path = os.path.join(output_dir, output_fname)
#                             output_path = output_path.replace('%04d', f'{video_counter:04d}')
#                             video_counter += 1
#                             start_time = time.time()
#                             writer = WriteGear(output=output_path, compression_mode=True, logging=True, **output_params)
#                             #print(f"Started recording: {output_path}")

#                 #         # # Write the current frame to the video fil

#                         writer.write(frame)
#                         frame_cnt += 1
#                         cv2.waitKey(1)
#                     # time.sleep(0.02)



#             else:


                
#                 while self.runing:
                        
#                         # #print('motion_status',self.motion_status)
                    
#                         frame = stream.read()
#                         if frame is None:
#                             #print('frame is NOne')
#                             self.camrea_connection = False
#                             break
                        

                        
#                         # #print(time.time()-t , type(frame),frame.size)

#                 #         # If no frame is received, stop the stream
#                 #         if frame is None:
#                 #             break

#                 #         # Emit resized frame every other frame for display
#                         if frame_cnt %2 == 0 and self.show_flag:
#                             show_frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
#                             self.signal_show.emit(show_frame)


#                 #         # Start a new video file every 60 seconds
#                         if writer is None or time.time() - start_time >= 10 * 60:
#                             if writer:
#                                 writer.close()
#                             output_dir, output_fname = self.build_path()
#                             output_path = os.path.join(output_dir, output_fname)
#                             output_path = output_path.replace('%04d', f'{video_counter:04d}')
#                             video_counter += 1
#                             start_time = time.time()
#                             writer = WriteGear(output=output_path, compression_mode=True, logging=True, **output_params)
#                             #print(f"Started recording: {output_path}")

#                 #         # # Write the current frame to the video fil

#                         writer.write(frame)
#                         frame_cnt += 1
#                         cv2.waitKey(1)




#             if writer is not None: # or time.time() - start_time >= 10 * 60:
#                 writer.close()
#                 writer=None
#         #         time.sleep(0.01)


#         if writer is not None: # or time.time() - start_time >= 10 * 60:
#             try:
#                 writer.close()
#             except:
#                 pass
#             writer = None


#         # finally:
#         #     # Cleanup resources
#         #     if writer:
#         #         writer.close()
#         #     stream.stop()


#         # finally:
#         #     # Release resources
#         #     stream.stop()
#         #     if writer:
#         #         writer.close()
#         #     #print("Recording stopped and resources released.")




#         # stream = ffmpeg.input(rstp_url, 
#         #                       ss=0,
#         #                       rtsp_transport='tcp',
#         #                       timeout ='5000000', 
#         #                         )
#         # # stream = self.add_write_info_filter(stream)
#         # # stream = ffmpeg.filter(stream, 'fps', fps=self.fps, round='up')

#         # stream = ffmpeg.output(stream, 
#         #                output_path, 
#         #                vcodec=self.codec,
#         #                f='segment',  # استفاده از فیلتر segment
#         #                segment_time=str( int(self.segments * self.fps/self.org_fps )),
#         #                reset_timestamps='1',
#         #             #    crf=50,
#         #             #    preset='faster',  # کاهش سرعت پردازش
#         #             #    tune='zerolatency'
#         #              )
        
#         # stream = ffmpeg.overwrite_output(stream)

#         # try:
#             # self.proccess = ffmpeg.run(stream, quiet=False, ) 
#             #-----------------------------------------------------------
#         #     log_msg = dorsa_logger.log_message(level=dorsa_logger.log_levels.WARNING,
#         #                                    text=f"ffmpeg run output {self.name}: {self.proccess}", 
#         #                                    code="FCR001")
#         #     self.logger.create_new_log(message=log_msg)
#         #     #-----------------------------------------------------------        
#         # except ffmpeg.Error as e:
#         #     #-----------------------------------------------------------
#         #     log_msg = dorsa_logger.log_message(level=dorsa_logger.log_levels.ERROR,
#         #                                        text=f"error occured in build_and_run_stream: {e.stderr.decode()}", 
#         #                                        code="FCBARS000")
#         #     self.logger.create_new_log(message=log_msg)
#         #     #-----------------------------------------------------------
#         # except KeyboardInterrupt:
#         #     #-----------------------------------------------------------
#         #     log_msg = dorsa_logger.log_message(level=dorsa_logger.log_levels.ERROR,
#         #                                        text=f"recoed stop manualy {self.name}", 
#         #                                        code="FCBARS001")
#         #     self.logger.create_new_log(message=log_msg)
#         #     #-----------------------------------------------------------

#     def check_motion(self, frames, join=False):
#         if self.thread_motion is None or not self.thread_motion.is_alive():
#             self.worker_motion = motionDetection(frames, 20, 350000)
#             self.worker_motion.motion_signal.connect(self.update_motion_status)
#             self.thread_motion = threading.Thread(target= self.worker_motion.check_motion)
#             self.thread_motion.start()
#             if join:
#                 self.thread_motion.join()


#     def update_motion_status(self, status):
#         self.motion_status = status

#     def terminate_ffmpeg(self,):
#         #-----------------------------------------------------------
#         log_msg = dorsa_logger.log_message(level=dorsa_logger.log_levels.DEBUG,
#                                                text=f"terminate ffmpeg {self.name}", 
#                                                code="FCTF000")
#         self.logger.create_new_log(message=log_msg)
#         #-----------------------------------------------------------
#         if self.proccess is not None:
#             try:
#                 self.proccess.terminate()
#             except Exception as e:
#                 #-----------------------------------------------------------
#                 log_msg = dorsa_logger.log_message(level=dorsa_logger.log_levels.ERROR,
#                                                     text=f"terminate ffmpeg {self.name}:{e}", 
#                                                     code="FCTF001")
#                 self.logger.create_new_log(message=log_msg)
#                 #-----------------------------------------------------------
#     def stop_thread(self,):
#         self.runing =False
#         #print('runing',self.runing)

#     def run(self,):
#       self.runing = True
#       #-----------------------------------------------------------
#       log_msg = dorsa_logger.log_message(level=dorsa_logger.log_levels.DEBUG,
#                                          text=f"run camera thread :{self.name}", 
#                                          code="FCR000")
#       self.logger.create_new_log(message=log_msg)
#       #-----------------------------------------------------------
#       while self.runing:
#         # #print('asdw'*80,self.name)
#         #-----------------------------------------------------------
#         log_msg = dorsa_logger.log_message(level=dorsa_logger.log_levels.DEBUG,
#                                            text=f"try connect to camera {self.name}", 
#                                            code="FCR001")
#         self.logger.create_new_log(message=log_msg)
#         #-----------------------------------------------------------
#         rstp_url = self.get_stream_url() 
#         #self.setup_camera() 
#         if rstp_url is None:
#            time.sleep(5)
#            continue
        
#         try:
#             output_dir, output_fname = self.build_path()
#             output_path = os.path.join(output_dir, output_fname)
            
#         except Exception as e:
#            #-----------------------------------------------------------
#            log_msg = dorsa_logger.log_message(level=dorsa_logger.log_levels.ERROR,
#                                               text=f"error happend in ffmpegCamera build path {self.name}: {e}", 
#                                               code="FCR002")
#            self.logger.create_new_log(message=log_msg)
#            #-----------------------------------------------------------
#            continue

        
#         #-----------------------------------------------------------
#         log_msg = dorsa_logger.log_message(level=dorsa_logger.log_levels.DEBUG,
#                                            text=f"connect to camera {self.name} success", 
#                                            code="FCR003")
#         self.logger.create_new_log(message=log_msg)
#         #-----------------------------------------------------------
#         try:
#             self.build_and_run_stream(rstp_url, output_path)
#         except Exception as e:
#            #-----------------------------------------------------------
#             log_msg = dorsa_logger.log_message(level=dorsa_logger.log_levels.ERROR,
#                                            text=f"error happend in run build_and_run_stream ffmpegCamera {self.name}: {e}", 
#                                            code="FCR004")
#             self.logger.create_new_log(message=log_msg)
#             #-----------------------------------------------------------
        
#         #-----------------------------------------------------------
#         log_msg = dorsa_logger.log_message(level=dorsa_logger.log_levels.DEBUG,
#                                            text=f"stream stop {self.name}", 
#                                            code="FCR005")
#         self.logger.create_new_log(message=log_msg)
#         #-----------------------------------------------------------

    
    
           
        

    

#         # command  = ffmpeg.compile(stream)

        
    

# # grabber = ffmpegCamera('left', 'admin', 'Milad1375422@', train_id='11BGDEF', ip='192.168.1.2', fps=25)
# # grabber.start()




if __name__=='__main__':
        
    onvif_camera = ONVIFCamera(host='192.168.1.36', port=8088, user='admin', passwd='admin123')
