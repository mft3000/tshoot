#! /usr/bin/env python

############ 0.7
#
# 0.1 start inint
# 0.2 add excel read, insert into sql for query data
# 0.3 split file
# 0.4 return questions
# 0.5 enhanced configuration
# 0.6 finish config
# 0.7 fix log file
#

import argparse, os, logging, random

from tsEngine import *

# ++++++++++++++++++++  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# --------------------

def hostname_to_port(prefix, hostname):
	port_no = '0' + hostname.replace('R','') if int(hostname.replace('R','')) < 10 else hostname.replace('R','')
	return prefix + port_no
	
def main():

        parser = argparse.ArgumentParser(description='')
        parser.add_argument('-f','--file', required=False, default='ts')
        parser.add_argument('-s','--scenario', required=False, default='*')
        parser.add_argument('-v','--version', required=False, default='*')
        parser.add_argument('-n','--number_of_faults', required=False, default='')
        parser.add_argument('--start-question', dest='start_question', required=False, default='1')
        parser.add_argument('--hostname', required=False, default='localhost')
        parser.add_argument('--port', required=False, default='20')

        parser.add_argument('--no-hide-in-insertion', dest='no_hide_in_insertion', required=False, action='store_false', default=True)

        parser.add_argument('--load-excel-in-sql', dest='load_excel_in_sql', required=False, action='store_true')

        parser.add_argument('-d','--debug', required=False, action='store_true')

        args = parser.parse_args()
		
        ############################## argparse EOF ##############################
		
        if args.load_excel_in_sql:
		
                print 
                print "THIS OPERATION WILL DELETE fault TABLE CONTAINED INTO FILE " + args.file + ".sqlite3"
                print "WITH INFORMATIONS CONTAINED INTO " + args.file + ".xlsx"
                print 
                reply = raw_input("Continue y/[N]: ")
                if not reply or 'n' in reply or 'N' in reply:
                        print 
                        print "Exit... DONE"
                        exit()
                
                # load excel

                x = excel( args.file )
                try:
                        x.connect()
                except IOError:
                        print
                        print "file " + args.file + " not found"
                        print "specify file_name with -f extension"
                        exit()

                csv = x.read()

                logging.debug(csv)

                # push it into sqlite

                s = sql( args.file )
                s.connect()

                s.drop_table()

                s.create_table()

                s.load(csv)

                s.close()


        else:   
				
		logs = log(args.file + '.log')
		logs.write("#\n")
		logs.write("# THIS FILE IS GENERATE TO SHOW WHICH FAULTS ARE INSERTED INTO TOPOLOGY\n")
		logs.write("#\n")
		logs.write("\n")
		logs.write("\n")

                s = sql( args.file )
                s.connect()

                scenarios, vers = s.db_summary()
				
                                
                if '*' in args.scenario:
                        print 
                        print "++++++++++++++++++++++++++++++++++++"
                        print "summary scenarios name inside sql:"
                        print
                        for scenario in scenarios:
                                print ' '.join(scenario)
                        print
                        print "----------------------------------"
                        print
                        exit()

                                
                if '*' in args.version:
                        print
                        print "++++++++++++++++++++++++++++++++++++"
                        print "summary versions inside sql for \'" + args.scenario + "\':"
                        print
                        for ver in vers:
                                if args.scenario in ver:
                                        print ' '.join(ver).replace(args.scenario + ' ', '')
                        print
                        print "------------------------------------"
                        print
                        exit()

                fault_no = 'all' if not args.number_of_faults else args.number_of_faults
                start_question = '1' if not args.start_question else args.start_question
                
                head = ""
                head += "\n******************************************\n"
                head += "Lab: 				" + args.scenario + "\n"
                head += "Version: 			" + args.version + "\n"
                head += "Question which start insert:	" + start_question + "\n"
                head += "Faults per ticket:              " + fault_no + "\n"
                head += "Hide faults in insert stage:    " + str(args.no_hide_in_insertion) + "\n"
                head += "Debug:                          " + str(args.debug) + "\n"
                head += "Excel file name:                " + args.file + ".xlsx\n"
                head += "Sqlite file name:               " + args.file + ".sqlite3\n"
                head += "Log file for find solutions: 	" + args.file + ".log\n"
                head += "******************************************\n\n"

                logs.write( head )

                print head
                 

                for question_number in range(1,10):
						# resume block of code: choose question number where start inject faults
                        if int(question_number) >= int(args.start_question):
								

                                for question in s.return_device_faults(scenario=args.scenario, ver=args.version, question_num=question_number, max_num_faults=args.number_of_faults):    

                                        head_question = ""
                                        head_question += "\n --- question no " + str(question[4]) + " (" + str(question[5]) + ") ---\n"
                                        head_question += "telnet " + args.hostname + ' ' + hostname_to_port(args.port, question[5]) + "\n"

                                        # write log file for 'book of solutions'
                                        logs.write( head_question )
                                        logs.write( "\n" + question[3] + "\n" )

                                        print head_question
										
                                        t = telnet( args.hostname, hostname_to_port(args.port, question[5]), question[3], debug = args.debug, hidden = args.no_hide_in_insertion)
										
					sim = False
										
                                        t.connect(simulation = sim, question = question[4])
                                        
					if not sim:
					   t.close()
                        else:
                                continue

                s.close()
                logs.close()


if __name__ == '__main__':
        main()