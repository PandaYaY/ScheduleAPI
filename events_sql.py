"""
Sql запросы для событий
"""

sample_regular = """select
r.id,
r.start_date,
r.end_date,
r.start_time :: char(5),
r.end_time :: char(5),
s.name as subject,
r.description,
u.fio,
cs.name as course_status,
dep.name as department,
ps.name as program_source,
r.children_count,
tf.name as training_format,
r.school,
r.classroom,
array(select array[
case 
when extract(dow from d) = 0 then 'Вс'
when extract(dow from d) = 1 then 'Пн'
when extract(dow from d) = 2 then 'Вт'
when extract(dow from d) = 3 then 'Ср'
when extract(dow from d) = 4 then 'Чт'
when extract(dow from d) = 5 then 'Пт'
when extract(dow from d) = 6 then 'Сб'
end, to_char(d, 'DD.MM.YYYY')]
from unnest(sort_array(r.dates)) as d) as dates

from "Regular_Events" as r

join "Decode_Program_Source" as ps on ps.id = r.program_source
join "Users" as u on u.id = r.teacher_id
join "Decode_Department" as dep on dep.id = r.department
join "Decode_Subject" as s on s.id = r.subject
join "Decode_Course_Status" as cs on cs.id = r.course_status
join "Decode_Training_Format" as tf on tf.id = r.training_format"""

sample_sub_regular = """select
s.id,
s.date,
s.start_time :: char(5),
s.end_time :: char(5),
subj.name as subject,
r.description,
u.fio,
es.name as event_status,
dep.name as department,
ps.name as program_source,
r.children_count,
f.name as training_format,
r.school,
r.classroom

from "Sub_Regular_Events" as s

join "Regular_Events" as r on r.id = s.mother_id
join "Users" as u on s.teacher_id = u.id
join "Decode_Department" as dep on r.department = dep.id
join "Decode_Training_Format" as f on s.training_format = f.id
join "Decode_Program_Source" as ps on ps.id = r.program_source
join "Decode_Event_Status" as es on es.id = s.event_status
join "Decode_Subject" as subj on subj.id = r.subject"""

sample_one_time = """select
one.id,
one.date,
one.start_time :: char(5),
one.end_time :: char(5),
s.name as subject,
one.description,
u.fio,
es.name as event_status,
dep.name as department,
ps.name as program_source,
one.children_count,
f.name as training_format,
one.school,
one.classroom

from "One_Time_Events" as one

join "Decode_Subject" as s on one.subject = s.id
join "Users" as u on one.teacher_id = u.id
join "Decode_Department" as dep on one.department = dep.id
join "Decode_Training_Format" as f on one.training_format = f.id
join "Decode_Program_Source" as ps on ps.id = one.program_source
join "Decode_Event_Status" as es on es.id = one.event_status"""

# Отобразить все курсы из таблицы Regular_Events
all_regular_events = f"{sample_regular}\nwhere end_date > now() - interval '15' day"

# Найти все в таблице Sub_Regular_Events
all_sub_regular_events = f"{sample_sub_regular}\nwhere s.date between %s and %s and is_confirm"

# Найти все в таблице One_Time_Events
all_one_time_events = f"{sample_one_time}\nwhere date between %s and %s and is_confirm"

# Найти записи регулярных событий по кафедре
dep_regular_events = f"{sample_regular}\nwhere r.department = %s and end_date > now() - interval '15' day"

# Найти все записи ивентов для кафедры в таблице Sub_Regular_Events
dep_sub_regular_events = f"{sample_sub_regular}\nwhere s.date between %s and %s and r.department = %s and is_confirm"

# Найти все записи ивентов для кафедры в таблице One_Time_Events
dep_one_time_events = f"{sample_one_time}\nwhere date between %s and %s and one.department = %s and is_confirm"

# Найти все записи событий по пользователю
teacher_regular_events = f"{sample_regular}\nwhere u.id = %s and end_date > now() - interval '15' day"

# Найти записи ивентов по пользователю в таблице Sub_Regular_Events
teacher_sub_regular_events = f"{sample_sub_regular}\nwhere date between %s and %s and u.id = %s and is_confirm"

