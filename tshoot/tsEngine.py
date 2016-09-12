#! /usr/bin/env python

############ 0.7
#
# 0.1 start inint
# 0.2 add excel read, insert into sql for query data
# 0.3 split file
# 0.4 return questions
# 0.5 enhanced configurations
# 0.6 finish config
# 0.7 fix log file
#

import logging, time, os

import sqlite3, telnetlib

# third party libs

from openpyxl import *

# ++++++++++++++++++++  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# --------------------

class excel(object):

        file = ''
        conn = ''

        def __init__(self, file):
                self.file = file

        def connect(self):
                self.wb = load_workbook( self.file + '.xlsx' )   

        def read(self):
                ws2 = self.wb.active

                unlock = False
                result = []
                reply = []

                for row in ws2.iter_rows():
                        for cell in row:
                                if cell.row == 1:
                                        continue
                                reply.append( str(cell.value) )
                                        
                        result.append(reply)
                        reply = []
                        unlock = False

                return result

class sql(object):
	
        file = ''
        conn = ''

        def __init__(self, file):
                self.file = file

        def connect(self):

                self.conn = sqlite3.connect(self.file + '.sqlite3')

        def drop_table(self):

                cur = self.conn.cursor()

                sql = "DROP TABLE IF EXISTS `fault`"

                cur.execute(sql)

                self.conn.commit()

        def create_table(self):

                cur = self.conn.cursor()

                sql = """CREATE TABLE IF NOT EXISTS `fault` (
                  `id` int(25) NOT NULL,
                  `scenario` varchar(50) default NULL,
                  `ver` varchar(30) default NULL,
                  `fault` text,
                  `question` int(25) default NULL,
                  `router` varchar(25) default NULL,
                  `status` varchar(10) default NULL,
                  `difficult` varchar(25) default '3',
                  `manualSelection` binary(255) default NULL,
                  PRIMARY KEY  (`id`)
                )"""

                cur.execute(sql)

                self.conn.commit()

        def query(self, sql):

                cur = self.conn.cursor()

                cur.execute(sql)

                self.conn.commit()

        def load(self, datas):

                cur = self.conn.cursor()
                
                for rows in datas:
                        if rows:
                                sql = """INSERT INTO `fault` (
                                  id,
                                  scenario,
                                  ver,
                                  fault,
                                  question,
                                  router,
                                  status,
                                  difficult,
                                  manualSelection
                                ) VALUES (
                                  \'""" + rows[0] + """\',
                                  \'""" + rows[1] + """\',
                                  \'""" + rows[2] + """\',
                                  \'""" + rows[3] + """\',
                                  \'""" + rows[4] + """\',
                                  \'""" + rows[5] + """\',
                                  \'""" + rows[6] + """\',
                                  \'""" + rows[7] + """\',
                                  \'""" + rows[8] + """\'
                                )"""

                                logging.debug(sql)

                                cur.execute(sql)
                                
                                self.conn.commit()


                logging.info("excel to sql LOADING...DONE")

        def db_summary(self):
                with self.conn:
                    
                        cur = self.conn.cursor()    

                        cur.execute("SELECT scenario FROM fault group by scenario")
                        scenario = cur.fetchall()
                        cur.execute("SELECT scenario,ver FROM fault group by scenario,ver")
                        ver = cur.fetchall()

                        return scenario, ver

        def return_device_faults(self, scenario='', ver='', question_num='', max_num_faults=''):
                with self.conn:
                    
                        cur = self.conn.cursor() 

                        condition_sql = "WHERE 1=1 AND status = 'OK'"
                        scenario_sql = ""
                        ver_sql = ""
                        question_start_sql = ""

                        if question_num:
                          question_start_sql = " AND question = \'" + str(question_num) + "\' "

                        if not max_num_faults:
                          order = " ORDER BY question ASC"
                        else:
                          order = " ORDER BY RANDOM() LIMIT " + max_num_faults

                        if '*' in scenario:
                          scenario_sql += ""
                        elif scenario:
                          scenario_sql += " AND scenario = \'" + scenario + "\'"

                        if '*' in ver:
                          ver_sql += ""
                        elif scenario:
                          ver_sql += " AND ver = \'" + ver + "\'"

                        sql_code = "SELECT * FROM fault " + condition_sql + scenario_sql + ver_sql + question_start_sql + order

                        cur.execute(sql_code)
                        logging.debug(sql_code)

                        rows = cur.fetchall()

                        return rows
        
        def close(self):

                self.conn.close()

class telnet(object):
        host = ''
        port = ''
        payload = ''
        debug = ''
        tn = ''
        hidden = False
  
        def __init__(self, host, port, payload, hidden = False, debug = False):
          self.host = host
          self.port = int(port)
          self.payload = str(payload)
          self.debug = debug
          self.hidden = hidden
        
        def connect(self, simulation = True, question = ''):
          

          if not simulation:
              if self.debug:
                logging.info("connecting...")
            # try:
              self.tn = telnetlib.Telnet(self.host, self.port, 30)

              if self.debug:
                self.tn.set_debuglevel(5)

              print( '...begin writing to router R'  + str(self.port).replace('20','') + ' fault id no. ' + str(question) )
              self.tn.write("\r\n")
              time.sleep(3)
              self.tn.write("\r\n")
              if self.debug:
                logging.info( '...asking for telnet connection' )
              enabled = self.tn.read_until(">", 2)
              if enabled[-1:] != "#":
                self.tn.write("en\r\n")
                if self.debug:
                  logging.info( '...asking for enable' )
                self.tn.read_until(": ", 2)
                if self.debug:
                  logging.info( '...sending enable password' )
                self.tn.write("cisco\r\n")
                if self.debug:
                  logging.info( '...enabled, sending commands' )
                self.tn.read_until("#", 3)
              else:
                if self.debug:
                  logging.info( '...already enabled, sending commands' )
              self.tn.write("conf t\r\n")
              self.tn.read_until("#", 3)
              if self.debug:
                logging.info( '...asking for telnet connection' )
              self.tn.write( self.payload )
              self.tn.read_until("#", 3)
              self.tn.write("\r\nend\r\n")
              #tn.write("exit\r\n")
              ####tn.write("wr\r\n")
              if not self.hidden:
                print '\n********************************\n'
                print self.tn.read_until("K]",5)
                print '\n\n********************************\n\n'

                print

            
        
        def close(self):
          self.tn.close()

class log(object):
    file = ''
    f = ''

    def __init__(self, file):
      self.file = file

      if os.path.isfile(self.file):
        os.remove(self.file)
		
      self.f = open(self.file, 'a')

    def write(self, payload):
      self.f.write( payload )

    def close(self):
      self.f.close()

# TBDeployed: unlock telnet port that is locked
# class ssh(object):

    # def __init__(self, file):
      # pass

    # def connect(self):
      # pass

    # def clear_console(self):
      # os.system("sudo kill -SIGHUP $(sudo fuser -n tcp " + str(self.port) + " 2>&1 | awk \'{print $2}\')\n")
      # pass

    # def close(self):
      # pass