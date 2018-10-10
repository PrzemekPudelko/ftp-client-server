import sys, socket, os
#Przemyslaw Pudelko

#Initialize values of ascii characters to be compared with reply-text and CRLf
#Initialize values for min length requirements
#reply_parser performs the function of FTPClient2.py in HW3
def reply_parser(line):
    asc_cr = 13
    asc_lf = 10
    min_asc = 0
    max_asc = 127
    min_reply_len = 4
    min_crlf_len = 6
    #Set reply_code to first 3 characters--must be exactly this length
    #Check that reply_code is an integer and between 100 and 599
    reply_code = line[0:3]
    #request = line.upper()[0:7]
    if not(reply_code.isdigit()):
        print("ERROR -- reply-code")
    elif not(100 <= int(reply_code) <= 599):
        print("ERROR -- reply-code")
    #Check that there is a space after reply_code
    elif not(line[3] == " "):
        print("ERROR -- reply-code")
        # Check to ensure that length of the input is at least 5 [reply-code + space + reply-text] at least
        # Initialize boolean value text_error to False, indicating no issue with reply_text
        # Set reply_text to all characters between reply_code and CRLF, strip all spaces before 1st char
    elif len(line) > min_reply_len:
        text_error = False
        reply_text = line[4:-2]
        # Check that reply_text is a string, and a string in the definition of HW2's string
        if len(reply_text) == 0 or not (isinstance(reply_text, str)):
            print("ERROR -- reply-text")
        else:
            # Loop through each character, ensure that it's ascii value < 128 and it's not CR or LF
            # Set text_error to True if these parameters are not met
            for r in reply_text:
                if not (min_asc <= ord(r) <= max_asc) or ord(r) == asc_cr or ord(r) == asc_lf:
                    print("ERROR -- reply-text")
                    text_error = True
                    break
            # Only runs if there was no error with reply_text
            # crlf set to last 2 characters, ensure that they are CR and LF
            # If so, print correct response
            # Else, print CRLF error
            if text_error == False:
                # Check to see that the length of the input is at least 7
                if len(line) > min_crlf_len:
                    crlf = line[-2:]
                    if ord(crlf[0]) == asc_cr and ord(crlf[1]) == asc_lf:
                        print("FTP reply " + reply_code + " accepted. Text is: " + reply_text)
                    else:
                        print("ERROR -- <CRLF>")
                # Error if length of line is not long enough CRLF but includes reply-text
                else:
                    print("ERROR -- <CRLF>")
    # Error if length of line is not long enough to include reply-text
    else:
        print("ERROR -- reply-text")
    # System exits when for-loop completed