# Найти записи ивентов по пользователю в таблице One_Time_Events
teacher_one_time_events = f"{sample_one_time}\nwhere date between %s and %s and u.id = %s and is_confirm"

full_all_reg = f"{sample_regular}\nwhere end_date >= now() :: date"
full_all_sub_regular = f"{sample_sub_regular}\nwhere date >= now() :: date and is_confirm"
full_all_one_time = f"{sample_one_time}\nwhere date >= now() :: date and is_confirm"

full_dep_reg = f"{sample_regular}\nwhere r.department = %s and end_date >= now() :: date"
full_dep_sub_regular = f"{sample_sub_regular}\nwhere r.department = %s and date >= now() :: date and is_confirm"
full_dep_one_time = f"{sample_one_time}\nwhere one.department = %s and date >= now() :: date and is_confirm"

full_teacher_reg = f"{sample_regular}\nwhere r.teacher_id = %s and end_date >= now() :: date"
full_teacher_sub_regular = f"{sample_sub_regular}\nwhere s.teacher_id = %s and date >= now() :: date and is_confirm"
full_teacher_one_time = f"{sample_one_time}\nwhere one.teacher_id = %s and date >= now() :: date and is_confirm"

new_events_regular = """select
id,
start_date,
end_date,
start_time,
end_time,
subject,
description,
fio,
course_status,
department,
program_source,
children_count,
training_format,
school,
classroom,
dates,
change_type
from (
select
r.id,
r.start_date,
r.end_date,
r.start_time :: char(5) as start_time,
r.end_time :: char(5) as end_time,
subj.name as subject,
r.description,
u.fio,
status.name as course_status,
dep.name as department,
ps.name as program_source,
r.children_count,
tf.name as training_format,
r.school,
r.classroom,
array(select array[
case
when extract(dow from d) = 0 then 'Вс'
when extract(dow from d) = 1 then 'Пн'
when extract(dow from d) = 2 then 'Вт'
when extract(dow from d) = 3 then 'Ср'
when extract(dow from d) = 4 then 'Чт'
when extract(dow from d) = 5 then 'Пт'
when extract(dow from d) = 6 then 'Сб'
end, to_char(d, 'DD.MM.YYYY')]
from unnest(sort_array(r.dates)) as d) as dates,
ct.name as change_type,
ch.user_id,
ch.mac

from "Events_Changes" as ch

join "Regular_Events" as r on ch.id = r.id and ch.table_name = 'Regular_Events'
join "Decode_Subject" as subj on r.subject = subj.id
join "Users" as u on r.teacher_id = u.id
join "Decode_Course_Status" status on r.course_status = status.id
join "Decode_Department" as dep on r.department = dep.id
join "Decode_Program_Source" as ps on r.program_source = ps.id
join "Decode_Training_Format" as tf on r.training_format = tf.id
join "Decode_Change_Type" as ct on ch.change_type = ct.id

union

select
d.event_id as id,
d.start_date,
d.end_date,
d.start_time :: char(5),
d.end_time :: char(5),
subj.name as subject,
d.description,
u.fio,
status.name as course_status,
dep.name as department,
ps.name as program_source,
d.children_count,
tf.name as training_format,
d.school,
d.classroom,
array(select array[
case 
when extract(dow from d) = 0 then 'Вс'
when extract(dow from d) = 1 then 'Пн'
when extract(dow from d) = 2 then 'Вт'
when extract(dow from d) = 3 then 'Ср'
when extract(dow from d) = 4 then 'Чт'
when extract(dow from d) = 5 then 'Пт'
when extract(dow from d) = 6 then 'Сб'
end, to_char(d, 'DD.MM.YYYY')]
from unnest(sort_array(d.dates)) as d) as dates,
ct.name as change_type,
ch.user_id,
ch.mac

from "Events_Changes" as ch

join "Deleted_Regular_Events" as d on ch.id = d.event_id and ch.table_name = 'Regular_Events'
join "Decode_Subject" as subj on d.subject = subj.id
join "Users" as u on d.teacher_id = u.id
join "Decode_Course_Status" as status on d.course_status = status.id
join "Decode_Department" as dep on d.department = dep.id
join "Decode_Program_Source" as ps on d.program_source = ps.id
join "Decode_Training_Format" as tf on d.training_format = tf.id
join "Decode_Change_Type" as ct on ch.change_type = ct.id
) as foo

where user_id = %s and %s = any(mac)"""

