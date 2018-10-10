import sys, shutil, os
from socket import*
#Przemyslaw Pudelko

#user_comm_passed set to False until USER command is executed
#login_passed set to False until PASS command is successfully executed
#port_passed set to False until PORT command is successfully executed
#retr_passed set to False until RETR command successfully executed
#num_files initially set to 1 for ease, increments with each file added to retr_files
access_passed = False
login_passed = False
port_passed = False
retr_passed = False
num_files = 1
#Unless proven otherwise, "comm_ok", the boolean variable that states if there is
#a command error, and "crlf_ok", the boolean variable that states if there is a
#crlf error, are both set to false
comm_ok = False
crlf_ok = False
min_comm_len = 4
data_port = "152.2.129.144"
data_ip = 8000
file_name = " "

#This function checks "comm" to ensure it is one of the 8 command prompts
#It takes in the first 4 characters of the command as variable "comm"
#and the 5th character as variable "space"
#All characters of "comm" were capitalized before being passed into this function
#Only "comm" is needed to check SYST, NOOP, or QUIT, which should have no spaces afterwords
#USER, PASS, TYPE, PORT and RETR should have a space after them
#The return argument of this function is passed to a boolean variable comm_ok
def check_comm(comm, space):
    if (comm == "USER" or comm == "PASS" or comm == "TYPE" or comm == "PORT" or comm == "RETR"):
        if (space == " "):
            return True
        else:
            return False
    elif (comm == "SYST" or comm == "NOOP" or comm == "QUIT"):
        return True
    else:
        return False

#This function checks that a username or password error was not committed
#It takes in a string variable "check", which represents the username or password
#First it checks that there is a username/password, then it checks that there is at least one
#character in "check" that is not a space
#Lastly, it checks that there are only ascii characters within the username/password
#b is a local variable meant holding the boolean value that will be returned to:
#user_ok or pass_ok
def check_parameter(check):
    if check != "":
        b = True
    else :
        b = False
        return b
    for c in check:
        if c != " ":
            b = True
            break
        else:
            b = False
    for c in check:
        max_asc = 128
        total = 0
        asc = ord(c)
        total += asc
        if (asc >= max_asc):
            b = False
            break
    return b

#This function checks that the 2nd to last variable in the command string is \r, and
#the last variable is \n, using a simple if statement
#A boolean value is returned to the boolean variable crlf_ok
def check_crlf(crlf):
    asc_cr = 13
    asc_lf = 10
    if ord(crlf[0]) == asc_cr and ord(crlf[1]) == asc_lf:
        return True
    else:
        return False

#This function takes in the file_name given by the retr command, and determines its source
#This way, we can use the returned file_path to copy the file
def get_file_path(file_name):
    curr_wor_dir = os.getcwd()
    file_path = curr_wor_dir  + os.sep + file_name
    return file_path

#Set global variables for values whose state must be kept
def server_reply(line):
    global access_passed
    global login_passed
    global port_passed
    global retr_passed
    global num_files
