from datetime import datetime, timedelta

import utils
import lab2dev_api

project_name = 'WHP TM - Alocação IT Engineer SRE'
default_description = 'Whirlpool - Automated'

lab2dev_projects = lab2dev_api.get('tracker/projects')

sre_project = list(filter(
  lambda project: (project['name'] == project_name), 
  lab2dev_projects,
))[0]

today = datetime.today()
next_date = datetime(today.year, today.month, 1)

while next_date.month == today.month:
  current_date = next_date
  next_date += timedelta(days=1)

  if current_date.weekday() in [5, 6]:
    continue

  formatted_date = current_date.strftime("%Y-%m-%dT03:00:00.000Z")

  start_date = current_date.strftime("%Y-%m-%dT09:00:00.000Z")
  end_date = current_date.strftime("%Y-%m-%dT17:00:00.000Z")

  appointment = {
    "date": formatted_date,
    "start": start_date,
    "end": end_date,

    "billable": True,
    "extra": False,
    "title": default_description,
    "project": sre_project['id'],
  }

  appointment_response = lab2dev_api.post('appointments', appointment)

  if "error" in appointment_response:
    print(f"❌ day {current_date}")
    
    utils.print_json({
      "request": appointment,
      "response": appointment_response,
    })
  else:
    print(f"✅ day {current_date}")