new_events_sub_regular = """select
id,
date,
start_time,
end_time,
subject,
description,
fio,
event_status,
department,
program_source,
children_count,
training_format,
school,
classroom,
change_type
from (
select
s.id,
s.date,
s.start_time :: char(5),
s.end_time :: char(5),
subj.name as subject,
r.description,
u.fio,
status.name as event_status,
dep.name as department,
ps.name as program_source,
r.children_count,
tf.name as training_format,
r.school,
s.classroom,
ct.name as change_type,
ch.user_id,
ch.mac

from "Events_Changes" ch

join "Sub_Regular_Events" s on ch.id = s.id and ch.table_name = 'Sub_Regular_Events'
join "Regular_Events" r on s.mother_id = r.id
join "Decode_Subject" subj on r.subject = subj.id
join "Users" u on s.teacher_id = u.id
join "Decode_Event_Status" status on s.event_status = status.id
join "Decode_Department" dep on r.department = dep.id
join "Decode_Program_Source" ps on r.program_source = ps.id
join "Decode_Training_Format" tf on r.training_format = tf.id
join "Decode_Change_Type" ct on ch.change_type = ct.id

union

select 
d.event_id as id,
d.date,
d.start_time :: char(5),
d.end_time :: char(5),
subj.name as subject,
d.description,
u.fio,
status.name as event_status,
dep.name as department,
ps.name as program_source,
d.children_count,
tf.name as training_format,
d.school,
d.classroom,
ct.name as change_type,
ch.user_id,
ch.mac

from "Events_Changes" ch

join "Deleted_Sub_Regular_Events" d on ch.id = d.event_id and ch.table_name = 'Sub_Regular_Events'
join "Decode_Subject" subj on d.subject = subj.id
join "Users" u on d.teacher_id = u.id
join "Decode_Event_Status" status on d.event_status = status.id
join "Decode_Department" dep on d.department = dep.id
join "Decode_Program_Source" ps on d.program_source = ps.id
join "Decode_Training_Format" tf on d.training_format = tf.id
join "Decode_Change_Type" ct on ch.change_type = ct.id
) as foo


where user_id = %s and %s = any(mac)
"""

new_events_one_time = """select
id,
date,
start_time,
end_time,
subject,
description,
fio,
event_status,
department,
program_source,
children_count,
training_format,
school,
classroom,
change_type
from (

select
one.id,
one.date,
one.start_time :: char(5),
one.end_time :: char(5),
subj.name as subject,
one.description,
u.fio,
status.name as event_status,
dep.name as department,
ps.name as program_source,
one.children_count,
tf.name as training_format,
one.school,
one.classroom,
ct.name as change_type,
ch.user_id,
ch.mac

from "Events_Changes" as ch

join "One_Time_Events" as one on ch.id = one.id and ch.table_name = 'One_Time_Events'
join "Decode_Subject" as subj on one.subject = subj.id
join "Users" as u on one.teacher_id = u.id
join "Decode_Event_Status" as status on one.event_status = status.id
join "Decode_Department" as dep on one.department = dep.id
join "Decode_Program_Source" as ps on one.program_source = ps.id
join "Decode_Training_Format" as tf on one.training_format = tf.id
join "Decode_Change_Type" as ct on ch.change_type = ct.id

union

select
d.event_id as id,
d.date,
d.start_time :: char(5),
d.end_time :: char(5),
subj.name as subject,
d.description,
u.fio,
status.name as event_status,
dep.name as department,
ps.name as program_source,
d.children_count,
tf.name as training_format,
d.school,
d.classroom,
ct.name as change_type,
ch.user_id,
ch.mac

from "Events_Changes" as ch

join "Deleted_One_Time_Events" d on ch.id = d.event_id and ch.table_name = 'One_Time_Events'
join "Decode_Subject" as subj on d.subject = subj.id
join "Users" as u on teacher_id = u.id
join "Decode_Event_Status" as status on d.event_status = status.id
join "Decode_Department" as dep on d.department = dep.id
join "Decode_Program_Source" as ps on d.program_source = ps.id
join "Decode_Training_Format" as tf on d.training_format = tf.id
join "Decode_Change_Type" as ct on ch.change_type = ct.id
) as foo

where user_id = %s and %s = any(mac)
"""