#Unless proven otherwise, "comm_ok", the boolean variable that states if there is
#a command error, and "crlf_ok", the boolean variable that states if there is a
#crlf error, are both set to false
    global comm_ok
    global crlf_ok
    global min_comm_len
    global data_port
    global data_ip
    global file_name
    #if the command string isn't longer than 4 characters, there is definitely a command error
    if (len(line) > min_comm_len):
        #capitalize all characters in comm; make call to function check_comm
        comm = line.upper()[0:4]
        space = line[4]
        comm_ok = check_comm(comm, space)

    #If command string isn't longer than 5 characters, there is definitely a crlf error
    min_crlf_len = 5
    if (len(line) > min_crlf_len):
        crlf = line[-2:]
        #make call to check_crlf, check that last 2 lines of command string are \r\n
        crlf_ok = check_crlf(crlf)
    #"user_ok" states if there is a username error, "pass_ok" for password error,
    #"type_ok" for type_error
    #all initally set to true because of how the final if-statements are written
    user_ok = True
    pass_ok = True
    type_ok = True
    #first ensure that "comm" matches one of the 6 commands
    if comm_ok == True:
        if comm == "USER":
            #lstrip because only spaces after an initial ascii character other than space
            #are included in username and password
            user = line[5:-2]
            user = user.lstrip()
            user_ok = check_parameter(user)
        elif comm == "PASS":
            password = line[5:-2]
            password = password.lstrip()
            pass_ok = check_parameter(password)
            #make call to check_parameter
            #although the code for "user" and "password" are almost exactly the same
            #they have their own distic error message and must be distinguished from each other
        elif comm == "TYPE":
            #type-code constitutes of only 1 leter, either "A" or "I"
            #strip() is used to test purely the test code
            #lstrip() used so that in testing, any spaces after type-code causes crlf error
            type_code = line[5:-2]
            type_code1 = type_code.strip()
            type_code2 = type_code.lstrip()
            type_len = 1
            if type_code1 == "A" or type_code1 == "I":
                type_ok = True
            else:
                type_ok = False
            if len(type_code2) != type_len:
                crlf_ok = False
        #If command is PORT, port_code is <host-port>, all spaces in front cleared
        elif comm == "PORT":
            port_error = False
            port_code = line[5:-2]
            port_code = port_code.lstrip()
            port_len = len(port_code)
            #Iterate through port_code, ensure that all the values are either integer digits or
            #a comma, no commas allowed together; else, error will occur
            for x in range(0,port_len):
                asc_0 = 48
                asc_9 = 57
                if not((ord(port_code[x]) >= asc_0 and ord(port_code[x]) <= asc_9)
                      or (port_code[x] == "," and port_code[x-1:x+1] != ",,")):
                    port_error = True
                    break
            #Only runs if there is no error already
            #Put all the numbers into a list, perform the multiplication and addition for the last 2 values
            #Ensure that there are only 6 integers, else an error will occur
            #Ensure no integer in the list is >= 256
            #Place all the values into the string port_string
            if port_error == False:
                port_code = port_code.split(",")
                port_code = [int(i) for i in port_code]
                if len(port_code) != 6:
                    port_error = True
                else:
                    for x in port_code:
                        if x >= 256:
                            port_error = True
                            break
                    port_code[4] = port_code[4]*256 + port_code[5]
                    del(port_code[5])
                    port_string = ".".join(map(str, port_code[0:4]))
                    #set the ip address and port number for the data ftp connection
                    data_ip = port_string
                    data_port = port_code[4]
                    p_num = ","+str(port_code[4])
                    port_string += p_num
        #If command is RETR, file_name is <pathname>, all spaces in front cleared
        #Eliminate "\" or "//" if first character in file_name
        #Call get_file_path to get the source of the file
        elif comm == "RETR":
            if port_passed == True:
                retr_error = False
                file_name = line[5:-2]
                file_name = file_name.lstrip()
                file_len = len(file_name)
                if file_name[0] == "/" or file_name[0] == "\\":
                    file_name = file_name[1:file_len+1]
                file_path = get_file_path(file_name)
                if os.path.exists(file_path):
                    retr_error = False
                else:
                    retr_error = True

    #If statements are formatted so that if there is a command error, it is printed out,
    # even if there is also a parameter error
    #if there is no command error but a parameter error, the parameter error prints out
    #if there are no errors "Command ok" prints out
    if comm_ok == True:
        #Test to ensure that directly after "SYST", "NOOP", and "QUIT" is "\r\n"
        if comm == "SYST" or comm == "NOOP" or comm == "QUIT":
            asc_cr = 13
            asc_lf = 10
            if crlf_ok == True:
                if ord(line[4]) != asc_cr or ord(line[5]) != asc_lf:
                    return "501 Syntax error in parameter.\r\n"
               #Here we parse between the different inputs to determine the correct output
               #If the command is QUIT, no more commands will be accepted, system exits
                elif comm == "QUIT":
                    return "221 Goodbye.\r\n"
                    #sys.exit()
                elif access_passed == False and login_passed == False:
                #if the USER command has not been passed and no one is logged in
                    return "530 Not logged in.\r\n"
                elif login_passed == False:
                #if no one is logged in(USER command has been passed is implied, taken care
                #of in previous if-statement)
                    return "503 Bad sequence of commands.\r\n"
                elif access_passed == True and login_passed == True:
                #if someone is logged in and the USER command has been passed
                    return "503 Bad sequence of commands.\r\n"
                elif comm == "SYST":
                    return "215 UNIX Type: L8.\r\n"
                else:
                    return "200 Command OK.\r\n"
            else:
                return "501 Syntax error in parameter.\r\n"
        elif user_ok == True and pass_ok == True and type_ok == True and crlf_ok == True:
            if comm == "USER":
            #If command is USER, ask for password, set access_passed to True
                access_passed = True
                return "331 Guest access OK, send password.\r\n"
            elif access_passed == False and login_passed == False:
            #If previous command wasn't USER and not already logged in
                return "530 Not logged in.\r\n"
            elif login_passed == False:
            #If USER already passed (implied) and not already logged in
                if comm == "PASS":
                #login if current command is PASS, USER no loger passed
                    login_passed = True
                    access_passed = False
                    return "230 Guest login OK.\r\n"
                else:
                #Error message if current command is not PASS
                    return "503 Bad sequence of commands.\r\n"
            elif access_passed == True and login_passed == True:
            #If previous command is USER and already logged in
                if comm == "PASS":
                #login to new user if currant command is PASS, no longer get 503 error
                    access_passed = False
                    return "230 Guest login OK.\r\n"
                else:
                #Error message if current command not PASS, get 503 error
                    return "503 Bad sequence of commands.\r\n"
            elif login_passed == True:
            #If already logged in and USER already has been passed (implied)
                if comm == "PASS":
                #If currant command is PASS, get Error message
                    return "503 Bad sequence of commands.\r\n"
                #If command is TYPE, prints out the proper output with proper type_code
                elif comm == "TYPE":
                    return "200 Type set to "+type_code1.strip()+ ".\r\n"
                #If command is PORT but there is an error, prints out Syntax error
                #If command is PORT and no error, prints out proper output
                elif comm == "PORT":
                    if port_error == True:
                        return "501 Syntax error in parameter.\r\n"
                    else:
                        port_passed = True
                        port_print = "200 Port command successful ("+port_string.strip()+")."
                        return port_print.strip()+"\r\n"
                #If command is RETR but there was an error with accessing/copying the file
                #or PORT hasn't been passed, prints out error
                #If no error, prints out proper output
                elif comm == "RETR":
                    if port_passed == False:
                        return "503 Bad sequence of commands.\r\n"
                    elif retr_error == True:
                        return "550 File not found or access denied.\r\n"
                    else:
                        num_files += 1
                        port_passed = False
                        return "150 File status okay.\r\n"
                       # return "250 Requested file action completed.\r\n"
        else:
            return "501 Syntax error in parameter.\r\n"
    else:
        return "500 Syntax error, command unrecognized.\r\n"


