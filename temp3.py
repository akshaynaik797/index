from apscheduler.schedulers.background import BackgroundScheduler

def fun():
    print(1)

sched = BackgroundScheduler(daemon=False)
sched.add_job(fun, max_instances=1)
sched.start()