auction_events = """select
id,
date,
start_time,
end_time,
subject,
description,
fio,
event_status,
department,
program_source,
children_count,
training_format,
school,
classroom,
type_event from (
select
one.id,
one.date,
one.start_time :: char(5) as start_time,
one.end_time :: char(5) as end_time,
subj.name as subject,
auc.description,
u.fio as fio,
status.name as event_status,
dep.name as department,
ps.name as program_source,
one.children_count,
tf.name as training_format,
one.school as school,
one.classroom,
auc.teachers,
'One_Time_Events' as type_event

from "One_Time_Events" one

join "Auction" auc on auc.event_id = one.id and auc.table_name = 'One_Time_Events'
join "Decode_Subject" subj on one.subject = subj.id
join "Users" u on one.teacher_id = u.id
join "Decode_Event_Status" status on one.event_status = status.id
join "Decode_Department" dep on one.department = dep.id
join "Decode_Program_Source" ps on one.program_source = ps.id
join "Decode_Training_Format" tf on one.training_format = tf.id

union

select
s.id,
s.date,
s.start_time :: char(5) as start_time,
s.end_time :: char(5) as end_time,
subj.name as subject,
auc.description,
u.fio as fio,
status.name as event_status,
dep.name as department,
ps.name as program_source,
r.children_count,
tf.name as training_format,
r.school,
s.classroom,
auc.teachers,
'Sub_Regular_Events' as type_event

from "Sub_Regular_Events" s

join "Auction" auc on auc.event_id = s.id and auc.table_name = 'Sub_Regular_Events'
join "Regular_Events" r on s.mother_id = r.id
join "Decode_Subject" subj on r.subject = subj.id
join "Users" u on s.teacher_id = u.id
join "Decode_Event_Status" status on s.event_status = status.id
join "Decode_Department" dep on r.department = dep.id
join "Decode_Program_Source" ps on r.program_source = ps.id
join "Decode_Training_Format" tf on r.training_format = tf.id
) as foo
where %s = any(teachers)"""

new_events_auction = """select
id,
date,
start_time,
end_time,
subject,
description,
fio,
event_status,
department,
program_source,
children_count,
training_format,
school,
classroom,
change_type,
type_event from (
select
one.id,
one.date,
one.start_time :: char(5) as start_time,
one.end_time :: char(5) as end_time,
subj.name as subject,
auc.description,
u.fio as fio,
status.name as event_status,
dep.name as department,
ps.name as program_source,
one.children_count,
tf.name as training_format,
one.school as school,
one.classroom,
ct.name as change_type,
ch.user_id,
ch.mac,
'One_Time_Events' as type_event

from "Events_Changes" ch

join "Auction" auc on ch.id = auc.id and auc.table_name = 'One_Time_Events'
join "One_Time_Events" one on auc.event_id = one.id
join "Decode_Subject" subj on one.subject = subj.id
join "Users" u on one.teacher_id = u.id
join "Decode_Event_Status" status on one.event_status = status.id
join "Decode_Department" dep on one.department = dep.id
join "Decode_Program_Source" ps on one.program_source = ps.id
join "Decode_Training_Format" tf on one.training_format = tf.id
join "Decode_Change_Type" as ct on ch.change_type = ct.id

union

select
s.id,
s.date,
s.start_time :: char(5) as start_time,
s.end_time :: char(5) as end_time,
subj.name as subject,
auc.description,
u.fio as fio,
status.name as event_status,
dep.name as department,
ps.name as program_source,
r.children_count,
tf.name as training_format,
r.school,
s.classroom,
ct.name as change_type,
ch.user_id,
ch.mac,
'Sub_Regular_Events' as type_event

from "Events_Changes" ch

join "Auction" auc on ch.id = auc.id
join "Sub_Regular_Events" s on auc.event_id = s.id and auc.table_name = 'Sub_Regular_Events'
join "Regular_Events" r on s.mother_id = r.id
join "Decode_Subject" subj on r.subject = subj.id
join "Users" u on s.teacher_id = u.id
join "Decode_Event_Status" status on s.event_status = status.id
join "Decode_Department" dep on r.department = dep.id
join "Decode_Program_Source" ps on r.program_source = ps.id
join "Decode_Training_Format" tf on r.training_format = tf.id
join "Decode_Change_Type" ct on ch.change_type = ct.id
) as foo

where user_id = %s and %s = any(mac)"""

