
# Assuming `user` is the user instance you're interested in
from users.models import EntryExitLog

from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, F ,Case, When, DurationField
from django.db.models.functions import TruncDate
from django.contrib.auth.models import User
from datetime import timedelta
from khayyam import JalaliDatetime




def get_latest_exit(user):


    try:
        last_log = EntryExitLog.objects.filter(user=user).latest('timestamp')  # Use appropriate timestamp field

        location = last_log.location.name
        if last_log.is_entry:
            last_status = 'ورود'
            msg = '{} به {} در ساعت و تاریخ {}'.format(last_status,location,last_log.jalali_date())

        
        else:
            last_status = 'خروج'
            msg = '{} از {} در ساعت {}'.format(last_status,location,last_log.jalali_date())



        return msg
    except EntryExitLog.DoesNotExist:
        last_status = 'بدون وضعیت'

        return last_status



def is_user_in(user):
    try:
        # Get the latest log for the user
        latest_log = EntryExitLog.objects.filter(user=user).latest('timestamp')

        # Check if the latest log is an entry log (is_entry=True) and no newer exit log exists
        if latest_log.is_entry:
            return True  # User is currently in
        else:
            return False  # User is currently out

    except EntryExitLog.DoesNotExist:
        return None  # If no log exists, assume user is out
    




class UserWorkTimeManager:

    def __init__(self):
        
        self.total_time_work = {}
        self.user = None
        
        pass

    


    def format_timedelta(self,td):
        """Format timedelta to exclude milliseconds."""

        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}:{minutes:02}:{seconds:02}"

    def convert_seconds_to_hms(self,total_seconds):
        # Convert to hours, minutes, and seconds
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Return formatted time as HH:MM:SS
        return f"{hours:02}:{minutes:02}:{seconds:02}"


    def func_total_time_work(self,td,user=None):

        if user is None:
            user = self.user

        self.total_time_work[user] +=  int(td.total_seconds())




    def user_work_time(self,username=None):
        # Get the current date and the start date for the past month
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        start_date = today - timedelta(days=30)  # Adjust the range as needed

        # Get all users
        users = User.objects.all()


        if username:
            user = User.objects.filter(id=username).first()
            users = [user] if user else []

        # Prepare a dictionary to hold user work times
        user_time_data = {}

        # Loop through each user and calculate their work time
        for user in users:

            self.total_time_work[user] = 0

            # Get the logs for the user within the date range, ordered by timestamp
            logs = (
                EntryExitLog.objects.filter(user=user, timestamp__range=[start_date, tomorrow])
                .order_by('timestamp')  # Order by day and time
            )

            daily_work_times = {}

            # Process logs in order of timestamp
            for cnt,log in enumerate(logs):
                log_date = log.jalali_date()  # Get Jalali date


                #print('log.is_entry  ',log.is_entry)
                entry_time = None
                exit_time = None

                new_raw = True
                jalali_time_out = None

                total_work_time =  timedelta(0)

                if log.is_entry:
                    
                    # If we already have an entry and no exit, we ignore it (missed logout case)
                    entry_time = log.timestamp  # Record the time when the user logs in
                    jalali_time_in = JalaliDatetime(entry_time).strftime('%Y/%m/%d  %H:%M:%S') 


                else:
                    exit_time = log.timestamp

                    if log_date == daily_work_times[cnt-1]['date'] :


                        new_raw = False

                        jalali_time_out = JalaliDatetime(exit_time).strftime('%Y/%m/%d  %H:%M:%S') 
                        daily_work_times[cnt-1]['time_out'] = exit_time
                        daily_work_times[cnt-1]['jalali_time_out'] = jalali_time_out


                        total_work_time = exit_time - daily_work_times[cnt-1]['time_in']

                        self.func_total_time_work(total_work_time,user)


                        daily_work_times[cnt-1]['total_work_time'] =self.format_timedelta(total_work_time)

                    



                if new_raw:
                
                    daily_work_times[cnt] = {
                        'date' : log_date,
                        'total_work_time': total_work_time,
                        'time_in': entry_time,
                        'jalali_time_in':jalali_time_in,
                        'time_out':exit_time,
                        'jalali_time_out':jalali_time_out,
                    }

        user_time_data[user.username] = daily_work_times

        sorted_dict = dict(sorted(
            daily_work_times.items(),
            key=lambda item: (item[1]['time_in'] is None, item[1]['time_in']),
            reverse=True
        ))

        user_time_data[user.username] = sorted_dict

        for user in self.total_time_work.keys():

            self.total_time_work[user] = self.convert_seconds_to_hms(self.total_time_work[user])
        

        return user_time_data , self.total_time_work