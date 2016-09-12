So you think ready for your CCIE Tshoot Lab, right? really?! So why don't you prepare a complex scenario and start to add some random mistakes with this script???

since it's introduction, Tshooting section is the tricky part of the exam and could let fall most expert guys (I failed my first exam attempt for 1 ******* ticket :).
When I prepare my exam the big challenge was find the proper way to practice.
I thought the weirdest ways to reach my goals, I even focused about involving some friends to messing a full working lab... not very feasible idea but this was a good starting point to think something good :)
This idea represented the foundation where build this project around, find (or 'build') a mate that could helps my training, introducing new faults every attempt and decrease the possibility to insert the same faults in multiple practice session.

I write this code around some simple main points

 1. you can facing with multiple different scenarios (identified by a -s name)
 2. a scenario could contain a large number of devices
 4. you need to solve multiple questions
 5. a questions regards a limited number of devices
 6. a question could contain multiple faults (multiple id in table with same scenarion name, version and question field)
 7. if you specify the number of faults to inject script will insert them in random way (-n num)

after define my own rules I start to write my own script... this is a evolution of the original one that helps me pass the exam many years ago.
```
$ python tshoot.py -h

usage: tshoot.py [-h] [-f FILE] [-s SCENARIO] [-v VERSION]
                 [-n NUMBER_OF_FAULTS] [--start-question START_QUESTION]
                 [--hostname HOSTNAME] [--no-hide-in-insertion]
                 [--load-excel-in-sql] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE
  -s SCENARIO, --scenario SCENARIO
  -v VERSION, --version VERSION
  -n NUMBER_OF_FAULTS, --number_of_faults NUMBER_OF_FAULTS
  --start-question START_QUESTION
  --hostname HOSTNAME
  --no-hide-in-insertion
  --load-excel-in-sql
  -d, --debug
```
==== first step - from excel to SQLite ====

create an excel file with your favourite name. this name needs to be specified in -f extension (if you do not specify anything, 'ts' will be used and -f is not needed). An extension will be concatenate to this string (.sqllite, .xlsx, .log)

the excel table needs to contain this structure (first row will be skipped during reading and insert into SQL)

```
id	scenario	ver		fault           question	router	status	difficult	ManualSelection
38	lab-21		0.1		hostname R10    4         R1      OK		  3			    None
```

id = id number of fault (must be UNIQUE)
scenario = identify a wide scenario / lab structure
ver = in order to differentiate multiple faults in same scenario topoligy, I introduce version field.
fault = IOS code to inject (use word wrap with Ctrl + Cmd + enter for multiple lines)
question = identify witch question this fault belongs
router = in witch router I need to inject this fault
status = if 'OK' this is eligible to be injected otherwise will be skipped
difficult = give a score to difficult of this fault (to be implementation)
ManualSelection = (to be implementation)

once filled the table we need to transfer this infos to sqlite DB with '--load-excel-in-sql' script extension (if a file already exist previous data will be erased). A new file '.sqlite3' will contains DB data
```
$ python tshoot.py --load-excel-in-sql

THIS OPERATION WILL DELETE fault TABLE CONTAINED INTO FILE ts.sqlite3
WITH INFORMATIONS CONTAINED INTO ts.xlsx

Continue y/[N]: y
/Library/Python/2.7/site-packages/openpyxl/reader/worksheet.py:322: UserWarning: Unknown extension is not supported and will be removed
  warn(msg)
INFO:root:excel to sql LOADING...DONE
```
sqlite is now ready to be queried!!!

==== second step - query SQL, retrieve faults and insert them into devices ====

At this time multiple scenarios and version are present inside sqlite 'fault' table. Next step is specify what choose by lunch tshoot.py without extensions. the script will suggest you step by step what you can specify with -s (scenario) and -v (version).

```
$ python tshoot.py 

++++++++++++++++++++++++++++++++++++
summary scenarios name inside sql:

lab-21

----------------------------------

$ python tshoot.py -s lab-21

++++++++++++++++++++++++++++++++++++
summary versions inside sql for 'lab-21':

0.1

----------------------------------

$ python tshoot.py -s lab-21 -s 0.1
```

these are the minimum script extensions required to successfully start inserting faults into devices

additional extensions could be specified:

1. -n: specify a random number of faults to be inserted (if inside the DB exists 10 faults for question 4, you can choose a random limited number of them). if not specified, all question related faults contained into SQL will be injected into routers 
2. --no-hide-in-insertion: shows in realtime which faults are injected into devices (default off)
3. --start-question: sometimes it could be happens that script crash at question number X. if you specify X + 1 with this extension program could resume inject procedure against start over
4. --hostname: the enter device procedure is 'telnet SOMEHOST 20xx'. SOMEHOST could be specified by this extension in order for example points VIRL devices
5. -d: enable verbose mode in order to see what it's happening (eg debug telnetlib)

==== fourt step - set timer to 02:00 and start solve all the questions ====

OK, faults are injected into devices. Set the timer and solve all questions in 2 hours.



remember that every time you run this script a third file with '*.log' extension will be created. This file contains all the faults that will be injected... it's a sort of 'book of solutions' :)

hope this tool could help us. Good Luck :)