# events_changes = """select
# table_name, array_agg(id) as id
# from "Events_Changes"
# where user_id = %s and %s = any(mac)
# group by table_name"""

all_deleted_regular = """select
d.delete_description,
d.event_id as id,
d.deleting_user_id,
d.start_date,
d.end_date,
d.start_time :: char(5),
d.end_time :: char(5),
s.name as subject,
d.description,
u.fio,
cs.name as course_status,
dep.name as department,
ps.name as program_source,
d.children_count,
tf.name as training_format,
d.school,
d.classroom,
array(select array[
case 
when extract(dow from d) = 0 then 'Вс'
when extract(dow from d) = 1 then 'Пн'
when extract(dow from d) = 2 then 'Вт'
when extract(dow from d) = 3 then 'Ср'
when extract(dow from d) = 4 then 'Чт'
when extract(dow from d) = 5 then 'Пт'
when extract(dow from d) = 6 then 'Сб'
end, to_char(d, 'DD.MM.YYYY')]
from unnest(sort_array(d.dates)) as d) as dates

from "Deleted_Regular_Events" as d

join "Decode_Program_Source" as ps on ps.id = d.program_source
join "Users" as u on u.id = d.teacher_id
join "Decode_Department" as dep on dep.id = d.department
join "Decode_Subject" as s on s.id = d.subject
join "Decode_Course_Status" as cs on cs.id = d.course_status
join "Decode_Training_Format" as tf on tf.id = d.training_format"""

all_deleted_sub_regular = """select
d.delete_description,
d.event_id as id,
du.fio as deleting_user,
d.date,
d.start_time :: char(5),
d.end_time :: char(5),
subj.name as subject,
d.description,
u.fio,
es.name as event_status,
dep.name as department,
ps.name as program_source,
d.children_count,
f.name as training_format,
d.school,
d.classroom

from "Deleted_Sub_Regular_Events" as d

join "Users" as u on d.teacher_id = u.id
join "Users" as du on d.deleting_user_id = du.id
join "Decode_Department" as dep on d.department = dep.id
join "Decode_Training_Format" as f on d.training_format = f.id
join "Decode_Program_Source" as ps on ps.id = d.program_source
join "Decode_Event_Status" as es on es.id = d.event_status
join "Decode_Subject" as subj on subj.id = d.subject"""

all_deleted_one_time = """select
d.delete_description,
d.event_id as id,
du.fio as deleting_user,
d.date,
d.start_time :: char(5),
d.end_time :: char(5),
s.name as subject,
d.description,
u.fio,
es.name as event_status,
dep.name as department,
ps.name as program_source,
d.children_count,
f.name as training_format,
d.school,
d.classroom

from "Deleted_One_Time_Events" as d

join "Decode_Subject" as s on d.subject = s.id
join "Users" as u on d.teacher_id = u.id
join "Users" as du on d.deleting_user_id = du.id
join "Decode_Department" as dep on d.department = dep.id
join "Decode_Training_Format" as f on d.training_format = f.id
join "Decode_Program_Source" as ps on ps.id = d.program_source
join "Decode_Event_Status" as es on es.id = d.event_status"""

dep_deleted_regular = f"{all_deleted_regular}\nwhere d.department = %s"

dep_deleted_sub_regular = f"{all_deleted_sub_regular}\nwhere d.department = %s"

dep_deleted_one_time = f"{all_deleted_one_time}\nwhere d.department = %s"