#Set a boolean value for wheter or not the CONNECT request has already been passed
#Set ascii values for the parameters of the elements in domain
#assign port_number and number of fiels in retr_files initially so they can be incremented
connect_passed = False
asc_A = 65
asc_Z = 90
asc_a = 97
asc_z = 122
asc_0 = 48
asc_9 = 57
num_files = 1
port_number = int(sys.argv[1])
#First ensure the first 4 letters are QUIT, then ensure only <EOL> could also be in the command
# loop through every line in the input
# print out every input request
# initially set request to be the length of CONNECT--easier to handle
for line in sys.stdin:
    sys.stdout.write(line)
    request = line.upper()[0:7]
    if request[0:4] == "QUIT":
        if len(line) > 5:
            print("ERROR -- request")
        #If CONNECT has not already been passed, Error message occurs
        #Otherwise, proper responses printed and program quits
        elif connect_passed == False:
            print("ERROR -- expecting CONNECT")
        else:
        #Quit is sent to the server, both the client socket and FTPClient.py program shut down
            print("QUIT accepted, terminating FTP client")
            message = "QUIT\r\n"
            sys.stdout.write(message)
            client_socket.send(message.encode())
            server_reply = client_socket.recv(1024).decode()
            reply_parser(server_reply)
            client_socket.close()
            sys.exit()
    #Else ensure that first 3 letters are GET, and ensure there's at least 1 space after
    elif request[0:3] == "GET":
        space1 = line[3]
        if not(space1 == " "):
            print("ERROR -- request")
        else:
            #Set pathname to all characters after <SP> and before <EOL>
            good_name = True
            pathname = line[4:-1]
            pathname = pathname.lstrip()
            max_asc = 127
            asc_cr = 13
            asc_lf = 10
            #Check each letter to ensure that they are not <CR> or <LF> and ascii value is not > 128
            #Set boolean parameter for pathname to false if otherwise
            for p in pathname:
               if not(ord(p) <= 127) or ord(p) == asc_cr or ord(p) == asc_lf:
                   print("ERROR -- pathname")
                   good_name = False
                   break
            #If pathname meets parameters and  CONNECT  has been passed:
            #Print initial message, retrieve host_address, change all "." to ",", append last 2 numbers
            #Last 2 numbers derived from operations on the port_number, initially gotten from sys.argv
            #Incrememnt port number by 1
            #Print out PORT and RETR commands
            #Setting up the welcoming socket using the client's ip address and port number
            if good_name == True:
                if connect_passed == True:
                    print("GET accepted for " + pathname)
                    my_ip = socket.gethostbyname(socket.gethostname())
                    host_address = my_ip.replace(".",",")
                    port_number_1 = port_number // 256
                    port_number_2 = port_number % 256
                    host_port = host_address + "," + str(port_number_1) + "," + str(port_number_2)
                    #Create the socket as though it were a temporary server
                    #Begin accepting connections once retrieve has successfully been sent
                    try:
                        welcoming_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        welcoming_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        welcoming_sock.bind(("", port_number))
                        welcoming_sock.listen(1)

                        #Print out PORT and RETR commands here and send them to FTPServer.py, then get reply
                        #Increment port number by 1
                        message = "PORT " + host_port + "\r\n"
                        sys.stdout.write(message)
                        client_socket.send(message.encode())
                        server_reply = client_socket.recv(1024).decode()
                        reply_parser(server_reply)
                        port_number += 1

                        message = "RETR " + pathname + "\r\n"
                        sys.stdout.write(message)
                        client_socket.send(message.encode())
                        server_reply = client_socket.recv(1024).decode()
                        reply_parser(server_reply)
                        #Set up data socket after receiving RETR 150 reply, receive file from Server
                        if(server_reply[0:3] == "150"):
                            data_sock, addr = welcoming_sock.accept()
                            new_dir = "retr_files"
                            new_file_path = new_dir + os.sep + "file" + str(num_files)
                            with open(new_file_path, 'wb') as f:
                                while True:
                                    data = data_sock.recv(1024)
                                    #FTP data socket closes once file is completely sent
                                    if len(data) == 0:
                                        data_sock.close()
                                        server_reply = client_socket.recv(1024).decode()
                                        reply_parser(server_reply)
                                        break
                                    f.write(data)
                            #increment file number received
                            num_files += 1
                    except socket.error as err:
                        print("GET failed, FTP-data port not allocated.")
                else:
                    #Print error message if CONNECT not passed yet
                    print("ERROR -- expecting CONNECT")
    #Else check to ensure that request is CONNECT, and ensure at least 1 <SP> after it
    elif request == "CONNECT":
        space1 = line[7]
        if not(space1 == " "):
            print("ERROR -- request")
        else:
            #Set value server_data to all characters after the first <SP>
            #If no <SP> anywhere in server_data, Error printed--need at least 1
            #Only do lstrip in case the second <SP> is present, but no server-port
            server_data = line[8:]
            server_data = server_data.lstrip()
            if not(" " in server_data):
                print("ERROR -- server-host")
            #If " " present, everything before is the server-host, everything after is the server-port
            elif " " in server_data:
                port_error = False
                for x in range(0,len(server_data)):
                    if server_data[x] == " ":
                        server_host = server_data[0:x]
                        space2 = server_data[x]
                        server_port = server_data[x+1:]
                        #Ensure no spaces after server_port, else ERROR occurs
                        server_port_test = server_port.lstrip()
                        server_port = server_port.strip()
                        #Check to make sure there are no extra spaces in server_port
                        #Else we set a boolean that activates an Error later on
                        if len(server_port_test) > len(server_port) + 1:
                            port_error = True
                        break
                #Ensure that the first character of the server-host is uppercase or lowercase  A to Z
                if not((asc_A <= ord(server_host[0]) <= asc_Z)  or (asc_a <= ord(server_host[0]) <= asc_z)):
                    print("ERROR -- server-host")
                #Ensure the last character is not a period
                elif server_host[-1] == ".":
                    print("ERROR -- server-host")
                elif not(server_host[-1] == "."):
                    #Ensure that every character after the first fits the proper parameters
                    for s in server_host[1:]:
                        if not(asc_A <= ord(s) <= asc_Z or asc_a <= ord(s) <= asc_z or asc_0 <= ord(s) <= asc_9 or s == "."):
                            print("ERROR -- server-host")
                            break
                    #Once server-host looks good, ensure that server-port is a number and there is no <SP> after server-port
                    if not(server_port.isdigit()) or port_error == True:
                        print("ERROR -- server-port")
                    #Ensure that server_port lies between 0 and 65535
                    elif 0 <= int(server_port) <= 65535:
                        #Ensure that 0 is not the first number if server_port is more than 1 digit
                        if len(server_port) > 1 and server_port[0] == "0":
                            print("ERROR -- server-port")
                        else:
                        #Print out all appropriate messages if CONNECT is passed
                            print("CONNECT accepted for FTP server at host " + server_host + " and port " + server_port)
                            serv_port = int(server_port)
                            #Send CONNECT command, and if successful, follow with USER, PASS, SYST and TYPE
                            try:
                                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                client_socket.connect((server_host, serv_port))
                                server_reply = client_socket.recv(1024).decode()
                                reply_parser(server_reply)

                                message = "USER anonymous\r\n"
                                sys.stdout.write(message)
                                client_socket.send(message.encode())
                                server_reply = client_socket.recv(1024).decode()
                                reply_parser(server_reply)

                                message = "PASS guest@\r\n"
                                sys.stdout.write(message)
                                client_socket.send(message.encode())
                                server_reply = client_socket.recv(1024).decode()
                                reply_parser(server_reply)

                                message = "SYST\r\n"
                                sys.stdout.write(message)
                                client_socket.send(message.encode())
                                server_reply = client_socket.recv(1024).decode()
                                reply_parser(server_reply)

                                message = "TYPE I\r\n"
                                sys.stdout.write(message)
                                client_socket.send(message.encode())
                                server_reply = client_socket.recv(1024).decode()
                                reply_parser(server_reply)

                                connect_passed = True

                            #Error message if connection fails
                            except Exception:
                                print("CONNECT failed")
                    #Error message if server_port is not in the proper bounds
                    else:
                        print("ERROR -- server-port")
    #Error message if the request is not GET, CONNECT, or QUIT
    else:
        print("ERROR -- request")
#Exit when all inputs are read
sys.exit()