#Setting up the Connection server socket using the Server's port number
port = int(sys.argv[1])
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server_socket.bind(('',port))
server_socket.listen(1)

#Begin accepting connections
#Incoming messages sent through server_reply method in order to get and send back proper response
#Special if-statement conditions for Quit and successful RETR
while True:
    con_socket, addr = server_socket.accept()
    sentence = "220 COMP 431 FTP server ready.\r\n"
    sys.stdout.write(sentence)
    con_socket.send(sentence.encode())
    while True:
        sentence = con_socket.recv(1024).decode()
        sys.stdout.write(sentence)
        line = server_reply(sentence)
        sys.stdout.write(line)
        con_socket.send(line.encode())
        if line == "221 Goodbye.\r\n":
            con_socket.close()
            break
        elif line[0:3] == "150":
            #Send the file being retrieved to the client
            #Print and send proper response and replies
            try:
                ftpdata_sock = socket(AF_INET, SOCK_STREAM)
                ftpdata_sock.connect((data_ip, data_port))
                with open(file_name, 'rb') as f:
                    contents = f.read()
                ftpdata_sock.sendall(contents)
                ftpdata_sock.close()
                con_line = "250 Requested file action completed.\r\n"
                sys.stdout.write(con_line)
                con_socket.send(con_line.encode())
            except Exception:
                sentence = "425 Can not open data connection.\r\n"
                #Server prints and sends to server error message
                sys.stdout.write(sentence)
                con_socket.send(sentence.encode())
                continue

    con_socket.close()

